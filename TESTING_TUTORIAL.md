# Tutoriel de Test et Publication du Wallet Topocoin

## 📋 Vue d'ensemble
Ce tutoriel te guide étape par étape pour tester ton wallet Topocoin sur Devnet, puis le publier sur Mainnet. Tout se fait en sécurité sur Devnet d'abord.

---

## 🔧 Prérequis
Avant de commencer, assure-toi d'avoir :
- Solana CLI installé (`solana --version` → v1.18.26+)
- Rust et Cargo installés
- Python avec Streamlit et les dépendances (`pip install -r requirements.txt`)
- Un keypair Solana (`solana-keygen new` si besoin)
- Le logo généré (`logo.png` dans le dossier)

---

## 🚀 Étape 1 : Configuration Devnet
1. **Vérifie ta config Solana :**
   ```bash
   solana config get
   ```
   - RPC URL doit être : `https://api.devnet.solana.com`
   - Si pas, change :
     ```bash
     solana config set --url https://api.devnet.solana.com
     ```

2. **Obtiens des SOL de test :**
   ```bash
   solana airdrop 2
   ```
   - Répète si besoin pour avoir ~5 SOL (frais de transaction).

3. **Vérifie ton solde :**
   ```bash
   solana balance
   ```

---

## 🧪 Étape 2 : Test de Base du Wallet
1. **Lance l'app Streamlit :**
   ```bash
   cd /home/belikan/Topocoin
   streamlit run app.py
   ```
   - Ouvre l'URL affichée (généralement http://localhost:8501)

2. **Sélectionne Devnet** dans le dropdown en haut de l'app.

3. **Vérifie les balances :**
   - SOL : Doit afficher ton solde airdropé
   - TPC : 0 (pas encore de tokens mintés)

4. **Test envoi SOL :**
   - Entre une adresse de test (ex: ton propre wallet ou un autre)
   - Envoie 0.1 SOL
   - Vérifie la transaction sur [Solana Explorer Devnet](https://explorer.solana.com/?cluster=devnet)

---

## 🪙 Étape 3 : Mint et Test Topocoin
1. **Vérifie le mint existant :**
   - Le mint `7EFKe74t3cXSfiVuAMfxqKJBmPP6gLEGdkAar55W2uCP` existe déjà sur Devnet.
   - Si tu veux créer un nouveau, utilise `create_token.sh` :
     ```bash
     chmod +x create_token.sh
     ./create_token.sh
     ```
     - Mets à jour `TOPOCOIN_MINT` dans `app.py` avec le nouveau mint.

2. **Mint des Topocoin :**
   ```bash
   spl-token mint 7EFKe74t3cXSfiVuAMfxqKJBmPP6gLEGdkAar55W2uCP 1000000
   ```
   - 1 million de TPC (avec 6 décimales = 1000 TPC)

3. **Vérifie dans l'app :**
   - Rafraîchis les balances
   - TPC doit afficher 1000.00

4. **Test envoi Topocoin :**
   - Entre une adresse destinataire
   - Envoie 10 TPC
   - Vérifie la création d'ATA automatique si nécessaire
   - Confirme sur Explorer

5. **Test réception :**
   - Envoie des TPC à ton propre wallet depuis un autre compte
   - Ou utilise un second wallet pour tester

---

## 🔄 Étape 4 : Tests Avancés
1. **Test création ATA :**
   - Envoie à une adresse sans ATA pour TPC
   - L'app doit créer l'ATA automatiquement

2. **Test erreurs :**
   - Envoi sans SOL (frais)
   - Adresse invalide
   - Montant négatif
   - Vérifie les messages d'erreur

3. **Test cache et refresh :**
   - Balances se mettent à jour automatiquement (cache 30s)
   - Utilise le bouton "Refresh Balances"

---

## 🌐 Étape 5 : Passage sur Mainnet
**⚠️ ATTENTION : Mainnet = argent réel. Teste TOUT sur Devnet d'abord !**

1. **Crée un nouveau mint sur Mainnet :**
   ```bash
   solana config set --url https://api.mainnet-beta.solana.com
   ```
   - Obtiens des SOL réels sur un exchange (au moins 0.1 SOL pour frais)
   - Modifie `create_token.sh` pour Mainnet
   - Lance `./create_token.sh`
   - Nouveau mint address

2. **Upload metadata :**
   - Modifie `metadata.js` avec le nouveau mint
   - Lance `node metadata.js`
   - Vérifie sur [Solana Explorer Mainnet](https://explorer.solana.com/)

3. **Test sur Mainnet :**
   - Change le réseau dans l'app à "Mainnet"
   - Mets à jour `TOPOCOIN_MINT` dans `app.py`
   - Répète les tests (sans airdrop, avec SOL réels)

---

## 📤 Étape 6 : Publication de l'App
1. **Prépare l'app pour production :**
   - Change `SOLANA_RPC_URL` par défaut à Mainnet si souhaité
   - Ajoute des warnings pour Mainnet
   - Teste une dernière fois

2. **Hébergement :**
   - **Streamlit Cloud :** Upload sur [share.streamlit.io](https://share.streamlit.io)
     - Crée un repo GitHub avec ton code
     - Connecte Streamlit Cloud
   - **Vercel/Netlify :** Pour plus de contrôle
   - **Serveur propre :** Avec Docker

3. **Sécurité :**
   - N'expose jamais ta clé privée
   - Utilise des variables d'environnement pour les configs sensibles
   - Ajoute une confirmation pour les transactions Mainnet

4. **Promotion :**
   - Partage le lien de ton wallet
   - Documente sur GitHub
   - Annonce sur les réseaux crypto

---

## 🐛 Dépannage
- **Erreur "insufficient funds" :** Airdrop plus de SOL
- **Mint pas trouvé :** Vérifie l'adresse et le réseau
- **ATA erreur :** L'app gère automatiquement, sinon manuel avec `spl-token create-account`
- **App ne lance pas :** `pip install -r requirements.txt`

---

## ✅ Checklist Finale
- [ ] Devnet : Balances OK
- [ ] Devnet : Envoi SOL OK
- [ ] Devnet : Mint TPC OK
- [ ] Devnet : Envoi TPC OK
- [ ] Devnet : Réception OK
- [ ] Mainnet : Mint créé
- [ ] Mainnet : Metadata uploadée
- [ ] Mainnet : Tests OK
- [ ] App hébergée
- [ ] Lien partagé

Bonne chance avec Topocoin ! 🚀