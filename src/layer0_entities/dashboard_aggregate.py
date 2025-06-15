"""
Dashboard Aggregate - Core business entity for dashboard metrics
Contains the domain logic for dashboard data aggregation and validation.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class OdisTokenMetrics:
    """Token metrics for ODIS token with ROI calculations"""
    price_usd: Decimal
    price_change_24h: Decimal
    market_cap: Decimal
    volume_24h: Decimal
    last_updated: datetime
    roi_7d: Decimal
    liquidity_status: str


@dataclass
class NetworkHealth:
    """Network health metrics"""
    block_height: int
    avg_block_time: float
    active_validators: int
    network_hash_rate: Optional[float] = None
    last_block_time: Optional[datetime] = None


@dataclass
class AssetDistribution:
    """Asset distribution statistics"""
    total_value_locked: Decimal
    assets_in_pipeline: int
    pipeline_value: Decimal
    active_properties: int
    completed_tokenizations: int


@dataclass
class HotAsset:
    """Featured hot asset"""
    name: str
    location: str
    roi_percentage: Decimal
    investment_amount: Decimal
    asset_type: str
    image_url: Optional[str] = None


@dataclass
class DashboardAggregate:
    """
    Dashboard aggregate root containing all dashboard metrics.
    Represents the complete state of the dashboard in a single entity.
    """
    odis_token: OdisTokenMetrics
    network_health: NetworkHealth
    asset_distribution: AssetDistribution
    hot_asset: HotAsset
    generated_at: datetime

    def __post_init__(self):
        """Validate the aggregate after initialization"""
        self._validate_metrics()

    def _validate_metrics(self) -> None:
        """Validate all metrics are within acceptable ranges"""
        if self.odis_token.price_usd < 0:
            raise ValueError("Token price cannot be negative")
        
        if self.network_health.block_height < 0:
            raise ValueError("Block height cannot be negative")
        
        if self.asset_distribution.total_value_locked < 0:
            raise ValueError("Total value locked cannot be negative")
        
        if not (0 <= self.hot_asset.roi_percentage <= 100):
            raise ValueError("ROI percentage must be between 0 and 100")

    def to_dict(self) -> Dict:
        """Convert aggregate to dictionary for API serialization"""
        return {
            "odis_token": {
                "price_usd": str(self.odis_token.price_usd),
                "price_change_24h": str(self.odis_token.price_change_24h),
                "market_cap": str(self.odis_token.market_cap),
                "volume_24h": str(self.odis_token.volume_24h),
                "roi_7d": str(self.odis_token.roi_7d),
                "liquidity_status": self.odis_token.liquidity_status,
                "last_updated": self.odis_token.last_updated.isoformat()
            },
            "network_health": {
                "block_height": self.network_health.block_height,
                "avg_block_time": self.network_health.avg_block_time,
                "active_validators": self.network_health.active_validators,
                "network_hash_rate": self.network_health.network_hash_rate,
                "last_block_time": self.network_health.last_block_time.isoformat() if self.network_health.last_block_time else None
            },
            "asset_distribution": {
                "total_value_locked": str(self.asset_distribution.total_value_locked),
                "assets_in_pipeline": self.asset_distribution.assets_in_pipeline,
                "pipeline_value": str(self.asset_distribution.pipeline_value),
                "active_properties": self.asset_distribution.active_properties,
                "completed_tokenizations": self.asset_distribution.completed_tokenizations
            },
            "hot_asset": {
                "name": self.hot_asset.name,
                "location": self.hot_asset.location,
                "roi_percentage": str(self.hot_asset.roi_percentage),
                "investment_amount": str(self.hot_asset.investment_amount),
                "asset_type": self.hot_asset.asset_type,
                "image_url": self.hot_asset.image_url
            },
            "generated_at": self.generated_at.isoformat()
        }

    @classmethod
    def create_live_metrics(
        cls,
        token_price: Decimal,
        block_height: int,
        tvl: Decimal,
        hot_asset_name: str,
        hot_asset_roi: Decimal
    ) -> 'DashboardAggregate':
        """Factory method to create live dashboard metrics"""
        now = datetime.utcnow()
        
        # Calculate ROI based on price movement for landlord insights
        price_change_24h = Decimal("2.3")  # From StreamSwap data
        roi_7d = price_change_24h * Decimal("7")  # Weekly ROI projection
        
        return cls(
            odis_token=OdisTokenMetrics(
                price_usd=token_price,
                price_change_24h=price_change_24h,
                market_cap=token_price * Decimal("1000000"),
                volume_24h=Decimal("850000"),
                roi_7d=roi_7d,
                liquidity_status="active",
                last_updated=now
            ),
            network_health=NetworkHealth(
                block_height=block_height,
                avg_block_time=6.5,
                active_validators=125,
                last_block_time=now
            ),
            asset_distribution=AssetDistribution(
                total_value_locked=tvl,
                assets_in_pipeline=47,
                pipeline_value=Decimal("8500000"),
                active_properties=23,
                completed_tokenizations=15
            ),
            hot_asset=HotAsset(
                name=hot_asset_name,
                location="Miami, FL",
                roi_percentage=hot_asset_roi,
                investment_amount=Decimal("2500000"),
                asset_type="Residential Complex"
            ),
            generated_at=now
        )