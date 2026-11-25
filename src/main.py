
from decimal import Decimal, InvalidOperation
from pathlib import Path

from models import Trade, DecisionStatus
from data_loader import DataLoader
from compliance_checker import ComplianceChecker
from portfolio_manager import PortfolioManager
from report_generator import ReportGenerator


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"


def get_trade_input():

    print("\n========== ENTER NEW TRADE ==========")

    portfolio_id = input("Portfolio ID: ").strip().upper()
    security_id = input("Security ID: ").strip().upper()
    action = input("Action (Buy/Sell): ").strip().capitalize()

    try:
        quantity = Decimal(input("Quantity: ").strip())
        price = Decimal(input("Price: ").strip())

    except InvalidOperation:
        quantity = Decimal("NaN")
        price = Decimal("NaN")

    security_type = input(
        "Security Type (Equity/Bond/ETF): "
    ).strip().capitalize()

    return Trade(
        portfolio_id=portfolio_id,
        security_id=security_id,
        action=action,
        quantity=quantity,
        price=price,
        security_type=security_type
    )


def process_single_trade(
    trade,
    portfolios,
    checker,
    manager,
    reporter
):

    portfolio = portfolios.get(trade.portfolio_id)

    if portfolio is None:

        print("\nPortfolio reference data not found.")

        # Do not execute or modify any portfolio.
        return

    # Run compliance validation
    decision = checker.validate_trade(
        trade, portfolio
    )

    print("\n========== VALIDATION RESULT ==========")
    print("Portfolio:", trade.portfolio_id)
    print("Security:", trade.security_id)
    print("Action:", trade.action)
    print("Quantity:", trade.quantity)
    print("Price:", trade.price)
    print("Decision:", decision.decision.value)
    print("Reason:", decision.reason)

    # Handle manual sign-off
    if decision.decision == DecisionStatus.NEEDS_MANUAL_SIGN_OFF:

        approval = input(
            "\nManual approval granted? (Y/N): "
        ).strip().upper()

        if approval == "Y":

            manager.execute_trade(trade, portfolio)

            decision.decision = DecisionStatus.APPROVED
            decision.reason = (
                "Manual approval granted. Trade executed."
            )

            print("\nTrade approved and portfolio updated.")

        else:

            decision.reason = (
                "Manual approval declined. Trade not executed."
            )

            print("\nTrade not executed.")

    # Execute automatically approved trades
    elif decision.decision == DecisionStatus.APPROVED:

        manager.execute_trade(trade, portfolio)

        print("\nTrade executed successfully.")
        print("Portfolio balances updated.")

    else:

        print("\nTrade rejected. Portfolio unchanged.")

    # Save result in trade history
    reporter.add_result(trade, decision)


def process_all_trades(
    trades,
    portfolios,
    checker,
    manager,
    reporter
):

    print("\n==========================================")
    print("       SEQUENTIAL TRADE PROCESSING")
    print("==========================================")

    total_trades = len(trades)

    print("Total proposed trades:", total_trades)

    for index, trade in enumerate(trades, start=1):

        print("\n")
        print("=" * 45)
        print(f" PROCESSING TRADE {index} OF {total_trades}")
        print("=" * 45)

        process_single_trade(
            trade,
            portfolios,
            checker,
            manager,
            reporter
        )

    print("\n==========================================")
    print("       BATCH PROCESSING COMPLETED")
    print("==========================================")

    reporter.display_summary()


def main():

    print("\n==========================================")
    print(" PORTFOLIO TRADE ORDER COMPLIANCE CHECKER")
    print("==========================================")

    # Load portfolio reference data
    try:

        portfolios = DataLoader.load_portfolios(
            DATA_DIR / "portfolio_reference.csv",
            DATA_DIR / "current_holding.csv",
            DATA_DIR / "restricted_securities.csv"
        )

        # Load proposed trades
        proposed_trades = DataLoader.load_proposed_trades(
            DATA_DIR / "trades_test.csv"
        )

    except (OSError, ValueError, KeyError, InvalidOperation) as error:

        print("\nUnable to load application data:", error)
        return

    checker = ComplianceChecker()
    manager = PortfolioManager()
    reporter = ReportGenerator()

    print("\nPortfolio reference data loaded successfully.")
    print("Proposed trades loaded:", len(proposed_trades))

    while True:

        print("\n========== MAIN MENU ==========")
        print("1. Enter New Trade Manually")
        print("2. Process All Proposed Trades")
        print("3. View Trade History")
        print("4. Export Compliance Report")
        print("5. View Portfolio Balances")
        print("6. Exit")

        choice = input("\nSelect option: ").strip()

        # Option 1: Manual trade
        if choice == "1":

            trade = get_trade_input()

            process_single_trade(
                trade,
                portfolios,
                checker,
                manager,
                reporter
            )

        # Option 2: Process all CSV trades
        elif choice == "2":

            confirm = input(
                "\nProcess all proposed trades sequentially? (Y/N): "
            ).strip().upper()

            if confirm == "Y":

                process_all_trades(
                    proposed_trades,
                    portfolios,
                    checker,
                    manager,
                    reporter
                )

            else:

                print("\nBatch processing cancelled.")

        # Option 3: View trade history
        elif choice == "3":

            reporter.display_history()

        # Option 4: Export report
        elif choice == "4":

            reporter.export_report()

        # Option 5: View portfolio balances
        elif choice == "5":

            print("\n========== PORTFOLIO BALANCES ==========")

            for portfolio in portfolios.values():

                print(f"\nPortfolio: {portfolio.portfolio_id}")
                print("Cash:", portfolio.cash_balance)

                print("\nCurrent Holdings:")

                for holding in portfolio.current_holdings.values():

                    print(
                        holding.security_id,
                        "| Quantity:", holding.quantity,
                        "| Market Price:", holding.market_price
                    )

        # Option 6: Exit
        elif choice == "6":

            reporter.display_summary()
            reporter.export_report()

            print("\nThank you for using the application.")
            break

        else:

            print("\nInvalid selection. Please try again.")


if __name__ == "__main__":
    main()
