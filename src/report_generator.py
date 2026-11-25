
import csv


class ReportGenerator:

    def __init__(self):
        self.trade_history = []

    def add_result(self, trade, decision):
        self.trade_history.append({
            "portfolio_id": trade.portfolio_id,
            "security_id": trade.security_id,
            "action": trade.action,
            "quantity": str(trade.quantity),
            "price": str(trade.price),
            "security_type": trade.security_type,
            "decision": decision.decision.value,
            "reason": decision.reason
        })

    def display_history(self):

        print("\n========== TRADE HISTORY ==========")

        if not self.trade_history:
            print("No trades have been entered.")
            return

        for index, trade in enumerate(
            self.trade_history, start=1
        ):
            print(f"\nTrade {index}")
            print("Portfolio:", trade["portfolio_id"])
            print("Security:", trade["security_id"])
            print("Action:", trade["action"])
            print("Quantity:", trade["quantity"])
            print("Decision:", trade["decision"])
            print("Reason:", trade["reason"])

    def export_report(self, filename="trade_results.csv"):

        if not self.trade_history:
            print("No trade results available to export.")
            return

        with open(filename, "w", newline="") as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.trade_history[0].keys()
            )

            writer.writeheader()
            writer.writerows(self.trade_history)

        print(f"\nReport exported: {filename}")

    def display_summary(self):

        total = len(self.trade_history)

        approved = sum(
            t["decision"] == "Approved"
            for t in self.trade_history
        )

        rejected = sum(
            t["decision"] == "Rejected"
            for t in self.trade_history
        )

        manual = sum(
            t["decision"] == "Needs Manual Sign-off"
            for t in self.trade_history
        )

        print("\n========== SUMMARY ==========")
        print("Total trades:", total)
        print("Approved:", approved)
        print("Rejected:", rejected)
        print("Needs Manual Sign-off:", manual)
