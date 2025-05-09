import os 

DATABASE_URL = 'sqlite:///./mafia.db'
SECRET_KEY = os.urandom(32)
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

UPLOAD_FOLDER = "static/products/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
MAX_CONTENT_LENGTH = 2 * 1024 * 1024
ALLOWED_EXTENTIONS = {"png", "jpg", "jpeg", "gif"}

ALGORITHM = "HS256"