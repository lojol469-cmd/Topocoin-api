const { createUmi } = require('@metaplex-foundation/umi-bundle-defaults');
const { mplTokenMetadata } = require('@metaplex-foundation/mpl-token-metadata');
const { keypairIdentity, generateSigner, publicKey } = require('@metaplex-foundation/umi');
const { createNft, updateV1 } = require('@metaplex-foundation/mpl-token-metadata');
const fs = require('fs');
const path = require('path');
const { NFTStorage, File } = require('nft.storage');

// Replace with your NFT.Storage API key
const NFT_STORAGE_API_KEY = 'YOUR_NFT_STORAGE_API_KEY'; // Get from https://nft.storage/

async function uploadToIPFS(metadata) {
    const client = new NFTStorage({ token: NFT_STORAGE_API_KEY });
    const metadataBlob = new File([JSON.stringify(metadata)], 'metadata.json', { type: 'application/json' });
    const cid = await client.storeBlob(metadataBlob);
    return `https://ipfs.io/ipfs/${cid}`;
}

async function main() {
    // Prompt for inputs (in a real script, use readline or args)
    const name = process.argv[2] || 'Topocoin';
    const symbol = process.argv[3] || 'TPC';
    const description = process.argv[4] || 'A token for Topocoin ecosystem';
    const imagePath = process.argv[5] || './logo.png'; // Path to image file
    const mintAddress = process.argv[6]; // The mint address from create_token.sh

    if (!mintAddress) {
        console.error('Usage: node metadata.js <name> <symbol> <description> <imagePath> <mintAddress>');
        process.exit(1);
    }

    // Upload image to IPFS
    const client = new NFTStorage({ token: NFT_STORAGE_API_KEY });
    const imageFile = fs.readFileSync(imagePath);
    const imageBlob = new File([imageFile], path.basename(imagePath), { type: 'image/png' }); // Adjust type
    const imageCid = await client.storeBlob(imageBlob);
    const imageUrl = `https://ipfs.io/ipfs/${imageCid}`;

    // Create metadata JSON
    const metadata = {
        name,
        symbol,
        description,
        image: imageUrl,
        // Add more fields if needed
    };

    // Upload metadata to IPFS
    const metadataUrl = await uploadToIPFS(metadata);
    console.log('Metadata uploaded to:', metadataUrl);

    // Now set metadata on Solana using Metaplex
    const umi = createUmi('https://api.devnet.solana.com'); // Use mainnet-beta for production

    // Load your keypair (replace with your keypair path)
    const keypairFile = fs.readFileSync(path.join(process.env.HOME, '.config/solana/id.json'));
    const keypair = umi.eddsa.createKeypairFromSecretKey(new Uint8Array(JSON.parse(keypairFile)));
    umi.use(keypairIdentity(keypair));
    umi.use(mplTokenMetadata());

    // For SPL token, use updateV1 on the mint
    const mint = publicKey(mintAddress);

    await updateV1(umi, {
        mint,
        data: {
            name,
            symbol,
            uri: metadataUrl,
            sellerFeeBasisPoints: 0, // For tokens, usually 0
            creators: null,
        },
    }).sendAndConfirm(umi);

    console.log('Metadata set for mint:', mintAddress);
}

main().catch(console.error);