from pathlib import Path

import pandas as pd


class RetrievalService:
    """
    Deterministic retrieval engine for Vaidya.

    The service searches historical recovery cases and
    returns cases that are most similar to a current
    revenue-at-risk event.

    This is intentionally deterministic.

    No LLM is used here.
    No random scores are generated.
    """

    # -----------------------------------------------------
    # Project paths
    # -----------------------------------------------------

    BASE_DIR = Path(__file__).resolve().parents[3]

    CASES_PATH = (
        BASE_DIR
        / "data"
        / "generated"
        / "historical_recovery_cases.csv"
    )

    # -----------------------------------------------------
    # Similarity weights
    # -----------------------------------------------------

    EVENT_TYPE_WEIGHT = 0.40

    ROOT_CAUSE_WEIGHT = 0.30

    AMOUNT_WEIGHT = 0.20

    CUSTOMER_WEIGHT = 0.10

    # -----------------------------------------------------
    # Constructor
    # -----------------------------------------------------

    def __init__(self, cases_path=None):

        if cases_path is None:
            cases_path = self.CASES_PATH

        self.cases_path = Path(cases_path)

        self.cases = self._load_cases()

    # -----------------------------------------------------
    # Load historical cases
    # -----------------------------------------------------

    def _load_cases(self):

        if not self.cases_path.exists():

            raise FileNotFoundError(
                f"Historical case file not found: "
                f"{self.cases_path}"
            )

        cases = pd.read_csv(
            self.cases_path
        )

        required_columns = [
            "case_id",
            "event_type",
            "amount",
            "customer_profile",
            "problem_summary",
            "root_cause",
            "action_taken",
            "policy_result",
            "outcome",
            "recovered_amount",
            "days_to_recovery",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in cases.columns
        ]

        if missing_columns:

            raise ValueError(
                "Historical case dataset is missing "
                f"columns: {missing_columns}"
            )

        return cases

    # -----------------------------------------------------
    # Event type similarity
    # -----------------------------------------------------

    @staticmethod
    def _event_type_similarity(
        current_event,
        historical_case
    ):

        if (
            current_event.get("event_type")
            == historical_case["event_type"]
        ):

            return 1.0

        return 0.0

    # -----------------------------------------------------
    # Root cause similarity
    # -----------------------------------------------------

    @staticmethod
    def _root_cause_similarity(
        current_event,
        historical_case
    ):

        current_root_cause = (
            current_event.get("root_cause")
        )

        historical_root_cause = (
            historical_case["root_cause"]
        )

        if (
            current_root_cause
            and current_root_cause
            == historical_root_cause
        ):

            return 1.0

        return 0.0

    # -----------------------------------------------------
    # Amount similarity
    # -----------------------------------------------------

    @staticmethod
    def _amount_similarity(
        current_amount,
        historical_amount
    ):

        if current_amount is None:
            return 0.0

        current_amount = float(
            current_amount
        )

        historical_amount = float(
            historical_amount
        )

        if current_amount <= 0:
            return 0.0

        # Relative difference between amounts.
        relative_difference = abs(
            current_amount
            - historical_amount
        ) / current_amount

        # Convert difference into similarity.
        #
        # Same amount = 1.0
        # 50% difference = 0.5
        # >=100% difference = 0.0

        similarity = max(
            0.0,
            1.0 - relative_difference
        )

        return round(
            similarity,
            4
        )

    # -----------------------------------------------------
    # Customer similarity
    # -----------------------------------------------------

    @staticmethod
    def _customer_similarity(
        current_event,
        historical_case
    ):
        """
        Lightweight customer-context matching.

        We currently use available profile signals rather
        than pretending that synthetic customer IDs represent
        real production identities.

        Matching logic:

        - If both cases describe a returning customer,
          return 1.0.
        - If both have comparable history-score language,
          return 0.5.
        - Otherwise return 0.0.
        """

        current_profile = str(
            current_event.get(
                "customer_profile",
                ""
            )
        ).lower()

        historical_profile = str(
            historical_case[
                "customer_profile"
            ]
        ).lower()

        # Returning-customer context.
        if (
            "returning customer"
            in current_profile
            and
            "returning customer"
            in historical_profile
        ):

            return 1.0

        # Checkout history score context.
        if (
            "history score"
            in current_profile
            and
            "history score"
            in historical_profile
        ):

            try:

                current_score = float(
                    current_profile
                    .split(":")[-1]
                    .strip()
                )

                historical_score = float(
                    historical_profile
                    .split(":")[-1]
                    .strip()
                )

                difference = abs(
                    current_score
                    - historical_score
                )

                return round(
                    max(
                        0.0,
                        1.0 - difference
                    ),
                    4
                )

            except ValueError:

                return 0.5

        # B2B invoice history.
        if (
            "previous invoices"
            in current_profile
            and
            "previous invoices"
            in historical_profile
        ):

            return 1.0

        return 0.0

    # -----------------------------------------------------
    # Overall similarity
    # -----------------------------------------------------

    def calculate_similarity(
        self,
        current_event,
        historical_case
    ):

        event_type_score = (
            self._event_type_similarity(
                current_event,
                historical_case
            )
        )

        root_cause_score = (
            self._root_cause_similarity(
                current_event,
                historical_case
            )
        )

        amount_score = (
            self._amount_similarity(
                current_event.get("amount"),
                historical_case["amount"]
            )
        )

        customer_score = (
            self._customer_similarity(
                current_event,
                historical_case
            )
        )

        total_score = (
            self.EVENT_TYPE_WEIGHT
            * event_type_score
            +
            self.ROOT_CAUSE_WEIGHT
            * root_cause_score
            +
            self.AMOUNT_WEIGHT
            * amount_score
            +
            self.CUSTOMER_WEIGHT
            * customer_score
        )

        return round(
            total_score,
            4
        )

    # -----------------------------------------------------
    # Retrieve similar cases
    # -----------------------------------------------------

    def retrieve(
        self,
        current_event,
        top_k=5,
        successful_only=False
    ):
        """
        Retrieve the most similar historical cases.

        Parameters
        ----------
        current_event:
            Dictionary describing the current case.

        top_k:
            Number of historical cases to return.

        successful_only:
            If True, prioritize only cases that actually
            recovered money.

        Returns
        -------
        list of dictionaries
        """

        if top_k <= 0:

            return []

        scored_cases = []

        for _, case in self.cases.iterrows():

            # -------------------------------------------------
            # Optional outcome filter.
            # -------------------------------------------------

            if successful_only:

                if case["outcome"] not in [
                    "recovered",
                    "partial"
                ]:

                    continue

            similarity = (
                self.calculate_similarity(
                    current_event,
                    case
                )
            )

            scored_cases.append(
                {
                    "case_id": case["case_id"],
                    "similarity": similarity,
                    "event_type": case["event_type"],
                    "amount": float(
                        case["amount"]
                    ),
                    "customer_profile": (
                        case["customer_profile"]
                    ),
                    "problem_summary": (
                        case["problem_summary"]
                    ),
                    "root_cause": (
                        case["root_cause"]
                    ),
                    "action_taken": (
                        case["action_taken"]
                    ),
                    "policy_result": (
                        case["policy_result"]
                    ),
                    "outcome": (
                        case["outcome"]
                    ),
                    "recovered_amount": float(
                        case["recovered_amount"]
                    ),
                    "days_to_recovery": int(
                        case["days_to_recovery"]
                    ),
                }
            )

        # -----------------------------------------------------
        # Highest similarity first.
        # -----------------------------------------------------

        scored_cases.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        return scored_cases[:top_k]

    # -----------------------------------------------------
    # Evidence summary
    # -----------------------------------------------------

    def summarize_evidence(
        self,
        retrieved_cases
    ):
        """
        Produce a compact summary of what the historical
        cases suggest.

        This is still deterministic and does not use an LLM.
        """

        if not retrieved_cases:

            return {
                "case_count": 0,
                "successful_cases": 0,
                "recovery_rate": 0.0,
                "recommended_actions": [],
            }

        successful_cases = [
            case
            for case in retrieved_cases
            if case["outcome"] in [
                "recovered",
                "partial"
            ]
        ]

        recovery_rate = (
            len(successful_cases)
            / len(retrieved_cases)
            * 100
        )

        action_counts = {}

        for case in successful_cases:

            action = case["action_taken"]

            action_counts[action] = (
                action_counts.get(
                    action,
                    0
                )
                + 1
            )

        recommended_actions = sorted(
            action_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return {
            "case_count": len(
                retrieved_cases
            ),
            "successful_cases": len(
                successful_cases
            ),
            "recovery_rate": round(
                recovery_rate,
                2
            ),
            "recommended_actions": [
                {
                    "action": action,
                    "successful_cases": count,
                }
                for action, count
                in recommended_actions
            ],
        }


# =========================================================
# SIMPLE MANUAL TEST
# =========================================================

def main():

    print()
    print("======================================")
    print("VAIDYA RETRIEVAL SERVICE TEST")
    print("======================================")

    service = RetrievalService()

    print()
    print(
        f"Loaded historical cases: "
        f"{len(service.cases)}"
    )

    # -----------------------------------------------------
    # Example current payment event.
    # -----------------------------------------------------

    current_event = {
        "event_type": "payment_failure",
        "root_cause": "network_error",
        "amount": 6200.00,
        "customer_profile": (
            "Returning customer with "
            "historical transaction activity."
        ),
    }

    print()
    print("Current event:")
    print(current_event)

    # -----------------------------------------------------
    # Retrieve cases.
    # -----------------------------------------------------

    results = service.retrieve(
        current_event,
        top_k=5,
        successful_only=False
    )

    print()
    print("Top similar historical cases:")

    for case in results:

        print(
            f"\n{case['case_id']}"
        )

        print(
            f"Similarity: "
            f"{case['similarity'] * 100:.2f}%"
        )

        print(
            f"Root cause: "
            f"{case['root_cause']}"
        )

        print(
            f"Action: "
            f"{case['action_taken']}"
        )

        print(
            f"Outcome: "
            f"{case['outcome']}"
        )

        print(
            f"Recovered: "
            f"₹{case['recovered_amount']:,.2f}"
        )

    # -----------------------------------------------------
    # Evidence summary.
    # -----------------------------------------------------

    evidence = service.summarize_evidence(
        results
    )

    print()
    print("Evidence summary:")

    print(
        f"Cases retrieved: "
        f"{evidence['case_count']}"
    )

    print(
        f"Successful cases: "
        f"{evidence['successful_cases']}"
    )

    print(
        f"Historical success rate: "
        f"{evidence['recovery_rate']:.2f}%"
    )

    print(
        "Successful actions:"
    )

    for action in evidence[
        "recommended_actions"
    ]:

        print(
            f"  {action['action']}: "
            f"{action['successful_cases']}"
        )


if __name__ == "__main__":
    main()