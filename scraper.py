import requests
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7',
    }
    
    try:
        # 1. Pridobimo celotno surovo vsebino strani
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        html = response.text
        
        vlak_data = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Taktika "Magnet": Iskanje vzorcev direktno v HTML kodi, ki so značilni za tvoje slike
        # Iščemo karkoli, kjer se pojavi "Kamnik" ali "Graben" in v bližini "min"
        # Razbijemo HTML na manjše dele okoli ključne besede Kamnik
        delilnik = "Kamnik"
        deli = html.split(delilnik)
        
        for del_kode in deli[1:]: # Izpustimo prvi del pred prvim "Kamnik"
            # Vzamemo 500 znakov okoli besede Kamnik
            iskano_obmocje = del_kode[:500]
            
            # Iščemo minute zamude (npr. 21 min ali 22 min)
            min_match = re.search(r'(\d+)\s*min', iskano_obmocje)
            
            if min_match:
                minute = int(min_match.group(1))
                if minute > 0:
                    # Poskusimo najti še številko vlaka v bližini (npr. LP 3186)
                    vlak_match = re.search(r'(?:LP|vlak)\s*(\d+)', iskano_obmocje, re.IGNORECASE)
                    vlak_id = f"LP {vlak_match.group(1)}" if vlak_match else "LP ????"
                    
                    vlak_data.append({
                        "cas_zajema": now_str,
                        "vlak": vlak_id,
                        "relacija": "Ljubljana - Kamnik proga",
                        "zamuda": minute,
                        "vzrok": "Zaznano v kodi strani"
                    })

        # 3. Shranjevanje rezultatov
        if vlak_data:
            # Odstranimo dvojnike, ki se lahko pojavijo zaradi surovega branja
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"USPEH: Najdenih {len(df)} zamud!")
        else:
            # Če res ne najdemo ničesar, zapišemo kontrolno točko
            df_log = pd.DataFrame([{
                "cas_zajema": now_str,
                "vlak": "KONTROLA",
                "relacija": "Kamnik proga",
                "zamuda": 0,
                "vzrok": "Ni vizualnih zamud v kodi"
            }])
            df_log.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print("V kodi strani ni bilo najdenih vzorcev zamud.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
