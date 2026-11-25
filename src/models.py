
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class Action(Enum):
    BUY = "Buy"
    SELL = "Sell"


class SecurityType(Enum):
    EQUITY = "Equity"
    BOND = "Bond"
    ETF = "ETF"


class DecisionStatus(Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    NEEDS_MANUAL_SIGN_OFF = "Needs Manual Sign-off"


@dataclass
class Trade:
    portfolio_id: str
    security_id: str
    action: str
    quantity: Decimal
    price: Decimal
    security_type: str


@dataclass
class Holding:
    security_id: str
    quantity: Decimal
    market_price: Decimal

    def get_market_value(self):
        return self.quantity * self.market_price


@dataclass
class Portfolio:
    portfolio_id: str
    cash_balance: Decimal
    max_position_pct: Decimal
    current_holdings: dict = field(default_factory=dict)
    restricted_securities: set = field(default_factory=set)


@dataclass
class TradeDecision:
    decision: DecisionStatus
    reason: str
