import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # To je naslov, kjer zemljevid SŽ dobi surove podatke o zamudah
    url = "https://zemljevidi.sz.si/api/trains/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://zemljevidi.sz.si/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vlak_data = []

        if response.status_code == 200:
            # Zemljevid vrne JSON seznam vseh aktivnih vlakov
            vlaki = response.json()
            
            for v in vlaki:
                # Preverimo če gre za kamniško progo (št. vlakov 31xx so običajno Kamnik)
                vlak_st = str(v.get('train_number', ''))
                relacija = v.get('relation', '')
                zamuda = int(v.get('delay', 0))
                
                # Filtriramo za Kamnik ali relacije, ki jih vidiva na slikah
                if "Kamnik" in relacija or "Graben" in relacija or vlak_st.startswith('31'):
                    if zamuda > 0:
                        vlak_data.append({
                            "cas_zajema": now_str,
                            "vlak": f"LP {vlak_st}",
                            "relacija": relacija,
                            "zamuda": zamuda,
                            "vzrok": "Podatek iz zemljevida SŽ"
                        })

        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates()
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Najdeno {len(df)} zamud na zemljevidu.")
        else:
            # Kontrolni zapis, če zemljevid dela, a ni zamud
            df_status = pd.DataFrame([{
                "cas_zajema": now_str,
                "vlak": "ZEMLJEVID",
                "relacija": "Povezava OK",
                "zamuda": 0,
                "vzrok": "Ni aktivnih zamud na progi"
            }])
            df_status.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print("Zemljevid dosegljiv, zamud za Kamnik ni.")

    except Exception as e:
        # Če zemljevid zavrne povezavo, poskusiva še zadnji "hack"
        print(f"Zemljevid API napaka: {e}")

if __name__ == "__main__":
    check_delays()
