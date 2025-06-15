from dataclasses import dataclass
from enum import Enum


class RoleType(Enum):
    LANDLORD = "landlord"
    ARCHITECT = "architect"
    CONTRACTOR = "contractor"
    INVESTOR = "investor"
    BROKER = "broker"


@dataclass
class Role:
    id: int
    user_id: int
    role_type: RoleType
    permissions: list[str]

    def can_tokenize(self) -> bool:
        return self.role_type in [RoleType.LANDLORD, RoleType.INVESTOR]

    def can_upload_bim(self) -> bool:
        return self.role_type in [RoleType.ARCHITECT, RoleType.CONTRACTOR]
