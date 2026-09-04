from app.services.retrieval_service import RetrievalService


class DecisionEngine:
    """
    Vaidya Decision Engine.

    Responsibilities:
    1. Retrieve historical evidence.
    2. Filter evidence to the relevant revenue surface.
    3. Evaluate historical recovery actions.
    4. Estimate expected recovery.
    5. Calculate decision confidence.
    6. Apply safety rules.
    7. Produce a transparent final decision.

    IMPORTANT:
    This engine DOES NOT execute payments.

    It only decides what Vaidya should do.
    """

    # =====================================================
    # CONFIGURATION
    # =====================================================

    DEFAULT_TOP_K = 10

    MINIMUM_SIMILARITY = 0.50

    MINIMUM_CONFIDENCE_FOR_AUTOMATION = 0.70

    # =====================================================
    # ACTIONS ALLOWED BY REVENUE SURFACE
    # =====================================================

    PAYMENT_ACTIONS = {
        "retry",
        "delayed_retry",
        "payment_method_update",
        "mandate_retry",
        "block_and_escalate",
        "human_review",
    }

    CHECKOUT_ACTIONS = {
        "reminder",
        "targeted_reminder",
        "stop_outreach",
        "human_review",
    }

    INVOICE_ACTIONS = {
        "promise_to_pay",
        "payment_reminder",
        "account_escalation",
        "human_review",
    }

    FRAUD_ACTIONS = {
        "block_and_escalate",
    }

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(self):

        self.retrieval_service = RetrievalService()

    # =====================================================
    # GET ALLOWED ACTIONS
    # =====================================================

    def get_allowed_actions(
        self,
        current_event,
    ):
        """
        Return actions that are relevant to the current
        revenue surface.

        This prevents, for example, an invoice action from
        competing against a payment retry.
        """

        event_type = current_event.get(
            "event_type"
        )

        root_cause = current_event.get(
            "root_cause"
        )

        # -------------------------------------------------
        # Fraud gets its own isolated action space.
        # -------------------------------------------------

        if root_cause == "fraud_risk":

            return self.FRAUD_ACTIONS

        # -------------------------------------------------
        # Payment failures.
        # -------------------------------------------------

        if event_type == "payment_failure":

            return self.PAYMENT_ACTIONS

        # -------------------------------------------------
        # Checkout abandonment.
        # -------------------------------------------------

        if event_type == "checkout_abandonment":

            return self.CHECKOUT_ACTIONS

        # -------------------------------------------------
        # Overdue invoices.
        # -------------------------------------------------

        if event_type == "overdue_invoice":

            return self.INVOICE_ACTIONS

        # -------------------------------------------------
        # Unknown event.
        # -------------------------------------------------

        return set()

    # =====================================================
    # ACTION SUCCESS RATE
    # =====================================================

    def calculate_action_success_rate(
        self,
        cases,
    ):
        """
        Calculate historical success rate for each action.

        Successful outcomes:
            recovered
            partial
        """

        action_statistics = {}

        for case in cases:

            action = case["action_taken"]

            if action not in action_statistics:

                action_statistics[action] = {
                    "total": 0,
                    "successful": 0,
                }

            action_statistics[action]["total"] += 1

            if case["outcome"] in [
                "recovered",
                "partial",
            ]:

                action_statistics[action][
                    "successful"
                ] += 1

        success_rates = {}

        for action, statistics in (
            action_statistics.items()
        ):

            total = statistics["total"]

            successful = statistics[
                "successful"
            ]

            if total == 0:

                success_rates[action] = 0.0

            else:

                success_rates[action] = (
                    successful / total
                )

        return success_rates

    # =====================================================
    # EXPECTED RECOVERY
    # =====================================================

    def calculate_expected_recovery(
        self,
        current_amount,
        cases,
    ):
        """
        Estimate expected recovery from historical cases.

        Formula:

            historical recovery rate =
                recovered amount / historical amount

            expected recovery =
                current amount
                × average historical recovery rate

        This is an estimate, NOT a guarantee.
        """

        if not cases:

            return 0.0

        recovery_rates = []

        for case in cases:

            historical_amount = float(
                case["amount"]
            )

            recovered_amount = float(
                case["recovered_amount"]
            )

            if historical_amount <= 0:

                continue

            recovery_rate = (
                recovered_amount
                / historical_amount
            )

            recovery_rates.append(
                recovery_rate
            )

        if not recovery_rates:

            return 0.0

        average_recovery_rate = (
            sum(recovery_rates)
            / len(recovery_rates)
        )

        expected_recovery = (
            current_amount
            * average_recovery_rate
        )

        return round(
            expected_recovery,
            2,
        )

    # =====================================================
    # ACTION EVALUATION
    # =====================================================

    def evaluate_actions(
        self,
        current_event,
        retrieved_cases,
    ):
        """
        Evaluate historical performance of each relevant
        action.

        Only actions appropriate for the current revenue
        surface are considered.
        """

        if not retrieved_cases:

            return []

        current_amount = float(
            current_event.get(
                "amount",
                0,
            )
        )

        allowed_actions = (
            self.get_allowed_actions(
                current_event
            )
        )

        # -------------------------------------------------
        # Group cases by action.
        # -------------------------------------------------

        action_groups = {}

        for case in retrieved_cases:

            action = case["action_taken"]

            # ---------------------------------------------
            # Ignore actions that don't belong to the
            # current revenue surface.
            # ---------------------------------------------

            if action not in allowed_actions:

                continue

            if action not in action_groups:

                action_groups[action] = []

            action_groups[action].append(
                case
            )

        evaluated_actions = []

        # -------------------------------------------------
        # Evaluate each relevant action.
        # -------------------------------------------------

        for action, cases in (
            action_groups.items()
        ):

            total_cases = len(cases)

            successful_cases = [
                case
                for case in cases
                if case["outcome"] in [
                    "recovered",
                    "partial",
                ]
            ]

            successful_count = len(
                successful_cases
            )

            success_rate = (
                successful_count
                / total_cases
            )

            average_similarity = (
                sum(
                    case["similarity"]
                    for case in cases
                )
                / total_cases
            )

            expected_recovery = (
                self.calculate_expected_recovery(
                    current_amount,
                    cases,
                )
            )

            evaluated_actions.append(
                {
                    "action": action,

                    "historical_cases": (
                        total_cases
                    ),

                    "successful_cases": (
                        successful_count
                    ),

                    "success_rate": round(
                        success_rate,
                        4,
                    ),

                    "success_rate_percentage": (
                        round(
                            success_rate * 100,
                            2,
                        )
                    ),

                    "average_similarity": (
                        round(
                            average_similarity,
                            4,
                        )
                    ),

                    "expected_recovery": (
                        expected_recovery
                    ),
                }
            )

        # -------------------------------------------------
        # Rank actions.
        # -------------------------------------------------

        evaluated_actions.sort(
            key=lambda action: (
                action["expected_recovery"],
                action["success_rate"],
                action["average_similarity"],
            ),
            reverse=True,
        )

        return evaluated_actions

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def calculate_confidence(
        self,
        selected_action,
    ):
        """
        Calculate decision confidence.

        This is NOT an ML probability.

        Formula:

            50% → historical success rate
            30% → average similarity
            20% → evidence volume

        Evidence volume reaches maximum strength at
        10 or more historical cases.
        """

        if not selected_action:

            return 0.0

        success_rate = float(
            selected_action[
                "success_rate"
            ]
        )

        similarity = float(
            selected_action[
                "average_similarity"
            ]
        )

        historical_cases = int(
            selected_action[
                "historical_cases"
            ]
        )

        evidence_strength = min(
            historical_cases / 10,
            1.0,
        )

        confidence = (
            0.50 * success_rate
            +
            0.30 * similarity
            +
            0.20 * evidence_strength
        )

        return round(
            confidence,
            4,
        )

    # =====================================================
    # SAFETY RULES
    # =====================================================

    def apply_safety_rules(
        self,
        current_event,
        selected_action,
    ):
        """
        Apply Vaidya safety rules.

        Fraud:
            ALWAYS block and escalate.

        Unknown root cause:
            Human review.

        No action:
            Human review.

        Normal supported event:
            Continue with selected action.
        """

        root_cause = current_event.get(
            "root_cause"
        )

        event_type = current_event.get(
            "event_type"
        )

        # -------------------------------------------------
        # FRAUD
        # -------------------------------------------------

        if root_cause == "fraud_risk":

            return {
                "allowed": False,

                "reason": (
                    "Fraud-risk events cannot "
                    "be automatically recovered."
                ),

                "final_action": (
                    "block_and_escalate"
                ),
            }

        # -------------------------------------------------
        # UNKNOWN EVENT TYPE
        # -------------------------------------------------

        if event_type not in {
            "payment_failure",
            "checkout_abandonment",
            "overdue_invoice",
        }:

            return {
                "allowed": False,

                "reason": (
                    "Unsupported event type "
                    "requires human review."
                ),

                "final_action": "human_review",
            }

        # -------------------------------------------------
        # UNKNOWN ROOT CAUSE
        # -------------------------------------------------

        if not root_cause:

            return {
                "allowed": False,

                "reason": (
                    "Root cause is unknown."
                ),

                "final_action": "human_review",
            }

        # -------------------------------------------------
        # NO SELECTED ACTION
        # -------------------------------------------------

        if not selected_action:

            return {
                "allowed": False,

                "reason": (
                    "No suitable historical "
                    "action was found."
                ),

                "final_action": "human_review",
            }

        # -------------------------------------------------
        # ACTION MUST BELONG TO EVENT TYPE
        # -------------------------------------------------

        allowed_actions = (
            self.get_allowed_actions(
                current_event
            )
        )

        selected_action_name = (
            selected_action["action"]
        )

        if (
            selected_action_name
            not in allowed_actions
        ):

            return {
                "allowed": False,

                "reason": (
                    "Selected action is not "
                    "allowed for this event type."
                ),

                "final_action": "human_review",
            }

        # -------------------------------------------------
        # NORMAL CASE
        # -------------------------------------------------

        return {
            "allowed": True,

            "reason": (
                "Action passed the current "
                "safety rules."
            ),

            "final_action": (
                selected_action_name
            ),
        }

    # =====================================================
    # MAIN DECISION
    # =====================================================

    def decide(
        self,
        current_event,
        top_k=None,
    ):
        """
        Produce a transparent Vaidya decision.
        """

        if top_k is None:

            top_k = self.DEFAULT_TOP_K

        # -------------------------------------------------
        # SAFETY PRE-CHECK
        # -------------------------------------------------

        root_cause = current_event.get(
            "root_cause"
        )

        event_type = current_event.get(
            "event_type"
        )

        # -------------------------------------------------
        # Fraud is handled immediately.
        #
        # We still retrieve evidence for explanation,
        # but fraud can never enter normal automation.
        # -------------------------------------------------

        is_fraud = (
            root_cause == "fraud_risk"
        )

        # -------------------------------------------------
        # Retrieve historical evidence.
        # -------------------------------------------------

        retrieved_cases = (
            self.retrieval_service.retrieve(
                current_event,
                top_k=top_k,
                successful_only=False,
            )
        )

        # -------------------------------------------------
        # Keep sufficiently similar cases.
        # -------------------------------------------------

        relevant_cases = [
            case
            for case in retrieved_cases
            if case["similarity"]
            >= self.MINIMUM_SIMILARITY
        ]

        # -------------------------------------------------
        # FRAUD HANDLING
        #
        # Fraud should only use fraud historical evidence
        # when evaluating its explanation.
        # -------------------------------------------------

        if is_fraud:

            fraud_cases = [
                case
                for case in relevant_cases
                if case["root_cause"]
                == "fraud_risk"
            ]

            fraud_action_cases = [
                case
                for case in fraud_cases
                if case["action_taken"]
                == "block_and_escalate"
            ]

            safety = (
                self.apply_safety_rules(
                    current_event,
                    {
                        "action": (
                            "block_and_escalate"
                        )
                    },
                )
            )

            # ---------------------------------------------
            # Fraud expected recovery is ALWAYS zero.
            # ---------------------------------------------

            return {
                "decision": "escalate",

                "action": (
                    "block_and_escalate"
                ),

                "confidence": (
                    self.calculate_fraud_confidence(
                        fraud_action_cases
                    )
                ),

                "confidence_percentage": (
                    round(
                        self.calculate_fraud_confidence(
                            fraud_action_cases
                        )
                        * 100,
                        2,
                    )
                ),

                "expected_recovery": 0.0,

                "historical_cases": len(
                    fraud_action_cases
                ),

                "reason": (
                    "Fraud-risk events cannot "
                    "be automatically recovered."
                ),

                "evidence": (
                    fraud_cases
                ),

                "action_analysis": (
                    self.evaluate_actions(
                        current_event,
                        fraud_cases,
                    )
                ),

                "safety": safety,
            }

        # -------------------------------------------------
        # UNKNOWN EVENT TYPE
        # -------------------------------------------------

        if event_type not in {
            "payment_failure",
            "checkout_abandonment",
            "overdue_invoice",
        }:

            return {
                "decision": "human_review",

                "action": "human_review",

                "confidence": 0.0,

                "confidence_percentage": 0.0,

                "expected_recovery": 0.0,

                "historical_cases": 0,

                "reason": (
                    "Unsupported event type "
                    "requires human review."
                ),

                "evidence": [],

                "action_analysis": [],

                "safety": (
                    self.apply_safety_rules(
                        current_event,
                        None,
                    )
                ),
            }

        # -------------------------------------------------
        # Filter evidence by event type.
        # -------------------------------------------------

        event_cases = [
            case
            for case in relevant_cases
            if case["event_type"]
            == event_type
        ]

        # -------------------------------------------------
        # No relevant evidence.
        # -------------------------------------------------

        if not event_cases:

            return {
                "decision": "human_review",

                "action": "human_review",

                "confidence": 0.0,

                "confidence_percentage": 0.0,

                "expected_recovery": 0.0,

                "historical_cases": 0,

                "reason": (
                    "No sufficiently similar "
                    "historical cases were found "
                    "for this revenue surface."
                ),

                "evidence": [],

                "action_analysis": [],

                "safety": (
                    self.apply_safety_rules(
                        current_event,
                        None,
                    )
                ),
            }

        # -------------------------------------------------
        # Evaluate actions.
        # -------------------------------------------------

        action_analysis = (
            self.evaluate_actions(
                current_event,
                event_cases,
            )
        )

        if not action_analysis:

            return {
                "decision": "human_review",

                "action": "human_review",

                "confidence": 0.0,

                "confidence_percentage": 0.0,

                "expected_recovery": 0.0,

                "historical_cases": len(
                    event_cases
                ),

                "reason": (
                    "No valid recovery actions "
                    "were found for this event."
                ),

                "evidence": event_cases,

                "action_analysis": [],

                "safety": (
                    self.apply_safety_rules(
                        current_event,
                        None,
                    )
                ),
            }

        # -------------------------------------------------
        # Select best action.
        # -------------------------------------------------

        selected_action = (
            action_analysis[0]
        )

        confidence = (
            self.calculate_confidence(
                selected_action
            )
        )

        # -------------------------------------------------
        # Apply safety.
        # -------------------------------------------------

        safety = (
            self.apply_safety_rules(
                current_event,
                selected_action,
            )
        )

        # -------------------------------------------------
        # Safety override.
        # -------------------------------------------------

        if not safety["allowed"]:

            final_action = (
                safety["final_action"]
            )

            return {
                "decision": (
                    "escalate"
                    if final_action
                    == "block_and_escalate"
                    else "human_review"
                ),

                "action": final_action,

                "confidence": confidence,

                "confidence_percentage": round(
                    confidence * 100,
                    2,
                ),

                # IMPORTANT:
                # If safety overrides the recovery action,
                # we do not claim an expected recovery.
                "expected_recovery": 0.0,

                "historical_cases": len(
                    event_cases
                ),

                "reason": safety[
                    "reason"
                ],

                "evidence": event_cases,

                "action_analysis": (
                    action_analysis
                ),

                "safety": safety,
            }

        # -------------------------------------------------
        # Confidence threshold.
        # -------------------------------------------------

        if (
            confidence
            < self.MINIMUM_CONFIDENCE_FOR_AUTOMATION
        ):

            final_action = "human_review"

            decision = "human_review"

            reason = (
                "Historical evidence exists, "
                "but confidence is below the "
                "automatic execution threshold."
            )

            expected_recovery = 0.0

        else:

            final_action = (
                selected_action["action"]
            )

            decision = "automate"

            reason = (
                f"Selected '{final_action}' "
                f"because it has the strongest "
                f"historical recovery evidence."
            )

            expected_recovery = (
                selected_action[
                    "expected_recovery"
                ]
            )

        # -------------------------------------------------
        # Final result.
        # -------------------------------------------------

        return {
            "decision": decision,

            "action": final_action,

            "confidence": confidence,

            "confidence_percentage": round(
                confidence * 100,
                2,
            ),

            "expected_recovery": (
                expected_recovery
            ),

            "historical_cases": len(
                event_cases
            ),

            "reason": reason,

            "evidence": event_cases,

            "action_analysis": (
                action_analysis
            ),

            "safety": safety,
        }

    # =====================================================
    # FRAUD CONFIDENCE
    # =====================================================

    def calculate_fraud_confidence(
        self,
        fraud_cases,
    ):
        """
        Calculate confidence in the fraud safety decision.

        This is NOT recovery confidence.

        It represents how strongly the historical fraud
        evidence supports the safety decision.
        """

        if not fraud_cases:

            return 0.0

        average_similarity = (
            sum(
                case["similarity"]
                for case in fraud_cases
            )
            / len(fraud_cases)
        )

        evidence_strength = min(
            len(fraud_cases) / 10,
            1.0,
        )

        confidence = (
            0.70 * average_similarity
            +
            0.30 * evidence_strength
        )

        return round(
            confidence,
            4,
        )


# =========================================================
# PRINT DECISION
# =========================================================

def print_decision(
    test_name,
    current_event,
    result,
):
    """
    Print a clean decision summary.
    """

    print()
    print("=" * 55)
    print(test_name)
    print("=" * 55)

    print()
    print("CURRENT EVENT")
    print("--------------------------------------")

    for key, value in current_event.items():

        if key == "amount":

            print(
                f"{key}: "
                f"₹{value:,.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print()
    print("VAIDYA DECISION")
    print("--------------------------------------")

    print(
        f"Decision: "
        f"{result['decision']}"
    )

    print(
        f"Action: "
        f"{result['action']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence_percentage']:.2f}%"
    )

    print(
        f"Expected recovery: "
        f"₹{result['expected_recovery']:,.2f}"
    )

    print(
        f"Historical cases used: "
        f"{result['historical_cases']}"
    )

    print(
        f"Reason: "
        f"{result['reason']}"
    )

    print()
    print("SAFETY")
    print("--------------------------------------")

    print(
        f"Allowed: "
        f"{result['safety']['allowed']}"
    )

    print(
        f"Safety reason: "
        f"{result['safety']['reason']}"
    )

    print()
    print("ACTION ANALYSIS")
    print("--------------------------------------")

    for action in result[
        "action_analysis"
    ]:

        print(
            f"\nAction: "
            f"{action['action']}"
        )

        print(
            f"Historical cases: "
            f"{action['historical_cases']}"
        )

        print(
            f"Successful cases: "
            f"{action['successful_cases']}"
        )

        print(
            f"Success rate: "
            f"{action['success_rate_percentage']:.2f}%"
        )

        print(
            f"Average similarity: "
            f"{action['average_similarity'] * 100:.2f}%"
        )

        print(
            f"Expected recovery: "
            f"₹{action['expected_recovery']:,.2f}"
        )

    print()
    print("TOP EVIDENCE")
    print("--------------------------------------")

    for case in result[
        "evidence"
    ][:3]:

        print(
            f"\n{case['case_id']}"
        )

        print(
            f"Similarity: "
            f"{case['similarity'] * 100:.2f}%"
        )

        print(
            f"Event type: "
            f"{case['event_type']}"
        )

        print(
            f"Root cause: "
            f"{case['root_cause']}"
        )

        print(
            f"Action: "
            f"{case['action_taken']}"
        )

        print(
            f"Outcome: "
            f"{case['outcome']}"
        )

        print(
            f"Recovered: "
            f"₹{case['recovered_amount']:,.2f}"
        )


# =========================================================
# TEST SUITE
# =========================================================

def run_test_suite():

    engine = DecisionEngine()

    print()
    print("==============================================")
    print("      VAIDYA DECISION ENGINE TEST SUITE")
    print("==============================================")

    print()

    print(
        f"Historical cases loaded: "
        f"{len(engine.retrieval_service.cases)}"
    )

    # =====================================================
    # TEST 1 — PAYMENT FAILURE
    # =====================================================

    payment_event = {
        "event_type": "payment_failure",

        "root_cause": "network_error",

        "amount": 6200.00,

        "customer_profile": (
            "Returning customer with "
            "historical transaction activity."
        ),
    }

    result_1 = engine.decide(
        payment_event,
        top_k=10,
    )

    print_decision(
        "TEST 1 — PAYMENT FAILURE",
        payment_event,
        result_1,
    )

    # =====================================================
    # TEST 2 — CHECKOUT ABANDONMENT
    # =====================================================

    checkout_event = {
        "event_type": "checkout_abandonment",

        "root_cause": "high_intent_abandonment",

        "amount": 5000.00,

        "customer_profile": (
            "Customer history score: 0.90"
        ),
    }

    result_2 = engine.decide(
        checkout_event,
        top_k=10,
    )

    print_decision(
        "TEST 2 — CHECKOUT ABANDONMENT",
        checkout_event,
        result_2,
    )

    # =====================================================
    # TEST 3 — OVERDUE INVOICE
    # =====================================================

    invoice_event = {
        "event_type": "overdue_invoice",

        "root_cause": "repeated_late_payer",

        "amount": 100000.00,

        "customer_profile": (
            "8 previous invoices; "
            "5 previous late payments."
        ),
    }

    result_3 = engine.decide(
        invoice_event,
        top_k=10,
    )

    print_decision(
        "TEST 3 — OVERDUE INVOICE",
        invoice_event,
        result_3,
    )

    # =====================================================
    # TEST 4 — FRAUD
    # =====================================================

    fraud_event = {
        "event_type": "payment_failure",

        "root_cause": "fraud_risk",

        "amount": 10000.00,

        "customer_profile": (
            "Returning customer with "
            "historical transaction activity."
        ),
    }

    result_4 = engine.decide(
        fraud_event,
        top_k=10,
    )

    print_decision(
        "TEST 4 — FRAUD RISK",
        fraud_event,
        result_4,
    )

    # =====================================================
    # TEST 5 — UNKNOWN CASE
    # =====================================================

    unknown_event = {
        "event_type": "unknown_event",

        "root_cause": None,

        "amount": 15000.00,

        "customer_profile": (
            "Unknown customer context."
        ),
    }

    result_5 = engine.decide(
        unknown_event,
        top_k=10,
    )

    print_decision(
        "TEST 5 — UNKNOWN CASE",
        unknown_event,
        result_5,
    )

    # =====================================================
    # FINAL SAFETY SUMMARY
    # =====================================================

    print()
    print("==============================================")
    print("             SAFETY TEST SUMMARY")
    print("==============================================")

    print()

    print(
        "Payment final action: "
        f"{result_1['action']}"
    )

    print(
        "Checkout final action: "
        f"{result_2['action']}"
    )

    print(
        "Invoice final action: "
        f"{result_3['action']}"
    )

    print(
        "Fraud final action: "
        f"{result_4['action']}"
    )

    print(
        "Fraud expected recovery: "
        f"₹{result_4['expected_recovery']:,.2f}"
    )

    print(
        "Unknown case final action: "
        f"{result_5['action']}"
    )

    print()

    # =====================================================
    # ASSERTIONS
    # =====================================================

    # -----------------------------------------------------
    # Payment
    # -----------------------------------------------------

    if result_1["action"] != "retry":

        raise AssertionError(
            "PAYMENT TEST FAILURE: "
            "Expected retry."
        )

    # -----------------------------------------------------
    # Checkout
    # -----------------------------------------------------

    if result_2["action"] not in {
        "reminder",
        "targeted_reminder",
        "stop_outreach",
    }:

        raise AssertionError(
            "CHECKOUT TEST FAILURE: "
            "Invalid checkout action."
        )

    # -----------------------------------------------------
    # Invoice
    # -----------------------------------------------------

    if result_3["action"] not in {
        "promise_to_pay",
        "payment_reminder",
        "account_escalation",
    }:

        raise AssertionError(
            "INVOICE TEST FAILURE: "
            "Invalid invoice action."
        )

    # -----------------------------------------------------
    # Fraud
    # -----------------------------------------------------

    if result_4["action"] != (
        "block_and_escalate"
    ):

        raise AssertionError(
            "SAFETY FAILURE: "
            "Fraud was not blocked."
        )

    if result_4["decision"] != "escalate":

        raise AssertionError(
            "SAFETY FAILURE: "
            "Fraud was not escalated."
        )

    if result_4["expected_recovery"] != 0.0:

        raise AssertionError(
            "SAFETY FAILURE: "
            "Fraud expected recovery must be ₹0."
        )

    if result_4["safety"]["allowed"]:

        raise AssertionError(
            "SAFETY FAILURE: "
            "Fraud was marked as allowed."
        )

    # -----------------------------------------------------
    # Unknown case
    # -----------------------------------------------------

    if result_5["action"] != "human_review":

        raise AssertionError(
            "SAFETY FAILURE: "
            "Unknown case was not sent "
            "to human review."
        )

    if result_5["decision"] != "human_review":

        raise AssertionError(
            "SAFETY FAILURE: "
            "Unknown case decision was not "
            "human_review."
        )

    # -----------------------------------------------------
    # Final success message.
    # -----------------------------------------------------

    print(
        "All critical decision and safety "
        "assertions PASSED."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_test_suite()