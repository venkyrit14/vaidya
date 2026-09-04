from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from pydantic import BaseModel, Field

from app.services.orchestrator import VaidyaOrchestrator


router = APIRouter(
    prefix="/api/recovery",
    tags=["Recovery"],
)


# =========================================================
# MODELS
# =========================================================

class RecoveryRequest(BaseModel):
    """
    Incoming event sent to Vaidya.
    """
    event_type: str = Field(
        ...,
        description="Type of revenue-risk event.",
        examples=[
            "payment_failure",
            "checkout_abandonment",
            "overdue_invoice",
        ],
    )
    root_cause: Optional[str] = Field(
        None,
        description="Detected reason for the revenue risk.",
        examples=[
            "network_error",
            "high_intent_abandonment",
            "repeated_late_payer",
        ],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Amount currently at risk.",
    )
    customer_profile: str = Field(
        ...,
        description="Customer context used by Vaidya.",
    )


class RecoveryResponse(BaseModel):
    """
    Full response returned to the frontend.
    """
    case_id: str
    event_type: str
    amount_at_risk: float
    decision: str
    action: str
    confidence: float
    expected_recovery: float
    policy_allowed: bool
    risk_level: str
    requires_human: bool
    execution_status: str
    outcome: str
    recovered_amount: float
    remaining_amount: float
    message: str
    timestamp: Optional[str] = None


class RecoverySummaryResponse(BaseModel):
    total_cases: int
    total_amount_at_risk: float
    total_recovered: float
    total_remaining: float
    recovery_rate: float
    successful_recoveries: int
    failed_recoveries: int
    partial_recoveries: int
    blocked_cases: int
    human_review_cases: int
    outcomes: Dict[str, int]
    actions: Dict[str, int]
    event_types: Dict[str, int]
    available_source_events: int
    available_source_amount: float


class PaginatedRecordsResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    limit: int
    total_pages: int


class BatchSummary(BaseModel):
    batch_id: str
    title: str
    surface: str
    description: str
    total_events: int
    total_amount_at_risk: float
    processed_count: int


class ProcessBatchRequest(BaseModel):
    batch_id: str
    limit: Optional[int] = 50


# =========================================================
# VAIDYA INSTANCE & DATA CACHE
# =========================================================

vaidya = VaidyaOrchestrator()

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "generated"

_DATASETS_CACHE: Dict[str, pd.DataFrame] = {}


def get_dataset(surface: str) -> pd.DataFrame:
    if surface not in _DATASETS_CACHE:
        file_map = {
            "payment_failure": DATA_DIR / "payment_failure_events.csv",
            "checkout_abandonment": DATA_DIR / "checkout_abandonment_events.csv",
            "overdue_invoice": DATA_DIR / "overdue_invoice_events.csv",
        }
        path = file_map.get(surface)
        if path and path.exists():
            _DATASETS_CACHE[surface] = pd.read_csv(path)
        else:
            _DATASETS_CACHE[surface] = pd.DataFrame()
    return _DATASETS_CACHE[surface]


def get_all_batches_config() -> List[Dict[str, Any]]:
    return [
        {
            "batch_id": "BATCH_DEMO_01",
            "title": "Curated Multi-Surface Demo Batch",
            "surface": "multi_surface",
            "description": "Representative mix of standard failures, high-intent abandonments, overdue invoices, high-value cases, and fraud.",
        },
        {
            "batch_id": "BATCH_PAY_01",
            "title": "Payment Failures: Batch 1",
            "surface": "payment_failure",
            "description": "UPI, Card, and Netbanking failures from payment processing.",
            "offset": 0,
            "limit": 50,
        },
        {
            "batch_id": "BATCH_PAY_02",
            "title": "Payment Failures: Batch 2",
            "surface": "payment_failure",
            "description": "Mandate failures and bank timeout events.",
            "offset": 50,
            "limit": 50,
        },
        {
            "batch_id": "BATCH_CHK_01",
            "title": "Checkout Abandonment: Batch 1",
            "surface": "checkout_abandonment",
            "description": "High-intent abandoned checkout carts.",
            "offset": 0,
            "limit": 50,
        },
        {
            "batch_id": "BATCH_CHK_02",
            "title": "Checkout Abandonment: Batch 2",
            "surface": "checkout_abandonment",
            "description": "Hesitation and repeated drop-offs.",
            "offset": 50,
            "limit": 50,
        },
        {
            "batch_id": "BATCH_INV_01",
            "title": "Overdue Invoices: Batch 1",
            "surface": "overdue_invoice",
            "description": "Commercial B2B invoice aging under 30 days.",
            "offset": 0,
            "limit": 50,
        },
        {
            "batch_id": "BATCH_INV_02",
            "title": "Overdue Invoices: Batch 2",
            "surface": "overdue_invoice",
            "description": "Repeated late payers and enterprise credit lines.",
            "offset": 50,
            "limit": 50,
        },
    ]


def get_events_for_batch(batch_id: str) -> List[Dict[str, Any]]:
    batches = {b["batch_id"]: b for b in get_all_batches_config()}
    if batch_id not in batches:
        return []

    cfg = batches[batch_id]
    if batch_id == "BATCH_DEMO_01":
        # Curated selection
        events = []
        df_pay = get_dataset("payment_failure")
        df_chk = get_dataset("checkout_abandonment")
        df_inv = get_dataset("overdue_invoice")

        # Normal payment failures
        if not df_pay.empty:
            for _, r in df_pay.head(4).iterrows():
                events.append({
                    "event_id": str(r.get("event_id", f"PAY_{len(events)}")),
                    "event_type": "payment_failure",
                    "amount": float(r.get("amount_at_risk", 6200.0)),
                    "root_cause": str(r.get("error_reason", "network_error")),
                    "customer_profile": "repeat_customer",
                    "customer_id": str(r.get("customer_id", "CUST_101")),
                    "timestamp": str(r.get("timestamp", "2026-08-31 10:00:00")),
                })
            # Add one fraud case
            fraud_rows = df_pay[df_pay["fraud_flag"] == True]
            if not fraud_rows.empty:
                r_fraud = fraud_rows.iloc[0]
                events.append({
                    "event_id": str(r_fraud.get("event_id", "PAY_FRD_001")),
                    "event_type": "payment_failure",
                    "amount": float(r_fraud.get("amount_at_risk", 10000.0)),
                    "root_cause": "fraud_risk",
                    "customer_profile": "elevated_risk_account",
                    "customer_id": str(r_fraud.get("customer_id", "CUST_FRD")),
                    "timestamp": str(r_fraud.get("timestamp", "2026-08-31 11:30:00")),
                })

        # Checkout abandonments
        if not df_chk.empty:
            for _, r in df_chk.head(4).iterrows():
                events.append({
                    "event_id": str(r.get("event_id", f"CHK_{len(events)}")),
                    "event_type": "checkout_abandonment",
                    "amount": float(r.get("amount_at_risk", 5000.0)),
                    "root_cause": "high_intent_abandonment",
                    "customer_profile": "high_intent_shopper",
                    "customer_id": str(r.get("customer_id", "CUST_CHK")),
                    "timestamp": str(r.get("timestamp", "2026-08-31 12:00:00")),
                })

        # Invoices (including standard and high-value)
        if not df_inv.empty:
            for _, r in df_inv.head(3).iterrows():
                amt = float(r.get("amount_at_risk", 50000.0))
                events.append({
                    "event_id": str(r.get("event_id", f"INV_{len(events)}")),
                    "event_type": "overdue_invoice",
                    "amount": amt,
                    "root_cause": "repeated_late_payer",
                    "customer_profile": "b2b_account",
                    "customer_id": str(r.get("customer_id", "B2B_101")),
                    "timestamp": str(r.get("timestamp", "2026-08-31 14:00:00")),
                })
            # Add high-value case
            high_val_rows = df_inv[df_inv["amount_at_risk"] > 100000.0]
            if not high_val_rows.empty:
                r_high = high_val_rows.iloc[0]
                events.append({
                    "event_id": str(r_high.get("event_id", "INV_HIGH_001")),
                    "event_type": "overdue_invoice",
                    "amount": float(r_high.get("amount_at_risk", 250000.0)),
                    "root_cause": "repeated_late_payer",
                    "customer_profile": "high_value_enterprise",
                    "customer_id": str(r_high.get("customer_id", "B2B_ENT")),
                    "timestamp": str(r_high.get("timestamp", "2026-08-31 16:00:00")),
                })
        return events

    # Surface-specific batch
    surface = cfg["surface"]
    df = get_dataset(surface)
    if df.empty:
        return []

    offset = cfg.get("offset", 0)
    limit = cfg.get("limit", 50)
    slice_df = df.iloc[offset : offset + limit]

    events = []
    for _, r in slice_df.iterrows():
        event_id = str(r.get("event_id", f"{surface[:3].upper()}_{len(events)+1}"))
        amt = float(r.get("amount_at_risk", 1000.0))
        customer_id = str(r.get("customer_id", "CUST_GENERIC"))
        timestamp = str(r.get("timestamp", "2026-08-31 12:00:00"))

        if surface == "payment_failure":
            root_cause = "fraud_risk" if bool(r.get("fraud_flag", False)) else str(r.get("error_reason", "network_error"))
            profile = "elevated_risk_account" if root_cause == "fraud_risk" else "repeat_customer"
        elif surface == "checkout_abandonment":
            root_cause = "high_intent_abandonment"
            profile = "high_intent_shopper"
        else:
            root_cause = "repeated_late_payer" if int(r.get("previous_late_payment_count", 0)) > 1 else "recently_overdue"
            profile = "high_value_enterprise" if amt > 100000 else "b2b_account"

        events.append({
            "event_id": event_id,
            "event_type": surface,
            "amount": amt,
            "root_cause": root_cause,
            "customer_profile": profile,
            "customer_id": customer_id,
            "timestamp": timestamp,
        })
    return events


# =========================================================
# ENDPOINTS
# =========================================================

@router.post(
    "/analyze",
    response_model=RecoveryResponse,
)
def analyze_recovery(request: RecoveryRequest):
    """
    Send a revenue-risk event through the complete Vaidya pipeline.
    """
    case_id = "API_" + uuid.uuid4().hex[:12].upper()
    event = {
        "event_type": request.event_type,
        "root_cause": request.root_cause,
        "amount": request.amount,
        "customer_profile": request.customer_profile,
    }

    result = vaidya.process_event(event=event, case_id=case_id)
    decision = result["decision"]
    policy = result["policy"]
    execution = result["execution"]
    recovery = result["recovery"]

    return RecoveryResponse(
        case_id=case_id,
        event_type=request.event_type,
        amount_at_risk=request.amount,
        decision=decision["decision"],
        action=decision["final_action"],
        confidence=decision["confidence"],
        expected_recovery=decision["expected_recovery"],
        policy_allowed=policy["allowed"],
        risk_level=policy["risk_level"],
        requires_human=(policy["requires_human"] or execution["requires_human"]),
        execution_status=execution["status"],
        outcome=execution["outcome"],
        recovered_amount=execution["recovered_amount"],
        remaining_amount=execution["remaining_amount"],
        message=execution["message"],
        timestamp=recovery.get("timestamp"),
    )


@router.get(
    "/summary",
    response_model=RecoverySummaryResponse,
)
def get_recovery_summary():
    """
    Return aggregated metrics from the real RecoveryTracker records and source datasets.
    """
    tracker_summary = vaidya.recovery_tracker.get_summary()

    # Calculate available source event metrics
    df_pay = get_dataset("payment_failure")
    df_chk = get_dataset("checkout_abandonment")
    df_inv = get_dataset("overdue_invoice")

    total_source_count = len(df_pay) + len(df_chk) + len(df_inv)
    total_source_amount = 0.0
    if not df_pay.empty and "amount_at_risk" in df_pay.columns:
        total_source_amount += float(df_pay["amount_at_risk"].sum())
    if not df_chk.empty and "amount_at_risk" in df_chk.columns:
        total_source_amount += float(df_chk["amount_at_risk"].sum())
    if not df_inv.empty and "amount_at_risk" in df_inv.columns:
        total_source_amount += float(df_inv["amount_at_risk"].sum())

    return RecoverySummaryResponse(
        total_cases=tracker_summary["total_cases"],
        total_amount_at_risk=tracker_summary["total_amount_at_risk"],
        total_recovered=tracker_summary["total_recovered"],
        total_remaining=tracker_summary["total_remaining"],
        recovery_rate=tracker_summary["recovery_rate"],
        successful_recoveries=tracker_summary["successful_recoveries"],
        failed_recoveries=tracker_summary["failed_recoveries"],
        partial_recoveries=tracker_summary["partial_recoveries"],
        blocked_cases=tracker_summary["blocked_cases"],
        human_review_cases=tracker_summary["human_review_cases"],
        outcomes=tracker_summary["outcomes"],
        actions=tracker_summary["actions"],
        event_types=tracker_summary["event_types"],
        available_source_events=total_source_count,
        available_source_amount=round(total_source_amount, 2),
    )


@router.get(
    "/records",
    response_model=PaginatedRecordsResponse,
)
def get_recovery_records(
    search: Optional[str] = Query(None, description="Search by case ID, action, event type, or message"),
    event_type: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    requires_human: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Retrieve paginated and filtered recovery records recorded by Vaidya.
    """
    raw_records = vaidya.recovery_tracker.get_all_cases()
    records = [asdict(r) for r in raw_records]

    # Filters
    filtered = []
    for r in records:
        if event_type and r.get("event_type") != event_type:
            continue
        if outcome and r.get("outcome") != outcome:
            continue
        if action and r.get("action") != action:
            continue
        if requires_human is not None and r.get("requires_human") != requires_human:
            continue
        if search:
            q = search.lower()
            match = (
                q in str(r.get("case_id", "")).lower()
                or q in str(r.get("event_type", "")).lower()
                or q in str(r.get("action", "")).lower()
                or q in str(r.get("outcome", "")).lower()
                or q in str(r.get("message", "")).lower()
            )
            if not match:
                continue
        filtered.append(r)

    # Sort descending by timestamp
    filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    end = start + limit
    page_items = filtered[start:end]

    return PaginatedRecordsResponse(
        items=page_items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/records/{case_id}")
def get_recovery_record_by_id(case_id: str):
    """
    Retrieve deep details of a specific case record, including evidence and policy evaluation.
    """
    record = vaidya.recovery_tracker.get_case(case_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Recovery record '{case_id}' not found.")

    record_dict = asdict(record)

    # Enrich with Decision Engine & Policy Engine context
    mock_event = {
        "event_type": record.event_type,
        "amount": record.amount_at_risk,
        "root_cause": "fraud_risk" if record.action == "block_and_escalate" else "network_error" if record.event_type == "payment_failure" else "high_intent_abandonment" if record.event_type == "checkout_abandonment" else "repeated_late_payer",
        "customer_profile": "repeat_customer",
    }
    decision = vaidya.decision_engine.decide(mock_event)
    policy_res = vaidya.policy_engine.evaluate(
        mock_event,
        action=record.action,
        confidence=decision.get("confidence", 0.85),
    )

    return {
        "record": record_dict,
        "decision_context": {
            "decision": decision.get("decision"),
            "action": decision.get("action"),
            "confidence": decision.get("confidence"),
            "expected_recovery": decision.get("expected_recovery"),
            "reason": decision.get("reason"),
            "historical_cases_count": decision.get("historical_cases"),
            "evidence": decision.get("evidence", [])[:5],
            "action_analysis": decision.get("action_analysis", []),
        },
        "policy_context": {
            "allowed": policy_res.allowed,
            "decision": policy_res.decision,
            "reason": policy_res.reason,
            "risk_level": policy_res.risk_level,
            "requires_human": policy_res.requires_human,
        },
    }


@router.get(
    "/batches",
    response_model=List[BatchSummary],
)
def get_batches():
    """
    List available pre-generated batches from canonical/synthetic datasets.
    """
    configs = get_all_batches_config()
    existing_case_ids = {r.case_id for r in vaidya.recovery_tracker.get_all_cases()}

    summaries = []
    for cfg in configs:
        events = get_events_for_batch(cfg["batch_id"])
        total_amt = sum(e["amount"] for e in events)
        processed_count = sum(1 for e in events if e.get("event_id") in existing_case_ids)

        summaries.append(
            BatchSummary(
                batch_id=cfg["batch_id"],
                title=cfg["title"],
                surface=cfg["surface"],
                description=cfg["description"],
                total_events=len(events),
                total_amount_at_risk=round(total_amt, 2),
                processed_count=processed_count,
            )
        )
    return summaries


@router.get("/batches/{batch_id}/events")
def get_batch_events(
    batch_id: str,
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get actual source events from a specific batch.
    """
    events = get_events_for_batch(batch_id)
    if not events:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found.")

    if search:
        q = search.lower()
        events = [
            e for e in events
            if q in e.get("event_id", "").lower()
            or q in e.get("customer_id", "").lower()
            or q in e.get("root_cause", "").lower()
            or q in e.get("event_type", "").lower()
        ]

    total = len(events)
    total_pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    end = start + limit
    page_events = events[start:end]

    return {
        "batch_id": batch_id,
        "items": page_events,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.post("/process-batch")
def process_batch(request: ProcessBatchRequest):
    """
    Process events from a real dataset batch through the complete Vaidya pipeline and record outcomes.
    """
    events = get_events_for_batch(request.batch_id)
    if not events:
        raise HTTPException(status_code=404, detail=f"Batch '{request.batch_id}' not found.")

    limit = request.limit or 50
    selected_events = events[:limit]

    processed_results = []
    for ev in selected_events:
        case_id = f"CASE_{ev['event_id']}_{uuid.uuid4().hex[:6].upper()}"
        result = vaidya.process_event(
            event={
                "event_type": ev["event_type"],
                "root_cause": ev.get("root_cause"),
                "amount": ev["amount"],
                "customer_profile": ev.get("customer_profile", "standard_customer"),
            },
            case_id=case_id,
        )

        decision = result["decision"]
        policy = result["policy"]
        execution = result["execution"]
        recovery = result["recovery"]

        processed_results.append({
            "case_id": case_id,
            "event_id": ev["event_id"],
            "event_type": ev["event_type"],
            "amount_at_risk": ev["amount"],
            "decision": decision["decision"],
            "action": decision["final_action"],
            "confidence": decision["confidence"],
            "expected_recovery": decision["expected_recovery"],
            "policy_allowed": policy["allowed"],
            "risk_level": policy["risk_level"],
            "requires_human": policy["requires_human"] or execution["requires_human"],
            "execution_status": execution["status"],
            "outcome": execution["outcome"],
            "recovered_amount": execution["recovered_amount"],
            "remaining_amount": execution["remaining_amount"],
            "message": execution["message"],
            "timestamp": recovery.get("timestamp"),
        })

    return {
        "batch_id": request.batch_id,
        "processed_count": len(processed_results),
        "results": processed_results,
    }


@router.get("/policies")
def get_policies_config():
    """
    Expose the active PolicyEngine rules, limits, and safety boundaries.
    """
    return {
        "max_automation_amount": vaidya.policy_engine.MAX_AUTOMATION_AMOUNT,
        "min_automation_confidence": vaidya.policy_engine.MIN_AUTOMATION_CONFIDENCE,
        "supported_event_types": list(vaidya.policy_engine.SUPPORTED_EVENT_TYPES),
        "allowed_actions": {
            "payment_failure": list(vaidya.policy_engine.PAYMENT_ACTIONS),
            "checkout_abandonment": list(vaidya.policy_engine.CHECKOUT_ACTIONS),
            "overdue_invoice": list(vaidya.policy_engine.INVOICE_ACTIONS),
        },
        "fraud_policy": {
            "rule": "Zero-tolerance fraud safety boundary",
            "action": "block_and_escalate",
            "allowed": False,
            "expected_recovery": 0.0,
            "risk_level": "critical",
            "requires_human": True,
            "description": "Any transaction flagged with fraud_risk is prohibited from automated recovery. The token is locked and the case is escalated to security operations.",
        },
        "high_value_policy": {
            "rule": "High-value human approval threshold",
            "threshold": 100000.0,
            "action": "human_review",
            "description": "Any revenue recovery case exceeding ₹1,00,000 requires explicit human manager approval prior to execution.",
        },
    }


@router.get("/system-status")
def get_system_status():
    """
    Expose operational telemetry across all Vaidya subsystems.
    """
    corpus_size = len(vaidya.decision_engine.retrieval_service.cases)
    records_count = len(vaidya.recovery_tracker.records)

    return {
        "api": {
            "name": "Vaidya Core API",
            "status": "nominal",
            "version": "0.1.0",
        },
        "decision_engine": {
            "name": "Deterministic Decision Engine",
            "status": "nominal",
            "initialized": True,
            "action_spaces_count": 3,
        },
        "retrieval_service": {
            "name": "Historical Retrieval Corpus",
            "status": "nominal",
            "corpus_size": corpus_size,
            "similarity_threshold": vaidya.decision_engine.MINIMUM_SIMILARITY,
            "storage_file": "historical_recovery_cases.csv",
        },
        "policy_engine": {
            "name": "Policy Engine & Safety Gating",
            "status": "nominal",
            "max_automation_amount": vaidya.policy_engine.MAX_AUTOMATION_AMOUNT,
            "min_confidence": vaidya.policy_engine.MIN_AUTOMATION_CONFIDENCE,
        },
        "execution_service": {
            "name": "Recovery Execution Service",
            "status": "nominal",
            "mode": "prototype_simulation",
            "live_payment_gateway": "simulated_sandbox",
        },
        "recovery_tracker": {
            "name": "Recovery Ledger & Persistence",
            "status": "nominal",
            "persisted_records_count": records_count,
            "storage_file": str(vaidya.recovery_tracker.storage_path.name),
        },
    }