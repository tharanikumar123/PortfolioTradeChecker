
from decimal import Decimal
from models import TradeDecision, DecisionStatus


class ComplianceChecker:

    def validate_trade(self, trade, portfolio):

        # STEP 1: Validate trade data
        if (
            not trade.portfolio_id
            or not trade.security_id
            or trade.action not in ("Buy", "Sell")
            or trade.security_type not in ("Equity", "Bond", "ETF")
            or not isinstance(trade.quantity, Decimal)
            or not isinstance(trade.price, Decimal)
            or not trade.quantity.is_finite()
            or not trade.price.is_finite()
            or trade.quantity <= 0
            or trade.price <= 0
        ):
            return self.reject("Invalid trade data.")

        # STEP 2: Restricted security check
        if trade.security_id in portfolio.restricted_securities:
            return self.reject(
                "Security is restricted for this portfolio."
            )

        # STEP 3: Sell holdings check
        if trade.action == "Sell":

            holding = portfolio.current_holdings.get(
                trade.security_id
            )

            existing_quantity = (
                holding.quantity if holding else Decimal("0")
            )

            if existing_quantity < trade.quantity:
                return self.reject(
                    "Insufficient holdings to sell."
                )

            return self.approve(
                "All applicable compliance checks passed."
            )

        # STEP 4: Buy affordability check
        purchase_cost = trade.quantity * trade.price

        if purchase_cost > portfolio.cash_balance:
            return self.reject(
                "Insufficient cash for this buy order."
            )

        # STEP 5: Position concentration check
        holding = portfolio.current_holdings.get(
            trade.security_id
        )

        existing_quantity = (
            holding.quantity if holding else Decimal("0")
        )

        post_trade_cash = (
            portfolio.cash_balance - purchase_cost
        )

        post_trade_quantity = (
            existing_quantity + trade.quantity
        )

        post_trade_security_value = (
            post_trade_quantity * trade.price
        )

        value_of_other_holdings = sum(
            (
                other_holding.get_market_value()
                for security_id, other_holding
                in portfolio.current_holdings.items()
                if security_id != trade.security_id
            ),
            Decimal("0")
        )

        total_portfolio_value_after = (
            post_trade_cash
            + post_trade_security_value
            + value_of_other_holdings
        )

        if total_portfolio_value_after <= 0:
            return self.reject(
                "Invalid total portfolio value."
            )

        position_pct = (
            post_trade_security_value
            / total_portfolio_value_after
        )

        if position_pct > portfolio.max_position_pct:
            return TradeDecision(
                DecisionStatus.NEEDS_MANUAL_SIGN_OFF,
                "Exceeds maximum position concentration "
                "— requires approval."
            )

        # STEP 6: Approved
        return self.approve(
            "All applicable compliance checks passed."
        )

    @staticmethod
    def reject(reason):
        return TradeDecision(
            DecisionStatus.REJECTED,
            reason
        )

    @staticmethod
    def approve(reason):
        return TradeDecision(
            DecisionStatus.APPROVED,
            reason
        )
