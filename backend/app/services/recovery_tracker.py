from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import json


# =========================================================
# RECOVERY RECORD
# =========================================================

@dataclass
class RecoveryRecord:
    """
    Represents the final state of one Vaidya recovery case.
    """

    case_id: str
    event_type: str
    amount_at_risk: float
    action: str
    execution_status: str
    outcome: str
    recovered_amount: float
    remaining_amount: float
    requires_human: bool
    timestamp: str
    message: str


# =========================================================
# RECOVERY TRACKER
# =========================================================

class RecoveryTracker:
    """
    Tracks recovery outcomes produced by Vaidya.

    Responsibilities:

        1. Record recovery outcomes.
        2. Calculate recovery metrics.
        3. Persist records locally.
        4. Retrieve individual cases.
        5. Provide dashboard-ready summaries.

    Current storage:
        Local JSON file.

    Later:
        Can be replaced with PostgreSQL,
        MongoDB, etc.
    """

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(
        self,
        storage_path: Optional[str] = None,
    ):

        if storage_path is None:

            backend_dir = (
                Path(__file__)
                .resolve()
                .parents[2]
            )

            storage_path = (
                backend_dir
                / "data"
                / "generated"
                / "recovery_records.json"
            )

        self.storage_path = Path(
            storage_path
        )

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.records: List[
            RecoveryRecord
        ] = []

        self._load_records()

    # =====================================================
    # LOAD RECORDS
    # =====================================================

    def _load_records(self):
        """
        Load previously saved recovery records.
        """

        if not self.storage_path.exists():

            self.records = []

            return

        try:

            with open(
                self.storage_path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):

                self.records = []

                return

            self.records = [
                RecoveryRecord(
                    **record
                )
                for record in data
            ]

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
            KeyError,
        ):

            self.records = []

    # =====================================================
    # SAVE RECORDS
    # =====================================================

    def _save_records(self):
        """
        Persist recovery records to disk.

        Uses a temporary file first so that a partially
        written JSON file is avoided.
        """

        data = [
            asdict(record)
            for record in self.records
        ]

        temporary_path = (
            self.storage_path.with_suffix(
                ".tmp"
            )
        )

        with open(
            temporary_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temporary_path.replace(
            self.storage_path
        )

    # =====================================================
    # VALIDATE AMOUNTS
    # =====================================================

    def _validate_amounts(
        self,
        amount_at_risk: float,
        recovered_amount: float,
    ):
        """
        Validate financial amounts.
        """

        if amount_at_risk < 0:

            raise ValueError(
                "Amount at risk cannot be negative."
            )

        if recovered_amount < 0:

            raise ValueError(
                "Recovered amount cannot be negative."
            )

        if recovered_amount > amount_at_risk:

            raise ValueError(
                "Recovered amount cannot exceed "
                "amount at risk."
            )

    # =====================================================
    # RECORD OUTCOME
    # =====================================================

    def record_outcome(
        self,
        case_id: str,
        event_type: str,
        amount_at_risk: float,
        action: str,
        execution_status: str,
        outcome: str,
        recovered_amount: float,
        requires_human: bool,
        message: str,
    ) -> RecoveryRecord:
        """
        Record one recovery outcome.
        """

        amount_at_risk = float(
            amount_at_risk
        )

        recovered_amount = float(
            recovered_amount
        )

        self._validate_amounts(
            amount_at_risk,
            recovered_amount,
        )

        # -------------------------------------------------
        # Calculate remaining amount
        # -------------------------------------------------

        remaining_amount = round(
            amount_at_risk
            - recovered_amount,
            2,
        )

        # -------------------------------------------------
        # Prevent duplicate cases
        # -------------------------------------------------

        existing_record = self.get_case(
            case_id
        )

        if existing_record is not None:

            raise ValueError(
                f"Recovery case '{case_id}' "
                f"already exists."
            )

        # -------------------------------------------------
        # Create record
        # -------------------------------------------------

        record = RecoveryRecord(

            case_id=case_id,

            event_type=event_type,

            amount_at_risk=round(
                amount_at_risk,
                2,
            ),

            action=action,

            execution_status=(
                execution_status
            ),

            outcome=outcome,

            recovered_amount=round(
                recovered_amount,
                2,
            ),

            remaining_amount=(
                remaining_amount
            ),

            requires_human=bool(
                requires_human
            ),

            timestamp=(
                datetime.now().isoformat()
            ),

            message=message,
        )

        # -------------------------------------------------
        # Store
        # -------------------------------------------------

        self.records.append(
            record
        )

        self._save_records()

        return record

    # =====================================================
    # RECORD EXECUTION RESULT
    # =====================================================

    def record_execution(
        self,
        case_id: str,
        event: Dict[str, Any],
        execution_result,
    ) -> RecoveryRecord:
        """
        Convert an ExecutionResult into a RecoveryRecord.
        """

        return self.record_outcome(

            case_id=case_id,

            event_type=event.get(
                "event_type",
                "unknown",
            ),

            amount_at_risk=(
                execution_result.amount_at_risk
            ),

            action=(
                execution_result.action
            ),

            execution_status=(
                execution_result.status
            ),

            outcome=(
                execution_result.outcome
            ),

            recovered_amount=(
                execution_result.recovered_amount
            ),

            requires_human=(
                execution_result.requires_human
            ),

            message=(
                execution_result.message
            ),
        )

    # =====================================================
    # GET ONE CASE
    # =====================================================

    def get_case(
        self,
        case_id: str,
    ) -> Optional[RecoveryRecord]:
        """
        Retrieve a recovery case by ID.
        """

        for record in self.records:

            if record.case_id == case_id:

                return record

        return None

    # =====================================================
    # GET ALL CASES
    # =====================================================

    def get_all_cases(
        self,
    ) -> List[RecoveryRecord]:
        """
        Return all recovery records.
        """

        return list(
            self.records
        )

    # =====================================================
    # TOTAL CASES
    # =====================================================

    def total_cases(
        self,
    ) -> int:

        return len(
            self.records
        )

    # =====================================================
    # TOTAL AMOUNT AT RISK
    # =====================================================

    def total_amount_at_risk(
        self,
    ) -> float:

        return round(
            sum(
                record.amount_at_risk
                for record in self.records
            ),
            2,
        )

    # =====================================================
    # TOTAL RECOVERED
    # =====================================================

    def total_recovered(
        self,
    ) -> float:

        return round(
            sum(
                record.recovered_amount
                for record in self.records
            ),
            2,
        )

    # =====================================================
    # TOTAL REMAINING
    # =====================================================

    def total_remaining(
        self,
    ) -> float:

        return round(
            sum(
                record.remaining_amount
                for record in self.records
            ),
            2,
        )

    # =====================================================
    # RECOVERY RATE
    # =====================================================

    def recovery_rate(
        self,
    ) -> float:

        amount_at_risk = (
            self.total_amount_at_risk()
        )

        if amount_at_risk == 0:

            return 0.0

        return round(
            (
                self.total_recovered()
                / amount_at_risk
            )
            * 100,
            2,
        )

    # =====================================================
    # OUTCOME DISTRIBUTION
    # =====================================================

    def outcome_distribution(
        self,
    ) -> Dict[str, int]:

        distribution = {}

        for record in self.records:

            outcome = record.outcome

            distribution[outcome] = (
                distribution.get(
                    outcome,
                    0,
                )
                + 1
            )

        return distribution

    # =====================================================
    # ACTION DISTRIBUTION
    # =====================================================

    def action_distribution(
        self,
    ) -> Dict[str, int]:

        distribution = {}

        for record in self.records:

            action = record.action

            distribution[action] = (
                distribution.get(
                    action,
                    0,
                )
                + 1
            )

        return distribution

    # =====================================================
    # EVENT TYPE DISTRIBUTION
    # =====================================================

    def event_type_distribution(
        self,
    ) -> Dict[str, int]:

        distribution = {}

        for record in self.records:

            event_type = (
                record.event_type
            )

            distribution[event_type] = (
                distribution.get(
                    event_type,
                    0,
                )
                + 1
            )

        return distribution

    # =====================================================
    # HUMAN REVIEW COUNT
    # =====================================================

    def human_review_count(
        self,
    ) -> int:

        return sum(
            1
            for record in self.records
            if record.requires_human
        )

    # =====================================================
    # SUCCESSFUL RECOVERY COUNT
    # =====================================================

    def successful_recovery_count(
        self,
    ) -> int:

        return sum(
            1
            for record in self.records
            if record.outcome
            == "recovered"
        )

    # =====================================================
    # FAILED RECOVERY COUNT
    # =====================================================

    def failed_recovery_count(
        self,
    ) -> int:

        return sum(
            1
            for record in self.records
            if record.outcome
            == "failed"
        )

    # =====================================================
    # PARTIAL RECOVERY COUNT
    # =====================================================

    def partial_recovery_count(
        self,
    ) -> int:

        return sum(
            1
            for record in self.records
            if record.outcome
            == "partial"
        )

    # =====================================================
    # BLOCKED COUNT
    # =====================================================

    def blocked_count(
        self,
    ) -> int:

        return sum(
            1
            for record in self.records
            if record.outcome
            == "blocked"
        )

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def get_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return dashboard-ready metrics.
        """

        return {

            "total_cases":
                self.total_cases(),

            "total_amount_at_risk":
                self.total_amount_at_risk(),

            "total_recovered":
                self.total_recovered(),

            "total_remaining":
                self.total_remaining(),

            "recovery_rate":
                self.recovery_rate(),

            "successful_recoveries":
                self.successful_recovery_count(),

            "failed_recoveries":
                self.failed_recovery_count(),

            "partial_recoveries":
                self.partial_recovery_count(),

            "blocked_cases":
                self.blocked_count(),

            "human_review_cases":
                self.human_review_count(),

            "outcomes":
                self.outcome_distribution(),

            "actions":
                self.action_distribution(),

            "event_types":
                self.event_type_distribution(),
        }


# =========================================================
# PRINT SUMMARY
# =========================================================

def print_summary(
    tracker: RecoveryTracker,
):
    """
    Print dashboard metrics.
    """

    summary = tracker.get_summary()

    print()
    print("=" * 60)
    print(
        "          VAIDYA RECOVERY TRACKER"
    )
    print("=" * 60)

    print()

    print(
        f"Total cases: "
        f"{summary['total_cases']}"
    )

    print(
        f"Total amount at risk: "
        f"₹{summary['total_amount_at_risk']:,.2f}"
    )

    print(
        f"Total recovered: "
        f"₹{summary['total_recovered']:,.2f}"
    )

    print(
        f"Total remaining: "
        f"₹{summary['total_remaining']:,.2f}"
    )

    print(
        f"Recovery rate: "
        f"{summary['recovery_rate']:.2f}%"
    )

    print(
        f"Successful recoveries: "
        f"{summary['successful_recoveries']}"
    )

    print(
        f"Failed recoveries: "
        f"{summary['failed_recoveries']}"
    )

    print(
        f"Partial recoveries: "
        f"{summary['partial_recoveries']}"
    )

    print(
        f"Blocked cases: "
        f"{summary['blocked_cases']}"
    )

    print(
        f"Human review cases: "
        f"{summary['human_review_cases']}"
    )

    print()
    print(
        "OUTCOMES"
    )
    print("-" * 60)

    for outcome, count in (
        summary["outcomes"].items()
    ):

        print(
            f"{outcome}: {count}"
        )

    print()
    print(
        "ACTIONS"
    )
    print("-" * 60)

    for action, count in (
        summary["actions"].items()
    ):

        print(
            f"{action}: {count}"
        )

    print()
    print(
        "EVENT TYPES"
    )
    print("-" * 60)

    for event_type, count in (
        summary["event_types"].items()
    ):

        print(
            f"{event_type}: {count}"
        )


# =========================================================
# TEST SUITE
# =========================================================

def run_tracker_tests():

    # -----------------------------------------------------
    # Temporary test storage
    # -----------------------------------------------------

    test_storage = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "generated"
        / "recovery_tracker_test.json"
    )

    # Remove previous test file

    if test_storage.exists():

        test_storage.unlink()

    tracker = RecoveryTracker(
        storage_path=str(
            test_storage
        )
    )

    print()
    print("=" * 60)
    print(
        "       VAIDYA RECOVERY TRACKER TESTS"
    )
    print("=" * 60)

    # =====================================================
    # TEST 1 — SUCCESSFUL RECOVERY
    # =====================================================

    record_1 = tracker.record_outcome(

        case_id="TEST_CASE_001",

        event_type="payment_failure",

        amount_at_risk=6200.00,

        action="retry",

        execution_status="completed",

        outcome="recovered",

        recovered_amount=6200.00,

        requires_human=False,

        message=(
            "Payment retry succeeded."
        ),
    )

    print()
    print(
        "TEST 1 — SUCCESSFUL RECOVERY"
    )

    print(
        f"Case: "
        f"{record_1.case_id}"
    )

    print(
        f"Recovered: "
        f"₹{record_1.recovered_amount:,.2f}"
    )

    print(
        f"Remaining: "
        f"₹{record_1.remaining_amount:,.2f}"
    )

    # =====================================================
    # TEST 2 — PARTIAL RECOVERY
    # =====================================================

    record_2 = tracker.record_outcome(

        case_id="TEST_CASE_002",

        event_type="overdue_invoice",

        amount_at_risk=100000.00,

        action="promise_to_pay",

        execution_status="scheduled",

        outcome="partial",

        recovered_amount=40000.00,

        requires_human=False,

        message=(
            "Partial payment received."
        ),
    )

    print()
    print(
        "TEST 2 — PARTIAL RECOVERY"
    )

    print(
        f"Case: "
        f"{record_2.case_id}"
    )

    print(
        f"Recovered: "
        f"₹{record_2.recovered_amount:,.2f}"
    )

    print(
        f"Remaining: "
        f"₹{record_2.remaining_amount:,.2f}"
    )

    # =====================================================
    # TEST 3 — FAILED RECOVERY
    # =====================================================

    record_3 = tracker.record_outcome(

        case_id="TEST_CASE_003",

        event_type="checkout_abandonment",

        amount_at_risk=5000.00,

        action="targeted_reminder",

        execution_status="sent",

        outcome="failed",

        recovered_amount=0.00,

        requires_human=False,

        message=(
            "Reminder sent but no payment."
        ),
    )

    print()
    print(
        "TEST 3 — FAILED RECOVERY"
    )

    print(
        f"Case: "
        f"{record_3.case_id}"
    )

    print(
        f"Recovered: "
        f"₹{record_3.recovered_amount:,.2f}"
    )

    print(
        f"Remaining: "
        f"₹{record_3.remaining_amount:,.2f}"
    )

    # =====================================================
    # TEST 4 — FRAUD / HUMAN REVIEW
    # =====================================================

    record_4 = tracker.record_outcome(

        case_id="TEST_CASE_004",

        event_type="payment_failure",

        amount_at_risk=10000.00,

        action="block_and_escalate",

        execution_status="blocked",

        outcome="blocked",

        recovered_amount=0.00,

        requires_human=True,

        message=(
            "Fraud case escalated."
        ),
    )

    print()
    print(
        "TEST 4 — FRAUD ESCALATION"
    )

    print(
        f"Case: "
        f"{record_4.case_id}"
    )

    print(
        f"Recovered: "
        f"₹{record_4.recovered_amount:,.2f}"
    )

    print(
        f"Requires human: "
        f"{record_4.requires_human}"
    )

    # =====================================================
    # TEST 5 — SUMMARY
    # =====================================================

    print_summary(
        tracker
    )

    # =====================================================
    # TEST ASSERTIONS
    # =====================================================

    print()
    print("=" * 60)
    print(
        "          TRACKER TEST SUMMARY"
    )
    print("=" * 60)

    # -----------------------------------------------------
    # Total cases
    # -----------------------------------------------------

    expected_cases = 4

    if tracker.total_cases() != expected_cases:

        raise AssertionError(
            "Total case count is incorrect."
        )

    # -----------------------------------------------------
    # Total amount at risk
    # -----------------------------------------------------

    expected_risk = (
        6200.00
        + 100000.00
        + 5000.00
        + 10000.00
    )

    if (
        tracker.total_amount_at_risk()
        != expected_risk
    ):

        raise AssertionError(
            "Total amount at risk is incorrect."
        )

    # -----------------------------------------------------
    # Total recovered
    # -----------------------------------------------------

    expected_recovered = (
        6200.00
        + 40000.00
    )

    if (
        tracker.total_recovered()
        != expected_recovered
    ):

        raise AssertionError(
            "Total recovered amount is incorrect."
        )

    # -----------------------------------------------------
    # Total remaining
    #
    # Case 1 = 6200 - 6200 = 0
    # Case 2 = 100000 - 40000 = 60000
    # Case 3 = 5000 - 0 = 5000
    # Case 4 = 10000 - 0 = 10000
    #
    # Total = 75000
    # -----------------------------------------------------

    expected_remaining = (
        60000.00
        + 5000.00
        + 10000.00
    )

    if (
        tracker.total_remaining()
        != expected_remaining
    ):

        raise AssertionError(
            "Total remaining amount is incorrect."
        )

    # -----------------------------------------------------
    # Recovery rate
    # -----------------------------------------------------

    expected_rate = round(
        (
            expected_recovered
            / expected_risk
        )
        * 100,
        2,
    )

    if (
        tracker.recovery_rate()
        != expected_rate
    ):

        raise AssertionError(
            "Recovery rate is incorrect."
        )

    # -----------------------------------------------------
    # Successful recoveries
    # -----------------------------------------------------

    if (
        tracker.successful_recovery_count()
        != 1
    ):

        raise AssertionError(
            "Successful recovery count is incorrect."
        )

    # -----------------------------------------------------
    # Failed recoveries
    # -----------------------------------------------------

    if (
        tracker.failed_recovery_count()
        != 1
    ):

        raise AssertionError(
            "Failed recovery count is incorrect."
        )

    # -----------------------------------------------------
    # Partial recoveries
    # -----------------------------------------------------

    if (
        tracker.partial_recovery_count()
        != 1
    ):

        raise AssertionError(
            "Partial recovery count is incorrect."
        )

    # -----------------------------------------------------
    # Blocked cases
    # -----------------------------------------------------

    if (
        tracker.blocked_count()
        != 1
    ):

        raise AssertionError(
            "Blocked case count is incorrect."
        )

    # -----------------------------------------------------
    # Human review
    # -----------------------------------------------------

    if (
        tracker.human_review_count()
        != 1
    ):

        raise AssertionError(
            "Human review count is incorrect."
        )

    # -----------------------------------------------------
    # Case retrieval
    # -----------------------------------------------------

    retrieved = tracker.get_case(
        "TEST_CASE_002"
    )

    if retrieved is None:

        raise AssertionError(
            "Case retrieval failed."
        )

    if (
        retrieved.recovered_amount
        != 40000.00
    ):

        raise AssertionError(
            "Retrieved recovered amount is incorrect."
        )

    if (
        retrieved.remaining_amount
        != 60000.00
    ):

        raise AssertionError(
            "Retrieved remaining amount is incorrect."
        )

    # -----------------------------------------------------
    # Unknown case
    # -----------------------------------------------------

    unknown_case = tracker.get_case(
        "DOES_NOT_EXIST"
    )

    if unknown_case is not None:

        raise AssertionError(
            "Unknown case should return None."
        )

    # -----------------------------------------------------
    # Duplicate protection
    # -----------------------------------------------------

    duplicate_blocked = False

    try:

        tracker.record_outcome(

            case_id="TEST_CASE_001",

            event_type="payment_failure",

            amount_at_risk=1000.00,

            action="retry",

            execution_status="completed",

            outcome="recovered",

            recovered_amount=1000.00,

            requires_human=False,

            message="Duplicate test.",
        )

    except ValueError:

        duplicate_blocked = True

    if not duplicate_blocked:

        raise AssertionError(
            "Duplicate case ID was not blocked."
        )

    # -----------------------------------------------------
    # Negative recovery protection
    # -----------------------------------------------------

    negative_recovery_blocked = False

    try:

        tracker.record_outcome(

            case_id="TEST_CASE_NEGATIVE",

            event_type="payment_failure",

            amount_at_risk=1000.00,

            action="retry",

            execution_status="completed",

            outcome="recovered",

            recovered_amount=-100.00,

            requires_human=False,

            message="Negative recovery test.",
        )

    except ValueError:

        negative_recovery_blocked = True

    if not negative_recovery_blocked:

        raise AssertionError(
            "Negative recovered amount "
            "was not blocked."
        )

    # -----------------------------------------------------
    # Recovery greater than risk protection
    # -----------------------------------------------------

    excessive_recovery_blocked = False

    try:

        tracker.record_outcome(

            case_id="TEST_CASE_EXCESSIVE",

            event_type="payment_failure",

            amount_at_risk=1000.00,

            action="retry",

            execution_status="completed",

            outcome="recovered",

            recovered_amount=2000.00,

            requires_human=False,

            message="Excessive recovery test.",
        )

    except ValueError:

        excessive_recovery_blocked = True

    if not excessive_recovery_blocked:

        raise AssertionError(
            "Recovered amount greater than "
            "amount at risk was not blocked."
        )

    # -----------------------------------------------------
    # Zero-risk recovery rate
    # -----------------------------------------------------

    empty_test_storage = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "generated"
        / "recovery_tracker_empty_test.json"
    )

    if empty_test_storage.exists():

        empty_test_storage.unlink()

    empty_tracker = RecoveryTracker(
        storage_path=str(
            empty_test_storage
        )
    )

    if (
        empty_tracker.recovery_rate()
        != 0.0
    ):

        raise AssertionError(
            "Empty tracker recovery rate "
            "should be 0."
        )

    if empty_test_storage.exists():

        empty_test_storage.unlink()

    # -----------------------------------------------------
    # Persistence test
    # -----------------------------------------------------

    persistence_storage = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "generated"
        / "recovery_tracker_persistence_test.json"
    )

    if persistence_storage.exists():

        persistence_storage.unlink()

    persistence_tracker = RecoveryTracker(
        storage_path=str(
            persistence_storage
        )
    )

    persistence_tracker.record_outcome(

        case_id="PERSISTENCE_TEST",

        event_type="payment_failure",

        amount_at_risk=5000.00,

        action="retry",

        execution_status="completed",

        outcome="recovered",

        recovered_amount=5000.00,

        requires_human=False,

        message="Persistence test.",
    )

    # Load a second tracker from the same file.

    reloaded_tracker = RecoveryTracker(
        storage_path=str(
            persistence_storage
        )
    )

    persisted_case = (
        reloaded_tracker.get_case(
            "PERSISTENCE_TEST"
        )
    )

    if persisted_case is None:

        raise AssertionError(
            "Recovery record was not persisted."
        )

    if (
        persisted_case.recovered_amount
        != 5000.00
    ):

        raise AssertionError(
            "Persisted recovery amount is incorrect."
        )

    if persistence_storage.exists():

        persistence_storage.unlink()

    # =====================================================
    # CLEANUP
    # =====================================================

    if test_storage.exists():

        test_storage.unlink()

    # =====================================================
    # SUCCESS
    # =====================================================

    print()

    print(
        "Record creation: PASSED"
    )

    print(
        "Partial recovery tracking: PASSED"
    )

    print(
        "Failed recovery tracking: PASSED"
    )

    print(
        "Fraud/human tracking: PASSED"
    )

    print(
        "Financial calculations: PASSED"
    )

    print(
        "Case retrieval: PASSED"
    )

    print(
        "Duplicate protection: PASSED"
    )

    print(
        "Negative recovery protection: PASSED"
    )

    print(
        "Excessive recovery protection: PASSED"
    )

    print(
        "Empty tracker handling: PASSED"
    )

    print(
        "Persistence: PASSED"
    )

    print()

    print(
        "ALL RECOVERY TRACKER TESTS PASSED."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_tracker_tests()