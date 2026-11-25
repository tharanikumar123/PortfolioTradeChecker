
from decimal import Decimal
from models import Holding, DecisionStatus


class PortfolioManager:

    def execute_trade(self, trade, portfolio):

        trade_value = trade.quantity * trade.price

        if trade.action == "Buy":

            portfolio.cash_balance -= trade_value

            holding = portfolio.current_holdings.get(
                trade.security_id
            )

            if holding:
                holding.quantity += trade.quantity
            else:
                portfolio.current_holdings[
                    trade.security_id
                ] = Holding(
                    security_id=trade.security_id,
                    quantity=trade.quantity,
                    market_price=trade.price
                )

        elif trade.action == "Sell":

            portfolio.cash_balance += trade_value

            holding = portfolio.current_holdings[
                trade.security_id
            ]

            holding.quantity -= trade.quantity

            if holding.quantity == Decimal("0"):
                del portfolio.current_holdings[
                    trade.security_id
                ]

        return True
