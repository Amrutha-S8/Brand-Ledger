from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import User, Rule, UserRole, RuleStatus, RuleCheckType, SeverityLevel
from app.security import get_password_hash

def seed_database():
    """Seed the database with demo data."""
    init_db()
    db = SessionLocal()
    
    try:
        # Create demo users
        users_data = [
            {"email": "manager@demo.com", "password": "demo1234", "full_name": "Manager User", "role": UserRole.MANAGER},
            {"email": "reviewer@demo.com", "password": "demo1234", "full_name": "Reviewer User", "role": UserRole.REVIEWER},
            {"email": "creator@demo.com", "password": "demo1234", "full_name": "Creator User", "role": UserRole.CREATOR},
        ]
        
        users = {}
        for user_data in users_data:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if not user:
                user = User(
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            users[user_data["email"]] = user
        
        # Create demo rules
        rules_data = [
            {
                "code": "BR-001",
                "name": "No Competitor Names",
                "description": "Brand content must not mention competitor names",
                "check_type": RuleCheckType.FORBIDDEN_TERM,
                "spec": {"term": "competitor", "case_sensitive": False},
                "severity": SeverityLevel.HIGH,
                "status": RuleStatus.APPROVED,
                "source_quote": "Section 2.1 of Brand Guidelines",
                "source_page": "10",
            },
            {
                "code": "BR-002",
                "name": "Required Trademark Symbol",
                "description": "Brand name must be followed by ™ or ®",
                "check_type": RuleCheckType.REQUIRED_IF,
                "spec": {"trigger": "BrandName", "required": "™"},
                "severity": SeverityLevel.MEDIUM,
                "status": RuleStatus.APPROVED,
                "source_quote": "Section 3.1 of Brand Guidelines",
                "source_page": "15",
            },
            {
                "code": "BR-003",
                "name": "Exclamation Mark Limit",
                "description": "Maximum 2 exclamation marks per paragraph",
                "check_type": RuleCheckType.MAX_COUNT,
                "spec": {"character": "!", "max": 2},
                "severity": SeverityLevel.LOW,
                "status": RuleStatus.APPROVED,
                "source_quote": "Section 4.2 of Brand Guidelines",
                "source_page": "20",
            },
            {
                "code": "BR-004",
                "name": "Email Pattern",
                "description": "All emails must follow corporate domain",
                "check_type": RuleCheckType.PATTERN,
                "spec": {"regex": r".*@corporate\.com$"},
                "severity": SeverityLevel.MEDIUM,
                "status": RuleStatus.CANDIDATE,
                "source_quote": "Section 5 of Contact Guidelines",
                "source_page": "25",
            },
        ]
        
        for rule_data in rules_data:
            rule = db.query(Rule).filter(Rule.code == rule_data["code"]).first()
            if not rule:
                rule = Rule(
                    code=rule_data["code"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    check_type=rule_data["check_type"],
                    spec=rule_data["spec"],
                    severity=rule_data["severity"],
                    status=rule_data["status"],
                    source_quote=rule_data["source_quote"],
                    source_page=rule_data["source_page"],
                    created_by=users["manager@demo.com"].id,
                )
                db.add(rule)
        
        db.commit()
        print("✅ Database seeded with demo users and rules")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
