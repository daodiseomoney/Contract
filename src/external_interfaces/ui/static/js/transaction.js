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

    // Create sign doc according to official Keplr docs
    // https://docs.keplr.app/api/sign.html#cosmjssignamino
    const signDoc = {
      chain_id: chainId,
      account_number: String(await getAccountNumber(userAddress)),
      sequence: String(await getAccountSequence(userAddress)),
      fee: {
        amount: [{ denom: "uodis", amount: "2500" }],
        gas: "100000"
      },
      msgs: [
        // IMPORTANT: Amino format WITH type/value structure
        // This is what Keplr expects when using signAmino
        {
          type: "cosmos-sdk/MsgSend",
          value: {
            from_address: userAddress,
            to_address: "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
            amount: [{ denom: "uodis", amount: "1000" }]
          }
        }
      ],
      memo: `${transactionId}:${contentHash}:${role}`
    };

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
      explorer_url: `https://testnet.explorer.nodeshub.online/odiseo/tx/${broadcastResult.txhash}`
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


// Transaction handling with Keplr
async function signWithKeplr(chainId, userAddress, signDoc) {
  try {
    // Enable Keplr for the chain
    await window.keplr.enable(chainId);
    console.log("Keplr enabled for chain");

    // Get the offline signer
    const offlineSigner = window.keplr.getOfflineSigner(chainId);
    console.log("Got offline signer");

    // Verify accounts
    const accounts = await offlineSigner.getAccounts();
    console.log("Accounts verified:", accounts.length);

    // Format message in Amino format according to Keplr docs
    // https://docs.keplr.app/api/sign.html#cosmjssignamino
    const aminoDoc = {
      ...signDoc,
      msgs: signDoc.msgs.map(msg => ({
        type: "cosmos-sdk/MsgSend",
        value: {
          from_address: msg.from_address,
          to_address: msg.to_address,
          amount: msg.amount
        }
      }))
    };

    console.log("Using signAmino with Keplr (properly formatted)");
    console.log("Clean sign doc for Keplr:", JSON.stringify(aminoDoc, null, 2));

    // Sign the transaction
    const signResponse = await window.keplr.signAmino(
      chainId,
      userAddress,
      aminoDoc,
      {
        preferNoSetFee: true
      }
    );

    console.log("Got sign response from Keplr:", signResponse);
    return signResponse;

  } catch (error) {
    console.error("Keplr signing error:", {
      message: error.message,
      stack: error.stack,
      fullError: error
    });
    throw error;
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