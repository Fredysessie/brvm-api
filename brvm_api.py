from fastapi import FastAPI, Query
from typing import List, Optional
from BRVM_scraper import BRVM_get
import pandas as pd
from fastapi.responses import StreamingResponse
import io

app = FastAPI(title="BRVM API", description="API publique BRVM utilisable dans Excel")

@app.get("/brvm")
def get_brvm_data(
    symbols: List[str] = Query(...),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    try:
        df = BRVM_get(symbols=symbols, from_date=from_date, to_date=to_date, verbose=False)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/brvm_csv")
def get_brvm_csv(
    symbols: List[str] = Query(...),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    df = BRVM_get(symbols=symbols, from_date=from_date, to_date=to_date, verbose=False)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=brvm.csv"
    return response
