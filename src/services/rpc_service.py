"""
Direct RPC Service for Daodiseo Testnet
Fetches real-time data from testnet-rpc.daodiseo.chaintools.tech
"""

import logging
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DaodiseoRPCService:
    """Direct RPC service for fetching real blockchain data"""
    
    def __init__(self):
        self.rpc_base = "https://testnet-rpc.daodiseo.chaintools.tech"
        self.session = requests.Session()
        self.session.timeout = 10
        
    def _make_rpc_call(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make RPC call to testnet"""
        try:
            url = f"{self.rpc_base}/{endpoint}"
            if params:
                response = self.session.get(url, params=params)
            else:
                response = self.session.get(url)
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"RPC call failed for {endpoint}: {e}")
            return None
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status and health"""
        try:
            status_data = self._make_rpc_call("status")
            health_data = self._make_rpc_call("health")
            
            if not status_data or 'result' not in status_data:
                return {"success": False, "error": "No status data available"}
                
            result = status_data['result']
            node_info = result.get('node_info', {})
            sync_info = result.get('sync_info', {})
            
            return {
                "success": True,
                "data": {
                    "block_height": int(sync_info.get('latest_block_height', 0)),
                    "block_time": sync_info.get('latest_block_time', ''),
                    "network": node_info.get('network', 'ithaca-1'),
                    "node_version": node_info.get('version', ''),
                    "catching_up": sync_info.get('catching_up', False),
                    "health_status": "healthy" if health_data else "unknown",
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return {"success": False, "error": str(e)}
    
    def get_validators(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Get current validators"""
        try:
            params = {"page": page, "per_page": per_page}
            validators_data = self._make_rpc_call("validators", params)
            
            if not validators_data or 'result' not in validators_data:
                return {"success": False, "error": "No validators data available"}
                
            result = validators_data['result']
            validators = result.get('validators', [])
            
            processed_validators = []
            for validator in validators:
                processed_validators.append({
                    "address": validator.get('address', ''),
                    "pub_key": validator.get('pub_key', {}).get('value', ''),
                    "voting_power": int(validator.get('voting_power', 0)),
                    "proposer_priority": int(validator.get('proposer_priority', 0))
                })
            
            return {
                "success": True,
                "data": {
                    "validators": processed_validators,
                    "total": result.get('total', len(processed_validators)),
                    "count": result.get('count', len(processed_validators)),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get validators: {e}")
            return {"success": False, "error": str(e)}
    
    def get_latest_block(self) -> Dict[str, Any]:
        """Get latest block information"""
        try:
            block_data = self._make_rpc_call("block")
            
            if not block_data or 'result' not in block_data:
                return {"success": False, "error": "No block data available"}
                
            result = block_data['result']
            block = result.get('block', {})
            header = block.get('header', {})
            
            return {
                "success": True,
                "data": {
                    "height": int(header.get('height', 0)),
                    "time": header.get('time', ''),
                    "chain_id": header.get('chain_id', ''),
                    "proposer_address": header.get('proposer_address', ''),
                    "num_txs": len(block.get('data', {}).get('txs', [])),
                    "block_hash": result.get('block_id', {}).get('hash', ''),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get latest block: {e}")
            return {"success": False, "error": str(e)}
    
    def search_transactions(self, query: str = "tx.height>0", page: int = 1, per_page: int = 30) -> Dict[str, Any]:
        """Search for transactions"""
        try:
            params = {
                "query": query,
                "page": page,
                "per_page": per_page,
                "order_by": "desc"
            }
            tx_data = self._make_rpc_call("tx_search", params)
            
            if not tx_data or 'result' not in tx_data:
                return {"success": False, "error": "No transaction data available"}
                
            result = tx_data['result']
            txs = result.get('txs', [])
            
            processed_txs = []
            for tx in txs:
                tx_result = tx.get('tx_result', {})
                processed_txs.append({
                    "hash": tx.get('hash', ''),
                    "height": int(tx.get('height', 0)),
                    "index": int(tx.get('index', 0)),
                    "tx": tx.get('tx', ''),
                    "result_code": tx_result.get('code', 0),
                    "gas_wanted": int(tx_result.get('gas_wanted', 0)),
                    "gas_used": int(tx_result.get('gas_used', 0)),
                    "events": tx_result.get('events', [])
                })
            
            return {
                "success": True,
                "data": {
                    "transactions": processed_txs,
                    "total_count": int(result.get('total_count', 0)),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to search transactions: {e}")
            return {"success": False, "error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network peer information"""
        try:
            net_info = self._make_rpc_call("net_info")
            
            if not net_info or 'result' not in net_info:
                return {"success": False, "error": "No network info available"}
                
            result = net_info['result']
            peers = result.get('peers', [])
            
            return {
                "success": True,
                "data": {
                    "listening": result.get('listening', False),
                    "n_peers": int(result.get('n_peers', 0)),
                    "peer_count": len(peers),
                    "peers": [
                        {
                            "node_id": peer.get('node_info', {}).get('id', ''),
                            "remote_ip": peer.get('remote_ip', ''),
                            "network": peer.get('node_info', {}).get('network', '')
                        }
                        for peer in peers[:5]  # Limit to first 5 peers
                    ],
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {"success": False, "error": str(e)}
    
    def get_consensus_state(self) -> Dict[str, Any]:
        """Get consensus state information"""
        try:
            consensus_data = self._make_rpc_call("consensus_state")
            
            if not consensus_data or 'result' not in consensus_data:
                return {"success": False, "error": "No consensus data available"}
                
            result = consensus_data['result']
            round_state = result.get('round_state', {})
            
            return {
                "success": True,
                "data": {
                    "height": int(round_state.get('height', 0)),
                    "round": int(round_state.get('round', 0)),
                    "step": round_state.get('step', 0),
                    "start_time": round_state.get('start_time', ''),
                    "commit_time": round_state.get('commit_time', ''),
                    "validators": round_state.get('validators', {}),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get consensus state: {e}")
            return {"success": False, "error": str(e)}