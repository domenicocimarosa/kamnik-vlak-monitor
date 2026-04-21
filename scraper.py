import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Pripravimo prazno vrstico za primer, ko ni zamud
    # To zagotovi, da se datoteka vedno ustvari
    prazni_podatki = {
        "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vlak": "SISTEM",
        "relacija": "Preverjanje",
        "zamuda": "0",
        "vzrok": "Ni zamud"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        vlak_data = []
        table = soup.find('table') 
        
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    relacija = cols[1].text.strip()
                    if "Kamnik" in relacija:
                        podatki = {
                            "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "vlak": cols[0].text.strip(),
                            "relacija": relacija,
                            "zamuda": cols[3].text.strip().replace(' min', '').strip(),
                            "vzrok": cols[4].text.strip() if len(cols) > 4 else ""
                        }
                        vlak_data.append(podatki)
        
        # Če ni dejanskih zamud, dodamo "sistemski" zapis, da datoteka obstaja
        if not vlak_data:
            vlak_data.append(prazni_podatki)
            
        df = pd.DataFrame(vlak_data)
        file_exists = os.path.isfile('zamude.csv')
        df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
        print("Zapis uspešen.")
            
    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
