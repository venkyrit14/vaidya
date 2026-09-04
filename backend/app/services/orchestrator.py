from pathlib import Path
from typing import Dict, Any

from app.services.decision_engine import DecisionEngine
from app.services.policy_engine import PolicyEngine
from app.services.execution_service import ExecutionService
from app.services.recovery_tracker import RecoveryTracker


class VaidyaOrchestrator:
    """
    Main Vaidya orchestration layer.

    Pipeline:

        Incoming Event
              ↓
        Decision Engine
              ↓
        Policy Engine
              ↓
        Execution Service
              ↓
        Recovery Tracker
              ↓
        Final Result
    """

    def __init__(self):

        print("Initializing Vaidya...")

        # DecisionEngine already owns its retrieval logic.
        self.decision_engine = DecisionEngine()

        self.policy_engine = PolicyEngine()

        self.execution_service = ExecutionService(
            random_seed=42
        )

        self.recovery_tracker = RecoveryTracker()

        print(
            "Historical cases loaded inside Decision Engine."
        )

        print(
            "Vaidya initialized successfully."
        )

    # =====================================================
    # PROCESS EVENT
    # =====================================================

    def process_event(
        self,
        event: Dict[str, Any],
        case_id: str,
    ) -> Dict[str, Any]:
        """
        Complete Vaidya pipeline.

        Event
          ↓
        Decision
          ↓
        Policy
          ↓
        Execution
          ↓
        Recovery Tracking
        """

        # =================================================
        # 1. DECISION ENGINE
        # =================================================

        decision = self.decision_engine.decide(
            current_event=event
        )

        if not isinstance(decision, dict):

            raise TypeError(
                "DecisionEngine.decide() "
                "must return a dictionary."
            )

        proposed_action = decision.get(
            "action",
            "human_review",
        )

        confidence = float(
            decision.get(
                "confidence",
                0.0,
            )
        )

        expected_recovery = float(
            decision.get(
                "expected_recovery",
                0.0,
            )
        )

        historical_cases = int(
            decision.get(
                "historical_cases",
                0,
            )
        )

        reason = decision.get(
            "reason",
            "",
        )

        evidence = decision.get(
            "evidence",
            [],
        )

        # =================================================
        # 2. POLICY ENGINE
        # =================================================

        policy_result = self.policy_engine.evaluate(
            event=event,
            action=proposed_action,
            confidence=confidence,
        )

        # PolicyEngine returns PolicyDecision object.
        if not hasattr(policy_result, "allowed"):

            raise TypeError(
                "PolicyEngine.evaluate() "
                "must return a PolicyDecision object."
            )

        # =================================================
        # 3. DETERMINE FINAL ACTION
        # =================================================

        if policy_result.allowed:

            final_action = proposed_action

        else:

            # Fraud is explicitly blocked/escalated.
            if (
                policy_result.decision == "blocked"
                and proposed_action
                == "block_and_escalate"
            ):

                final_action = (
                    "block_and_escalate"
                )

            else:

                # High value, low confidence,
                # unsupported event, etc.
                final_action = (
                    "human_review"
                )

        # =================================================
        # 4. EXECUTION SERVICE
        # =================================================

        execution_result = (
            self.execution_service.execute(
                event=event,
                action=final_action,
            )
        )

        # =================================================
        # 5. RECOVERY TRACKER
        # =================================================

        recovery_record = (
            self.recovery_tracker.record_execution(
                case_id=case_id,
                event=event,
                execution_result=execution_result,
            )
        )

        # =================================================
        # 6. FINAL DECISION
        # =================================================

        if (
            final_action
            == "block_and_escalate"
        ):

            final_decision = "escalate"

        elif (
            final_action
            == "human_review"
        ):

            final_decision = "human_review"

        elif policy_result.allowed:

            final_decision = "automate"

        else:

            final_decision = "human_review"

        # =================================================
        # 7. COMPLETE RESPONSE
        # =================================================

        return {

            "case_id": case_id,

            "event": event,

            "decision": {

                "decision":
                    final_decision,

                "proposed_action":
                    proposed_action,

                "final_action":
                    final_action,

                "confidence":
                    confidence,

                "expected_recovery":
                    expected_recovery,

                "historical_cases":
                    historical_cases,

                "reason":
                    reason,

                "evidence":
                    evidence,
            },

            "policy": {

                "allowed":
                    policy_result.allowed,

                "decision":
                    policy_result.decision,

                "reason":
                    policy_result.reason,

                "risk_level":
                    policy_result.risk_level,

                "requires_human":
                    policy_result.requires_human,

                "action":
                    policy_result.action,
            },

            "execution": {

                "executed":
                    execution_result.executed,

                "action":
                    execution_result.action,

                "status":
                    execution_result.status,

                "outcome":
                    execution_result.outcome,

                "amount_at_risk":
                    execution_result.amount_at_risk,

                "recovered_amount":
                    execution_result.recovered_amount,

                "remaining_amount":
                    execution_result.remaining_amount,

                "requires_human":
                    execution_result.requires_human,

                "message":
                    execution_result.message,
            },

            "recovery": {

                "case_id":
                    recovery_record.case_id,

                "amount_at_risk":
                    recovery_record.amount_at_risk,

                "recovered_amount":
                    recovery_record.recovered_amount,

                "remaining_amount":
                    recovery_record.remaining_amount,

                "outcome":
                    recovery_record.outcome,

                "action":
                    recovery_record.action,

                "requires_human":
                    recovery_record.requires_human,

                "timestamp":
                    recovery_record.timestamp,
            },
        }


# =========================================================
# PRINT RESULT
# =========================================================

def print_result(
    result: Dict[str, Any],
):

    event = result["event"]

    decision = result["decision"]

    policy = result["policy"]

    execution = result["execution"]

    recovery = result["recovery"]

    print()
    print("=" * 60)
    print(
        "                    VAIDYA"
    )
    print("=" * 60)

    # =====================================================
    # EVENT
    # =====================================================

    print()
    print(
        "INCOMING EVENT"
    )
    print("-" * 60)

    print(
        f"Case ID: "
        f"{result['case_id']}"
    )

    print(
        f"Event type: "
        f"{event.get('event_type')}"
    )

    print(
        f"Root cause: "
        f"{event.get('root_cause')}"
    )

    print(
        f"Amount at risk: "
        f"₹{float(event.get('amount', 0)):,.2f}"
    )

    # =====================================================
    # DECISION
    # =====================================================

    print()
    print(
        "DECISION ENGINE"
    )
    print("-" * 60)

    print(
        f"Proposed action: "
        f"{decision['proposed_action']}"
    )

    print(
        f"Final action: "
        f"{decision['final_action']}"
    )

    print(
        f"Confidence: "
        f"{decision['confidence'] * 100:.2f}%"
    )

    print(
        f"Historical cases: "
        f"{decision['historical_cases']}"
    )

    print(
        f"Expected recovery: "
        f"₹{decision['expected_recovery']:,.2f}"
    )

    print(
        f"Reason: "
        f"{decision['reason']}"
    )

    # =====================================================
    # POLICY
    # =====================================================

    print()
    print(
        "POLICY ENGINE"
    )
    print("-" * 60)

    print(
        f"Allowed: "
        f"{policy['allowed']}"
    )

    print(
        f"Risk level: "
        f"{policy['risk_level']}"
    )

    print(
        f"Requires human: "
        f"{policy['requires_human']}"
    )

    print(
        f"Policy decision: "
        f"{policy['decision']}"
    )

    print(
        f"Policy action: "
        f"{policy['action']}"
    )

    print(
        f"Reason: "
        f"{policy['reason']}"
    )

    # =====================================================
    # EXECUTION
    # =====================================================

    print()
    print(
        "EXECUTION"
    )
    print("-" * 60)

    print(
        f"Executed: "
        f"{execution['executed']}"
    )

    print(
        f"Action: "
        f"{execution['action']}"
    )

    print(
        f"Status: "
        f"{execution['status']}"
    )

    print(
        f"Outcome: "
        f"{execution['outcome']}"
    )

    print(
        f"Recovered: "
        f"₹{execution['recovered_amount']:,.2f}"
    )

    print(
        f"Remaining: "
        f"₹{execution['remaining_amount']:,.2f}"
    )

    print(
        f"Requires human: "
        f"{execution['requires_human']}"
    )

    print(
        f"Message: "
        f"{execution['message']}"
    )

    # =====================================================
    # RECOVERY TRACKER
    # =====================================================

    print()
    print(
        "RECOVERY TRACKER"
    )
    print("-" * 60)

    print(
        f"Case ID: "
        f"{recovery['case_id']}"
    )

    print(
        f"Amount at risk: "
        f"₹{recovery['amount_at_risk']:,.2f}"
    )

    print(
        f"Recovered amount: "
        f"₹{recovery['recovered_amount']:,.2f}"
    )

    print(
        f"Remaining amount: "
        f"₹{recovery['remaining_amount']:,.2f}"
    )

    print(
        f"Outcome: "
        f"{recovery['outcome']}"
    )

    print(
        f"Tracked action: "
        f"{recovery['action']}"
    )

    print(
        f"Requires human: "
        f"{recovery['requires_human']}"
    )

    print()
    print("=" * 60)


# =========================================================
# ASSERTION HELPER
# =========================================================

def assert_result(
    result: Dict[str, Any],
    expected_action: str,
    expected_decision: str,
):

    decision = result["decision"]

    execution = result["execution"]

    recovery = result["recovery"]

    if (
        decision["final_action"]
        != expected_action
    ):

        raise AssertionError(
            f"Expected final action "
            f"'{expected_action}', "
            f"got "
            f"'{decision['final_action']}'."
        )

    if (
        decision["decision"]
        != expected_decision
    ):

        raise AssertionError(
            f"Expected decision "
            f"'{expected_decision}', "
            f"got "
            f"'{decision['decision']}'."
        )

    if (
        execution["action"]
        != expected_action
    ):

        raise AssertionError(
            f"Execution action mismatch. "
            f"Expected '{expected_action}', "
            f"got '{execution['action']}'."
        )

    if (
        recovery["action"]
        != expected_action
    ):

        raise AssertionError(
            f"Recovery tracker action mismatch. "
            f"Expected '{expected_action}', "
            f"got '{recovery['action']}'."
        )


# =========================================================
# TEST SUITE
# =========================================================

def run_orchestrator_tests():

    # -----------------------------------------------------
    # Isolated tracker for tests
    # -----------------------------------------------------

    test_storage = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "generated"
        / "orchestrator_test_records.json"
    )

    if test_storage.exists():

        test_storage.unlink()

    # -----------------------------------------------------
    # Initialize
    # -----------------------------------------------------

    vaidya = VaidyaOrchestrator()

    # Use isolated tracker
    vaidya.recovery_tracker = RecoveryTracker(
        storage_path=str(
            test_storage
        )
    )

    print()
    print("=" * 60)
    print(
        "       VAIDYA ORCHESTRATOR TEST SUITE"
    )
    print("=" * 60)

    # =====================================================
    # TEST 1 — PAYMENT FAILURE
    # =====================================================

    print()
    print("=" * 60)
    print(
        "TEST 1 — PAYMENT FAILURE"
    )
    print("=" * 60)

    payment_event = {

        "event_type":
            "payment_failure",

        "root_cause":
            "network_error",

        "amount":
            6200.00,

        "customer_profile":
            "Returning customer with historical transaction activity.",
    }

    payment_result = (
        vaidya.process_event(
            event=payment_event,
            case_id="ORCH_TEST_001",
        )
    )

    print_result(
        payment_result
    )

    assert_result(
        payment_result,
        expected_action="retry",
        expected_decision="automate",
    )

    # =====================================================
    # TEST 2 — CHECKOUT
    # =====================================================

    print()
    print("=" * 60)
    print(
        "TEST 2 — CHECKOUT ABANDONMENT"
    )
    print("=" * 60)

    checkout_event = {

        "event_type":
            "checkout_abandonment",

        "root_cause":
            "high_intent_abandonment",

        "amount":
            5000.00,

        "customer_profile":
            "Customer history score: 0.90",
    }

    checkout_result = (
        vaidya.process_event(
            event=checkout_event,
            case_id="ORCH_TEST_002",
        )
    )

    print_result(
        checkout_result
    )

    assert_result(
        checkout_result,
        expected_action="targeted_reminder",
        expected_decision="automate",
    )

    # =====================================================
    # TEST 3 — INVOICE
    # =====================================================

    print()
    print("=" * 60)
    print(
        "TEST 3 — OVERDUE INVOICE"
    )
    print("=" * 60)

    invoice_event = {

        "event_type":
            "overdue_invoice",

        "root_cause":
            "repeated_late_payer",

        "amount":
            50000.00,

        "customer_profile":
            "8 previous invoices; 5 previous late payments.",
    }

    invoice_result = (
        vaidya.process_event(
            event=invoice_event,
            case_id="ORCH_TEST_003",
        )
    )

    print_result(
        invoice_result
    )

    assert_result(
        invoice_result,
        expected_action="promise_to_pay",
        expected_decision="automate",
    )

    # =====================================================
    # TEST 4 — FRAUD
    # =====================================================

    print()
    print("=" * 60)
    print(
        "TEST 4 — FRAUD RISK"
    )
    print("=" * 60)

    fraud_event = {

        "event_type":
            "payment_failure",

        "root_cause":
            "fraud_risk",

        "amount":
            10000.00,

        "customer_profile":
            "Returning customer with historical transaction activity.",
    }

    fraud_result = (
        vaidya.process_event(
            event=fraud_event,
            case_id="ORCH_TEST_004",
        )
    )

    print_result(
        fraud_result
    )

    assert_result(
        fraud_result,
        expected_action="block_and_escalate",
        expected_decision="escalate",
    )

    if fraud_result["execution"]["executed"]:

        raise AssertionError(
            "Fraud action must not execute."
        )

    if (
        fraud_result["execution"]
        ["recovered_amount"]
        != 0.0
    ):

        raise AssertionError(
            "Fraud recovery must be zero."
        )

    if not (
        fraud_result["execution"]
        ["requires_human"]
    ):

        raise AssertionError(
            "Fraud must require human review."
        )

    # =====================================================
    # TEST 5 — HIGH VALUE
    # =====================================================

    print()
    print("=" * 60)
    print(
        "TEST 5 — HIGH VALUE"
    )
    print("=" * 60)

    high_value_event = {

        "event_type":
            "overdue_invoice",

        "root_cause":
            "repeated_late_payer",

        "amount":
            250000.00,

        "customer_profile":
            "8 previous invoices; 5 previous late payments.",
    }

    high_value_result = (
        vaidya.process_event(
            event=high_value_event,
            case_id="ORCH_TEST_005",
        )
    )

    print_result(
        high_value_result
    )

    assert_result(
        high_value_result,
        expected_action="human_review",
        expected_decision="human_review",
    )

    if high_value_result["execution"]["executed"]:

        raise AssertionError(
            "High-value case must not execute automatically."
        )

    # =====================================================
    # TEST 6 — UNKNOWN EVENT
    # =====================================================

    print()
    print("=" * 60)
    print(
        "TEST 6 — UNKNOWN EVENT"
    )
    print("=" * 60)

    unknown_event = {

        "event_type":
            "unknown_event",

        "root_cause":
            None,

        "amount":
            15000.00,

        "customer_profile":
            "Unknown customer context.",
    }

    unknown_result = (
        vaidya.process_event(
            event=unknown_event,
            case_id="ORCH_TEST_006",
        )
    )

    print_result(
        unknown_result
    )

    assert_result(
        unknown_result,
        expected_action="human_review",
        expected_decision="human_review",
    )

    if unknown_result["execution"]["executed"]:

        raise AssertionError(
            "Unknown events must not execute automatically."
        )

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print()
    print("=" * 60)
    print(
        "          FINAL RECOVERY SUMMARY"
    )
    print("=" * 60)

    summary = (
        vaidya.recovery_tracker
        .get_summary()
    )

    print()

    print(
        f"Total cases tracked: "
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

    # =====================================================
    # FINAL ASSERTIONS
    # =====================================================

    if summary["total_cases"] != 6:

        raise AssertionError(
            "Expected exactly 6 tracked cases."
        )

    if summary["blocked_cases"] != 1:

        raise AssertionError(
            "Expected exactly 1 blocked case."
        )

    if summary["human_review_cases"] != 3:

        raise AssertionError(
            "Expected exactly 3 human-review cases."
        )

    # -----------------------------------------------------
    # Verify tracker records
    # -----------------------------------------------------

    expected_cases = [

        "ORCH_TEST_001",
        "ORCH_TEST_002",
        "ORCH_TEST_003",
        "ORCH_TEST_004",
        "ORCH_TEST_005",
        "ORCH_TEST_006",

    ]

    for case_id in expected_cases:

        record = (
            vaidya.recovery_tracker
            .get_case(case_id)
        )

        if record is None:

            raise AssertionError(
                f"Missing recovery record: "
                f"{case_id}"
            )

    # -----------------------------------------------------
    # Cleanup
    # -----------------------------------------------------

    if test_storage.exists():

        test_storage.unlink()

    # =====================================================
    # SUCCESS
    # =====================================================

    print()
    print("=" * 60)
    print(
        "             ORCHESTRATOR SUMMARY"
    )
    print("=" * 60)

    print()

    print(
        "Payment pipeline: PASSED"
    )

    print(
        "Checkout pipeline: PASSED"
    )

    print(
        "Invoice pipeline: PASSED"
    )

    print(
        "Fraud safety pipeline: PASSED"
    )

    print(
        "High-value safety pipeline: PASSED"
    )

    print(
        "Unknown-case safety pipeline: PASSED"
    )

    print(
        "Execution integration: PASSED"
    )

    print(
        "Recovery tracking integration: PASSED"
    )

    print()

    print(
        "ALL ORCHESTRATOR TESTS PASSED."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_orchestrator_tests()