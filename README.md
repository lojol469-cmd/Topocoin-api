# Topocoin API et Wallet Streamlit

Ce projet contient une API FastAPI pour les opérations wallet Topocoin sur Solana, ainsi qu'une interface utilisateur Streamlit.

## Fonctionnalités

- API REST pour les opérations blockchain (balances, envois SOL et Topocoin)
- Interface web moderne avec Streamlit
- Support Devnet et Mainnet Solana
- Gestion automatique des Associated Token Accounts (ATA)

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/lojol469-cmd/Topocoin-api.git
cd Topocoin-api
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez vos wallets Solana :
```bash
# Créez les keypairs si nécessaire
solana-keygen new -o ~/.config/solana/id.json
solana-keygen new -o ~/.config/solana/id_test.json
solana-keygen new -o ~/.config/solana/id_test2.json
```

## Utilisation

### Démarrer l'API
```bash
python api.py
```
L'API sera disponible sur http://localhost:8000

### Démarrer l'interface Streamlit
```bash
streamlit run app.py
```
L'interface sera disponible sur http://localhost:8501

## Docker

### Construire l'image
```bash
docker build -t topocoin .
```

### Lancer le conteneur
```bash
docker run -p 8000:8000 -p 8501:8501 topocoin
```

## Endpoints API

- `GET /balance/{network}/{wallet}` - Obtenir les balances SOL et TPC
- `POST /send_sol` - Envoyer des SOL
- `POST /send_tpc` - Envoyer des Topocoin
- `GET /wallets` - Liste des wallets disponibles
- `GET /networks` - Liste des réseaux disponibles

## Configuration

- Mint Topocoin : `6zhMkoDvNg7cw8ojTH6BBdkYkDwery4GTRxZKVAPv2EW` (Devnet)
- Réseaux supportés : Devnet, Mainnet

## Sécurité

⚠️ **Important** : Ne partagez jamais vos clés privées. L'application charge les keypairs depuis des fichiers locaux sécurisés.

## Tests

Voir le tutoriel intégré dans l'application Streamlit pour les étapes de test détaillées.

## Licence

[Ajoutez votre licence ici]