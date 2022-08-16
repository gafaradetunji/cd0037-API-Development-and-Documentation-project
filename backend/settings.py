from dotenv import load_dotenv
import os
load_dotenv()
DB_HOST=os.getenv("DB_HOST", '127.0.0.1:5432')
DB_NAME = os.environ.get("DB_NAME", 'trivia')
DB_USER=os.environ.get("DB_USER", 'postgres')
DB_PASSWORD = os.environ.get("DB_PASSWORD", 'miami')