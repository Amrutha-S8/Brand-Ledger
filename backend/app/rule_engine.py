import re
from typing import Optional, Dict, List, Tuple
from enum import Enum
from app.models import Rule, RuleCheckType, RuleStatus

class EvaluationResult(str, Enum):
    PASS = "pass"
    FAIL = "fail_with_evidence"
    UNABLE_TO_EVALUATE = "unable_to_evaluate"

class RuleEngineResponse:
    def __init__(self, result: EvaluationResult, spans: List[Tuple[int, int]] = None, explanation: str = ""):
        self.result = result
        self.spans = spans or []
        self.explanation = explanation

def evaluate_forbidden_term(content: str, spec: Dict) -> RuleEngineResponse:
    """
    Evaluates if a forbidden term appears in the content.
    spec: {"term": "string", "case_sensitive": bool}
    """
    try:
        term = spec.get("term", "")
        case_sensitive = spec.get("case_sensitive", False)
        
        if not term:
            return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation="No term specified")
        
        search_content = content if case_sensitive else content.lower()
        search_term = term if case_sensitive else term.lower()
        
        spans = []
        pattern = r'\b' + re.escape(search_term) + r'\b'
        
        for match in re.finditer(pattern, search_content, 0 if case_sensitive else re.IGNORECASE):
            spans.append((match.start(), match.end()))
        
        if spans:
            return RuleEngineResponse(EvaluationResult.FAIL, spans=spans, explanation=f"Found forbidden term(s)")
        else:
            return RuleEngineResponse(EvaluationResult.PASS, explanation=f"Term '{term}' not found")
    except Exception as e:
        return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation=f"Error: {str(e)}")

def evaluate_pattern(content: str, spec: Dict) -> RuleEngineResponse:
    """
    Evaluates if a regex pattern matches.
    spec: {"regex": "string", "match_type": "any" or "all"}
    """
    try:
        regex = spec.get("regex", "")
        if not regex:
            return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation="No regex specified")
        
        compiled = re.compile(regex)
        spans = []
        
        for match in compiled.finditer(content):
            spans.append((match.start(), match.end()))
        
        if spans:
            return RuleEngineResponse(EvaluationResult.FAIL, spans=spans, explanation=f"Pattern matched")
        else:
            return RuleEngineResponse(EvaluationResult.PASS, explanation=f"Pattern did not match")
    except re.error as e:
        return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation=f"Invalid regex: {str(e)}")
    except Exception as e:
        return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation=f"Error: {str(e)}")

def evaluate_required_if(content: str, spec: Dict) -> RuleEngineResponse:
    """
    If a trigger phrase appears, a required phrase must also appear.
    spec: {"trigger": "string", "required": "string"}
    """
    try:
        trigger = spec.get("trigger", "")
        required = spec.get("required", "")
        
        if not trigger or not required:
            return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation="Trigger or required phrase not specified")
        
        # Find trigger
        trigger_pattern = r'\b' + re.escape(trigger) + r'\b'
        trigger_matches = list(re.finditer(trigger_pattern, content, re.IGNORECASE))
        
        if not trigger_matches:
            return RuleEngineResponse(EvaluationResult.PASS, explanation=f"Trigger '{trigger}' not found")
        
        # Check if required phrase exists
        required_pattern = r'\b' + re.escape(required) + r'\b'
        required_matches = list(re.finditer(required_pattern, content, re.IGNORECASE))
        
        if required_matches:
            return RuleEngineResponse(EvaluationResult.PASS, explanation=f"Required phrase found with trigger")
        else:
            # Report all trigger occurrences as violations
            spans = [(m.start(), m.end()) for m in trigger_matches]
            return RuleEngineResponse(EvaluationResult.FAIL, spans=spans, 
                                    explanation=f"Trigger '{trigger}' found but required phrase '{required}' missing")
    except Exception as e:
        return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation=f"Error: {str(e)}")

def evaluate_max_count(content: str, spec: Dict) -> RuleEngineResponse:
    """
    Checks that a character appears at most N times.
    spec: {"character": "string", "max": int}
    """
    try:
        character = spec.get("character", "")
        max_count = spec.get("max", 0)
        
        if not character:
            return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation="Character not specified")
        
        matches = list(re.finditer(re.escape(character), content))
        count = len(matches)
        
        if count <= max_count:
            return RuleEngineResponse(EvaluationResult.PASS, explanation=f"Character appears {count} times (max {max_count})")
        else:
            # Report all excess occurrences (from max_count+1 onwards)
            spans = [(m.start(), m.end()) for m in matches[max_count:]]
            return RuleEngineResponse(EvaluationResult.FAIL, spans=spans,
                                    explanation=f"Character appears {count} times (max {max_count})")
    except Exception as e:
        return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation=f"Error: {str(e)}")

def evaluate_ai(content: str, spec: Dict) -> RuleEngineResponse:
    """
    AI-based evaluation (tone, judgment). Must be handled by AI provider.
    Returns UNABLE_TO_EVALUATE - caller must handle AI evaluation.
    """
    return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation="AI evaluation required")

def evaluate_rule(content: str, rule: Rule) -> RuleEngineResponse:
    """
    Route to appropriate evaluator based on rule type.
    """
    if rule.check_type == RuleCheckType.FORBIDDEN_TERM:
        return evaluate_forbidden_term(content, rule.spec)
    elif rule.check_type == RuleCheckType.PATTERN:
        return evaluate_pattern(content, rule.spec)
    elif rule.check_type == RuleCheckType.REQUIRED_IF:
        return evaluate_required_if(content, rule.spec)
    elif rule.check_type == RuleCheckType.MAX_COUNT:
        return evaluate_max_count(content, rule.spec)
    elif rule.check_type == RuleCheckType.AI:
        return evaluate_ai(content, rule.spec)
    else:
        return RuleEngineResponse(EvaluationResult.UNABLE_TO_EVALUATE, explanation=f"Unknown rule type: {rule.check_type}")

def evaluate_content(content: str, rules: List[Rule]) -> List[Dict]:
    """
    Evaluate content against all rules.
    Returns list of findings (only rule_engine verified findings, no AI yet).
    """
    findings = []
    
    for rule in rules:
        if rule.status != RuleStatus.APPROVED or not rule.is_current:
            continue
        
        response = evaluate_rule(content, rule)
        
        # Only report FAIL results
        if response.result == EvaluationResult.FAIL:
            for span_start, span_end in response.spans:
                findings.append({
                    "rule_id": rule.id,
                    "rule_code": rule.code,
                    "rule_version": rule.version,
                    "rule_name": rule.name,
                    "severity": rule.severity,
                    "span_start": span_start,
                    "span_end": span_end,
                    "span_text": content[span_start:span_end],
                    "explanation": response.explanation,
                    "verified_by": "rule_engine",
                    "source_quote": rule.source_quote,
                    "source_page": rule.source_page
                })
    
    return findings
