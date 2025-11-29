from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
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
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Topocoin Wallet API", description="API for Topocoin Wallet operations with user management", version="1.0.0")

# Database
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client[os.getenv("MONGO_DB_NAME")]

# Security
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    wallet_address: str
    seed_phrase_encrypted: str = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    email: str
    wallet_address: str
    created_at: datetime

# Networks
networks = {
    "Devnet": "https://api.devnet.solana.com",
    "Mainnet": "https://api.mainnet-beta.solana.com"
}

TOPOCOIN_MINT = "6zhMkoDvNg7cw8ojTH6BBdkYkDwery4GTRxZKVAPv2EW"

# Pydantic models
class SendSolRequest(BaseModel):
    recipient: str
    amount: float

class SendTpcRequest(BaseModel):
    recipient: str
    amount: float

class BalanceResponse(BaseModel):
    sol_balance: float
    tpc_balance: float

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

# Helper functions
def get_client(network: str):
    if network not in networks:
        raise HTTPException(status_code=400, detail="Invalid network")
    return Client(networks[network])

def load_keypair_from_user(user):
    # For now, assume keypair is stored or generated
    # In production, users manage their own keys
    # This is a placeholder
    raise HTTPException(status_code=400, detail="Keypair management not implemented")

def get_decimals(client: Client):
    try:
        mint_info = client.get_account_info(Pubkey.from_string(TOPOCOIN_MINT))
        if mint_info.value and mint_info.value.data:
            data = mint_info.value.data
            return data[44] if len(data) > 44 else 6
        return 6
    except:
        return 6

# User endpoints
@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user
    user_dict = {
        "email": user.email,
        "hashed_password": hashed_password,
        "wallet_address": user.wallet_address,
        "seed_phrase_encrypted": user.seed_phrase_encrypted,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "wallet_address": current_user["wallet_address"],
        "created_at": current_user["created_at"]
    }

@app.get("/api/wallet/balance/{wallet_address}")
async def get_wallet_balance(wallet_address: str):
    # Use Devnet for now
    client = get_client("Devnet")
    
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
    
    return {"sol_balance": sol_balance, "tpc_balance": tpc_balance}

@app.post("/api/wallet/send_sol")
async def send_sol_api(request: dict):
    # Expect signedTransaction in request
    signed_tx_b64 = request.get("signedTransaction")
    if not signed_tx_b64:
        raise HTTPException(status_code=400, detail="Missing signedTransaction")
    
    client = get_client("Devnet")
    try:
        signed_tx_bytes = base64.b64decode(signed_tx_b64)
        tx = Transaction.from_bytes(signed_tx_bytes)
        result = client.send_transaction(tx)
        return {"signature": result.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/wallet/send_tpc")
async def send_tpc_api(request: dict):
    # Expect signedTransaction in request
    signed_tx_b64 = request.get("signedTransaction")
    if not signed_tx_b64:
        raise HTTPException(status_code=400, detail="Missing signedTransaction")
    
    client = get_client("Devnet")
    try:
        signed_tx_bytes = base64.b64decode(signed_tx_b64)
        tx = Transaction.from_bytes(signed_tx_bytes)
        result = client.send_transaction(tx)
        return {"signature": result.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wallets")
def get_wallets():
    return {"wallets": list(wallets.keys())}

@app.get("/networks")
def get_networks():
    return {"networks": list(networks.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
