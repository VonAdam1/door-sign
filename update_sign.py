import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys
import os

# 1. SETUP - Hitta rätt sökväg till nyckelfilen automatiskt
# Detta gör att skriptet hittar JSON-filen oavsett varifrån det körs
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(script_dir, "serviceAccountKey.json")

try:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"❌ Fel vid initiering av Firebase: {e}")
    sys.exit(1)

# 2. LÄS ARGUMENT
if len(sys.argv) < 2:
    print("Användning: python update_sign.py [home|auto|busy|free]")
    sys.exit(1)

ny_status = sys.argv[1]

# 3. UPPDATERA FIREBASE
try:
    doc_ref = db.collection(u'doorsign').document(u'settings')
    doc_ref.set({
        u'status': ny_status
    }, merge=True)
    print(f"✅ Status uppdaterad till: {ny_status}")
except Exception as e:
    print(f"❌ Fel vid uppdatering av Firestore: {e}")