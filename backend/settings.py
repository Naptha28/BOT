# settings.py

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
DOCTOR_JSON  = os.getenv("DOCTOR_JSON", "data/doctors.json")
DEBUG        = os.getenv("DEBUG", "false").lower() == "true"
