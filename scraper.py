import requests
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    # Glavna stran z zamudami
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html_content = response.text
        
        # Razbijemo vsebino po vrsticah/blokih, da lažje iščemo
        blocks = re.split(r'</tr>|</div>', html_content)
        vlak_data = []
        
        for block in blocks:
            # Preverimo, če blok vsebuje Kamnik in besedo "min" (ki označuje zamudo)
            if ("Kamnik" in block or "Graben" in block) and "min" in block:
                # Očistimo HTML značke, da dobimo čisto besedilo
                clean_text = re.sub('<[^<]+?>', ' ', block)
                
                # Izvlečemo številko vlaka (npr. LP 3186)
                vlak_match = re.search(r'LP\s*\d+', clean_text)
                vlak_id = vlak_match.group(0) if vlak_match else "Vlak"
                
                # Izvlečemo minute zamude
                minute_match = re.search(r'(\d+)\s*min', clean_text)
                if minute_match:
                    minute = int(minute_match.group(1))
                    
                    podatki = {
                        "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "vlak": vlak_id,
                        "relacija": "Ljubljana - Kamnik",
                        "zamuda": minute,
                        "vzrok": "Zabeleženo na SŽ"
                    }
                    vlak_data.append(podatki)
        
        if vlak_data:
            # Odstranimo dvojnike (če isti vlak najde večkrat v kodi)
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Najdeno in shranjeno: {len(df)} zamud.")
        else:
            # Če ni zamud, zapišemo sistemsko vrstico
            df_prazno = pd.DataFrame([{
                "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vlak": "SISTEM",
                "relacija": "Brez zamud",
                "zamuda": 0,
                "vzrok": "Vse teče po voznem redu"
            }])
            file_exists = os.path.isfile('zamude.csv')
            df_prazno.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print("Zamud trenutno ni v kodi strani.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
