#!/bin/bash

# Script to create and mint a Solana SPL token on devnet
# Assumes Solana CLI and spl-token-cli are installed and configured

echo "Topocoin Token Creation Script"
echo "=============================="

# Prompt for token details (with defaults)
SYMBOL=${1:-TPC}
DECIMALS=${2:-6}
MINT_AMOUNT=${3:-10000000}

echo ""
echo "Creating token with $DECIMALS decimals..."

# Create the token mint
MINT_OUTPUT=$(spl-token create-token --decimals $DECIMALS)
MINT=$(echo "$MINT_OUTPUT" | grep -oE "([A-Za-z0-9]{32,})")

if [ -z "$MINT" ]; then
    echo "Failed to create token. Output: $MINT_OUTPUT"
    exit 1
fi

echo "Token mint created: $MINT"

# Create associated account
ACCOUNT_OUTPUT=$(spl-token create-account $MINT)
ACCOUNT=$(echo "$ACCOUNT_OUTPUT" | grep -oE "([A-Za-z0-9]{32,})")

if [ -z "$ACCOUNT" ]; then
    echo "Failed to create account. Output: $ACCOUNT_OUTPUT"
    exit 1
fi

echo "Associated account created: $ACCOUNT"

# Mint tokens
echo "Minting $MINT_AMOUNT tokens..."
spl-token mint $MINT $MINT_AMOUNT $ACCOUNT

# Check supply
echo "Token supply:"
spl-token supply $MINT

# Check accounts
echo "Token accounts:"
spl-token accounts

# Secure the mint
echo "Disabling mint authority..."
spl-token authorize $MINT mint --disable

echo "Disabling freeze authority..."
spl-token authorize $MINT freeze --disable

echo ""
echo "Token creation complete!"
echo "Mint Address: $MINT"
echo "Associated Account: $ACCOUNT"
echo "Symbol: $SYMBOL"
echo "Decimals: $DECIMALS"
echo "Initial Supply: $MINT_AMOUNT"
echo ""
echo "Next steps: Add metadata using Metaplex tools."