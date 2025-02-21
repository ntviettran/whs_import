import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
  'DRIVER': os.getenv('DB_DRIVER'),
  'SERVER': os.getenv('DB_SERVER'),
  'DATABASE': os.getenv('DB_DATABASE'),
  'UID': os.getenv('DB_USERNAME'),
  'PWD': os.getenv('DB_PASSWORD')
}
