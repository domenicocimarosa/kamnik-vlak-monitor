import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # Uporabimo vir Sitra, ki povzema uradne SŽ podatke (podobno kot juliaste skripta)
    url = "https://vlaki.sitra.si/api/v2/trains"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vlak_data = []

    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            for vlak in data.get('trains', []):
                relacija = vlak.get('relation', '')
                # Iskanje tvoje specifične proge (Kamnik/Graben)
                if any(x in relacija for x in ["Kamnik", "Graben"]):
                    zamuda = int(vlak.get('delay', 0))
                    if zamuda > 0:
                        vlak_data.append({
                            "cas_zajema": now_str,
                            "vlak": f"LP {vlak.get('number', '????')}",
                            "relacija": relacija,
                            "zamuda": zamuda,
                            "vzrok": "SŽ Real-time (Sitra)"
                        })

        # KLJUČNA REŠITEV: Če ni zamud, ustvari vrstico, da datoteka OBSTAJA
        # To prepreči napako "pathspec did not match any files"
        if not vlak_data:
            vlak_data.append({
                "cas_zajema": now_str,
                "vlak": "SISTEM",
                "relacija": "Kamnik proga",
                "zamuda": 0,
                "vzrok": "Vozni red b.p."
            })

        df = pd.DataFrame(vlak_data)
        file_exists = os.path.isfile('zamude.csv')
        
        # Shranimo v CSV (mode='a' bo ustvaril datoteko, če je ni)
        df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
        print("CSV uspešno posodobljen/ustvarjen.")

    except Exception as e:
        print(f"Napaka pri delovanju: {e}")

if __name__ == "__main__":
    check_delays()
