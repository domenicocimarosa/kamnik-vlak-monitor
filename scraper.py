import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # Vir: Sitra API (prijazen do avtomatizacije)
    url = "https://vlaki.sitra.si/api/v2/trains"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vlak_data = []

    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            for vlak in data.get('trains', []):
                relacija = vlak.get('relation', '')
                # Iskanje tvoje proge
                if any(x in relacija for x in ["Kamnik", "Graben"]):
                    zamuda = int(vlak.get('delay', 0))
                    if zamuda > 0:
                        vlak_data.append({
                            "cas_zajema": now_str,
                            "vlak": f"LP {vlak.get('number', '????')}",
                            "relacija": relacija,
                            "zamuda": zamuda,
                            "vzrok": "Sitra Real-time"
                        })

        # REŠITEV: Če ni zamud, ustvarimo vrstico, da datoteka OBSTAJA
        if not vlak_data:
            vlak_data.append({
                "cas_zajema": now_str,
                "vlak": "OSVEŽENO",
                "relacija": "Kamnik proga",
                "zamuda": 0,
                "vzrok": "Brez zamud"
            })

        df = pd.DataFrame(vlak_data)
        # Preverimo, če datoteka že obstaja za glavo (header)
        file_exists = os.path.isfile('zamude.csv')
        
        # 'a' (append) mode doda podatke, če datoteka ne obstaja, jo ustvari
        df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
        print("Uspeh: zamude.csv je bila posodobljena.")

    except Exception as e:
        print(f"Napaka: {e}")

if __name__ == "__main__":
    check_delays()
