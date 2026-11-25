
import csv
from decimal import Decimal
from models import Portfolio, Holding, Trade


class DataLoader:

    # Load portfolio reference data, holdings and restrictions
    @staticmethod
    def load_portfolios(
        reference_file,
        holdings_file,
        restricted_file
    ):

        portfolios = {}

        # 1. Load portfolio reference data
        with open(reference_file, "r", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                portfolio = Portfolio(
                    portfolio_id=row["portfolio_id"],
                    cash_balance=Decimal(row["cash_balance"]),
                    max_position_pct=Decimal(row["max_position_pct"])
                )

                portfolios[portfolio.portfolio_id] = portfolio

        # 2. Load current holdings
        with open(holdings_file, "r", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                portfolio = portfolios.get(row["portfolio_id"])

                if portfolio is None:
                    raise ValueError(
                        f"Unknown portfolio in holdings: "
                        f"{row['portfolio_id']}"
                    )

                holding = Holding(
                    security_id=row["security_id"],
                    quantity=Decimal(row["quantity"]),
                    market_price=Decimal(row["market_price"])
                )

                if holding.security_id in portfolio.current_holdings:
                    raise ValueError(
                        f"Duplicate holding: {portfolio.portfolio_id}, "
                        f"{holding.security_id}"
                    )

                portfolio.current_holdings[
                    holding.security_id
                ] = holding

        # 3. Load restricted securities
        with open(restricted_file, "r", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                portfolio = portfolios.get(row["portfolio_id"])

                if portfolio is None:
                    raise ValueError(
                        f"Unknown portfolio in restrictions: "
                        f"{row['portfolio_id']}"
                    )

                portfolio.restricted_securities.add(
                    row["security_id"]
                )

        return portfolios

    # Load proposed trades from CSV
    @staticmethod
    def load_proposed_trades(proposed_trades_file):

        trades = []

        with open(proposed_trades_file, "r", newline="") as file:

            reader = csv.DictReader(file)

            required_columns = {
                "portfolio_id",
                "security_id",
                "action",
                "quantity",
                "price",
                "security_type"
            }

            if not reader.fieldnames or not required_columns.issubset(
                set(reader.fieldnames)
            ):
                raise ValueError(
                    "Invalid proposed trades CSV headers."
                )

            for row_number, row in enumerate(reader, start=2):

                try:

                    trade = Trade(
                        portfolio_id=row["portfolio_id"].strip().upper(),
                        security_id=row["security_id"].strip().upper(),
                        action=row["action"].strip().capitalize(),
                        quantity=Decimal(row["quantity"].strip()),
                        price=Decimal(row["price"].strip()),
                        security_type=row["security_type"].strip().capitalize()
                    )

                    trades.append(trade)

                except Exception as error:

                    raise ValueError(
                        f"Invalid trade data at CSV row {row_number}: {error}"
                    ) from error

        return trades
