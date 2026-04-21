import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    # Uporabimo realen User-Agent, da nas ne blokirajo
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # Zagotovimo slovenske šumnike
        soup = BeautifulSoup(response.text, 'html.parser')
        
        vlak_data = []
        
        # Poiščemo VSE vrstice v vseh tabelah na strani
        all_rows = soup.find_all('tr')
        print(f"Najdenih vrstic na strani: {len(all_rows)}") # Za loge v GitHub Actions

        for row in all_rows:
            cols = row.find_all(['td', 'th']) # Preiščemo vse celice
            row_text = row.get_text().strip()
            
            # Preverimo, če vrstica vsebuje ključne besede za Kamnik
            if "Kamnik" in row_text or "Graben" in row_text:
                if len(cols) >= 4:
                    vlak_st = cols[0].get_text().strip()
                    relacija = cols[1].get_text().strip()
                    stanje = cols[3].get_text().strip()
                    vzrok = cols[4].get_text().strip() if len(cols) > 4 else ""

                    # Izluščimo minute (npr. iz "zamuda 15 min" dobi 15)
                    minute = 0
                    stevilke = re.findall(r'\d+', stanje)
                    if stevilke:
                        minute = int(stevilke[0])

                    # Zapišemo vse, kar je povezano s Kamnikom, da vidimo, če sploh kaj najde
                    podatki = {
                        "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "vlak": vlak_st,
                        "relacija": relacija,
                        "zamuda": minute,
                        "vzrok": vzrok
                    }
                    vlak_data.append(podatki)
                    print(f"Najden vlak: {vlak_st} z zamudo {minute} min")

        # Če smo karkoli našli, shranimo
        if vlak_data:
            df = pd.DataFrame(vlak_data)
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print("CSV uspešno posodobljen.")
        else:
            # Ustvarimo sistemski zapis, da vemo, da je scraper delal, a ni našel zamud
            print("Ni najdenih zamud za Kamnik.")
            df_prazno = pd.DataFrame([{
                "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vlak": "SISTEM",
                "relacija": "Brez zamud",
                "zamuda": 0,
                "vzrok": "Vse teče po voznem redu"
            }])
            file_exists = os.path.isfile('zamude.csv')
            df_prazno.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)

    except Exception as e:
        print(f"Kritična napaka: {e}")

if __name__ == "__main__":
    check_delays()
