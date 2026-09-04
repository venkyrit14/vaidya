import hashlib
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "canonical_events.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "generated"

OUTPUT_PATH = (
    OUTPUT_DIR
    / "payment_failure_events.csv"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TOTAL_EVENTS = 5000
FRAUD_EVENTS = 30

# The remaining events are non-fraud payment cases.
NORMAL_EVENTS = TOTAL_EVENTS - FRAUD_EVENTS


# ---------------------------------------------------------
# Deterministic helper
# ---------------------------------------------------------

def stable_number(value):
    """
    Convert a value into a deterministic integer.

    We use MD5 instead of Python's built-in hash()
    because Python hash values can change between runs.
    """

    digest = hashlib.md5(
        str(value).encode("utf-8")
    ).hexdigest()

    return int(digest[:8], 16)


# ---------------------------------------------------------
# Scenario assignment
# ---------------------------------------------------------

def assign_failure_scenario(event_id):
    """
    Deterministically assign a payment failure scenario.

    This is synthetic scenario generation.
    It is not claimed to represent Razorpay's actual
    production failure distribution.
    """

    number = stable_number(event_id) % 100

    if number < 30:
        return "insufficient_funds"

    if number < 55:
        return "bank_timeout"

    if number < 75:
        return "network_error"

    if number < 90:
        return "expired_card"

    return "mandate_failure"


# ---------------------------------------------------------
# Payment method assignment
# ---------------------------------------------------------

def assign_payment_method(event_id, scenario):
    """
    Assign a logically compatible payment method.
    """

    if scenario == "mandate_failure":
        return "upi_autopay"

    number = stable_number(event_id) % 3

    methods = [
        "card",
        "upi",
        "netbanking",
    ]

    return methods[number]


# ---------------------------------------------------------
# Failure details
# ---------------------------------------------------------

FAILURE_DETAILS = {
    "insufficient_funds": {
        "error_code": "FUNDS_UNAVAILABLE",
        "error_description": "Available balance was insufficient for the payment.",
        "error_source": "bank",
        "error_step": "authorization",
    },
    "bank_timeout": {
        "error_code": "BANK_TIMEOUT",
        "error_description": "The issuing bank did not respond within the allowed window.",
        "error_source": "bank",
        "error_step": "authorization",
    },
    "network_error": {
        "error_code": "NETWORK_ERROR",
        "error_description": "A temporary network error interrupted the payment flow.",
        "error_source": "gateway",
        "error_step": "payment_processing",
    },
    "expired_card": {
        "error_code": "CARD_EXPIRED",
        "error_description": "The payment card is expired or no longer valid.",
        "error_source": "customer_payment_method",
        "error_step": "payment_validation",
    },
    "mandate_failure": {
        "error_code": "MANDATE_FAILED",
        "error_description": "The recurring payment mandate could not be executed.",
        "error_source": "bank",
        "error_step": "mandate_execution",
    },
}


# ---------------------------------------------------------
# Build payment failure events
# ---------------------------------------------------------

def create_payment_events():

    print("Loading canonical transaction data...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Available canonical events: {len(df)}")

    # Separate fraud and non-fraud transactions.
    fraud_df = df[df["fraud_flag"] == True]

    normal_df = df[df["fraud_flag"] == False]

    if len(fraud_df) < FRAUD_EVENTS:
        raise ValueError(
            "Not enough fraud events available in canonical dataset."
        )

    if len(normal_df) < NORMAL_EVENTS:
        raise ValueError(
            "Not enough non-fraud events available in canonical dataset."
        )

    # -----------------------------------------------------
    # Select normal transactions.
    # -----------------------------------------------------

    normal_sample = normal_df.sample(
        n=NORMAL_EVENTS,
        random_state=42
    )

    # -----------------------------------------------------
    # Select fraud transactions.
    #
    # We intentionally include a small number of fraud
    # cases so the safety branch can be demonstrated.
    # -----------------------------------------------------

    fraud_sample = fraud_df.sample(
        n=FRAUD_EVENTS,
        random_state=42
    )

    selected = pd.concat(
        [
            normal_sample,
            fraud_sample
        ],
        ignore_index=True
    )

    # Shuffle final dataset.
    selected = selected.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # Create output dataframe.
    # -----------------------------------------------------

  

    events = pd.DataFrame(index=selected.index)

    events["event_id"] = (
    "PAY_"
    + (events.index + 1).astype(str).str.zfill(5)
    )

    events["event_type"] = "payment_failure"

    events["timestamp"] = selected["timestamp"].values

    events["customer_id"] = selected["customer_id"].values

    events["amount_at_risk"] = selected["amount"].round(2).values

    events["currency"] = "INR"

    events["merchant"] = selected["merchant"].values

    events["merchant_category"] = (
        selected["merchant_category"].values
    )

    events["fraud_flag"] = selected["fraud_flag"].values

    # -----------------------------------------------------
    # Assign synthetic failure scenarios.
    #
    # Fraud cases are handled separately so that the
    # scenario does not imply a recovery action.
    # -----------------------------------------------------

    scenarios = []

    for _, row in selected.iterrows():

        if bool(row["fraud_flag"]):
            scenarios.append("fraud_risk")

        else:
            scenarios.append(
                assign_failure_scenario(row["event_id"])
            )

    events["error_reason"] = scenarios

    # -----------------------------------------------------
    # Payment methods
    # -----------------------------------------------------

    payment_methods = []

    for event_id, scenario in zip(
        events["event_id"],
        events["error_reason"]
    ):

        if scenario == "fraud_risk":
            payment_methods.append("card")
        else:
            payment_methods.append(
                assign_payment_method(
                    event_id,
                    scenario
                )
            )

    events["payment_method"] = payment_methods

    # -----------------------------------------------------
    # Payment status
    # -----------------------------------------------------

    events["payment_status"] = "failed"

    # -----------------------------------------------------
    # Failure details
    # -----------------------------------------------------

    error_codes = []
    error_descriptions = []
    error_sources = []
    error_steps = []

    for scenario in events["error_reason"]:

        if scenario == "fraud_risk":

            error_codes.append("RISK_BLOCK")
            error_descriptions.append(
                "Transaction requires risk review before recovery."
            )
            error_sources.append("risk_engine")
            error_steps.append("risk_screening")

        else:

            details = FAILURE_DETAILS[scenario]

            error_codes.append(
                details["error_code"]
            )

            error_descriptions.append(
                details["error_description"]
            )

            error_sources.append(
                details["error_source"]
            )

            error_steps.append(
                details["error_step"]
            )

    events["error_code"] = error_codes
    events["error_description"] = error_descriptions
    events["error_source"] = error_sources
    events["error_step"] = error_steps

    # -----------------------------------------------------
    # Previous attempts
    # -----------------------------------------------------

    previous_attempts = []

    for event_id in events["event_id"]:

        number = stable_number(event_id) % 4

        previous_attempts.append(number)

    events["previous_attempts"] = previous_attempts

    # -----------------------------------------------------
    # Sort columns into a clean order.
    # -----------------------------------------------------

    events = events[
        [
            "event_id",
            "event_type",
            "timestamp",
            "customer_id",
            "amount_at_risk",
            "currency",
            "merchant",
            "merchant_category",
            "payment_method",
            "payment_status",
            "error_code",
            "error_description",
            "error_source",
            "error_step",
            "error_reason",
            "fraud_flag",
            "previous_attempts",
        ]
    ]

    return events


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

def save_events(events):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    events.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("Payment failure dataset created.")
    print(f"Total events: {len(events)}")
    print(f"Fraud events: {events['fraud_flag'].sum()}")
    print()
    print("Failure scenario distribution:")
    print(
        events["error_reason"]
        .value_counts()
    )
    print()
    print("Saved to:")
    print(OUTPUT_PATH)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    events = create_payment_events()

    save_events(events)


if __name__ == "__main__":
    main()