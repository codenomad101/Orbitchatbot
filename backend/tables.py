import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.models import Base
from database.config import engine

# This line ensures that all tables defined in models.py (and imported here)
# are created in the database.
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")