from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PolicyDecision:
    """
    Result returned by the Policy Engine.
    """

    allowed: bool
    decision: str
    reason: str
    risk_level: str
    requires_human: bool
    action: str


class PolicyEngine:
    """
    Vaidya Policy Engine.

    The Decision Engine answers:

        "What should we do?"

    The Policy Engine answers:

        "Are we allowed to do it?"

    This separation is intentional.

    IMPORTANT:
    These are prototype policies created for Vaidya.
    They are NOT claims about Razorpay's internal policies.
    """

    # =====================================================
    # CONFIGURATION
    # =====================================================

    SUPPORTED_EVENT_TYPES = {
        "payment_failure",
        "checkout_abandonment",
        "overdue_invoice",
    }

    # -----------------------------------------------------
    # Maximum amount that can be automatically handled.
    #
    # Above this amount, human approval is required.
    # -----------------------------------------------------

    MAX_AUTOMATION_AMOUNT = 100000.00

    # -----------------------------------------------------
    # Minimum confidence required for automation.
    # -----------------------------------------------------

    MIN_AUTOMATION_CONFIDENCE = 0.70

    # =====================================================
    # SAFE ACTIONS BY EVENT TYPE
    # =====================================================

    PAYMENT_ACTIONS = {
        "retry",
        "delayed_retry",
        "payment_method_update",
        "mandate_retry",
    }

    CHECKOUT_ACTIONS = {
        "reminder",
        "targeted_reminder",
        "stop_outreach",
    }

    INVOICE_ACTIONS = {
        "promise_to_pay",
        "payment_reminder",
    }

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(self):

        pass

    # =====================================================
    # GET ALLOWED ACTIONS
    # =====================================================

    def get_allowed_actions(
        self,
        event_type: str,
    ):
        """
        Return actions that are eligible for the given
        revenue surface.
        """

        if event_type == "payment_failure":

            return self.PAYMENT_ACTIONS

        if event_type == "checkout_abandonment":

            return self.CHECKOUT_ACTIONS

        if event_type == "overdue_invoice":

            return self.INVOICE_ACTIONS

        return set()

    # =====================================================
    # BASIC EVENT VALIDATION
    # =====================================================

    def validate_event(
        self,
        event: Dict[str, Any],
    ):
        """
        Validate the minimum information required for a
        policy decision.
        """

        errors = []

        event_type = event.get(
            "event_type"
        )

        amount = event.get(
            "amount"
        )

        if event_type not in (
            self.SUPPORTED_EVENT_TYPES
        ):

            errors.append(
                "Unsupported event type."
            )

        if amount is None:

            errors.append(
                "Transaction amount is missing."
            )

        else:

            try:

                amount = float(amount)

                if amount <= 0:

                    errors.append(
                        "Transaction amount must "
                        "be greater than zero."
                    )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    "Transaction amount must "
                    "be numeric."
                )

        return errors

    # =====================================================
    # FRAUD POLICY
    # =====================================================

    def check_fraud_policy(
        self,
        event: Dict[str, Any],
        action: str,
    ):
        """
        Fraud is a hard safety boundary.

        If the event is identified as fraud-risk:

            - no recovery action
            - no automatic retry
            - no automatic reminder
            - no payment-method update

        The case must be blocked/escalated.
        """

        root_cause = event.get(
            "root_cause"
        )

        if root_cause != "fraud_risk":

            return None

        return PolicyDecision(
            allowed=False,
            decision="blocked",
            reason=(
                "Fraud-risk event detected. "
                "Automatic recovery actions are "
                "not permitted."
            ),
            risk_level="critical",
            requires_human=True,
            action="block_and_escalate",
        )

    # =====================================================
    # AMOUNT POLICY
    # =====================================================

    def check_amount_policy(
        self,
        event: Dict[str, Any],
        action: str,
    ):
        """
        High-value cases require human approval.

        This protects against the system automatically
        making aggressive decisions on large amounts.
        """

        amount = float(
            event["amount"]
        )

        if amount > self.MAX_AUTOMATION_AMOUNT:

            return PolicyDecision(
                allowed=False,
                decision="approval_required",
                reason=(
                    f"Amount ₹{amount:,.2f} exceeds "
                    f"the automatic handling limit of "
                    f"₹{self.MAX_AUTOMATION_AMOUNT:,.2f}."
                ),
                risk_level="high",
                requires_human=True,
                action=action,
            )

        return None

    # =====================================================
    # ACTION POLICY
    # =====================================================

    def check_action_policy(
        self,
        event: Dict[str, Any],
        action: str,
    ):
        """
        Make sure the action is appropriate for the
        revenue surface.
        """

        event_type = event.get(
            "event_type"
        )

        allowed_actions = (
            self.get_allowed_actions(
                event_type
            )
        )

        if action not in allowed_actions:

            return PolicyDecision(
                allowed=False,
                decision="blocked",
                reason=(
                    f"Action '{action}' is not "
                    f"permitted for event type "
                    f"'{event_type}'."
                ),
                risk_level="high",
                requires_human=True,
                action="human_review",
            )

        return None

    # =====================================================
    # CONFIDENCE POLICY
    # =====================================================

    def check_confidence_policy(
        self,
        confidence: float,
        action: str,
    ):
        """
        Prevent low-confidence decisions from being
        automatically executed.
        """

        if confidence < (
            self.MIN_AUTOMATION_CONFIDENCE
        ):

            return PolicyDecision(
                allowed=False,
                decision="approval_required",
                reason=(
                    f"Decision confidence "
                    f"{confidence * 100:.2f}% is below "
                    f"the automatic execution threshold "
                    f"of "
                    f"{self.MIN_AUTOMATION_CONFIDENCE * 100:.0f}%."
                ),
                risk_level="medium",
                requires_human=True,
                action="human_review",
            )

        return None

    # =====================================================
    # MAIN POLICY EVALUATION
    # =====================================================

    def evaluate(
        self,
        event: Dict[str, Any],
        action: str,
        confidence: float = 0.0,
    ):
        """
        Evaluate whether an action is allowed.

        Policy evaluation order:

            1. Validate event
            2. Fraud check
            3. Action check
            4. Amount check
            5. Confidence check
            6. Approve

        The first blocking rule wins.
        """

        # -------------------------------------------------
        # 1. Validate event.
        # -------------------------------------------------

        validation_errors = (
            self.validate_event(
                event
            )
        )

        if validation_errors:

            return PolicyDecision(
                allowed=False,
                decision="invalid",
                reason=" ".join(
                    validation_errors
                ),
                risk_level="high",
                requires_human=True,
                action="human_review",
            )

        # -------------------------------------------------
        # 2. Fraud policy.
        # -------------------------------------------------

        fraud_result = (
            self.check_fraud_policy(
                event,
                action,
            )
        )

        if fraud_result is not None:

            return fraud_result

        # -------------------------------------------------
        # 3. Action policy.
        # -------------------------------------------------

        action_result = (
            self.check_action_policy(
                event,
                action,
            )
        )

        if action_result is not None:

            return action_result

        # -------------------------------------------------
        # 4. Amount policy.
        # -------------------------------------------------

        amount_result = (
            self.check_amount_policy(
                event,
                action,
            )
        )

        if amount_result is not None:

            return amount_result

        # -------------------------------------------------
        # 5. Confidence policy.
        # -------------------------------------------------

        confidence_result = (
            self.check_confidence_policy(
                confidence,
                action,
            )
        )

        if confidence_result is not None:

            return confidence_result

        # -------------------------------------------------
        # 6. Everything passed.
        # -------------------------------------------------

        return PolicyDecision(
            allowed=True,
            decision="approved",
            reason=(
                "Action passed all current "
                "Vaidya policy checks."
            ),
            risk_level="low",
            requires_human=False,
            action=action,
        )


# =========================================================
# PRINT HELPER
# =========================================================

def print_policy_result(
    test_name,
    result,
):
    """
    Print a readable policy result.
    """

    print()
    print("=" * 60)
    print(test_name)
    print("=" * 60)

    print()

    print(
        f"Allowed: "
        f"{result.allowed}"
    )

    print(
        f"Decision: "
        f"{result.decision}"
    )

    print(
        f"Action: "
        f"{result.action}"
    )

    print(
        f"Risk level: "
        f"{result.risk_level}"
    )

    print(
        f"Requires human: "
        f"{result.requires_human}"
    )

    print(
        f"Reason: "
        f"{result.reason}"
    )


# =========================================================
# POLICY TEST SUITE
# =========================================================

def run_policy_tests():

    engine = PolicyEngine()

    print()
    print("==============================================")
    print("          VAIDYA POLICY ENGINE TESTS")
    print("==============================================")

    # =====================================================
    # TEST 1 — NORMAL PAYMENT RETRY
    # =====================================================

    payment_event = {
        "event_type": "payment_failure",
        "root_cause": "network_error",
        "amount": 6200.00,
    }

    result_1 = engine.evaluate(
        event=payment_event,
        action="retry",
        confidence=0.8992,
    )

    print_policy_result(
        "TEST 1 — NORMAL PAYMENT RETRY",
        result_1,
    )

    # =====================================================
    # TEST 2 — NORMAL CHECKOUT REMINDER
    # =====================================================

    checkout_event = {
        "event_type": "checkout_abandonment",
        "root_cause": "high_intent_abandonment",
        "amount": 5000.00,
    }

    result_2 = engine.evaluate(
        event=checkout_event,
        action="targeted_reminder",
        confidence=0.8953,
    )

    print_policy_result(
        "TEST 2 — CHECKOUT TARGETED REMINDER",
        result_2,
    )

    # =====================================================
    # TEST 3 — NORMAL INVOICE
    # =====================================================

    invoice_event = {
        "event_type": "overdue_invoice",
        "root_cause": "repeated_late_payer",
        "amount": 50000.00,
    }

    result_3 = engine.evaluate(
        event=invoice_event,
        action="promise_to_pay",
        confidence=0.90,
    )

    print_policy_result(
        "TEST 3 — NORMAL INVOICE",
        result_3,
    )

    # =====================================================
    # TEST 4 — FRAUD
    # =====================================================

    fraud_event = {
        "event_type": "payment_failure",
        "root_cause": "fraud_risk",
        "amount": 10000.00,
    }

    result_4 = engine.evaluate(
        event=fraud_event,
        action="retry",
        confidence=0.95,
    )

    print_policy_result(
        "TEST 4 — FRAUD BLOCK",
        result_4,
    )

    # =====================================================
    # TEST 5 — HIGH VALUE
    # =====================================================

    high_value_event = {
        "event_type": "overdue_invoice",
        "root_cause": "repeated_late_payer",
        "amount": 250000.00,
    }

    result_5 = engine.evaluate(
        event=high_value_event,
        action="promise_to_pay",
        confidence=0.95,
    )

    print_policy_result(
        "TEST 5 — HIGH VALUE HUMAN APPROVAL",
        result_5,
    )

    # =====================================================
    # TEST 6 — LOW CONFIDENCE
    # =====================================================

    low_confidence_event = {
        "event_type": "payment_failure",
        "root_cause": "network_error",
        "amount": 6000.00,
    }

    result_6 = engine.evaluate(
        event=low_confidence_event,
        action="retry",
        confidence=0.42,
    )

    print_policy_result(
        "TEST 6 — LOW CONFIDENCE",
        result_6,
    )

    # =====================================================
    # TEST 7 — INVALID ACTION
    # =====================================================

    invalid_action_event = {
        "event_type": "payment_failure",
        "root_cause": "network_error",
        "amount": 6000.00,
    }

    result_7 = engine.evaluate(
        event=invalid_action_event,
        action="promise_to_pay",
        confidence=0.95,
    )

    print_policy_result(
        "TEST 7 — INVALID ACTION",
        result_7,
    )

    # =====================================================
    # TEST 8 — UNKNOWN EVENT
    # =====================================================

    unknown_event = {
        "event_type": "unknown_event",
        "root_cause": "unknown",
        "amount": 5000.00,
    }

    result_8 = engine.evaluate(
        event=unknown_event,
        action="retry",
        confidence=0.95,
    )

    print_policy_result(
        "TEST 8 — UNKNOWN EVENT",
        result_8,
    )

    # =====================================================
    # ASSERTIONS
    # =====================================================

    print()
    print("==============================================")
    print("             POLICY TEST SUMMARY")
    print("==============================================")

    # -----------------------------------------------------
    # Normal payment
    # -----------------------------------------------------

    if not result_1.allowed:

        raise AssertionError(
            "TEST FAILURE: Normal payment retry "
            "should be allowed."
        )

    # -----------------------------------------------------
    # Checkout
    # -----------------------------------------------------

    if not result_2.allowed:

        raise AssertionError(
            "TEST FAILURE: Checkout reminder "
            "should be allowed."
        )

    # -----------------------------------------------------
    # Invoice
    # -----------------------------------------------------

    if not result_3.allowed:

        raise AssertionError(
            "TEST FAILURE: Normal invoice action "
            "should be allowed."
        )

    # -----------------------------------------------------
    # Fraud
    # -----------------------------------------------------

    if result_4.allowed:

        raise AssertionError(
            "SAFETY FAILURE: Fraud was allowed."
        )

    if result_4.action != (
        "block_and_escalate"
    ):

        raise AssertionError(
            "SAFETY FAILURE: Fraud did not "
            "become block_and_escalate."
        )

    if not result_4.requires_human:

        raise AssertionError(
            "SAFETY FAILURE: Fraud does not "
            "require human review."
        )

    # -----------------------------------------------------
    # High value
    # -----------------------------------------------------

    if result_5.allowed:

        raise AssertionError(
            "SAFETY FAILURE: High-value case "
            "was automatically approved."
        )

    if not result_5.requires_human:

        raise AssertionError(
            "SAFETY FAILURE: High-value case "
            "does not require human approval."
        )

    # -----------------------------------------------------
    # Low confidence
    # -----------------------------------------------------

    if result_6.allowed:

        raise AssertionError(
            "SAFETY FAILURE: Low-confidence "
            "action was automatically approved."
        )

    # -----------------------------------------------------
    # Invalid action
    # -----------------------------------------------------

    if result_7.allowed:

        raise AssertionError(
            "SAFETY FAILURE: Invalid action "
            "was approved."
        )

    # -----------------------------------------------------
    # Unknown event
    # -----------------------------------------------------

    if result_8.allowed:

        raise AssertionError(
            "SAFETY FAILURE: Unknown event "
            "was approved."
        )

    print()
    print(
        "All policy and safety assertions PASSED."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_policy_tests()