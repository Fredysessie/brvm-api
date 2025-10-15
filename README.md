# BRVM API

Cette API permet de récupérer des données de la BRVM et de les utiliser dans Excel ou autre.

## 🚀 Lancer en local

```bash
uvicorn brvm_api:app --reload
```

## 🌍 Déploiement sur Render

1. Créer un compte gratuit sur https://render.com
2. Importer ce repo GitHub
3. Configurer le service web :
   - **Environment**: Python 3.11
   - **Start Command**: `uvicorn brvm_api:app --host 0.0.0.0 --port 10000`
4. Déployer 🚀

## 🔗 Exemple d'appel

- JSON :  
`https://votre-api.onrender.com/brvm?symbols=BOAB&from_date=2024-01-01&to_date=2024-12-31`

- CSV :  
`https://votre-api.onrender.com/brvm_csv?symbols=BOAB&from_date=2024-01-01&to_date=2024-12-31`
