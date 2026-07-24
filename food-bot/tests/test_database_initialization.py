import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, SessionLocal, engine
from app.models import Stall


class DatabaseInitializationTests(unittest.TestCase):
    def test_initialize_database_creates_tables_and_seed_data(self):
        Base.metadata.drop_all(bind=engine)

        from app.database import initialize_database

        initialize_database()

        db = SessionLocal()
        try:
            stall_count = db.query(Stall).count()
            self.assertGreater(stall_count, 0)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
