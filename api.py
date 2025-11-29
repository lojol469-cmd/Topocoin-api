from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from spl.token.instructions import transfer as spl_transfer, TransferParams as SplTransferParams, get_associated_token_address, create_associated_token_account
from spl.token.constants import TOKEN_PROGRAM_ID
import json
import os
import uvicorn

app = FastAPI(title="Topocoin Wallet API", description="API for Topocoin Wallet operations", version="1.0.0")

# Networks
networks = {
    "Devnet": "https://api.devnet.solana.com",
    "Mainnet": "https://api.mainnet-beta.solana.com"
}

# Wallets
wallets = {
    "Main_Wallet": "~/.config/solana/id.json",
    "Test_Wallet": "~/.config/solana/id_test.json",
    "Test_Wallet_2": "~/.config/solana/id_test2.json"
}

TOPOCOIN_MINT = "6zhMkoDvNg7cw8ojTH6BBdkYkDwery4GTRxZKVAPv2EW"

# Pydantic models
class SendSolRequest(BaseModel):
    network: str
    wallet: str
    recipient: str
    amount: float

class SendTpcRequest(BaseModel):
    network: str
    wallet: str
    recipient: str
    amount: float

class BalanceResponse(BaseModel):
    sol_balance: float
    tpc_balance: float

# Helper functions
def get_client(network: str):
    if network not in networks:
        raise HTTPException(status_code=400, detail="Invalid network")
    return Client(networks[network])

def load_keypair(wallet: str):
    if wallet not in wallets:
        raise HTTPException(status_code=400, detail="Invalid wallet")
    keypair_path = os.path.expanduser(wallets[wallet])
    if not os.path.exists(keypair_path):
        raise HTTPException(status_code=400, detail=f"Keypair not found for {wallet}")
    with open(keypair_path, 'r') as f:
        secret_key = json.load(f)
    return Keypair.from_bytes(bytes(secret_key))

def get_decimals(client: Client):
    try:
        mint_info = client.get_account_info(Pubkey.from_string(TOPOCOIN_MINT))
        if mint_info.value and mint_info.value.data:
            data = mint_info.value.data
            return data[44] if len(data) > 44 else 6
        return 6
    except:
        return 6

@app.get("/balance/{network}/{wallet}", response_model=BalanceResponse)
def get_balance(network: str, wallet: str):
    client = get_client(network)
    keypair = load_keypair(wallet)
    
    # SOL balance
    sol_balance_resp = client.get_balance(keypair.pubkey())
    sol_balance = sol_balance_resp.value / 1e9
    
    # TPC balance
    try:
        ata = get_associated_token_address(owner=keypair.pubkey(), mint=Pubkey.from_string(TOPOCOIN_MINT))
        tpc_balance_resp = client.get_token_account_balance(ata)
        tpc_balance = tpc_balance_resp.value.ui_amount or 0
    except:
        tpc_balance = 0
    
    return BalanceResponse(sol_balance=sol_balance, tpc_balance=tpc_balance)

@app.post("/send_sol")
def send_sol(request: SendSolRequest):
    client = get_client(request.network)
    keypair = load_keypair(request.wallet)
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    try:
        recent_blockhash = client.get_latest_blockhash().value.blockhash
        transaction = Transaction.new_signed_with_payer(
            [transfer(TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=Pubkey.from_string(request.recipient),
                lamports=int(request.amount * 1e9)
            ))],
            keypair.pubkey(),
            [keypair],
            recent_blockhash
        )
        resp = client.send_transaction(transaction)
        return {"success": True, "signature": str(resp.value)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/send_tpc")
def send_tpc(request: SendTpcRequest):
    client = get_client(request.network)
    keypair = load_keypair(request.wallet)
    decimals = get_decimals(client)
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    # Check balance
    try:
        ata_source = get_associated_token_address(owner=keypair.pubkey(), mint=Pubkey.from_string(TOPOCOIN_MINT))
        balance_resp = client.get_token_account_balance(ata_source)
        current_balance = balance_resp.value.ui_amount or 0
        if current_balance < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient Topocoin balance")
    except:
        raise HTTPException(status_code=400, detail="Unable to check balance")
    
    try:
        recipient_pubkey = Pubkey.from_string(request.recipient)
        mint_pubkey = Pubkey.from_string(TOPOCOIN_MINT)
        ata_dest = get_associated_token_address(owner=recipient_pubkey, mint=mint_pubkey)
        
        instructions = []
        
        # Ensure source ATA exists
        account_info = client.get_account_info(ata_source)
        if account_info.value is None:
            instructions.append(create_associated_token_account(
                payer=keypair.pubkey(),
                owner=keypair.pubkey(),
                mint=mint_pubkey
            ))
        
        # Ensure dest ATA exists
        account_info = client.get_account_info(ata_dest)
        if account_info.value is None:
            instructions.append(create_associated_token_account(
                payer=keypair.pubkey(),
                owner=recipient_pubkey,
                mint=mint_pubkey
            ))
        
        # Transfer
        instructions.append(spl_transfer(SplTransferParams(
            program_id=TOKEN_PROGRAM_ID,
            source=ata_source,
            dest=ata_dest,
            owner=keypair.pubkey(),
            amount=int(request.amount * (10 ** decimals))
        )))
        
        recent_blockhash = client.get_latest_blockhash().value.blockhash
        transaction = Transaction.new_signed_with_payer(
            instructions,
            keypair.pubkey(),
            [keypair],
            recent_blockhash
        )
        resp = client.send_transaction(transaction)
        return {"success": True, "signature": str(resp.value)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wallets")
def get_wallets():
    return {"wallets": list(wallets.keys())}

@app.get("/networks")
def get_networks():
    return {"networks": list(networks.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
