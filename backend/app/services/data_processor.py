import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "fraudTrain.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "canonical_events.csv"


def load_raw_data():
    """Load the raw Kaggle transaction dataset."""
    return pd.read_csv(RAW_DATA_PATH)


def create_canonical_events(df):
    """Transform raw transaction data into Vaidya's canonical format."""

    canonical = pd.DataFrame()

    # Transaction identifier
    canonical["event_id"] = df["trans_num"]

    # Timestamp
    canonical["timestamp"] = pd.to_datetime(
        df["trans_date_trans_time"]
    )

    # Create an anonymous customer identifier.
    # We do not store the original card number.
    canonical["customer_id"] = (
        "CUST_" + pd.factorize(df["cc_num"])[0].astype(str)
    )

    # Merchant information
    canonical["merchant"] = df["merchant"]
    canonical["merchant_category"] = df["category"]

    # The public dataset uses transaction amounts from a US-based
# synthetic transaction environment.
#
# For Vaidya's Razorpay-style demo, we normalize these amounts
# into INR using a fixed simulation conversion rate.
    USD_TO_INR = 83.0

    canonical["amount"] = (df["amt"] * USD_TO_INR).round(2)

# This is a demo normalization, not a live FX rate.
    canonical["currency"] = "INR"

    # Fraud signal from the public dataset
    canonical["fraud_flag"] = df["is_fraud"].astype(bool)

    # Derive a simple customer/location segment.
    canonical["customer_segment"] = pd.cut(
        df["city_pop"],
        bins=[-1, 50000, 200000, float("inf")],
        labels=["low", "medium", "high"]
    ).astype(str)

    return canonical


def save_canonical_events(canonical):
    """Save processed events to the data/processed directory."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    canonical.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(f"Saved {len(canonical)} events to:")
    print(OUTPUT_PATH)


def main():
    print("Loading raw transaction data...")

    df = load_raw_data()

    print(f"Loaded {len(df)} transactions.")

    print("Creating canonical Vaidya events...")

    canonical = create_canonical_events(df)

    save_canonical_events(canonical)


if __name__ == "__main__":
    main()