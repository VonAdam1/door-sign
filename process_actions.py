import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
import sys

# --- KONFIGURATION ---
HA_URL = "http://127.0.0.1:8123/api"
# KOM IHÅG: Klistra in din Long-Lived Access Token mellan citattecknen nedan
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhMWJkOTlmYWY0Njc0Y2FkYjM4N2NiYTM4YjU5YjU1ZiIsImlhdCI6MTc2OTI5NTE4MywiZXhwIjoyMDg0NjU1MTgzfQ.jT7YRSm3UH1IWzt5va__JX67QFo1yNKQ3tbDmz8iVFE"

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_dir, 'serviceAccountKey.json')
    log_file = os.path.join(current_dir, 'bridge_debug.log')

    def log(msg):
        with open(log_file, "a") as f:
            f.write(f"{msg}\n")
        print(msg)

    log("--- Bryggan startar ---")

    if not os.path.exists(key_path):
        log(f"FEL: Hittar inte serviceAccountKey.json på: {key_path}")
        sys.exit(1)

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        doc_ref = db.collection('doorsign').document('settings')
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            last_action = data.get('lastAction', '')
            
            last_processed_file = os.path.join(current_dir, 'last_processed.txt')
            processed_action = ""
            if os.path.exists(last_processed_file):
                with open(last_processed_file, 'r') as f:
                    processed_action = f.read().strip()

            if last_action and last_action != processed_action:
                log(f"Ny handling upptäckt: {last_action}")
                
                # Trigga notisen
                if "test_notification" in last_action:
                    log("Triggar automation: ask_adam_if_working")
                    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
                    r = requests.post(f"{HA_URL}/services/automation/trigger", 
                                     headers=headers, 
                                     json={"entity_id": "automation.dorrskylt_fraga_om_hemarbete_2"})
                    log(f"HA svarade: {r.status_code}")
                
                # Trigga reset
                elif "reset_system" in last_action:
                    log("Nollställer systemet...")
                    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
                    requests.post(f"{HA_URL}/services/input_boolean/turn_off", headers=headers, json={"entity_id": "input_boolean.adam_jobbar_hemma"})
                    requests.post(f"{HA_URL}/services/shell_command/update_door_sign_auto", headers=headers)

                with open(last_processed_file, 'w') as f:
                    f.write(last_action)
            else:
                log("Ingen ny handling.")
        else:
            log("Dokumentet 'settings' saknas i Firebase.")

    except Exception as e:
        log(f"KRASCH: {str(e)}")

if __name__ == "__main__":
    main()