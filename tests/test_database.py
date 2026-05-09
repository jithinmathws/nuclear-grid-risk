from sqlalchemy import text

from app.core.database import SessionLocal


def test_database_connection():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        db.close()