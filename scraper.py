import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # Uporabimo javni vir podatkov o prometu, ki ga SŽ ne blokira
    # Ta API vrne vse aktivne dogodke v prometu v Sloveniji
    url = "https://www.promet.si/api/v1/trafficevents/all/sl-si"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        vlak_data = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if response.status_code == 200:
            events = response.json().get('data', [])
            
            for event in events:
                opis = str(event.get('description', ''))
                # Iščemo dogodke, ki omenjajo vlak, zamudo in progo proti Kamniku
                if "vlak" in opis.lower() and ("kamnik" in opis.lower() or "graben" in opis.lower()):
                    # Iz opisa poskušamo izluščiti minute (npr. "zamuda 20 minut")
                    import re
                    min_match = re.search(r'(\d+)\s*(?:minut|min)', opis)
                    minute = int(min_match.group(1)) if min_match else 5 # Če ne piše, predvidevamo vsaj 5 min
                    
                    vlak_data.append({
                        "cas_zajema": now_str,
                        "vlak": "Vlak SŽ",
                        "relacija": "Ljubljana - Kamnik",
                        "zamuda": minute,
                        "vzrok": opis[:100] # Vzamemo začetek opisa kot vzrok
                    })

        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates()
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Najdeno {len(df)} zamud preko Promet.si")
        else:
            # Kontrolni zapis
            df_empty = pd.DataFrame([{
                "cas_zajema": now_str,
                "vlak": "DARS_CHECK",
                "relacija": "Kamnik proga",
                "zamuda": 0,
                "vzrok": "Ni poročil o zamudah"
            }])
            df_empty.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print("Promet.si trenutno ne poroča o zamudah za te vlake.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
