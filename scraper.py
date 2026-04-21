import requests
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    
    # Ta seznam glav (headers) je zdaj identičen tistemu, ki ga pošlje pravi brskalnik
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7',
        'Referer': 'https://potniski.sz.si/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # Poskusimo dobiti stran z vsemi brskalniškimi parametri
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        html = response.text
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vlak_data = []

        # Diagnostika: če je koda še vedno kratka, nas še vedno blokirajo
        dolzina = len(html)
        
        # Iskanje po tvojem vzorcu: številka vlaka LP in nato minute v bližini
        # Regex išče LP XXXX, potem pa poljubnih 300 znakov, kjer se pojavi "min"
        patterns = re.findall(r'(LP\s*\d+)(.{1,300}?)(\d+)\s*min', html, re.DOTALL)
        
        for p_vlak, p_vmes, p_min in patterns:
            if "Kamnik" in p_vmes or "Graben" in p_vmes or "Domžale" in p_vmes:
                vlak_data.append({
                    "cas_zajema": now_str,
                    "vlak": p_vlak,
                    "relacija": "Kamnik proga",
                    "zamuda": int(p_min),
                    "vzrok": "Zaznano z globokim skeniranjem"
                })

        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"KONČNO! Najdenih {len(df)} zamud.")
        else:
            # Če ne najde, zapišemo dolžino, da vidiva napredek
            df_diag = pd.DataFrame([{
                "cas_zajema": now_str,
                "vlak": "SIMULACIJA",
                "relacija": f"Koda: {dolzina}",
                "zamuda": 0,
                "vzrok": "Vzorci niso ujeti"
            }])
            df_diag.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print(f"Koda dolžine {dolzina}, a brez ulovljenih zamud.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
