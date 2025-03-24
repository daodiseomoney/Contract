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

    // Enable Keplr for the chain
    try {
      await window.keplr.enable(chainId);
      console.log("Keplr enabled for chain");
    } catch (keplrError) {
      console.error("Error enabling Keplr:", keplrError);
      throw new Error(`Failed to enable Keplr for chain ${chainId}: ${keplrError.message}`);
    }

    // Get the offline signer from Keplr
    const offlineSigner = window.keplr.getOfflineSigner(chainId);
    console.log("Got offline signer");

    // Get user's account info from Keplr
    let accounts;
    try {
      accounts = await offlineSigner.getAccounts();
      console.log("Keplr accounts:", accounts);
    } catch (accountsError) {
      console.error("Error getting accounts from Keplr:", accountsError);
      throw new Error(`Failed to get accounts from Keplr: ${accountsError.message}`);
    }

    const userAccount = accounts.find(acc => acc.address === userAddress);
    if (!userAccount) {
      console.error("User account not found in Keplr. Available accounts:", accounts);
      throw new Error("User account not found in Keplr");
    }

    // Get the latest account details from the chain
    let accountInfo;
    try {
      accountInfo = await fetchAccountInfo(userAddress);
      console.log("Account data from chain:", accountInfo);
    } catch (accountError) {
      console.error("Error fetching account info:", accountError);
      throw new Error(`Failed to fetch account info: ${accountError.message}`);
    }

    // Ensure account data is valid
    if (!accountInfo || !accountInfo.account_number || !accountInfo.sequence) {
      console.error("Invalid account data:", accountInfo);
      throw new Error("Invalid account data received from the chain");
    }

    // Use simple string memo without any complex formatting
    const memo = `${transactionId}:${contentHash}:${role}`;
    console.log("Using very simple memo string:", memo);

    // Extract message data
    const msgSendData = {
      // Direct message fields without nesting
      from_address: userAddress,
      to_address: "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
      amount: [{ amount: "1000", denom: "uodis" }]
    };
    
    // Create the sign doc using proper Keplr-compatible format
    // Ensure all numeric values are strings for consistency
    const signDoc = {
      chain_id: chainId,
      account_number: String(accountInfo.account_number),
      sequence: String(accountInfo.sequence),
      fee: {
        amount: [{ amount: "2500", denom: "uodis" }],
        gas: "100000"
      },
      msgs: [
        {
          // Use @type field instead of type for Keplr compatibility
          "@type": "/cosmos.bank.v1beta1.MsgSend",
          // Include message fields directly at this level instead of nesting in value
          ...msgSendData
        }
      ],
      memo: memo // Ultra-simple memo string
    };

    // Log the complete sign doc for debugging
    console.log("Amino sign doc for Keplr:", JSON.stringify(signDoc, null, 2));

    // Sign the transaction with Keplr
    console.log("Requesting Keplr signature with Amino format...");
    let signResponse;
    try {
      // Use window.keplr.signAmino with properly formatted Amino doc
      signResponse = await window.keplr.signAmino(chainId, userAddress, signDoc);
      console.log("Got sign response from Keplr:", signResponse);
    } catch (signingError) {
      console.error("Error during Keplr signing:", signingError);
      // Check if user rejected the request
      if (signingError.message.includes("Request rejected") || 
          signingError.message.includes("User denied")) {
        throw new Error("Transaction was rejected by the user");
      }
      throw new Error(`Failed to sign transaction with Keplr: ${signingError.message}`);
    }

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

// Helper function to convert Keplr-compatible message to Proto format
function convertAminoToProto(keplerMsg) {
  console.log("Converting message to Proto format:", keplerMsg);
  
  // Handle the new flattened Keplr message format with @type field
  if (keplerMsg["@type"]) {
    // Extract the typeUrl (e.g. "/cosmos.bank.v1beta1.MsgSend")
    const typeUrl = keplerMsg["@type"];
    
    // For MsgSend, convert snake_case to camelCase
    if (typeUrl === "/cosmos.bank.v1beta1.MsgSend") {
      return {
        typeUrl: typeUrl,
        value: {
          fromAddress: keplerMsg.from_address,
          toAddress: keplerMsg.to_address,
          amount: keplerMsg.amount
        }
      };
    }
    
    // For other message types, create a default conversion
    const value = { ...keplerMsg };
    delete value["@type"]; // Remove the @type field from the value
    
    return {
      typeUrl: typeUrl,
      value: value
    };
  }
  
  // Handle legacy Amino format (backward compatibility)
  if (keplerMsg.type && keplerMsg.value) {
    // Map Amino types to Proto typeUrls
    const typeUrlMapping = {
      'cosmos-sdk/MsgSend': '/cosmos.bank.v1beta1.MsgSend',
      // Add other message types as needed
    };
    
    // Get corresponding typeUrl from mapping
    const typeUrl = typeUrlMapping[keplerMsg.type];
    if (!typeUrl) {
      console.error('Unknown message type:', keplerMsg.type);
      throw new Error(`Unknown message type: ${keplerMsg.type}`);
    }
    
    // Create Proto format message with proper field naming conversion
    if (keplerMsg.type === 'cosmos-sdk/MsgSend') {
      return {
        typeUrl: typeUrl,
        value: {
          fromAddress: keplerMsg.value.from_address,
          toAddress: keplerMsg.value.to_address,
          amount: keplerMsg.value.amount
        }
      };
    }
    
    // For other message types
    return {
      typeUrl: typeUrl,
      value: keplerMsg.value
    };
  }
  
  // If unable to convert, log an error
  console.error("Unknown message format:", keplerMsg);
  throw new Error("Unable to convert message to Proto format");
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

// Export the function
export { createAndSignTransaction };