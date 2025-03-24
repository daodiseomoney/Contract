// Transaction handling with Keplr
async function createAndSignTransaction(fileData, userAddress, role) {
  try {
    console.log("Starting Keplr signing process...");
    console.log("File data:", fileData);
    console.log("User address:", userAddress);
    console.log("Role:", role);

    // Create transaction metadata
    const transactionId = fileData.transaction_id || "tx_1";
    const contentHash = fileData.content_hash;

    // Get chain information
    const chainId = "odiseotestnet_1234-1";
    console.log("Using chain ID:", chainId);
    
    // First step - ALWAYS suggest chain to Keplr before doing anything else
    // This is critical for the Keplr wallet to work with custom chains
    if (window.keplr) {
      try {
        console.log("Pre-registering Odiseo chain before transaction");
        await suggestOdiseoChain(chainId);
        console.log("Chain registration succeeded");
      } catch (regError) {
        console.error("Error registering chain:", regError);
        throw new Error(`Failed to register chain with Keplr: ${regError.message}`);
      }
    } else {
      console.error("Keplr wallet not available");
      throw new Error("Keplr wallet extension not detected. Please install Keplr and refresh the page.");
    }

    // Create sign doc using Amino format structure first
    // We'll convert this to Direct format in signWithKeplr
    const signDoc = {
      chain_id: chainId,
      account_number: String(await getAccountNumber(userAddress)),
      sequence: String(await getAccountSequence(userAddress)),
      fee: {
        amount: [{ denom: "uodis", amount: "2500" }],
        gas: "100000"
      },
      msgs: [
        // Using Amino format with type/value structure
        // This will be converted to Proto format for signDirect
        {
          type: "cosmos-sdk/MsgSend",
          value: {
            from_address: userAddress,
            to_address: "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
            amount: [{ denom: "uodis", amount: "1000" }]
          }
        }
      ],
      memo: `tx:${transactionId}|hash:${contentHash}|role:${role}`
    };
    
    console.log("Using signDirect instead of signAmino for Keplr transaction");

    // Log the complete sign doc for debugging
    console.log("Amino sign doc for Keplr:", JSON.stringify(signDoc, null, 2));

    // Sign the transaction with Keplr using the new function
    const signResponse = await signContract(chainId, userAddress, signDoc);


    if (!signResponse || !signResponse.signature) {
      throw new Error("Failed to get signature from Keplr (empty response)");
    }

    // Broadcast the signed transaction
    console.log("Broadcasting signed transaction...");
    let broadcastResult;
    try {
      broadcastResult = await broadcastTransaction(signResponse);
      console.log("Broadcast result:", broadcastResult);
    } catch (broadcastError) {
      console.error("Error broadcasting transaction:", broadcastError);
      throw new Error(`Failed to broadcast transaction: ${broadcastError.message}`);
    }

    // Create success response with transaction details
    return {
      success: true,
      transaction_id: transactionId,
      blockchain_tx_hash: broadcastResult.txhash,
      explorer_url: `https://explorer.odiseotestnet.com/tx/${broadcastResult.txhash}`
    };
  } catch (error) {
    // Enhanced error logging with detailed context
    const errorContext = {
      message: error.message,
      stack: error.stack,
      fullError: error,
      chainId: chainId,
      userAddress: userAddress,
      transactionId: fileData?.transaction_id,
      contentHash: fileData?.content_hash,
      timestamp: new Date().toISOString()
    };

    console.error("Keplr transaction error:", errorContext);

    // Try to get specific Keplr error information
    let keplrErrorDetails = "Unknown Keplr error";
    if (error.message.includes("User rejected") || error.message.includes("denied")) {
      keplrErrorDetails = "User rejected the transaction signing request";
    } else if (error.message.includes("Request rejected")) {
      keplrErrorDetails = "Keplr rejected the signing request";
    } else if (error.message.includes("not found")) {
      keplrErrorDetails = "Keplr wallet or account not found";
    } else if (error.message.includes("account") && error.message.includes("sequence")) {
      keplrErrorDetails = "Account sequence mismatch. Try refreshing the page and try again.";
    }

    // Create a more informative error for handling
    const enhancedError = new Error(`Transaction failed: ${error.message}`);
    enhancedError.details = {
      keplrErrorDetails,
      userAddress,
      chainId: chainId || "odiseotestnet_1234-1",
      transactionId: fileData?.transaction_id,
      timestamp: new Date().toISOString()
    };
    enhancedError.originalError = error;

    throw enhancedError;
  }
}

// Helper function to fetch account info from the chain
async function fetchAccountInfo(address) {
  try {
    const response = await fetch(`/api/account?address=${address}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to fetch account data");
    }

    const accountData = await response.json();
    return {
      account_number: String(accountData.account_number || "0"),
      address: address,
      sequence: String(accountData.sequence || "0")
    };
  } catch (error) {
    // Enhanced error logging for account fetching
    const errorContext = {
      message: error.message,
      stack: error.stack,
      fullError: error,
      address: address,
      endpoint: `/api/account?address=${address}`,
      timestamp: new Date().toISOString()
    };

    console.error("Error fetching account info:", errorContext);

    // Create more informative error
    const enhancedError = new Error(`Account info fetch failed: ${error.message}`);
    enhancedError.details = {
      address: address,
      timestamp: new Date().toISOString(),
      originalMessage: error.message
    };
    enhancedError.originalError = error;

    throw enhancedError;
  }
}

async function getAccountNumber(address) {
    const accountInfo = await fetchAccountInfo(address);
    return accountInfo.account_number;
}

async function getAccountSequence(address) {
    const accountInfo = await fetchAccountInfo(address);
    return accountInfo.sequence;
}


// Register Odiseo chain with Keplr
async function suggestOdiseoChain(chainId) {
  console.log("Suggesting Odiseo testnet chain to Keplr...");
  try {
    await window.keplr.experimentalSuggestChain({
      chainId: chainId, // Use the passed chainId
      chainName: "Odiseo Testnet",
      rpc: "https://odiseo.test.rpc.nodeshub.online",
      rest: "https://odiseo.test.api.nodeshub.online",
      bip44: {
        coinType: 118 // Standard Cosmos coin type
      },
      bech32Config: {
        bech32PrefixAccAddr: "odiseo",
        bech32PrefixAccPub: "odiseopub",
        bech32PrefixValAddr: "odiseovaloper",
        bech32PrefixValPub: "odiseovaloperpub",
        bech32PrefixConsAddr: "odiseovalcons",
        bech32PrefixConsPub: "odiseovalconspub"
      },
      currencies: [
        {
          coinDenom: "ODIS",
          coinMinimalDenom: "uodis",
          coinDecimals: 6
        }
      ],
      feeCurrencies: [
        {
          coinDenom: "ODIS",
          coinMinimalDenom: "uodis",
          coinDecimals: 6,
          gasPriceStep: {
            low: 0.01,
            average: 0.025,
            high: 0.04
          }
        }
      ],
      stakeCurrency: {
        coinDenom: "ODIS",
        coinMinimalDenom: "uodis",
        coinDecimals: 6
      }
    });
    console.log("Successfully suggested Odiseo testnet to Keplr");
    return true;
  } catch (error) {
    console.error("Failed to suggest Odiseo testnet to Keplr:", error);
    throw error;
  }
}

// Transaction handling with Keplr using Protobuf (Direct) signing
async function signWithKeplr(chainId, userAddress, signDoc) {
  try {
    // First, suggest the chain to Keplr
    await suggestOdiseoChain(chainId);
    console.log("Chain suggestion complete");
    
    // Enable Keplr for the chain
    await window.keplr.enable(chainId);
    console.log("Keplr enabled for chain");

    // Get the offline signer
    const offlineSigner = window.keplr.getOfflineSigner(chainId);
    console.log("Got offline signer");

    // Verify accounts
    const accounts = await offlineSigner.getAccounts();
    console.log("Accounts verified:", accounts.length);

    // Convert Amino messages to Proto format for DirectSigning
    const protoMsgs = signDoc.msgs.map(msg => {
      // Convert from Amino to Proto format
      return {
        typeUrl: "/cosmos.bank.v1beta1.MsgSend",
        value: {
          fromAddress: msg.value.from_address,
          toAddress: msg.value.to_address,
          amount: msg.value.amount
        }
      };
    });

    console.log("Converted to Proto messages for signDirect:", JSON.stringify(protoMsgs, null, 2));

    // Create a proper DirectSignDoc according to Keplr docs
    // https://docs.keplr.app/api/sign.html#request
    
    // For signDirect, we need to create properly encoded protocol buffer messages
    // Since we don't have actual protobuf encoding available in the browser,
    // we'll create Uint8Array representations that Keplr can parse
    
    // Convert object to binary format (simplified mock of protobuf encoding)
    const bodyObj = {
      messages: protoMsgs,
      memo: signDoc.memo
    };
    
    // Convert to text encoder for proper binary representation
    const encoder = new TextEncoder();
    const bodyBytes = encoder.encode(JSON.stringify(bodyObj));
    
    // Create auth info with fee information
    const authInfoObj = {
      fee: {
        amount: signDoc.fee.amount,
        gas_limit: signDoc.fee.gas // Use gas_limit instead of gasLimit for Cosmos SDK compatibility
      },
      signer_infos: [] // Empty for Keplr to fill in
    };
    
    const authInfoBytes = encoder.encode(JSON.stringify(authInfoObj));

    // Create the DirectSignDoc required by signDirect
    const directSignDoc = {
      bodyBytes,
      authInfoBytes,
      chainId,
      accountNumber: parseInt(signDoc.account_number)
    };

    console.log("Using signDirect with Keplr (Proto format)");
    console.log("DirectSignDoc for Keplr:", JSON.stringify(directSignDoc, null, 2));

    // Sign the transaction with signDirect
    const signResponse = await window.keplr.signDirect(
      chainId,
      userAddress,
      directSignDoc
    );

    console.log("Got signDirect response from Keplr:", signResponse);
    
    // For compatibility with the existing code expecting signAmino format
    // we'll transform the response to match the expected structure
    const compatResponse = {
      signed: {
        ...signDoc,
        // Keep the original messages for broadcasting
        msgs: signDoc.msgs
      },
      signature: {
        pub_key: { 
          type: "tendermint/PubKeySecp256k1",
          value: encodeToBase64(signResponse.pubKey)
        },
        signature: signResponse.signature
      }
    };
    
    console.log("Transformed response for compatibility:", compatResponse);
    return compatResponse;

  } catch (error) {
    console.error("Keplr signing error:", {
      message: error.message,
      stack: error.stack,
      fullError: error
    });
    throw error;
  }
}

// Helper function to encode data to base64
function encodeToBase64(data) {
  if (typeof data === 'string') {
    // If it's already a string, encode it directly
    return btoa(data);
  } else if (data instanceof Uint8Array) {
    // If it's a Uint8Array, convert to string and then encode
    return uint8ArrayToBase64(data);
  } else {
    // For other types, JSON stringify and encode
    return btoa(JSON.stringify(data));
  }
}

async function signContract(chainId, userAddress, signDoc) {
  console.log("Starting Keplr signing process...");
  return await signWithKeplr(chainId, userAddress, signDoc);
}

// Convert Uint8Array to base64 string
function uint8ArrayToBase64(uint8Array) {
  // Use browser-friendly approach
  let binary = '';
  const bytes = new Uint8Array(uint8Array);
  const len = bytes.byteLength;

  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }

  return window.btoa(binary);
}

// Helper function to convert message to Proto format
function convertAminoToProto(msg) {
  console.log("Converting message to Proto format:", msg);

  // We now use Amino format WITH type/value structure for signAmino
  // For broadcast, we need to convert from Amino format to Proto format

  // Handle direct object format for backward compatibility
  // Note: This format does NOT work with Keplr's signAmino and will cause errors
  if (msg.from_address && msg.to_address && msg.amount) {
    console.log("Processing direct format message (converting to Proto):", msg);

    // Add the typeUrl for Proto format
    return {
      typeUrl: "/cosmos.bank.v1beta1.MsgSend",
      value: {
        fromAddress: msg.from_address,
        toAddress: msg.to_address,
        amount: msg.amount
      }
    };
  }

  // For backward compatibility, handle Amino format with type/value structure
  if (msg.type && msg.value) {
    // Map Amino types to Proto typeUrls
    const typeUrlMapping = {
      'cosmos-sdk/MsgSend': '/cosmos.bank.v1beta1.MsgSend',
      // Add other message types as needed
    };

    // Get corresponding typeUrl from mapping
    const typeUrl = typeUrlMapping[msg.type];
    if (!typeUrl) {
      console.error('Unknown message type:', msg.type);
      throw new Error(`Unknown message type: ${msg.type}`);
    }

    console.log(`Converting Amino type '${msg.type}' to Proto typeUrl '${typeUrl}'`);

    // For MsgSend, convert snake_case to camelCase
    if (msg.type === 'cosmos-sdk/MsgSend') {
      return {
        typeUrl: typeUrl,
        value: {
          fromAddress: msg.value.from_address,
          toAddress: msg.value.to_address,
          amount: msg.value.amount
        }
      };
    }

    // For other message types, pass value as-is
    return {
      typeUrl: typeUrl,
      value: msg.value
    };
  }

  // Handle direct format with @type field (Proto format)
  if (msg["@type"]) {
    const typeUrl = msg["@type"];

    // Extract all fields except @type
    const value = {...msg};
    delete value["@type"];

    // For MsgSend with direct format, convert snake_case to camelCase
    if (typeUrl === "/cosmos.bank.v1beta1.MsgSend") {
      return {
        typeUrl: typeUrl,
        value: {
          fromAddress: msg.from_address,
          toAddress: msg.to_address,
          amount: msg.amount
        }
      };
    }

    // For other message types with direct format
    return {
      typeUrl: typeUrl,
      value: value
    };
  }

  // If message is in an unknown format, log an error
  console.error("Unexpected message format:", msg);
  throw new Error("Unsupported message format");
}

// Helper function to broadcast the signed transaction
async function broadcastTransaction(signResponse) {
  try {
    console.log("Preparing to broadcast transaction...");
    console.log("Sign response:", signResponse);

    // Ensure public key is properly formatted for blockchain
    let pubKey = signResponse.signature.pub_key;

    // Format signature for network compatibility
    // Check if we have the public key in the correct format
    if (pubKey && !pubKey.type) {
      // Keplr sometimes returns pub_key as array or base64 string directly
      if (pubKey.key) {
        // Already has a key field (Keplr format)
        console.log("Found pub_key with key field:", pubKey);
      } else if (Array.isArray(pubKey) || pubKey instanceof Uint8Array) {
        // Need to convert Uint8Array to base64
        const keyBase64 = uint8ArrayToBase64(pubKey);
        console.log("Converted pub_key from array to base64:", keyBase64);
        pubKey = {
          type: "tendermint/PubKeySecp256k1",
          value: keyBase64
        };
      } else if (typeof pubKey === 'string') {
        // Already a string (might be base64)
        console.log("Using string pub_key:", pubKey);
        pubKey = {
          type: "tendermint/PubKeySecp256k1",
          value: pubKey
        };
      } else {
        console.log("Using pubkey as-is:", pubKey);
      }
    }

    // Make sure signature is a string
    let signature = signResponse.signature.signature;
    if (signature instanceof Uint8Array) {
      signature = uint8ArrayToBase64(signature);
      console.log("Converted signature to base64:", signature);
    }

    // Convert Amino messages to Proto format
    const protoMsgs = signResponse.signed.msgs.map(msg => convertAminoToProto(msg));
    console.log("Converted messages to Proto format:", protoMsgs);

    // Prepare the transaction for broadcasting with properly formatted pub_key and Proto messages
    const broadcastBody = {
      tx: {
        msg: protoMsgs, // Using converted Proto messages
        fee: signResponse.signed.fee,
        signatures: [
          {
            pub_key: pubKey,
            signature: signature
          }
        ],
        memo: signResponse.signed.memo // Use the simple string memo
      },
      mode: "block" // Use "block" to wait for confirmation
    };

    console.log("Broadcasting transaction:", JSON.stringify(broadcastBody, null, 2));

    // Send to your backend API endpoint that will broadcast to the blockchain
    const response = await fetch("/api/broadcast", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(broadcastBody)
    });

    console.log("Broadcast response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error response text:", errorText);

      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        errorData = { error: "Failed to parse error response" };
      }

      throw new Error(errorData.error || `Failed to broadcast transaction: ${response.status}`);
    }

    const result = await response.json();
    console.log("Broadcast result:", result);
    return result;
  } catch (error) {
    // Enhanced error logging with as much detail as possible
    console.error("Error broadcasting transaction:", {
      message: error.message,
      stack: error.stack,
      fullError: error
    });

    // Try to extract more detailed error information
    let errorDetails = {
      message: error.message,
      type: error.name || 'Error',
      timestamp: new Date().toISOString()
    };

    // Enhanced error with more context
    const enhancedError = new Error(`Transaction broadcast failed: ${error.message}`);
    enhancedError.details = errorDetails;
    enhancedError.originalError = error;

    throw enhancedError;
  }
}

// Export functions
window.signContract = signContract;
export { createAndSignTransaction };