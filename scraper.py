import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # To je odprt vir, ki ga vzdržuje skupnost in ne blokira robotov
    url = "https://vlaki.sitra.si/api/v2/trains"
    
    try:
        response = requests.get(url, timeout=20)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vlak_data = []

        if response.status_code == 200:
            data = response.json()
            # Vir vrne seznam vlakov v realnem času
            for vlak in data.get('trains', []):
                relacija = vlak.get('relation', '')
                # Preverimo če gre za kamniško progo
                if "Kamnik" in relacija or "Graben" in relacija:
                    zamuda = int(vlak.get('delay', 0))
                    
                    if zamuda > 0:
                        vlak_data.append({
                            "cas_zajema": now_str,
                            "vlak": f"LP {vlak.get('number', '????')}",
                            "relacija": relacija,
                            "zamuda": zamuda,
                            "vzrok": "Zaznano prek Sitra API"
                        })

        if vlak_data:
            df = pd.DataFrame(vlak_data).drop_duplicates()
            file_exists = os.path.isfile('zamude.csv')
            df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
            print(f"Najdeno {len(df)} zamud.")
        else:
            # Kontrolni zapis
            df_status = pd.DataFrame([{
                "cas_zajema": now_str,
                "vlak": "SITRA_OK",
                "relacija": "Brez zamud",
                "zamuda": 0,
                "vzrok": "Vozni red b.p."
            }])
            df_status.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
            print("Povezava s Sitro deluje, zamud ni.")

    except Exception as e:
        print(f"Napaka pri povezavi: {e}")

if __name__ == "__main__":
    check_delays()
