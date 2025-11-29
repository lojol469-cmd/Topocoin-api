# Topocoin Wallet

A multi-user Solana wallet for Topocoin with FastAPI backend and Streamlit frontend.

## Architecture

- **Backend**: Python FastAPI API for user management and transactions (`backend/`)
- **Frontend**: Streamlit web app for user interface (`frontend/`)

## Quick Start with Docker Compose

1. Ensure Docker and Docker Compose are installed.

2. Clone the repository and navigate to the project directory.

3. Run the services:
   ```bash
   docker-compose up --build
   ```

4. Access the app:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## Manual Setup

See `backend/README.md` and `frontend/README.md` for individual setup instructions.

## Environment Variables

Configure `.env` files in `backend/` and `frontend/` directories as described in their respective READMEs.

## Deployment

- Deploy `backend/` to a cloud service like Render or Heroku
- Deploy `frontend/` to Streamlit Cloud
- Update `API_BASE_URL` in `frontend/.env` with the deployed backend URL

## Fonctionnalités

- API REST pour les opérations blockchain (balances, envois SOL et Topocoin)
- Interface web moderne avec Streamlit
- Support Devnet et Mainnet Solana
- Gestion automatique des Associated Token Accounts (ATA)
- Authentification multi-utilisateur sécurisée

## Sécurité

⚠️ **Important** : Les clés privées sont stockées chiffrées en base de données. Ne partagez jamais vos seed phrases.

## Tests

Voir le tutoriel intégré dans l'application Streamlit pour les étapes de test détaillées.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.