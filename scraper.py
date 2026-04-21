import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        vlak_data = []
        # Iskanje tabele na strani SŽ
        table = soup.find('table') 
        
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    relacija = cols[1].text.strip()
                    # Preverimo obe smeri za Kamnik
                    if "Kamnik" in relacija:
                        podatki = {
                            "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "vlak": cols[0].text.strip(),
                            "relacija": relacija,
                            "zamuda": cols[3].text.strip().replace(' min', '').strip(),
                            "vzrok": cols[4].text.strip() if len(cols) > 4 else "Ni navedeno"
                        }
                        vlak_data.append(podatki)
        
        if vlak_data:
            df = pd.DataFrame(vlak_data)
            # Če datoteka še ne obstaja, jo ustvarimo z glavo, sicer samo dodajamo
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Uspešno zabeleženo {len(vlak_data)} vlakov.")
        else:
            # Če ni zamud, ustvarimo prazno vrstico, da vemo, da je scraper tekel
            print("Trenutno ni zamud na relaciji Kamnik.")
            
    except Exception as e:
        print(f"Napaka pri zajemu: {e}")

if __name__ == "__main__":
    check_delays()
