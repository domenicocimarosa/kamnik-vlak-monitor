import requests
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    # Glavna stran z zamudami
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    
    # Dodamo še več "človeških" parametrov v glavo
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    try:
        # Uporabimo session, da ohranimo piškotke
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        html = response.text
        
        vlak_data = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Taktika: Najprej poiščemo vse številke vlakov (LP ali RG)
        # SŽ uporablja LP za lokalne vlake (tvoj primer LP 3186)
        vlak_matches = re.finditer(r'(LP|RG|IC)\s*(\d+)', html)
        
        for match in vlak_matches:
            # Za vsako najdeno številko vlaka pogledamo 500 znakov NAPREJ v kodi
            start = match.start()
            vsebina_okoli = html[start : start + 600]
            
            # Preverimo, če je v tem kosu besedila Kamnik ali Graben
            if "Kamnik" in vsebina_okoli or "Graben" in vsebina_okoli or "Domžale" in vsebina_okoli:
                # Iščemo minute (npr. "17 min" ali "26 min")
                delay_find = re.search(r'(\d+)\s*min', vsebina_okoli)
                
                if delay_find:
                    minute = int(delay_find.group(1))
                    if minute > 0:
                        vlak_id = f"{match.group(1)} {match.group(2)}"
                        vlak_data.append({
                            "cas_zajema": now_str,
                            "vlak": vlak_id,
                            "relacija": "Ljubljana - Kamnik proga",
                            "zamuda": minute,
                            "vzrok": "Zaznano v surovem tekstu"
                        })

        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"USPEH: Najdenih {len(df)} zamud!")
        else:
            # Če še vedno ne najde nič, bomo v CSV zapisali del surove kode za diagnostiko
            # (tako bom naslednjič vedel, kaj Python dejansko vidi)
            diag_info = "Prazno (Koda dolžine: " + str(len(html)) + ")"
            df_err = pd.DataFrame([{
                "cas_zajema": now_str,
                "vlak": "DIAGNOSTIKA",
                "relacija": diag_info,
                "zamuda": 0,
                "vzrok": "Stran vrnjena, a brez vzorcev"
            }])
            df_err.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print("Vzorci niso bili najdeni v HTML kodi.")

    except Exception as e:
        print(f"Kritična napaka: {e}")

if __name__ == "__main__":
    check_delays()
