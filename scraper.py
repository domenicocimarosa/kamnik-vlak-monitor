import requests
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    # SŽ pogosto uporablja ta pod-naslov za osveževanje podatkov
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        html = response.text
        
        # Zdaj iščemo VSE kar diši po zamudi v celotnem tekstu, 
        # ne glede na to kje v kodi se nahaja
        vlak_data = []
        
        # Poiščemo vse številke vlakov (LP ali RG) in besedilo okoli njih
        # Ta vzorec ujame vlak in do 200 znakov besedila za njim
        matches = re.findall(r'((?:LP|RG|IC|EC|EN|MV|MVG)\s*\d+).*?(?=LP|RG|IC|EC|EN|MV|MVG|$)', html, re.DOTALL)
        
        for match in matches:
            vlak_info = match
            # Preverimo če je v tem bloku Kamnik ali Graben
            if "Kamnik" in vlak_info or "Graben" in vlak_info:
                # Iščemo karkoli z "min"
                delay_match = re.search(r'(\d+)\s*min', vlak_info)
                if delay_match:
                    minute = int(delay_match.group(1))
                    
                    # Najdemo številko vlaka
                    vlak_id_match = re.search(r'(?:LP|RG|IC|EC|EN|MV|MVG)\s*\d+', vlak_info)
                    vlak_id = vlak_id_match.group(0) if vlak_id_match else "Vlak"
                    
                    vlak_data.append({
                        "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "vlak": vlak_id,
                        "relacija": "Ljubljana - Kamnik",
                        "zamuda": minute,
                        "vzrok": "Zaznana zamuda"
                    })

        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Uspeh! Najdenih {len(df)} zamud.")
        else:
            # Če res nič ne najde, vsaj zapišemo da smo preverili
            df_check = pd.DataFrame([{
                "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vlak": "PREVERJENO",
                "relacija": "Kamnik proga",
                "zamuda": 0,
                "vzrok": "Ni najdenih zamud v kodi"
            }])
            file_exists = os.path.isfile('zamude.csv')
            df_check.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print("V kodi strani ni najdenih aktivnih minut zamud.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
