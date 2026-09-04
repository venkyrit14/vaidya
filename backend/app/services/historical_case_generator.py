from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

OUTPUT_DIR = BASE_DIR / "data" / "generated"

OUTPUT_PATH = (
    OUTPUT_DIR
    / "historical_recovery_cases.csv"
)


# =========================================================
# CONFIGURATION
# =========================================================

TOTAL_CASES = 3000

RANDOM_SEED = 2026


# =========================================================
# PAYMENT RECOVERY SCENARIOS
# =========================================================

PAYMENT_SCENARIOS = [
    {
        "root_cause": "insufficient_funds",
        "action": "delayed_retry",
        "success_probability": 0.65,
    },
    {
        "root_cause": "bank_timeout",
        "action": "delayed_retry",
        "success_probability": 0.80,
    },
    {
        "root_cause": "network_error",
        "action": "retry",
        "success_probability": 0.85,
    },
    {
        "root_cause": "expired_card",
        "action": "payment_method_update",
        "success_probability": 0.55,
    },
    {
        "root_cause": "mandate_failure",
        "action": "mandate_retry",
        "success_probability": 0.70,
    },
]


# =========================================================
# CHECKOUT RECOVERY SCENARIOS
# =========================================================

CHECKOUT_SCENARIOS = [
    {
        "root_cause": "high_intent_abandonment",
        "action": "targeted_reminder",
        "success_probability": 0.72,
    },
    {
        "root_cause": "checkout_hesitation",
        "action": "reminder",
        "success_probability": 0.50,
    },
    {
        "root_cause": "repeated_abandonment",
        "action": "stop_outreach",
        "success_probability": 0.20,
    },
]


# =========================================================
# INVOICE RECOVERY SCENARIOS
# =========================================================

INVOICE_SCENARIOS = [
    {
        "root_cause": "recently_overdue",
        "action": "payment_reminder",
        "success_probability": 0.65,
    },
    {
        "root_cause": "repeated_late_payer",
        "action": "promise_to_pay",
        "success_probability": 0.72,
    },
    {
        "root_cause": "high_value_overdue",
        "action": "account_escalation",
        "success_probability": 0.50,
    },
    {
        "root_cause": "customer_dispute",
        "action": "human_review",
        "success_probability": 0.25,
    },
]


# =========================================================
# OUTCOME GENERATION
# =========================================================

def generate_outcome(rng, success_probability):
    """
    Generate a historical recovery outcome.

    recovered:
        Full amount recovered.

    partial:
        Some amount recovered.

    failed:
        Nothing recovered.

    blocked:
        Recovery was intentionally prevented by policy.
    """

    random_value = rng.random()

    if success_probability <= 0:
        return "blocked"

    if random_value < success_probability:
        return "recovered"

    if random_value < success_probability + 0.10:
        return "partial"

    return "failed"


# =========================================================
# RECOVERY AMOUNT
# =========================================================

def generate_recovered_amount(
    rng,
    amount,
    outcome
):
    """
    Calculate the amount recovered from a historical case.
    """

    if outcome == "recovered":
        return round(amount, 2)

    if outcome == "partial":

        recovery_fraction = rng.uniform(
            0.25,
            0.75
        )

        return round(
            amount * recovery_fraction,
            2
        )

    # failed / blocked
    return 0.0


# =========================================================
# PAYMENT CASES
# =========================================================

def create_payment_cases(
    payment_df,
    count,
    rng
):
    """
    Create historical payment-recovery cases.

    IMPORTANT:

    Fraud is NEVER randomly assigned.

    A case becomes fraud_risk ONLY when the source
    payment event has fraud_flag=True.
    """

    selected = payment_df.sample(
        n=count,
        replace=True,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    cases = []

    for _, row in selected.iterrows():

        amount = float(
            row["amount_at_risk"]
        )

        fraud_flag = bool(
            row["fraud_flag"]
        )

        # -------------------------------------------------
        # SAFETY BRANCH
        # -------------------------------------------------

        if fraud_flag:

            root_cause = "fraud_risk"

            action = "block_and_escalate"

            policy_result = "blocked"

            outcome = "blocked"

            recovered_amount = 0.0

            days_to_recovery = 0

        # -------------------------------------------------
        # NORMAL PAYMENT RECOVERY
        # -------------------------------------------------

        else:

            scenario = PAYMENT_SCENARIOS[
                rng.integers(
                    0,
                    len(PAYMENT_SCENARIOS)
                )
            ]

            root_cause = scenario["root_cause"]

            action = scenario["action"]

            policy_result = "approved"

            outcome = generate_outcome(
                rng,
                scenario["success_probability"]
            )

            recovered_amount = (
                generate_recovered_amount(
                    rng,
                    amount,
                    outcome
                )
            )

            if outcome == "recovered":

                days_to_recovery = int(
                    rng.integers(1, 4)
                )

            elif outcome == "partial":

                days_to_recovery = int(
                    rng.integers(2, 7)
                )

            else:

                days_to_recovery = 0

        # -------------------------------------------------
        # DESCRIPTIVE INFORMATION
        # -------------------------------------------------

        problem_summary = (
            f"Payment of ₹{amount:,.2f} "
            f"failed during the payment flow."
        )

        customer_profile = (
            "Returning customer with "
            "historical transaction activity."
        )

        cases.append(
            {
                "event_type": "payment_failure",
                "amount": amount,
                "customer_profile": customer_profile,
                "problem_summary": problem_summary,
                "root_cause": root_cause,
                "action_taken": action,
                "policy_result": policy_result,
                "outcome": outcome,
                "recovered_amount": recovered_amount,
                "days_to_recovery": days_to_recovery,
            }
        )

    return cases


# =========================================================
# CHECKOUT CASES
# =========================================================

def create_checkout_cases(
    checkout_df,
    count,
    rng
):
    """
    Create historical checkout-recovery cases.

    Customer history is used to determine the historical
    scenario.
    """

    selected = checkout_df.sample(
        n=count,
        replace=True,
        random_state=RANDOM_SEED + 1
    ).reset_index(drop=True)

    cases = []

    for _, row in selected.iterrows():

        history_score = float(
            row["customer_history_score"]
        )

        abandonment_age = int(
            row["abandonment_age_minutes"]
        )

        cart_value = float(
            row["amount_at_risk"]
        )

        # -------------------------------------------------
        # Determine scenario.
        # -------------------------------------------------

        if history_score >= 0.80:

            scenario = CHECKOUT_SCENARIOS[0]

        elif history_score < 0.60:

            scenario = CHECKOUT_SCENARIOS[2]

        else:

            scenario = CHECKOUT_SCENARIOS[1]

        # -------------------------------------------------
        # Generate outcome.
        # -------------------------------------------------

        outcome = generate_outcome(
            rng,
            scenario["success_probability"]
        )

        policy_result = "approved"

        recovered_amount = (
            generate_recovered_amount(
                rng,
                cart_value,
                outcome
            )
        )

        if outcome == "recovered":

            days_to_recovery = int(
                rng.integers(1, 3)
            )

        elif outcome == "partial":

            days_to_recovery = int(
                rng.integers(1, 5)
            )

        else:

            days_to_recovery = 0

        # -------------------------------------------------
        # Descriptive information.
        # -------------------------------------------------

        problem_summary = (
            f"Checkout worth ₹{cart_value:,.2f} "
            f"was abandoned after "
            f"{abandonment_age} minutes."
        )

        customer_profile = (
            f"Customer history score: "
            f"{history_score:.2f}"
        )

        cases.append(
            {
                "event_type": "checkout_abandonment",
                "amount": cart_value,
                "customer_profile": customer_profile,
                "problem_summary": problem_summary,
                "root_cause": scenario["root_cause"],
                "action_taken": scenario["action"],
                "policy_result": policy_result,
                "outcome": outcome,
                "recovered_amount": recovered_amount,
                "days_to_recovery": days_to_recovery,
            }
        )

    return cases


# =========================================================
# INVOICE CASES
# =========================================================

def create_invoice_cases(
    invoice_df,
    count,
    rng
):
    """
    Create historical B2B invoice recovery cases.

    The scenario assignment deliberately covers all four
    invoice recovery scenarios.
    """

    selected = invoice_df.sample(
        n=count,
        replace=True,
        random_state=RANDOM_SEED + 2
    ).reset_index(drop=True)

    cases = []

    for index, row in selected.iterrows():

        amount = float(
            row["amount_at_risk"]
        )

        days_overdue = int(
            row["days_overdue"]
        )

        previous_late_payments = int(
            row["previous_late_payment_count"]
        )

        # -------------------------------------------------
        # IMPORTANT:
        #
        # We intentionally introduce customer disputes
        # using a deterministic synthetic rule.
        #
        # This does NOT claim the source data contains
        # disputes.
        # -------------------------------------------------

        dispute_signal = (
            index % 20 == 0
        )

        # -------------------------------------------------
        # Scenario priority:
        #
        # 1. Customer dispute
        # 2. High-value overdue
        # 3. Repeated late payer
        # 4. Recently overdue
        # -------------------------------------------------

        if dispute_signal:

            scenario = INVOICE_SCENARIOS[3]

        elif (
            amount >= 500000
            and days_overdue >= 30
        ):

            scenario = INVOICE_SCENARIOS[2]

        elif previous_late_payments >= 4:

            scenario = INVOICE_SCENARIOS[1]

        elif days_overdue <= 15:

            scenario = INVOICE_SCENARIOS[0]

        else:

            scenario = INVOICE_SCENARIOS[1]

        # -------------------------------------------------
        # Generate outcome.
        # -------------------------------------------------

        outcome = generate_outcome(
            rng,
            scenario["success_probability"]
        )

        # Human review is an escalation workflow.
        if scenario["action"] == "human_review":

            policy_result = "escalated"

        else:

            policy_result = "approved"

        recovered_amount = (
            generate_recovered_amount(
                rng,
                amount,
                outcome
            )
        )

        if outcome == "recovered":

            days_to_recovery = int(
                rng.integers(2, 15)
            )

        elif outcome == "partial":

            days_to_recovery = int(
                rng.integers(5, 20)
            )

        else:

            days_to_recovery = 0

        # -------------------------------------------------
        # Descriptive information.
        # -------------------------------------------------

        problem_summary = (
            f"Invoice of ₹{amount:,.2f} "
            f"is {days_overdue} days overdue."
        )

        customer_profile = (
            f"{row['previous_invoice_count']} "
            f"previous invoices; "
            f"{previous_late_payments} "
            f"previous late payments."
        )

        cases.append(
            {
                "event_type": "overdue_invoice",
                "amount": amount,
                "customer_profile": customer_profile,
                "problem_summary": problem_summary,
                "root_cause": scenario["root_cause"],
                "action_taken": scenario["action"],
                "policy_result": policy_result,
                "outcome": outcome,
                "recovered_amount": recovered_amount,
                "days_to_recovery": days_to_recovery,
            }
        )

    return cases


# =========================================================
# MAIN CASE GENERATION
# =========================================================

def create_historical_cases():

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    print("Loading Vaidya event datasets...")

    payment_path = (
        BASE_DIR
        / "data"
        / "generated"
        / "payment_failure_events.csv"
    )

    checkout_path = (
        BASE_DIR
        / "data"
        / "generated"
        / "checkout_abandonment_events.csv"
    )

    invoice_path = (
        BASE_DIR
        / "data"
        / "generated"
        / "overdue_invoice_events.csv"
    )

    # -----------------------------------------------------
    # Load datasets.
    # -----------------------------------------------------

    payment_df = pd.read_csv(
        payment_path
    )

    checkout_df = pd.read_csv(
        checkout_path
    )

    invoice_df = pd.read_csv(
        invoice_path
    )

    print(
        f"Payment events: {len(payment_df)}"
    )

    print(
        f"Checkout events: {len(checkout_df)}"
    )

    print(
        f"Invoice events: {len(invoice_df)}"
    )

    # -----------------------------------------------------
    # Split total historical cases.
    # -----------------------------------------------------

    payment_count = int(
        TOTAL_CASES * 0.45
    )

    checkout_count = int(
        TOTAL_CASES * 0.30
    )

    invoice_count = (
        TOTAL_CASES
        - payment_count
        - checkout_count
    )

    # -----------------------------------------------------
    # Generate cases.
    # -----------------------------------------------------

    cases = []

    cases.extend(
        create_payment_cases(
            payment_df,
            payment_count,
            rng
        )
    )

    cases.extend(
        create_checkout_cases(
            checkout_df,
            checkout_count,
            rng
        )
    )

    cases.extend(
        create_invoice_cases(
            invoice_df,
            invoice_count,
            rng
        )
    )

    # -----------------------------------------------------
    # Convert to DataFrame.
    # -----------------------------------------------------

    historical = pd.DataFrame(
        cases
    )

    # -----------------------------------------------------
    # Add unique case IDs.
    # -----------------------------------------------------

    historical.insert(
        0,
        "case_id",
        [
            f"CASE_{i:05d}"
            for i in range(
                1,
                len(historical) + 1
            )
        ]
    )

    return historical


# =========================================================
# VALIDATION BEFORE SAVING
# =========================================================

def validate_cases(historical):

    print()
    print("Running internal validation...")

    errors = []

    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------

    if len(historical) != TOTAL_CASES:
        errors.append(
            f"Expected {TOTAL_CASES} cases, "
            f"found {len(historical)}."
        )

    if historical["case_id"].duplicated().any():
        errors.append(
            "Duplicate case IDs detected."
        )

    if historical.isnull().any().any():
        errors.append(
            "Missing values detected."
        )

    # -----------------------------------------------------
    # Financial validation
    # -----------------------------------------------------

    if (
        historical["amount"] <= 0
    ).any():

        errors.append(
            "Non-positive historical amount detected."
        )

    if (
        historical["recovered_amount"] < 0
    ).any():

        errors.append(
            "Negative recovered amount detected."
        )

    if (
        historical["recovered_amount"]
        > historical["amount"]
    ).any():

        errors.append(
            "Recovered amount exceeds original amount."
        )

    # -----------------------------------------------------
    # Outcome validation
    # -----------------------------------------------------

    invalid_recovered = (
        (historical["outcome"] == "recovered")
        & (
            historical["recovered_amount"] <= 0
        )
    )

    if invalid_recovered.any():

        errors.append(
            "Recovered case has zero recovered amount."
        )

    invalid_failed = (
        (historical["outcome"] == "failed")
        & (
            historical["recovered_amount"] > 0
        )
    )

    if invalid_failed.any():

        errors.append(
            "Failed case has recovered amount."
        )

    invalid_blocked = (
        (historical["outcome"] == "blocked")
        & (
            historical["recovered_amount"] > 0
        )
    )

    if invalid_blocked.any():

        errors.append(
            "Blocked case has recovered amount."
        )

    # -----------------------------------------------------
    # FRAUD SAFETY VALIDATION
    # -----------------------------------------------------

    fraud_cases = historical[
        historical["root_cause"] == "fraud_risk"
    ]

    if len(fraud_cases) > 0:

        invalid_fraud_action = (
            fraud_cases["action_taken"]
            != "block_and_escalate"
        ).any()

        if invalid_fraud_action:

            errors.append(
                "Fraud case has an invalid action."
            )

        invalid_fraud_policy = (
            fraud_cases["policy_result"]
            != "blocked"
        ).any()

        if invalid_fraud_policy:

            errors.append(
                "Fraud case has an approved policy result."
            )

        invalid_fraud_outcome = (
            fraud_cases["outcome"]
            != "blocked"
        ).any()

        if invalid_fraud_outcome:

            errors.append(
                "Fraud case has a non-blocked outcome."
            )

        fraud_recovery = (
            fraud_cases["recovered_amount"] > 0
        ).any()

        if fraud_recovery:

            errors.append(
                "Fraud case has recovered revenue."
            )

    # -----------------------------------------------------
    # Invoice dispute validation
    # -----------------------------------------------------

    dispute_cases = historical[
        historical["root_cause"] == "customer_dispute"
    ]

    if len(dispute_cases) > 0:

        invalid_dispute_action = (
            dispute_cases["action_taken"]
            != "human_review"
        ).any()

        if invalid_dispute_action:

            errors.append(
                "Customer dispute has invalid action."
            )

        invalid_dispute_policy = (
            dispute_cases["policy_result"]
            != "escalated"
        ).any()

        if invalid_dispute_policy:

            errors.append(
                "Customer dispute is not escalated."
            )

    # -----------------------------------------------------
    # Report validation.
    # -----------------------------------------------------

    if errors:

        print()
        print("VALIDATION FAILED.")

        for error in errors:
            print(f"- {error}")

        raise ValueError(
            "Historical case validation failed."
        )

    print(
        "Internal validation PASSED."
    )


# =========================================================
# SAVE
# =========================================================

def save_cases(historical):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    historical.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print(
        "Historical recovery case dataset created."
    )

    print(
        f"Total cases: {len(historical)}"
    )

    print()
    print("Cases by event type:")

    print(
        historical["event_type"]
        .value_counts()
    )

    print()
    print("Root causes:")

    print(
        historical["root_cause"]
        .value_counts()
    )

    print()
    print("Actions:")

    print(
        historical["action_taken"]
        .value_counts()
    )

    print()
    print("Policy results:")

    print(
        historical["policy_result"]
        .value_counts()
    )

    print()
    print("Outcomes:")

    print(
        historical["outcome"]
        .value_counts()
    )

    print()

    total_amount = (
        historical["amount"].sum()
    )

    total_recovered = (
        historical["recovered_amount"].sum()
    )

    recovery_rate = (
        total_recovered
        / total_amount
        * 100
    )

    print(
        f"Total historical amount: "
        f"₹{total_amount:,.2f}"
    )

    print(
        f"Total recovered amount: "
        f"₹{total_recovered:,.2f}"
    )

    print(
        f"Historical recovery rate: "
        f"{recovery_rate:.2f}%"
    )

    print()
    print("Saved to:")
    print(OUTPUT_PATH)


# =========================================================
# MAIN
# =========================================================

def main():

    historical = create_historical_cases()

    validate_cases(
        historical
    )

    save_cases(
        historical
    )


if __name__ == "__main__":
    main()