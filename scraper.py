import requests
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'sl-SI,sl;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        html = response.text
        
        # Iskanje vseh blokov, ki vsebujejo postajo Kamnik ali progo do Grabna
        # Uporabimo delitev po vrsticah tabele ali značilnih ločilih
        segments = re.split(r'<tr>|<div class="vlak-row">', html)
        vlak_data = []
        
        for seg in segments:
            # Preverimo če je v tem delu kode Kamnik
            if "Kamnik" in seg or "Graben" in seg:
                # 1. Izluščimo številko zamude (iščemo vzorec npr. 26 min)
                # Ta regex pokrije "26 min", "3 min", "PREDVIDENA ZAMUDA 10 min" itd.
                delay_match = re.search(r'(\d+)\s*min', seg)
                
                if delay_match:
                    minute = int(delay_match.group(1))
                    
                    # 2. Izluščimo številko vlaka (iščemo npr. LP 3187)
                    vlak_match = re.search(r'LP\s*(\d+)', seg)
                    vlak_id = f"LP {vlak_match.group(1)}" if vlak_match else "Vlak"
                    
                    # 3. Določimo relacijo
                    relacija = "Kamnik Graben - Ljubljana" if "Ljubljana" in seg else "Ljubljana - Kamnik Graben"
                    
                    vlak_data.append({
                        "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "vlak": vlak_id,
                        "relacija": relacija,
                        "zamuda": minute,
                        "vzrok": "Zabeležena zamuda v prometu"
                    })

        if vlak_data:
            # Odstranimo morebitne dvojnike v istem zajemu
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Uspeh! Zabeleženih {len(df)} zamud.")
        else:
            # Če ni zamud, zapišemo sistemsko vrstico, da vemo, da je scraper delal
            df_empty = pd.DataFrame([{
                "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vlak": "INFO",
                "relacija": "Kamnik proga",
                "zamuda": 0,
                "vzrok": "Vozni red b.p."
            }])
            file_exists = os.path.isfile('zamude.csv')
            df_empty.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print("Trenutno ni zaznanih zamud v kodi.")

    except Exception as e:
        print(f"Napaka pri zajemu: {e}")

if __name__ == "__main__":
    check_delays()
