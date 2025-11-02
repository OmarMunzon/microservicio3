import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar variables de entorno
load_dotenv()

# Inicializar Firebase
cred = credentials.Certificate(os.getenv('SERVICE_ACCOUNT_KEY_PATH'))
firebase_admin.initialize_app(cred)
db = firestore.client()
