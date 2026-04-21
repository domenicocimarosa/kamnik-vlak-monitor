import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # Ciljamo neposredno na API vir podatkov, ki ga uporablja njihov interaktivni zemljevid
    # Ta vir običajno vsebuje surove podatke o vseh vlakih v realnem času
    api_url = "https://potniski.sz.si/wp-json/sz-api/v1/trains-delays" 
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # 1. Poskusimo dobiti podatke preko API-ja
        response = requests.get(api_url, headers=headers, timeout=20)
        
        vlak_data = []
        
        if response.status_code == 200:
            data = response.json()
            # SŽ API vrne seznam vseh vlakov z zamudami
            for vlak in data:
                relacija = vlak.get('relation', '')
                if "Kamnik" in relacija or "Graben" in relacija:
                    zamuda = int(vlak.get('delay', 0))
                    if zamuda > 0:
                        vlak_data.append({
                            "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "vlak": f"LP {vlak.get('train_number', '????')}",
                            "relacija": relacija,
                            "zamuda": zamuda,
                            "vzrok": vlak.get('cause', 'Prometni razlogi')
                        })
        
        # 2. Če API ne vrne ničesar, uporabimo "rezervni plan" (iskanje po surovi vsebini z novo taktiko)
        if not vlak_data:
            backup_url = "https://potniski.sz.si/pomoc-uporabnikom-in-stanje-v-prometu/"
            res = requests.get(backup_url, headers=headers)
            # Iščemo vzorec, ki se pojavi v tvojih modrih okvirčkih v HTML kodi
            import re
            # Ta regex išče številko vlaka in zamudo v neposredni bližini v surovem HTML
            raw_matches = re.findall(r'(?:LP|vlak)\s*(\d+).*?(\d+)\s*min', res.text, re.DOTALL | re.IGNORECASE)
            for m_vlak, m_min in raw_matches:
                # Preverimo, če je ta del kode blizu besede Kamnik (v območju 500 znakov)
                if "Kamnik" in res.text[res.text.find(m_vlak)-250 : res.text.find(m_vlak)+250]:
                    vlak_data.append({
                        "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "vlak": f"LP {m_vlak}",
                        "relacija": "Kamnik proga",
                        "zamuda": int(m_min),
                        "vzrok": "Zaznano v HTML"
                    })

        # 3. Shranjevanje
        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates(subset=['vlak', 'zamuda'])
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"USPEH: Najdenih {len(df)} zamud!")
        else:
            # Zapišemo samo čas preverjanja, da vemo da sistem teče
            df_empty = pd.DataFrame([{
                "cas_zajema": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vlak": "OSVEŽENO",
                "relacija": "Brez zamud",
                "zamuda": 0,
                "vzrok": "Vozni red OK"
            }])
            df_empty.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print("Ni bilo najdenih aktivnih zamud za Kamnik.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
