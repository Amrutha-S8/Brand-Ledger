from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

class UserRole(str, PyEnum):
    MANAGER = "manager"
    REVIEWER = "reviewer"
    CREATOR = "creator"

class RuleStatus(str, PyEnum):
    DRAFT = "draft"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    DEPRECATED = "deprecated"

class RuleCheckType(str, PyEnum):
    FORBIDDEN_TERM = "forbidden_term"
    PATTERN = "pattern"
    REQUIRED_IF = "required_if"
    MAX_COUNT = "max_count"
    AI = "ai"

class SeverityLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CREATOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(Text)
    check_type = Column(Enum(RuleCheckType))
    spec = Column(JSON)  # Rule configuration
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MEDIUM)
    status = Column(Enum(RuleStatus), default=RuleStatus.DRAFT)
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True)
    source_quote = Column(Text)
    source_page = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    rule_id = Column(Integer, ForeignKey("rules.id"))
    severity = Column(Enum(SeverityLevel))
    span_start = Column(Integer)
    span_end = Column(Integer)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    decision = Column(String)  # "accept_finding", "reject_finding", "override_rule"
    reason = Column(Text)
    decided_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
