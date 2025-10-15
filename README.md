# API BRVM

Cette API permet de récupérer les données boursières de la Bourse Régionale des Valeurs Mobilières (BRVM).

## Déploiement sur Render.com

1. Créer un compte sur [render.com](https://render.com)
2. Cliquer sur "New +" → "Web Service"
3. Connecter votre repository GitHub
4. Configuration :
   - **Name**: `brvm-api` (ou le nom de votre choix)
   - **Environment**: `Python 3`
   - **Region**: Choisir la région la plus proche
   - **Branch**: `main` (ou la branche principale)
   - **Root Directory**: `brvm_api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn brvm_api:app --host 0.0.0.0 --port $PORT`

## Utilisation depuis Excel

### Méthode 1 : Power Query (Recommandé)

1. Dans Excel, aller dans **Données** → **Obtenir des données** → **À partir d'autres sources** → **À partir du Web**
2. Entrer l'URL de votre API : `https://votre-api.render.com/api/brvm?symbols=BICC,ABJC&from_date=2024-01-01&to_date=2024-12-31`
3. Excel va détecter le JSON et vous pourrez transformer les données

### Méthode 2 : Fonction WEBSERVICE (Excel 365)

```excel
=WEBSERVICE("https://votre-api.render.com/api/brvm?symbols=BICC&from_date=2024-01-01")