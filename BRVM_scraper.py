import pandas as pd
import requests

def BRVM_get(symbols, from_date=None, to_date=None, verbose=False):
    # Exemple simple: retourne un DataFrame factice
    data = []
    for symbol in symbols:
        data.append({
            "symbol": symbol,
            "date": from_date if from_date else "2025-01-01",
            "price": 100,
            "volume": 1000
        })
    return pd.DataFrame(data)
