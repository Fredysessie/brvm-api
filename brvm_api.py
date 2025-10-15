from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from typing import List, Optional
from datetime import datetime
import BRVM_scraper

app = FastAPI(
    title="BRVM API",
    description="API pour récupérer les données boursières de la BRVM",
    version="1.0.0"
)

# Configuration CORS pour autoriser les appels depuis Excel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, restreindre aux domaines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API BRVM",
        "version": "1.0.0",
        "endpoints": {
            "donnees": "/api/brvm?symbols=BICC,ABJC&from_date=2024-01-01&to_date=2024-12-31",
            "symboles": "/api/symbols",
            "santé": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/symbols")
async def get_available_symbols():
    """Retourne la liste de tous les symboles disponibles"""
    symbols = [
        "ABJC","BICC","BNBC","BOAB","BOABF","BOAC","BOAM","BOAN","BOAS","CABC","CBIBF","CFAC",
        "CIEC","ECOC","ETIT","FTSC","NEIC","NSBC","NTLC","ONTBF","ORGT","ORAC","PALC","PRSC",
        "SAFC","SCRC","SDCC","SDSC","SEMC","SGBC","SHEC","SIBC","SICC","SIVC","SLBC","SMBC",
        "SNTS","SOGC","SPHC","STAC","STBC","SVOC","TTLC","TTLS","UNLC","UNXC"
    ]
    return {"symbols": symbols}

@app.get("/api/brvm")
async def get_brvm_data(
    symbols: str = Query(..., description="Symboles séparés par des virgules, ou 'ALL' pour tous les symboles"),
    from_date: Optional[str] = Query(None, description="Date de début (format: YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Date de fin (format: YYYY-MM-DD)"),
    verbose: bool = Query(False, description="Mode verbeux")
):
    """
    Récupère les données boursières BRVM pour les symboles spécifiés
    """
    try:
        # Conversion de la chaîne de symboles en liste
        symbols_list = [s.strip().upper() for s in symbols.split(",")]
        
        # Appel de la fonction BRVM_get
        df = BRVM_scraper.BRVM_get(
            symbols=symbols_list,
            from_date=from_date,
            to_date=to_date,
            verbose=verbose
        )
        
        # Conversion du DataFrame en format JSON
        if df.empty:
            return JSONResponse(
                status_code=404,
                content={"error": "Aucune donnée trouvée pour les critères spécifiés"}
            )
        
        # Conversion en format adapté pour Excel
        result = {
            "metadata": {
                "symbols": symbols_list,
                "from_date": from_date,
                "to_date": to_date,
                "total_records": len(df),
                "date_range": {
                    "start": df["Date"].min().strftime("%Y-%m-%d") if not df.empty else None,
                    "end": df["Date"].max().strftime("%Y-%m-%d") if not df.empty else None
                }
            },
            "data": df.to_dict("records")
        }
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {str(e)}")

@app.get("/api/brvm/csv")
async def get_brvm_data_csv(
    symbols: str = Query(..., description="Symboles séparés par des virgules, ou 'ALL' pour tous les symboles"),
    from_date: Optional[str] = Query(None, description="Date de début (format: YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Date de fin (format: YYYY-MM-DD)")
):
    """
    Retourne les données au format CSV pour Excel
    """
    try:
        symbols_list = [s.strip().upper() for s in symbols.split(",")]
        
        df = BRVM_scraper.BRVM_get(
            symbols=symbols_list,
            from_date=from_date,
            to_date=to_date,
            verbose=False
        )
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée")
        
        # Retourner en CSV
        csv_content = df.to_csv(index=False)
        
        return JSONResponse(
            content={"csv": csv_content},
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)