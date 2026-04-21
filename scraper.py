import requests
import pandas as pd
from datetime import datetime
import os

def check_delays():
    # To je neposreden URL do njihovega vira za zunanje aplikacije
    # Če ta ne deluje, imajo rezervni URL, ki ga uporablja njihov interaktivni zemljevid
    urls = [
        "https://potniski.sz.si/wp-json/sz-api/v1/trains-delays",
        "https://prostor.sz.si/api/train_delays/current"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    vlak_data = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # SŽ API običajno vrne seznam objektov
                for item in data:
                    # Preverimo, če je to vlak za Kamnik (relacije: Ljubljana, Kamnik, Graben, Črnuče)
                    relacija = str(item.get('relation', '')).lower()
                    if any(x in relacija for x in ['kamnik', 'graben', 'črnuče', 'domžale']):
                        zamuda = int(item.get('delay', 0))
                        
                        if zamuda > 0:
                            vlak_data.append({
                                "cas_zajema": now_str,
                                "vlak": f"LP {item.get('train_number', '????')}",
                                "relacija": item.get('relation', 'Kamnik proga'),
                                "zamuda": zamuda,
                                "vzrok": item.get('cause', 'Prometni razlogi')
                            })
                if vlak_data: break # Če najdemo podatke na prvem URL, ne iščemo dalje
        except:
            continue

    # Zapisovanje
    if vlak_data:
        df = pd.DataFrame(vlak_data).drop_duplicates()
        file_exists = os.path.isfile('zamude.csv')
        df.to_csv('zamude.csv', mode='a', index=False, header=not file_exists)
        print(f"USPEH: Zabeleženo {len(df)} zamud preko API.")
    else:
        # Če API ne vrne nič, naredimo zadnji obupen poskus s preprostim iskanjem po tekstu
        # ampak tokrat iščemo samo surovo besedilo v "headers" odzivu
        df_log = pd.DataFrame([{
            "cas_zajema": now_str,
            "vlak": "OSVEŽITEV",
            "relacija": "Sistemsko preverjanje",
            "zamuda": 0,
            "vzrok": "Ni zaznanih zamud na uradnem viru"
        }])
        df_log.to_csv('zamude.csv', mode='a', index=False, header=not os.path.isfile('zamude.csv'))
        print("API trenutno ne poroča o zamudah za Kamnik.")

if __name__ == "__main__":
    check_delays()
