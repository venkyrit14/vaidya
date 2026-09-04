import pandas as pd

file_path = "../data/generated/historical_recovery_cases.csv"

df = pd.read_csv(file_path)

print("\n========== DATASET OVERVIEW ==========")

print(f"Total cases: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\nCOLUMNS:")
print(df.columns.tolist())


print("\n========== EVENT TYPE DISTRIBUTION ==========")

print(
    df["event_type"].value_counts()
)


print("\n========== ROOT CAUSE DISTRIBUTION ==========")

print(
    df["root_cause"].value_counts()
)


print("\n========== ACTION DISTRIBUTION ==========")

print(
    df["action_taken"].value_counts()
)


print("\n========== POLICY DISTRIBUTION ==========")

print(
    df["policy_result"].value_counts()
)


print("\n========== OUTCOME DISTRIBUTION ==========")

print(
    df["outcome"].value_counts()
)


print("\n========== FINANCIAL CHECK ==========")

print(
    f"Total historical amount: "
    f"₹{df['amount'].sum():,.2f}"
)

print(
    f"Total recovered amount: "
    f"₹{df['recovered_amount'].sum():,.2f}"
)

recovery_rate = (
    df["recovered_amount"].sum()
    / df["amount"].sum()
    * 100
)

print(
    f"Historical recovery rate: "
    f"{recovery_rate:.2f}%"
)


print("\n========== RECOVERY AMOUNT CHECK ==========")

invalid_recovery = (
    df["recovered_amount"] < 0
).sum()

recovery_exceeds_amount = (
    df["recovered_amount"]
    > df["amount"]
).sum()

print(
    f"Negative recovered amounts: "
    f"{invalid_recovery}"
)

print(
    f"Recovered amount greater than original amount: "
    f"{recovery_exceeds_amount}"
)


print("\n========== OUTCOME CONSISTENCY ==========")

recovered_zero = (
    (df["outcome"] == "recovered")
    & (df["recovered_amount"] <= 0)
).sum()

failed_with_recovery = (
    (df["outcome"] == "failed")
    & (df["recovered_amount"] > 0)
).sum()

blocked_with_recovery = (
    (df["outcome"] == "blocked")
    & (df["recovered_amount"] > 0)
).sum()

print(
    f"Recovered cases with ₹0 recovered: "
    f"{recovered_zero}"
)

print(
    f"Failed cases with recovery amount: "
    f"{failed_with_recovery}"
)

print(
    f"Blocked cases with recovery amount: "
    f"{blocked_with_recovery}"
)


print("\n========== PAYMENT SAFETY CHECK ==========")

fraud_cases = df[
    df["root_cause"] == "fraud_risk"
]

print(
    f"Fraud-risk historical cases: "
    f"{len(fraud_cases)}"
)

if len(fraud_cases) > 0:

    print(
        "\nFraud root-cause actions:"
    )

    print(
        fraud_cases["action_taken"]
        .value_counts()
    )

    print(
        "\nFraud root-cause outcomes:"
    )

    print(
        fraud_cases["outcome"]
        .value_counts()
    )

    print(
        "\nFraud policy results:"
    )

    print(
        fraud_cases["policy_result"]
        .value_counts()
    )

    fraud_recovery = fraud_cases[
        fraud_cases["recovered_amount"] > 0
    ]

    print(
        f"\nFraud cases with recovery: "
        f"{len(fraud_recovery)}"
    )


print("\n========== ACTION / OUTCOME MATRIX ==========")

matrix = pd.crosstab(
    df["action_taken"],
    df["outcome"]
)

print(matrix)


print("\n========== MISSING VALUES ==========")

print(
    df.isnull().sum()
)


print("\n========== UNIQUE CASE IDs ==========")

print(
    f"Unique case IDs: "
    f"{df['case_id'].nunique()}"
)

print(
    f"Duplicate case IDs: "
    f"{df['case_id'].duplicated().sum()}"
)


print("\n========== SAMPLE CASES ==========")

print(
    df.sample(
        10,
        random_state=42
    ).to_string(index=False)
)