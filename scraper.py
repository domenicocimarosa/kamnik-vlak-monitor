import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re

def extract_minutes(text):
    # Poišče številke v besedilu (npr. iz "24 min V ODHODU" dobi 24)
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else 0

def check_delays():
    url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        vlak_data = []
        # Poiščemo vse vrstice v tabelah
        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                vlak_id = cols[0].text.strip()
                relacija = cols[1].text.strip()
                stanje_tekst = cols[3].text.strip() # Tukaj piše "24 min V ODHODU"
                
                # Preverimo, če gre za kamniško progo (v obe smeri)
                if "Kamnik" in relacija or "Graben" in relacija:
                    minute = extract_minutes(stanje_tekst)
                    
                    # Zabeležimo le, če je dejansko zamuda (več kot 0 min)
                    if minute > 0:
                        podatki = {
                            "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "vlak": vlak_id,
                            "relacija": relacija,
                            "zamuda": minute,
                            "vzrok": cols[4].text.strip() if len(cols) > 4 else "Ni navedeno"
                        }
                        vlak_data.append(podatki)
        
        if vlak_data:
            df = pd.DataFrame(vlak_data)
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Uspešno zabeleženo {len(vlak_data)} zamud.")
        else:
            print("Trenutno ni aktivnih zamud za Kamnik.")
            
    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
