import requests
import pandas as pd
import time

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

    symbol_vec = [t for t in tickers if t in Symbole]
    if len(symbol_vec) == 0:
        raise ValueError("No valid tickers after filtering against Symbole list.")

    returns = pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume","Ticker"])
    headers = {"User-Agent": "Mozilla/5.0"}

    for tick in symbol_vec:
        if verbose:
            print("Processing:", tick)
        url = f"https://www.richbourse.com/common/mouvements/technique/{tick}/status/200"
        try:
            resp = requests.get(url, timeout=15, headers=headers)
            page = resp.text.splitlines()
        except Exception as e:
            print(f"Request error for {tick}:", e)
            continue

        vect_data = [i for i, ln in enumerate(page) if ln.strip().startswith("data")]
        if len(vect_data) < 2:
            vect_data = [i for i, ln in enumerate(page) if "data:" in ln or '"data"' in ln]

        if len(vect_data) < 2:
            continue

        try:
            data1_raw = page[vect_data[0]].split(":", 1)[1].strip()
            data2_raw = page[vect_data[1]].split(":", 1)[1].strip()

            data1_pieces = [s.replace("[","").replace("]","") for s in data1_raw.replace(" ", "").split("],") if s.strip()!=""]
            rows = [p.split(",")[:5] for p in data1_pieces if len(p.split(",")) >= 5]
            df1 = pd.DataFrame(rows, columns=["Date","Open","High","Low","Close"])
            df1[["Open","High","Low","Close"]] = df1[["Open","High","Low","Close"]].apply(pd.to_numeric, errors='coerce')
            df1["Date"] = pd.to_numeric(df1["Date"], errors='coerce')
            df1 = df1.dropna(subset=["Date"])
            df1["Date"] = pd.to_datetime((df1["Date"] + 0.1) / 1000, unit='s')

            data2_pieces = [s.replace("[","").replace("]","") for s in data2_raw.replace(" ", "").split("],") if s.strip()!=""]
            d_dates = [p.split(",")[0] for p in data2_pieces if len(p.split(",")) >= 2]
            d_vols  = [p.split(",")[1] for p in data2_pieces if len(p.split(",")) >= 2]
            df2 = pd.DataFrame({"Date": pd.to_numeric(d_dates, errors='coerce'), "Volume": pd.to_numeric(d_vols, errors='coerce')})
            df2 = df2.dropna(subset=["Date"])
            df2["Date"] = pd.to_datetime((df2["Date"] + 0.1) / 1000, unit='s')

            final = pd.merge(df1, df2, on="Date", how="inner")
            if final["Date"].duplicated().any():
                final = final.groupby("Date", as_index=False).agg({
                    "Open":"mean", "High":"mean", "Low":"mean", "Close":"mean", "Volume":"mean"
                })
            final["Ticker"] = tick
            returns = pd.concat([returns, final], ignore_index=True)
        except Exception as e:
            print("Error parsing", tick, ":", e)
            continue

        time.sleep(0.6)

    if not returns.empty:
        returns["Date"] = pd.to_datetime(returns["Date"])
        returns = returns[(returns["Date"] >= start_date) & (returns["Date"] <= end_date)]

    if "Ticker" in returns.columns and returns["Ticker"].nunique() <= 1:
        returns = returns.drop(columns=["Ticker"])

    return returns.reset_index(drop=True)
