// Transaction handling with Keplr
async function createAndSignTransaction(fileData, userAddress, role) {
  try {
    console.log("Starting Keplr signing process...");

    // Create transaction metadata
    const transactionId = fileData.transaction_id || "tx_1";
    const contentHash = fileData.content_hash;

    // Get chain information
    const chainId = "odiseotestnet_1234-1";
    console.log("Using chain ID:", chainId);

    // Enable Keplr for your chain
    await window.keplr.enable(chainId);
    console.log("Keplr enabled for chain");

    // Get the offline signer from Keplr
    const offlineSigner = window.keplr.getOfflineSigner(chainId);
    console.log("Got offline signer");

    // Get user's account info from the chain
    const accounts = await offlineSigner.getAccounts();
    const userAccount = accounts.find(acc => acc.address === userAddress);

    if (!userAccount) {
      throw new Error("User account not found in Keplr");
    }

    console.log("User address:", userAddress);

    // Get the latest account details from the chain
    const accountInfo = await fetchAccountInfo(userAddress);
    console.log("Account data:", accountInfo);

    // IMPORTANT: Use simple string format without JSON - this is the key fix
    const memo = `tx:${transactionId}|hash:${contentHash}|role:${role}`;
    console.log("Using simple memo string:", memo);

    // Create the sign doc with the correct format
    const signDoc = {
      chain_id: chainId,
      account_number: accountInfo.account_number,
      sequence: accountInfo.sequence,
      fee: {
        amount: [{ amount: "2500", denom: "uodis" }],
        gas: "100000"
      },
      msgs: [
        {
          type: "cosmos-sdk/MsgSend",
          value: {
            amount: [{ amount: "1000", denom: "uodis" }],
            from_address: userAddress,
            to_address: "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"
          }
        }
      ],
      memo: memo // Simple string memo without any JSON
    };

    // Sign the transaction
    console.log("Requesting Keplr signature...");
    const signResponse = await offlineSigner.signAmino(userAddress, signDoc);
    console.log("Got sign response:", signResponse);

    if (!signResponse || !signResponse.signature) {
      throw new Error("Failed to get signature from Keplr");
    }

    // Broadcast the signed transaction
    const broadcastResult = await broadcastTransaction(signResponse);
    console.log("Broadcast result:", broadcastResult);

    return {
      success: true,
      transaction_id: transactionId,
      blockchain_tx_hash: broadcastResult.txhash,
      explorer_url: `https://explorer.odiseotestnet.com/tx/${broadcastResult.txhash}`
    };
  } catch (error) {
    console.error("Keplr signing error:", {
      message: error.message,
      stack: error.stack,
      fullError: error
    });
    throw error;
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
    console.error("Error fetching account info:", error);
    throw error;
  }
}

// Helper function to broadcast the signed transaction
async function broadcastTransaction(signResponse) {
  try {
    // Prepare the transaction for broadcasting
    const broadcastBody = {
      tx: {
        msg: signResponse.signed.msgs,
        fee: signResponse.signed.fee,
        signatures: [
          {
            pub_key: signResponse.signature.pub_key,
            signature: signResponse.signature.signature
          }
        ],
        memo: signResponse.signed.memo // Use the simple string memo from signResponse
      },
      mode: "block" // Use "block" to wait for confirmation
    };

    // Send to your backend API endpoint that will broadcast to the blockchain
    const response = await fetch("/api/broadcast", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(broadcastBody)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to broadcast transaction");
    }

    return await response.json();
  } catch (error) {
    console.error("Error broadcasting transaction:", {
      message: error.message,
      stack: error.stack,
      fullError: error,
      responseType: typeof response,
      responseStatus: response?.status
    });
    throw error;
  }
}

// Export the function
export { createAndSignTransaction };