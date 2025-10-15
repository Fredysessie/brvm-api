import requests
import pandas as pd
import time
import re
from datetime import datetime, timedelta

def BRVM_get(symbols, from_date=None, to_date=None, verbose=True):
    # Defaults dates
    if from_date is None:
        start_date = pd.Timestamp.now() - pd.Timedelta(days=365)
    else:
        start_date = pd.to_datetime(from_date)
    if to_date is None:
        end_date = pd.Timestamp.now() - pd.Timedelta(days=1)
    else:
        end_date = pd.to_datetime(to_date)

    # Tickers valid list
    Symbole = [
        "ABJC","BICC","BNBC","BOAB","BOABF","BOAC","BOAM","BOAN","BOAS","CABC","CBIBF","CFAC",
        "CIEC","ECOC","ETIT","FTSC","NEIC","NSBC","NTLC","ONTBF","ORGT","ORAC","PALC","PRSC",
        "SAFC","SCRC","SDCC","SDSC","SEMC","SGBC","SHEC","SIBC","SICC","SIVC","SLBC","SMBC",
        "SNTS","SOGC","SPHC","STAC","STBC","SVOC","TTLC","TTLS","UNLC","UNXC"
    ]

    tickers = list({s.upper() for s in symbols})
    if "ALL" in tickers:
        tickers = Symbole

    if len(tickers) == 0:
        raise ValueError("The list of tickers is empty.")
    if start_date > end_date:
        raise ValueError("The start date must be before the end date.")

    # Filter by allowed symbols
    symbol_vec = [t for t in tickers if t in Symbole]
    if len(symbol_vec) == 0:
        raise ValueError("No valid tickers after filtering against Symbole list.")

    returns = pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume","Ticker"])

    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'priority': 'u=0, i',
    'referer': 'https://www.richbourse.com/common/mouvements/technique',
    'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
    }

    for tick in symbol_vec:
        if verbose:
            print("\n=== Processing:", tick, "===")
        url = f"https://www.richbourse.com/common/mouvements/technique/{tick}/status/200"
        try:
            resp = requests.get(url, timeout=15, headers=headers)
            if verbose:
                print("HTTP status:", resp.status_code)
            page = resp.text.splitlines()
            if verbose:
                print("len(page) =", len(page))
        except Exception as e:
            print(f"Request error for {tick}:", e)
            continue

        # Recherche améliorée des lignes de données
        vect_data = []
        for i, line in enumerate(page):
            line_stripped = line.strip()
            # Chercher les lignes data avec des tableaux de données
            if line_stripped.startswith("data:") and "[" in line_stripped and "]" in line_stripped:
                # Vérifier que c'est bien des données numériques et pas une fonction
                if "function" not in line_stripped and "highcharts_grouping_units" not in line_stripped:
                    vect_data.append(i)
        
        # Fallback: recherche plus large si nécessaire
        if len(vect_data) < 2:
            vect_data = [i for i, ln in enumerate(page) if ln.strip().startswith("data:") and "[" in ln]
        
        if verbose:
            print("vect_data indices (first 10):", vect_data[:10])

        if len(vect_data) < 1:
            print(f"Could not find valid 'data' lines for {tick}.")
            continue

        # Extraction des données OHLC (toujours le premier dataset)
        try:
            data1_line = page[vect_data[0]]
            data1_raw = data1_line.split("data:", 1)[1].strip().rstrip(',')
            if verbose:
                print("data1_raw prefix:", data1_raw[:300])
        except Exception as e:
            print("Error extracting OHLC data line for", tick, ":", e)
            continue

        # Recherche spécifique des données de volume
        data2_raw = None
        for i in vect_data[1:]:  # Commencer à partir du deuxième élément
            try:
                line = page[i]
                content = line.split("data:", 1)[1].strip().rstrip(',')
                # Vérifier si ce sont des données de volume (format [timestamp, volume])
                if "[" in content and "]" in content and "highcharts_grouping_units" not in content:
                    # Essayer de parser pour confirmer que c'est du volume
                    test_content = content.replace("[", "").replace("]", "").split(",")
                    if len(test_content) >= 2 and test_content[0].strip().isdigit() and test_content[1].strip().isdigit():
                        data2_raw = content
                        if verbose:
                            print("Found volume data at index", i)
                        break
            except:
                continue
        
        if data2_raw is None and verbose:
            print("No volume data found for", tick)

        # Parsing OHLC data
        try:
            # Nettoyage et préparation des données OHLC
            data1_clean = data1_raw.replace(" ", "").rstrip(',')
            data1_pieces = [s for s in data1_clean.split("],[") if s.strip()]
            
            rows = []
            for piece in data1_pieces:
                clean_piece = piece.replace("[", "").replace("]", "")
                parts = clean_piece.split(",")
                if len(parts) >= 5:
                    rows.append(parts[:5])
                else:
                    if verbose:
                        print("Skipping malformed OHLC row:", piece[:200])

            if len(rows) == 0:
                if verbose:
                    print("No valid OHLC rows parsed for", tick)
                continue

            df1 = pd.DataFrame(rows, columns=["Date","Open","High","Low","Close"])
            df1[["Open","High","Low","Close"]] = df1[["Open","High","Low","Close"]].apply(pd.to_numeric, errors='coerce')
            df1["Date"] = pd.to_numeric(df1["Date"], errors='coerce')
            df1 = df1.dropna(subset=["Date"])
            df1["Date"] = pd.to_datetime(df1["Date"] / 1000, unit='s')  # Conversion timestamp en datetime
        except Exception as e:
            print("Error parsing OHLC (data1) for", tick, ":", e)
            continue

        # Parsing Volume data (si disponible)
        df2 = pd.DataFrame()
        if data2_raw is not None:
            try:
                data2_clean = data2_raw.replace(" ", "").rstrip(',')
                data2_pieces = [s for s in data2_clean.split("],[") if s.strip()]
                
                d_dates = []
                d_vols = []
                for piece in data2_pieces:
                    clean_piece = piece.replace("[", "").replace("]", "")
                    parts = clean_piece.split(",")
                    if len(parts) >= 2:
                        d_dates.append(parts[0])
                        d_vols.append(parts[1])
                    else:
                        if verbose:
                            print("Skipping malformed Volume row:", piece[:200])

                if len(d_dates) > 0:
                    df2 = pd.DataFrame({
                        "Date": pd.to_numeric(d_dates, errors='coerce'), 
                        "Volume": pd.to_numeric(d_vols, errors='coerce')
                    })
                    df2 = df2.dropna(subset=["Date"])
                    df2["Date"] = pd.to_datetime(df2["Date"] / 1000, unit='s')
                else:
                    if verbose:
                        print("No valid Volume rows parsed for", tick)
            except Exception as e:
                print("Error parsing Volume (data2) for", tick, ":", e)
                # Continuer sans les données de volume

        # Merge OHLC avec Volume
        try:
            if not df2.empty:
                final = pd.merge(df1, df2, on="Date", how="left")
                # Remplir les volumes manquants avec 0
                final["Volume"] = final["Volume"].fillna(0)
            else:
                final = df1.copy()
                final["Volume"] = 0  # Ajouter colonne Volume avec des zéros
            
            if final.empty and verbose:
                print("Final dataframe is empty for", tick)
            
            # Aggregate duplicates
            if final["Date"].duplicated().any():
                final = final.groupby("Date", as_index=False).agg({
                    "Open":"mean", "High":"mean", "Low":"mean", "Close":"mean", "Volume":"mean"
                })
            
            final["Ticker"] = tick
            returns = pd.concat([returns, final], ignore_index=True)
            
            if verbose:
                print(f"Successfully processed {len(final)} rows for {tick}")
                
        except Exception as e:
            print("Error merging dataframes for", tick, ":", e)
            continue

        # small polite pause
        time.sleep(0.6)

    # Filter by requested date range
    if not returns.empty:
        returns["Date"] = pd.to_datetime(returns["Date"])
        returns = returns[(returns["Date"] >= start_date) & (returns["Date"] <= end_date)]

    if "Ticker" in returns.columns and returns["Ticker"].nunique() <= 1:
        returns = returns.drop(columns=["Ticker"])

    if verbose:
        print("Finished. Processed tickers:", ", ".join(symbol_vec))
    return returns.reset_index(drop=True)