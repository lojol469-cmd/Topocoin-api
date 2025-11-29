import streamlit as st
import requests
import os
from solders.keypair import Keypair
import base64

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# API configuration
# API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

# Custom CSS for modern design
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .balance {
        font-size: 24px;
        font-weight: bold;
        color: #28a745;
    }
    .header {
        text-align: center;
        color: #007bff;
    }
</style>
""", unsafe_allow_html=True)



# Initialize Solana client (for decimals, but can be removed if not needed)
# client = Client(SOLANA_RPC_URL)

# Function to get token decimals (can be removed if API handles everything)
# @st.cache_data
# def get_token_decimals():
#     try:
#         mint_info = client.get_account_info(Pubkey.from_string(TOPOCOIN_MINT))
#         if mint_info.value and mint_info.value.data:
#             # Parse mint data, decimals at offset 44
#             data = mint_info.value.data
#             return data[44] if len(data) > 44 else 6
#         return 6
#     except:
#         return 6

# DECIMALS = get_token_decimals()

# Load keypair from file
def load_keypair():
    keypair_path = os.path.expanduser(wallets[selected_wallet])
    if os.path.exists(keypair_path):
        with open(keypair_path, 'r') as f:
            secret_key = json.load(f)
        return Keypair.from_bytes(bytes(secret_key))
    else:
        st.error(f"Keypair not found for {selected_wallet}. Please generate one with solana-keygen new.")
        return None

keypair = load_keypair()
if keypair:
    wallet_address = str(keypair.pubkey())
else:
    wallet_address = None

# Tabs
tab1, tab2 = st.tabs(["💰 Wallet", "📚 Tutorial"])

with tab1:
    if not keypair:
        st.stop()

    # Title with logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        st.image(logo_path, width=100)
        st.markdown("<h1 class='header'>Topocoin Official Wallet</h1>", unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center;'>{selected_wallet.replace('_', ' ')} Address: <code>{wallet_address}</code></p>", unsafe_allow_html=True)

    # Function to get balances directly from Solana
    @st.cache_data(ttl=30)  # Cache for 30 seconds
    def get_balances(wallet_address):
        try:
            client = Client(SOLANA_RPC_URL)
            # SOL balance
            sol_balance_resp = client.get_balance(Pubkey.from_string(wallet_address))
            sol_balance = sol_balance_resp.value / 1e9
            
            # TPC balance
            try:
                ata = get_associated_token_address(owner=Pubkey.from_string(wallet_address), mint=Pubkey.from_string(TOPOCOIN_MINT))
                tpc_balance_resp = client.get_token_account_balance(ata)
                tpc_balance = tpc_balance_resp.value.ui_amount or 0
            except:
                tpc_balance = 0
            
            return sol_balance, tpc_balance
        except Exception as e:
            st.error(f"Error fetching balances: {e}")
            return 0.0, 0.0

    # Balances section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💰 Balances")
    col1, col2 = st.columns(2)
    sol_balance, topocoin_balance = get_balances(wallet_address)
    with col1:
        st.markdown(f"<p class='balance'>SOL: {sol_balance:.4f}</p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p class='balance'>TPC: {topocoin_balance:.2f}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Send SOL section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📤 Send SOL")
    recipient = st.text_input("Recipient Address", key="sol_recipient")
    amount_sol = st.number_input("Amount (SOL)", min_value=0.0, key="sol_amount")
    if st.button("Send SOL", key="send_sol"):
        if recipient and amount_sol > 0:
            try:
                # Create transaction
                to_pubkey = Pubkey.from_string(recipient)
                transfer_ix = transfer(TransferParams(
                    from_pubkey=keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=int(amount_sol * 1e9)
                ))
                tx = Transaction().add(transfer_ix)
                client = Client(SOLANA_RPC_URL)
                recent_blockhash = client.get_recent_blockhash().value.blockhash
                tx.recent_blockhash = recent_blockhash
                tx.sign(keypair)
                
                # Send transaction directly
                result = client.send_transaction(tx)
                st.success(f"SOL sent successfully! Signature: {result.value}")
                st.cache_data.clear()  # Clear cache to refresh balances
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Invalid input")
    st.markdown("</div>", unsafe_allow_html=True)

    # Send Topocoin section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📤 Send Topocoin")
    recipient_tpc = st.text_input("Recipient Address", key="tpc_recipient")
    amount_tpc = st.number_input("Amount (TPC)", min_value=0.0, key="tpc_amount")
    if st.button("Send Topocoin", key="send_tpc"):
        if recipient_tpc and amount_tpc > 0:
            if topocoin_balance < amount_tpc:
                st.error("Insufficient Topocoin balance")
            else:
                try:
                    # Create SPL token transfer transaction
                    to_pubkey = Pubkey.from_string(recipient_tpc)
                    mint_pubkey = Pubkey.from_string(TOPOCOIN_MINT)
                    
                    from_ata = get_associated_token_address(keypair.pubkey(), mint_pubkey)
                    to_ata = get_associated_token_address(to_pubkey, mint_pubkey)
                    
                    transfer_ix = spl_transfer(SplTransferParams(
                        program_id=TOKEN_PROGRAM_ID,
                        source=from_ata,
                        destination=to_ata,
                        owner=keypair.pubkey(),
                        amount=int(amount_tpc * 10**6),  # Assuming 6 decimals
                        decimals=6
                    ))
                    
                    tx = Transaction().add(transfer_ix)
                    client = Client(SOLANA_RPC_URL)
                    recent_blockhash = client.get_recent_blockhash().value.blockhash
                    tx.recent_blockhash = recent_blockhash
                    tx.sign(keypair)
                    
                    # Send transaction directly
                    result = client.send_transaction(tx)
                    st.success(f"Topocoin sent successfully! Signature: {result.value}")
                    st.cache_data.clear()  # Clear cache
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.error("Invalid input")
    st.markdown("</div>", unsafe_allow_html=True)

    # Receive section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📥 Receive")
    st.write(f"Share your {selected_wallet.replace('_', ' ')} address to receive SOL or Topocoin:")
    st.code(wallet_address, language="")
    st.markdown("</div>", unsafe_allow_html=True)

    # Refresh button
    if st.button("🔄 Refresh Balances"):
        st.cache_data.clear()
        st.rerun()

with tab2:
    tutorial_content = """
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
   cd /home/belikan/Topocoin/frontend/frontend
   streamlit run app.py
   ```
   - Ouvre l'URL affichée (généralement http://localhost:8501)

2. **Sélectionne Devnet** dans la sidebar de l'app.

3. **Sélectionne "Test Wallet"** dans la sidebar (pour les tests sécurisés).

4. **Vérifie les balances :**
   - SOL : Doit afficher ton solde airdropé
   - TPC : 0 (pas encore de tokens mintés)

5. **Test envoi SOL :**
   - Entre une adresse de test (ex: ton propre wallet ou un autre)
   - Envoie 0.1 SOL
   - Vérifie la transaction sur [Solana Explorer Devnet](https://explorer.solana.com/?cluster=devnet)

---

## 🪙 Étape 3 : Mint et Test Topocoin
1. **Vérifie le mint existant :**
   - Le mint `6zhMkoDvNg7cw8ojTH6BBdkYkDwery4GTRxZKVAPv2EW` existe déjà sur Devnet.
   - Si tu veux créer un nouveau, utilise `create_token.sh` :
     ```bash
     chmod +x create_token.sh
     ./create_token.sh
     ```
     - Mets à jour `TOPOCOIN_MINT` dans `app.py` avec le nouveau mint.

2. **Mint des Topocoin :**
   ```bash
   spl-token mint 6zhMkoDvNg7cw8ojTH6BBdkYkDwery4GTRxZKVAPv2EW 1000000
   ```
   - 1 million de TPC (avec 6 décimales = 1000 TPC)

3. **Vérifie dans l'app :**
   - Rafraîchis les balances
   - TPC doit afficher 1000.00

4. **Test envoi Topocoin :**
   - Sélectionne "Test Wallet 2" dans la sidebar pour recevoir
   - Entre l'adresse du Test Wallet 2 comme destinataire
   - Envoie 10 TPC
   - Vérifie la création d'ATA automatique si nécessaire
   - Confirme sur Explorer

5. **Test réception :**
   - Bascule vers "Test Wallet 2" dans la sidebar
   - Vérifie que les 10 TPC sont arrivés
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
   - Change le réseau dans la sidebar à "Mainnet"
   - Sélectionne "Main Wallet" dans la sidebar (avec SOL réels)
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
"""
    st.markdown(tutorial_content)
