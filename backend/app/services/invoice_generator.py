from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[3]

OUTPUT_DIR = BASE_DIR / "data" / "generated"

OUTPUT_PATH = (
    OUTPUT_DIR
    / "overdue_invoice_events.csv"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TOTAL_INVOICES = 1500

RANDOM_SEED = 2026


# ---------------------------------------------------------
# Generate B2B customer profiles
# ---------------------------------------------------------

def create_customer_profiles(rng):
    """
    Create a synthetic set of B2B customer profiles.

    These customers are intentionally separate from the
    consumer/card customers in the Kaggle transaction
    dataset because an invoice represents a different
    business object.
    """

    customer_ids = [
        f"B2B_{i:04d}"
        for i in range(1, 301)
    ]

    profiles = []

    for customer_id in customer_ids:

        previous_invoice_count = int(
            rng.integers(3, 15)
        )

        # Some customers have a history of late payments.
        late_payment_probability = rng.choice(
            [
                0.05,
                0.15,
                0.30,
                0.50
            ],
            p=[
                0.35,
                0.35,
                0.20,
                0.10
            ]
        )

        previous_late_payment_count = int(
            rng.binomial(
                previous_invoice_count,
                late_payment_probability
            )
        )

        profiles.append(
            {
                "customer_id": customer_id,
                "previous_invoice_count":
                    previous_invoice_count,
                "previous_late_payment_count":
                    previous_late_payment_count,
            }
        )

    return pd.DataFrame(profiles)


# ---------------------------------------------------------
# Generate invoice events
# ---------------------------------------------------------

def create_invoice_events():

    rng = np.random.default_rng(RANDOM_SEED)

    print("Creating synthetic B2B customer profiles...")

    customers = create_customer_profiles(rng)

    print(
        f"Created {len(customers)} B2B customer profiles."
    )

    # -----------------------------------------------------
    # Select customers for current overdue invoices.
    # -----------------------------------------------------

    selected_customers = customers.sample(
        n=TOTAL_INVOICES,
        replace=True,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    events = pd.DataFrame(
        index=selected_customers.index
    )

    # -----------------------------------------------------
    # IDs
    # -----------------------------------------------------

    events["event_id"] = (
        "INV_EVT_"
        + (events.index + 1)
        .astype(str)
        .str.zfill(5)
    )

    events["event_type"] = "overdue_invoice"

    events["invoice_id"] = (
        "INV_"
        + (events.index + 1)
        .astype(str)
        .str.zfill(6)
    )

    events["customer_id"] = (
        selected_customers["customer_id"]
        .values
    )

    # -----------------------------------------------------
    # Invoice amounts
    #
    # B2B invoice values are deliberately larger than
    # typical consumer checkout amounts.
    # -----------------------------------------------------

    amounts = rng.lognormal(
        mean=np.log(75000),
        sigma=0.8,
        size=TOTAL_INVOICES
    )

    amounts = np.clip(
        amounts,
        10000,
        1000000
    )

    events["amount_at_risk"] = (
        np.round(amounts, 2)
    )

    events["currency"] = "INR"

    # -----------------------------------------------------
    # Invoice dates
    # -----------------------------------------------------

    invoice_dates = pd.Timestamp("2026-08-01") - pd.to_timedelta(
        rng.integers(
            15,
            120,
            size=TOTAL_INVOICES
        ),
        unit="D"
    )

    events["invoice_date"] = invoice_dates

    # -----------------------------------------------------
    # Payment due dates
    #
    # Typical B2B payment terms are simulated as
    # 15 / 30 / 45 day terms.
    # -----------------------------------------------------

    payment_terms = rng.choice(
        [15, 30, 45],
        size=TOTAL_INVOICES,
        p=[0.25, 0.55, 0.20]
    )

    events["due_date"] = (
        events["invoice_date"]
        + pd.to_timedelta(
            payment_terms,
            unit="D"
        )
    )

    # -----------------------------------------------------
    # Detection date
    #
    # We use a fixed simulated current date so the dataset
    # remains reproducible.
    # -----------------------------------------------------

    detection_date = pd.Timestamp(
        "2026-08-29"
    )

    events["timestamp"] = detection_date

    # -----------------------------------------------------
    # Days overdue
    # -----------------------------------------------------

    events["days_overdue"] = (
        detection_date
        - events["due_date"]
    ).dt.days

    # -----------------------------------------------------
    # Keep only genuinely overdue invoices.
    # -----------------------------------------------------

    events = events[
        events["days_overdue"] > 0
    ].copy()

    # -----------------------------------------------------
    # Payment status
    # -----------------------------------------------------

    events["payment_status"] = "overdue"

    # -----------------------------------------------------
    # Previous payment history
    # -----------------------------------------------------

    events["previous_invoice_count"] = (
        selected_customers.loc[
            events.index,
            "previous_invoice_count"
        ].values
    )

    events["previous_late_payment_count"] = (
        selected_customers.loc[
            events.index,
            "previous_late_payment_count"
        ].values
    )

    # -----------------------------------------------------
    # Reminder history
    #
    # More overdue invoices may already have received
    # reminders.
    # -----------------------------------------------------

    # Simulate reminder history with a more realistic
# distribution rather than making reminder count
# directly proportional to days overdue.

    events["reminder_count"] = rng.choice(
    [0, 1, 2, 3],
    size=len(events),
    p=[0.20, 0.30, 0.30, 0.20]
     )

    # -----------------------------------------------------
    # Payment status consistency
    # -----------------------------------------------------

    events["payment_received"] = False

    # -----------------------------------------------------
    # Clean column order
    # -----------------------------------------------------

    events = events[
        [
            "event_id",
            "event_type",
            "timestamp",
            "invoice_id",
            "customer_id",
            "amount_at_risk",
            "currency",
            "invoice_date",
            "due_date",
            "days_overdue",
            "payment_status",
            "payment_received",
            "previous_invoice_count",
            "previous_late_payment_count",
            "reminder_count",
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
    print("Overdue invoice dataset created.")

    print(
        f"Total overdue invoices: "
        f"{len(events)}"
    )

    print(
        f"Minimum amount: "
        f"₹{events['amount_at_risk'].min():,.2f}"
    )

    print(
        f"Maximum amount: "
        f"₹{events['amount_at_risk'].max():,.2f}"
    )

    print(
        f"Average amount: "
        f"₹{events['amount_at_risk'].mean():,.2f}"
    )

    print(
        f"Average days overdue: "
        f"{events['days_overdue'].mean():.1f}"
    )

    print()
    print("Saved to:")
    print(OUTPUT_PATH)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    events = create_invoice_events()

    save_events(events)


if __name__ == "__main__":
    main()