from dataclasses import dataclass
from typing import Dict, Any
import random


@dataclass
class ExecutionResult:
    """
    Result produced by the Vaidya Execution Service.
    """

    executed: bool
    action: str
    status: str
    outcome: str
    amount_at_risk: float
    recovered_amount: float
    remaining_amount: float
    message: str
    requires_human: bool


class ExecutionService:
    """
    Vaidya Execution Service.

    This service represents the action layer.

    It receives an approved action and simulates
    execution.

    IMPORTANT:

    This is a prototype simulation.

    It does NOT:
        - charge a real customer
        - call Razorpay
        - send a real message
        - modify a real invoice
        - move real money

    Real integrations will be added later.
    """

    # =====================================================
    # SUPPORTED ACTIONS
    # =====================================================

    SUPPORTED_ACTIONS = {
        "retry",
        "delayed_retry",
        "payment_method_update",
        "mandate_retry",
        "reminder",
        "targeted_reminder",
        "stop_outreach",
        "promise_to_pay",
        "payment_reminder",
        "block_and_escalate",
        "human_review",
    }

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(
        self,
        random_seed: int = 42,
    ):
        """
        Initialize the execution service.

        A fixed seed is used for deterministic
        prototype tests.
        """

        self.random_generator = random.Random(
            random_seed
        )

    # =====================================================
    # VALIDATE EVENT
    # =====================================================

    def validate_event(
        self,
        event: Dict[str, Any],
    ):
        """
        Validate an event before execution.
        """

        if not isinstance(
            event,
            dict,
        ):

            return False, (
                "Event must be a dictionary."
            )

        if "amount" not in event:

            return False, (
                "Event amount is missing."
            )

        try:

            amount = float(
                event["amount"]
            )

        except (
            TypeError,
            ValueError,
        ):

            return False, (
                "Event amount must be numeric."
            )

        if amount <= 0:

            return False, (
                "Event amount must be greater "
                "than zero."
            )

        return True, ""

    # =====================================================
    # VALIDATE ACTION
    # =====================================================

    def validate_action(
        self,
        action: str,
    ):
        """
        Validate that the requested action is
        supported by the execution layer.
        """

        if action not in (
            self.SUPPORTED_ACTIONS
        ):

            return False, (
                f"Unsupported execution action: "
                f"{action}"
            )

        return True, ""

    # =====================================================
    # NON-EXECUTABLE ACTIONS
    # =====================================================

    def handle_human_review(
        self,
        amount: float,
    ):

        return ExecutionResult(

            executed=False,

            action="human_review",

            status="human_review",

            outcome="pending",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Case sent for human review. "
                "No automatic recovery action "
                "was executed."
            ),

            requires_human=True,
        )

    # =====================================================
    # FRAUD / BLOCK
    # =====================================================

    def handle_block_and_escalate(
        self,
        amount: float,
    ):

        return ExecutionResult(

            executed=False,

            action="block_and_escalate",

            status="blocked",

            outcome="blocked",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Payment recovery was blocked "
                "because the case requires "
                "human/security review."
            ),

            requires_human=True,
        )

    # =====================================================
    # RETRY
    # =====================================================

    def execute_retry(
        self,
        amount: float,
    ):

        # Prototype simulation:
        # retry succeeds approximately 80% of the time.

        success = (
            self.random_generator.random()
            < 0.80
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="retry",

                status="completed",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Payment retry succeeded "
                    "in the prototype simulation."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="retry",

            status="completed",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Payment retry failed in the "
                "prototype simulation."
            ),

            requires_human=False,
        )

    # =====================================================
    # DELAYED RETRY
    # =====================================================

    def execute_delayed_retry(
        self,
        amount: float,
    ):

        # Prototype success probability.

        success = (
            self.random_generator.random()
            < 0.70
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="delayed_retry",

                status="scheduled",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Delayed payment retry was "
                    "scheduled and simulated as "
                    "successful."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="delayed_retry",

            status="scheduled",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Delayed retry was scheduled but "
                "did not recover the amount in "
                "the prototype simulation."
            ),

            requires_human=False,
        )

    # =====================================================
    # PAYMENT METHOD UPDATE
    # =====================================================

    def execute_payment_method_update(
        self,
        amount: float,
    ):

        success = (
            self.random_generator.random()
            < 0.65
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="payment_method_update",

                status="completed",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Payment method update "
                    "successfully recovered the "
                    "amount in the prototype."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="payment_method_update",

            status="completed",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Payment method update did not "
                "recover the amount."
            ),

            requires_human=False,
        )

    # =====================================================
    # MANDATE RETRY
    # =====================================================

    def execute_mandate_retry(
        self,
        amount: float,
    ):

        success = (
            self.random_generator.random()
            < 0.72
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="mandate_retry",

                status="completed",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Mandate retry succeeded "
                    "in the prototype simulation."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="mandate_retry",

            status="completed",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Mandate retry did not recover "
                "the amount."
            ),

            requires_human=False,
        )

    # =====================================================
    # CHECKOUT REMINDER
    # =====================================================

    def execute_reminder(
        self,
        amount: float,
    ):

        success = (
            self.random_generator.random()
            < 0.55
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="reminder",

                status="sent",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Reminder sent. Customer "
                    "completed payment in the "
                    "prototype simulation."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="reminder",

            status="sent",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Reminder was sent but payment "
                "was not recovered."
            ),

            requires_human=False,
        )

    # =====================================================
    # TARGETED REMINDER
    # =====================================================

    def execute_targeted_reminder(
        self,
        amount: float,
    ):

        success = (
            self.random_generator.random()
            < 0.70
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="targeted_reminder",

                status="sent",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Targeted reminder was sent "
                    "and payment was recovered "
                    "in the prototype."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="targeted_reminder",

            status="sent",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Targeted reminder was sent but "
                "payment was not recovered."
            ),

            requires_human=False,
        )

    # =====================================================
    # STOP OUTREACH
    # =====================================================

    def execute_stop_outreach(
        self,
        amount: float,
    ):

        return ExecutionResult(

            executed=True,

            action="stop_outreach",

            status="completed",

            outcome="no_action",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Further automated outreach "
                "was stopped."
            ),

            requires_human=False,
        )

    # =====================================================
    # PROMISE TO PAY
    # =====================================================

    def execute_promise_to_pay(
        self,
        amount: float,
    ):

        success = (
            self.random_generator.random()
            < 0.75
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="promise_to_pay",

                status="scheduled",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Customer promise-to-pay "
                    "was recorded and payment "
                    "was simulated as recovered."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="promise_to_pay",

            status="scheduled",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Promise-to-pay was recorded but "
                "payment was not recovered in "
                "the prototype simulation."
            ),

            requires_human=False,
        )

    # =====================================================
    # PAYMENT REMINDER
    # =====================================================

    def execute_payment_reminder(
        self,
        amount: float,
    ):

        success = (
            self.random_generator.random()
            < 0.55
        )

        if success:

            recovered = round(
                amount,
                2,
            )

            return ExecutionResult(

                executed=True,

                action="payment_reminder",

                status="sent",

                outcome="recovered",

                amount_at_risk=amount,

                recovered_amount=recovered,

                remaining_amount=0.0,

                message=(
                    "Payment reminder was sent "
                    "and payment was recovered "
                    "in the prototype."
                ),

                requires_human=False,
            )

        return ExecutionResult(

            executed=True,

            action="payment_reminder",

            status="sent",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Payment reminder was sent but "
                "payment was not recovered."
            ),

            requires_human=False,
        )

    # =====================================================
    # MAIN EXECUTION METHOD
    # =====================================================

    def execute(
        self,
        event: Dict[str, Any],
        action: str,
    ):
        """
        Execute an approved Vaidya action.

        IMPORTANT:

        In the final architecture this method should
        only be called AFTER PolicyEngine approval.

        The service still contains safety checks so
        that unsafe actions cannot accidentally be
        executed directly.
        """

        # -------------------------------------------------
        # Validate event
        # -------------------------------------------------

        valid_event, event_error = (
            self.validate_event(
                event
            )
        )

        if not valid_event:

            return ExecutionResult(

                executed=False,

                action="human_review",

                status="error",

                outcome="failed",

                amount_at_risk=0.0,

                recovered_amount=0.0,

                remaining_amount=0.0,

                message=event_error,

                requires_human=True,
            )

        amount = float(
            event["amount"]
        )

        # -------------------------------------------------
        # Validate action
        # -------------------------------------------------

        valid_action, action_error = (
            self.validate_action(
                action
            )
        )

        if not valid_action:

            return ExecutionResult(

                executed=False,

                action="human_review",

                status="error",

                outcome="failed",

                amount_at_risk=amount,

                recovered_amount=0.0,

                remaining_amount=amount,

                message=action_error,

                requires_human=True,
            )

        # -------------------------------------------------
        # Human review
        # -------------------------------------------------

        if action == "human_review":

            return self.handle_human_review(
                amount
            )

        # -------------------------------------------------
        # Fraud / security escalation
        # -------------------------------------------------

        if action == "block_and_escalate":

            return (
                self.handle_block_and_escalate(
                    amount
                )
            )

        # -------------------------------------------------
        # Execute action
        # -------------------------------------------------

        if action == "retry":

            return self.execute_retry(
                amount
            )

        if action == "delayed_retry":

            return self.execute_delayed_retry(
                amount
            )

        if action == "payment_method_update":

            return (
                self.execute_payment_method_update(
                    amount
                )
            )

        if action == "mandate_retry":

            return self.execute_mandate_retry(
                amount
            )

        if action == "reminder":

            return self.execute_reminder(
                amount
            )

        if action == "targeted_reminder":

            return (
                self.execute_targeted_reminder(
                    amount
                )
            )

        if action == "stop_outreach":

            return self.execute_stop_outreach(
                amount
            )

        if action == "promise_to_pay":

            return (
                self.execute_promise_to_pay(
                    amount
                )
            )

        if action == "payment_reminder":

            return (
                self.execute_payment_reminder(
                    amount
                )
            )

        # -------------------------------------------------
        # Defensive fallback
        # -------------------------------------------------

        return ExecutionResult(

            executed=False,

            action="human_review",

            status="error",

            outcome="failed",

            amount_at_risk=amount,

            recovered_amount=0.0,

            remaining_amount=amount,

            message=(
                "Execution could not determine "
                "a safe handler for this action."
            ),

            requires_human=True,
        )


# =========================================================
# PRINT HELPER
# =========================================================

def print_execution_result(
    test_name: str,
    result: ExecutionResult,
):
    """
    Print execution result in readable form.
    """

    print()
    print("=" * 60)
    print(test_name)
    print("=" * 60)

    print()

    print(
        f"Executed: "
        f"{result.executed}"
    )

    print(
        f"Action: "
        f"{result.action}"
    )

    print(
        f"Status: "
        f"{result.status}"
    )

    print(
        f"Outcome: "
        f"{result.outcome}"
    )

    print(
        f"Amount at risk: "
        f"₹{result.amount_at_risk:,.2f}"
    )

    print(
        f"Recovered amount: "
        f"₹{result.recovered_amount:,.2f}"
    )

    print(
        f"Remaining amount: "
        f"₹{result.remaining_amount:,.2f}"
    )

    print(
        f"Requires human: "
        f"{result.requires_human}"
    )

    print(
        f"Message: "
        f"{result.message}"
    )


# =========================================================
# TEST SUITE
# =========================================================

def run_execution_tests():

    execution_service = (
        ExecutionService(
            random_seed=42
        )
    )

    print()
    print("=" * 60)
    print(
        "       VAIDYA EXECUTION SERVICE TESTS"
    )
    print("=" * 60)

    # =====================================================
    # TEST 1 — RETRY
    # =====================================================

    payment_event = {
        "event_type":
            "payment_failure",

        "root_cause":
            "network_error",

        "amount":
            6200.00,
    }

    retry_result = (
        execution_service.execute(
            event=payment_event,
            action="retry",
        )
    )

    print_execution_result(
        "TEST 1 — PAYMENT RETRY",
        retry_result,
    )

    # =====================================================
    # TEST 2 — TARGETED REMINDER
    # =====================================================

    checkout_event = {
        "event_type":
            "checkout_abandonment",

        "root_cause":
            "high_intent_abandonment",

        "amount":
            5000.00,
    }

    reminder_result = (
        execution_service.execute(
            event=checkout_event,
            action="targeted_reminder",
        )
    )

    print_execution_result(
        "TEST 2 — TARGETED REMINDER",
        reminder_result,
    )

    # =====================================================
    # TEST 3 — PROMISE TO PAY
    # =====================================================

    invoice_event = {
        "event_type":
            "overdue_invoice",

        "root_cause":
            "repeated_late_payer",

        "amount":
            50000.00,
    }

    promise_result = (
        execution_service.execute(
            event=invoice_event,
            action="promise_to_pay",
        )
    )

    print_execution_result(
        "TEST 3 — PROMISE TO PAY",
        promise_result,
    )

    # =====================================================
    # TEST 4 — FRAUD
    # =====================================================

    fraud_event = {
        "event_type":
            "payment_failure",

        "root_cause":
            "fraud_risk",

        "amount":
            10000.00,
    }

    fraud_result = (
        execution_service.execute(
            event=fraud_event,
            action="block_and_escalate",
        )
    )

    print_execution_result(
        "TEST 4 — FRAUD ESCALATION",
        fraud_result,
    )

    # =====================================================
    # TEST 5 — HUMAN REVIEW
    # =====================================================

    high_value_event = {
        "event_type":
            "overdue_invoice",

        "root_cause":
            "repeated_late_payer",

        "amount":
            250000.00,
    }

    human_result = (
        execution_service.execute(
            event=high_value_event,
            action="human_review",
        )
    )

    print_execution_result(
        "TEST 5 — HUMAN REVIEW",
        human_result,
    )

    # =====================================================
    # TEST 6 — STOP OUTREACH
    # =====================================================

    stop_result = (
        execution_service.execute(
            event={
                "event_type":
                    "checkout_abandonment",

                "root_cause":
                    "repeated_abandonment",

                "amount":
                    4000.00,
            },

            action="stop_outreach",
        )
    )

    print_execution_result(
        "TEST 6 — STOP OUTREACH",
        stop_result,
    )

    # =====================================================
    # TEST 7 — INVALID ACTION
    # =====================================================

    invalid_result = (
        execution_service.execute(
            event=payment_event,
            action="invalid_action",
        )
    )

    print_execution_result(
        "TEST 7 — INVALID ACTION",
        invalid_result,
    )

    # =====================================================
    # ASSERTIONS
    # =====================================================

    print()
    print("=" * 60)
    print(
        "             EXECUTION TEST SUMMARY"
    )
    print("=" * 60)

    # -----------------------------------------------------
    # Retry
    # -----------------------------------------------------

    if retry_result.action != "retry":

        raise AssertionError(
            "Retry action was not executed correctly."
        )

    if (
        retry_result.recovered_amount
        < 0
    ):

        raise AssertionError(
            "Recovered amount cannot be negative."
        )

    # -----------------------------------------------------
    # Targeted reminder
    # -----------------------------------------------------

    if (
        reminder_result.action
        != "targeted_reminder"
    ):

        raise AssertionError(
            "Targeted reminder was not executed."
        )

    # -----------------------------------------------------
    # Promise to pay
    # -----------------------------------------------------

    if (
        promise_result.action
        != "promise_to_pay"
    ):

        raise AssertionError(
            "Promise-to-pay was not executed."
        )

    # -----------------------------------------------------
    # Fraud
    # -----------------------------------------------------

    if fraud_result.executed:

        raise AssertionError(
            "Fraud action must never execute "
            "automatically."
        )

    if (
        fraud_result.action
        != "block_and_escalate"
    ):

        raise AssertionError(
            "Fraud action must be "
            "block_and_escalate."
        )

    if (
        fraud_result.recovered_amount
        != 0.0
    ):

        raise AssertionError(
            "Fraud recovery must be zero."
        )

    if not fraud_result.requires_human:

        raise AssertionError(
            "Fraud must require human review."
        )

    # -----------------------------------------------------
    # Human review
    # -----------------------------------------------------

    if human_result.executed:

        raise AssertionError(
            "Human review must not execute "
            "an automatic recovery action."
        )

    if (
        human_result.action
        != "human_review"
    ):

        raise AssertionError(
            "High-value case must remain "
            "human_review."
        )

    if not human_result.requires_human:

        raise AssertionError(
            "Human review case must require "
            "human intervention."
        )

    # -----------------------------------------------------
    # Stop outreach
    # -----------------------------------------------------

    if (
        stop_result.action
        != "stop_outreach"
    ):

        raise AssertionError(
            "Stop outreach was not handled."
        )

    if (
        stop_result.recovered_amount
        != 0.0
    ):

        raise AssertionError(
            "Stop outreach should not recover "
            "money automatically."
        )

    # -----------------------------------------------------
    # Invalid action
    # -----------------------------------------------------

    if invalid_result.executed:

        raise AssertionError(
            "Invalid action must not execute."
        )

    if (
        invalid_result.action
        != "human_review"
    ):

        raise AssertionError(
            "Invalid action must fall back "
            "to human review."
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    print()

    print(
        "Payment retry: PASSED"
    )

    print(
        "Targeted reminder: PASSED"
    )

    print(
        "Promise-to-pay: PASSED"
    )

    print(
        "Fraud safety: PASSED"
    )

    print(
        "Human review safety: PASSED"
    )

    print(
        "Stop outreach: PASSED"
    )

    print(
        "Invalid action safety: PASSED"
    )

    print()

    print(
        "ALL EXECUTION TESTS PASSED."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_execution_tests()