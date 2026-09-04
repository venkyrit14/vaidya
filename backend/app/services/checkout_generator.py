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
    / "checkout_abandonment_events.csv"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TOTAL_CHECKOUTS = 2000

# Minimum time after which an incomplete checkout
# can be considered abandoned.
MIN_ABANDONMENT_MINUTES = 30

# Maximum simulated abandonment age.
MAX_ABANDONMENT_MINUTES = 1440  # 24 hours


# ---------------------------------------------------------
# Customer history score
# ---------------------------------------------------------

def calculate_customer_history(df):
    """
    Create a simple customer behavior score from the
    transaction history available in the canonical dataset.

    This is a derived demo feature, not a production
    credit/risk score.
    """

    customer_stats = (
        df.groupby("customer_id")
        .agg(
            transaction_count=("event_id", "count"),
            average_amount=("amount", "mean"),
            fraud_count=("fraud_flag", "sum")
        )
        .reset_index()
    )

    # Normalize transaction count.
    max_transactions = customer_stats["transaction_count"].max()

    if max_transactions == 0:
        customer_stats["activity_score"] = 0.0
    else:
        customer_stats["activity_score"] = (
            customer_stats["transaction_count"]
            / max_transactions
        )

    # Fraud-free history receives a positive contribution.
    customer_stats["trust_score"] = (
        1
        - (
            customer_stats["fraud_count"]
            / customer_stats["transaction_count"]
        )
    )

    # Final history score.
    customer_stats["customer_history_score"] = (
        0.6 * customer_stats["activity_score"]
        + 0.4 * customer_stats["trust_score"]
    ).round(3)

    return customer_stats[
        [
            "customer_id",
            "customer_history_score"
        ]
    ]


# ---------------------------------------------------------
# Generate checkout events
# ---------------------------------------------------------

def create_checkout_events():

    print("Loading canonical transaction data...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Available canonical events: {len(df)}")

    if len(df) < TOTAL_CHECKOUTS:
        raise ValueError(
            "Not enough canonical events to create checkout cases."
        )

    # -----------------------------------------------------
    # Build customer history.
    # -----------------------------------------------------

    customer_history = calculate_customer_history(df)

    # -----------------------------------------------------
    # Select representative transactions.
    #
    # These transactions provide realistic customer IDs,
    # amounts and merchant context for the checkout
    # simulation.
    # -----------------------------------------------------

    selected = df.sample(
        n=TOTAL_CHECKOUTS,
        random_state=2026
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # Attach customer history score.
    # -----------------------------------------------------

    selected = selected.merge(
        customer_history,
        on="customer_id",
        how="left"
    )

    # -----------------------------------------------------
    # Create checkout IDs.
    # -----------------------------------------------------

    events = pd.DataFrame(index=selected.index)

    events["event_id"] = (
        "CHK_"
        + (events.index + 1)
        .astype(str)
        .str.zfill(5)
    )

    events["event_type"] = "checkout_abandonment"

    # -----------------------------------------------------
    # Simulate the checkout timestamps.
    #
    # We use the transaction timestamp as the starting
    # point for the simulated checkout.
    # -----------------------------------------------------

    checkout_started = pd.to_datetime(
        selected["timestamp"]
    )

    events["checkout_started_at"] = checkout_started

    # -----------------------------------------------------
    # Generate deterministic abandonment durations.
    # -----------------------------------------------------

    durations = (
        (
            events.index * 37
            + 47
        )
        % (
            MAX_ABANDONMENT_MINUTES
            - MIN_ABANDONMENT_MINUTES
            + 1
        )
        + MIN_ABANDONMENT_MINUTES
    )

    events["abandonment_age_minutes"] = durations.astype(int)

    # Last activity happens shortly after checkout starts.
    activity_offset = (
        events.index % 10
    )

    events["last_activity_at"] = (
        checkout_started
        + pd.to_timedelta(
            activity_offset,
            unit="m"
        )
    )

    # Detection timestamp.
    events["timestamp"] = (
        events["last_activity_at"]
        + pd.to_timedelta(
            events["abandonment_age_minutes"],
            unit="m"
        )
    )

    # -----------------------------------------------------
    # Customer information.
    # -----------------------------------------------------

    events["customer_id"] = selected["customer_id"].values

    events["customer_history_score"] = (
        selected["customer_history_score"]
        .round(3)
        .values
    )

    # -----------------------------------------------------
    # Checkout ID.
    # -----------------------------------------------------

    events["checkout_id"] = (
        "CHK_SESSION_"
        + (events.index + 1)
        .astype(str)
        .str.zfill(6)
    )

    # -----------------------------------------------------
    # Cart information.
    # -----------------------------------------------------

    events["cart_value"] = (
        selected["amount"]
        .clip(lower=83)
        .round(2)
        .values
    )

    events["amount_at_risk"] = events["cart_value"]

    events["currency"] = "INR"

    # Generate item counts from transaction amounts.
    events["items_count"] = (
        (
            events["cart_value"] / 1000
        )
        .round()
        .clip(
            lower=1,
            upper=10
        )
        .astype(int)
    )

    # -----------------------------------------------------
    # Checkout lifecycle state.
    #
    # Because this file represents the ABANDONMENT queue,
    # completion is always false.
    # -----------------------------------------------------

    events["payment_attempted"] = False

    events["payment_completed"] = False

    events["checkout_completed"] = False

    # -----------------------------------------------------
    # Abandonment detection.
    # -----------------------------------------------------

    events["abandonment_detected"] = (
        (events["checkout_completed"] == False)
        & (
            events["abandonment_age_minutes"]
            >= MIN_ABANDONMENT_MINUTES
        )
    )

    # -----------------------------------------------------
    # Keep only events that actually crossed the
    # abandonment threshold.
    # -----------------------------------------------------

    events = events[
        events["abandonment_detected"] == True
    ].copy()

    # -----------------------------------------------------
    # Clean column ordering.
    # -----------------------------------------------------

    events = events[
        [
            "event_id",
            "event_type",
            "timestamp",
            "checkout_id",
            "customer_id",
            "amount_at_risk",
            "currency",
            "cart_value",
            "items_count",
            "checkout_started_at",
            "last_activity_at",
            "abandonment_age_minutes",
            "payment_attempted",
            "payment_completed",
            "checkout_completed",
            "abandonment_detected",
            "customer_history_score",
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
    print("Checkout abandonment dataset created.")
    print(f"Total events: {len(events)}")

    print(
        f"Minimum abandonment age: "
        f"{events['abandonment_age_minutes'].min()} minutes"
    )

    print(
        f"Maximum abandonment age: "
        f"{events['abandonment_age_minutes'].max()} minutes"
    )

    print(
        f"Average cart value: "
        f"₹{events['cart_value'].mean():,.2f}"
    )

    print()
    print("Saved to:")
    print(OUTPUT_PATH)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    events = create_checkout_events()

    save_events(events)


if __name__ == "__main__":
    main()