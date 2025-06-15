"""
Get Token Metrics Use Case - Clean Architecture Layer 1
Application business rule for retrieving and processing token metrics
"""

from typing import Dict, Any
from src.layer2_interface_adapters.gateways.blockchain_gateway import BlockchainGatewayInterface

class GetTokenMetricsUseCase:
    """Use case for getting ODIS token metrics and market data"""
    
    def __init__(self, blockchain_gateway: BlockchainGatewayInterface = None):
        from src.layer2_interface_adapters.gateways.blockchain_gateway import BlockchainGateway
        self.blockchain_gateway = blockchain_gateway or BlockchainGateway()
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the use case to get token metrics
        
        Returns:
            Dict containing processed token metrics and market data
        """
        # Get raw token data from blockchain gateway
        token_data = self.blockchain_gateway.get_token_price()
        
        # Apply business rules for metric processing
        processed_metrics = self._process_token_metrics(token_data)
        
        return processed_metrics
    
    def _process_token_metrics(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business logic to process token metrics"""
        current_price = token_data.get("current_price", 0)
        price_change_24h = token_data.get("price_change_24h", 0)
        market_cap = token_data.get("market_cap", 0)
        volume_24h = token_data.get("volume_24h", 0)
        
        # Calculate percentage change
        if current_price > 0:
            percentage_change = (price_change_24h / (current_price - price_change_24h)) * 100
        else:
            percentage_change = 0
        
        # Determine trend
        trend = "up" if price_change_24h > 0 else "down" if price_change_24h < 0 else "stable"
        
        # Calculate market metrics
        price_volatility = self._calculate_volatility(price_change_24h, current_price)
        liquidity_score = self._calculate_liquidity_score(volume_24h, market_cap)
        
        return {
            "token_symbol": token_data.get("token_symbol", "ODIS"),
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "price_change_percentage": round(percentage_change, 2),
            "market_cap": market_cap,
            "volume_24h": volume_24h,
            "circulating_supply": token_data.get("circulating_supply", 0),
            "total_supply": token_data.get("total_supply", 0),
            "trend": trend,
            "volatility": price_volatility,
            "liquidity_score": liquidity_score,
            "last_updated": token_data.get("last_updated", ""),
            "is_bullish": price_change_24h > 0 and percentage_change > 2
        }
    
    def _calculate_volatility(self, price_change: float, current_price: float) -> str:
        """Calculate price volatility classification"""
        if current_price == 0:
            return "unknown"
        
        volatility_percentage = abs(price_change / current_price) * 100
        
        if volatility_percentage < 2:
            return "low"
        elif volatility_percentage < 5:
            return "medium"
        else:
            return "high"
    
    def _calculate_liquidity_score(self, volume_24h: float, market_cap: float) -> float:
        """Calculate liquidity score (0-10)"""
        if market_cap == 0:
            return 0
        
        volume_ratio = volume_24h / market_cap
        
        # Score based on volume/market cap ratio
        if volume_ratio > 0.1:
            score = 10
        elif volume_ratio > 0.05:
            score = 8
        elif volume_ratio > 0.02:
            score = 6
        elif volume_ratio > 0.01:
            score = 4
        else:
            score = 2
        
        return score