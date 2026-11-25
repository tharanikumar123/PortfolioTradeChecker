# PortfolioTradeChecker
# Overview 
The Portfolio Trade Order Compliance & Execution Checker is a Python-based console application designed to validate proposed portfolio trades before execution.

The application ensures that every proposed Buy or Sell order complies with predefined portfolio rules. It checks available cash, existing holdings, restricted securities, and maximum position concentration.

Based on the validation results, each trade receives one of three decisions:

Approved – The trade passes all applicable compliance checks.
Rejected – The trade violates a mandatory compliance rule.
Needs Manual Sign-off – The trade exceeds the maximum position concentration limit and requires additional authorization.
The application supports both manual trade entry and sequential processing of multiple proposed trades from a CSV file.

# Project Structure

PortfolioTradeChecker/
│
├── data/
│   ├── portfolio_reference.csv
│   ├── current_holdings.csv
│   ├── restricted_securities.csv
│   └── proposed_trades.csv
│
├── src/
│   ├── main.py
│   ├── models.py
│   ├── data_loader.py
│   ├── compliance_checker.py
│   ├── portfolio_manager.py
│   └── report_generator.py
│
└── README.md
