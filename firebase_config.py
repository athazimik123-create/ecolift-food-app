# ============================================================
# firebase_config.py — EcoLift Firebase Integration Module
# ============================================================
# Initializes Firebase Admin SDK (Firestore, Auth, Storage)
# and exposes helper CRUD functions used across all pages.
#
# SETUP:
#   1. Download your serviceAccountKey.json from Firebase Console
#      → Project Settings → Service Accounts → Generate new private key
#   2. Place serviceAccountKey.json in the project root
#   3. Fill in .env with your project credentials
# ============================================================

import os
import json
import uuid
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────
load_dotenv()

SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
PROJECT_ID           = os.getenv("FIREBASE_PROJECT_ID", "ecolift-demo")
STORAGE_BUCKET       = os.getenv("FIREBASE_STORAGE_BUCKET", "ecolift-demo.appspot.com")
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "DEMO_KEY")

# ── Firebase Initialization (singleton guard) ─────────────────
def _init_firebase() -> None:
    """
    Initializes the Firebase Admin SDK exactly once.
    Falls back to a mock mode if serviceAccountKey.json is not present,
    so the UI remains runnable for development/demo without real credentials.
    """
    if firebase_admin._apps:
        return  # Already initialized

    if os.path.exists(SERVICE_ACCOUNT_PATH):
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            "storageBucket": STORAGE_BUCKET,
            "projectId":     PROJECT_ID,
        })
        print("[Firebase] Initialized with service account.")
    else:
        # ── DEMO / MOCK MODE ─────────────────────────────────
        # When no credentials are present, the app operates on in-memory
        # mock data. Replace with real credentials for production.
        print("[Firebase] serviceAccountKey.json not found — running in MOCK MODE.")


_init_firebase()

# ── Client handles (available after init) ────────────────────
def get_db():
    """Returns the Firestore client. Returns None in mock mode."""
    try:
        return firestore.client()
    except Exception:
        return None


def get_auth():
    """Returns the Firebase Auth client. Returns None in mock mode."""
    try:
        return auth
    except Exception:
        return None


def get_storage():
    """Returns the Firebase Storage bucket handle. Returns None in mock mode."""
    try:
        return storage.bucket()
    except Exception:
        return None


db = get_db()


# ════════════════════════════════════════════════════════════
# ── AUTH HELPERS ─────────────────────────────────────────────
# Firebase Admin SDK is server-side only; client auth uses
# the Firebase Auth REST API (returns idToken stored in session).
# ════════════════════════════════════════════════════════════

import requests as _requests

FIREBASE_AUTH_SIGN_IN_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    "?key={api_key}"
)
FIREBASE_AUTH_SIGN_UP_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    "?key={api_key}"
)


def sign_in_with_email_password(email: str, password: str) -> dict:
    """
    Authenticates a user via Firebase Auth REST API.

    Returns:
        dict with keys: idToken, localId, email, error (on failure)
    """
    if FIREBASE_WEB_API_KEY == "DEMO_KEY":
        # ── MOCK AUTH ────────────────────────────────────────
        # Returns a fake session so the UI works without Firebase.
        mock_users = {
            "admin@ecolift.com":    {"role": "admin",     "name": "Alex Admin"},
            "donor@ecolift.com":    {"role": "donor",     "name": "Diana Donor"},
            "receiver@ecolift.com": {"role": "receiver",  "name": "Rachel Receiver"},
            "logistics@ecolift.com":{"role": "logistics", "name": "Leo Logistics"},
        }
        if email in mock_users and password == "demo1234":
            fake_uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
            return {
                "idToken": f"MOCK_TOKEN_{fake_uid}",
                "localId": fake_uid,
                "email":   email,
                "role":    mock_users[email]["role"],
                "name":    mock_users[email]["name"],
            }
        return {"error": "Invalid email or password (mock mode: use demo1234)"}

    # ── LIVE Firebase REST call ──────────────────────────────
    # REPLACE NOTHING — this is the production path.
    try:
        resp = _requests.post(
            FIREBASE_AUTH_SIGN_IN_URL.format(api_key=FIREBASE_WEB_API_KEY),
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10,
        )
        data = resp.json()
        if "idToken" not in data:
            return {"error": data.get("error", {}).get("message", "Authentication failed")}

        # Fetch role from Firestore users collection
        user_doc = get_user(data["localId"])
        data["role"] = user_doc.get("role", "receiver") if user_doc else "receiver"
        data["name"] = user_doc.get("name", email.split("@")[0]) if user_doc else email.split("@")[0]
        return data
    except Exception as e:
        return {"error": str(e)}


def sign_up_with_email_password(email: str, password: str, name: str, role: str) -> dict:
    """
    Registers a new user via Firebase Auth REST API, then stores
    their profile in Firestore users/{uid}.
    """
    if FIREBASE_WEB_API_KEY == "DEMO_KEY":
        return {"error": "Sign-up requires real Firebase credentials. Running in mock mode."}

    try:
        resp = _requests.post(
            FIREBASE_AUTH_SIGN_UP_URL.format(api_key=FIREBASE_WEB_API_KEY),
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10,
        )
        data = resp.json()
        if "idToken" not in data:
            return {"error": data.get("error", {}).get("message", "Registration failed")}

        uid = data["localId"]
        # Write initial user profile to Firestore
        create_user_profile(uid, {
            "uid":               uid,
            "role":              role,
            "name":              name,
            "email":             email,
            "subscription_tier": "basic",
            "stripe_customer_id": None,
            "location_geo":      None,
            "created_at":        datetime.now(timezone.utc),
        })
        data["role"] = role
        data["name"] = name
        return data
    except Exception as e:
        return {"error": str(e)}


def verify_id_token(id_token: str) -> dict | None:
    """
    Server-side token verification using Firebase Admin SDK.
    Returns decoded claims dict or None if invalid/mock.
    """
    if id_token.startswith("MOCK_TOKEN_"):
        return {"uid": id_token.replace("MOCK_TOKEN_", ""), "mock": True}
    try:
        return auth.verify_id_token(id_token)
    except Exception:
        return None


# ════════════════════════════════════════════════════════════
# ── USERS COLLECTION ─────────────────────────────────────────
# ════════════════════════════════════════════════════════════

def create_user_profile(uid: str, profile: dict) -> None:
    """Creates or overwrites a user profile document in Firestore."""
    if db:
        db.collection("users").document(uid).set(profile)


def get_user(uid: str) -> dict | None:
    """Fetches a single user profile by UID. Returns None if not found."""
    if db:
        doc = db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    # Mock fallback
    return _MOCK_USERS.get(uid)


def update_user_subscription(uid: str, tier: str) -> None:
    """Updates a user's subscription tier (basic | pro)."""
    if db:
        db.collection("users").document(uid).update({"subscription_tier": tier})


# ════════════════════════════════════════════════════════════
# ── PREDICTIONS COLLECTION ───────────────────────────────────
# ════════════════════════════════════════════════════════════

def save_prediction(prediction_data: dict) -> str:
    """
    Saves a raw waste prediction from the external system to Firestore.

    Args:
        prediction_data: dict in the format returned by waste_api.fetch_waste_predictions()

    Returns:
        prediction_id (str)
    """
    prediction_id = str(uuid.uuid4())
    doc = {
        "prediction_id":         prediction_id,
        "source_system_id":      prediction_data.get("location_id"),
        "waste_data": {
            "location_id":           prediction_data.get("location_id"),
            "business_name":         prediction_data.get("business_name"),
            "predicted_waste_kg":    prediction_data.get("predicted_waste_kg"),
            "food_type":             prediction_data.get("food_type"),
            "prediction_timestamp":  prediction_data.get("prediction_timestamp"),
        },
        "confidence":            prediction_data.get("confidence_score", 0.0),
        "is_converted_to_rescue": False,
        "created_at":            datetime.now(timezone.utc),
    }
    if db:
        db.collection("predictions").document(prediction_id).set(doc)
    return prediction_id


def get_predictions(limit: int = 20) -> list[dict]:
    """Returns the most recent predictions, sorted by created_at descending."""
    if db:
        # Single collection scan — order_by on a single field is fine
        # (Firestore auto-indexes created_at).
        docs = (
            db.collection("predictions")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [d.to_dict() for d in docs]
    return _MOCK_PREDICTIONS


# ════════════════════════════════════════════════════════════
# ── RESCUES COLLECTION ───────────────────────────────────────
# ════════════════════════════════════════════════════════════

def create_rescue(donor_id: str, prediction_data: dict) -> str:
    """
    Converts an accepted prediction into a live rescue listing.

    Args:
        donor_id: UID of the accepting donor
        prediction_data: original prediction dict

    Returns:
        rescue_id (str)
    """
    rescue_id = str(uuid.uuid4())
    doc = {
        "rescue_id":               rescue_id,
        "donor_id":                donor_id,
        "receiver_id":             None,
        "logistics_partner_id":    None,
        "status":                  "pending",
        "food_details": {
            "type":        prediction_data.get("food_type", "Mixed"),
            "description": f"Surplus from {prediction_data.get('business_name', 'Unknown')}",
            "quantity_kg": prediction_data.get("predicted_waste_kg", 0),
            "expiry_dt":   None,
        },
        "predicted_vs_actual_kg": {
            "predicted": prediction_data.get("predicted_waste_kg", 0),
            "actual":    None,
        },
        "premium_delivery":   False,
        "revenue_generated":  0.0,
        "business_name":      prediction_data.get("business_name", "Unknown"),
        "confidence_score":   prediction_data.get("confidence_score", 0),
        "created_at":         datetime.now(timezone.utc),
    }
    if db:
        db.collection("rescues").document(rescue_id).set(doc)
    else:
        # Store in in-memory mock store for demo
        _MOCK_RESCUES.append(doc)
    return rescue_id


def get_active_rescues(limit: int = 50) -> list[dict]:
    """Returns all rescues with status 'pending' or 'accepted'."""
    if db:
        # order_by removed to avoid composite index requirement.
        # Firestore requires a composite index when combining where()+order_by().
        # We sort in Python instead after fetching.
        docs = (
            db.collection("rescues")
            .where("status", "in", ["pending", "accepted"])
            .limit(limit)
            .stream()
        )
        results = [d.to_dict() for d in docs]
        # Sort by created_at descending in Python
        results.sort(key=lambda r: r.get("created_at") or "", reverse=True)
        return results
    return [r for r in _MOCK_RESCUES if r["status"] in ("pending", "accepted")]


def claim_rescue(rescue_id: str, receiver_id: str, premium: bool = False) -> None:
    """Marks a rescue as claimed by a receiver."""
    update = {
        "receiver_id":      receiver_id,
        "status":           "accepted",
        "premium_delivery": premium,
        "revenue_generated": 4.99 if premium else 0.0,
        "claimed_at":       datetime.now(timezone.utc),
    }
    if db:
        db.collection("rescues").document(rescue_id).update(update)
    else:
        for r in _MOCK_RESCUES:
            if r["rescue_id"] == rescue_id:
                r.update(update)
                break


def get_donor_rescues(donor_id: str) -> list[dict]:
    """Returns all rescues created by a specific donor."""
    if db:
        # Single-field where() — no composite index needed.
        # Firestore auto-indexes single fields; order_by on a different
        # field would require a composite index, so we sort in Python.
        docs = (
            db.collection("rescues")
            .where("donor_id", "==", donor_id)
            .stream()
        )
        results = [d.to_dict() for d in docs]
        results.sort(key=lambda r: r.get("created_at") or "", reverse=True)
        return results
    return [r for r in _MOCK_RESCUES if r.get("donor_id") == donor_id]


# ════════════════════════════════════════════════════════════
# ── TRANSACTIONS COLLECTION ──────────────────────────────────
# ════════════════════════════════════════════════════════════

def log_transaction(user_id: str, amount: float, tx_type: str, metadata: dict = None) -> str:
    """
    Logs a financial transaction to Firestore.

    tx_type options: 'subscription' | 'logistics_fee' | 'csr_credit'
    """
    tx_id = str(uuid.uuid4())
    doc = {
        "transaction_id": tx_id,
        "user_id":        user_id,
        "amount":         amount,
        "type":           tx_type,
        "metadata":       metadata or {},
        "timestamp":      datetime.now(timezone.utc),
    }
    if db:
        db.collection("transactions").document(tx_id).set(doc)
    else:
        _MOCK_TRANSACTIONS.append(doc)
    return tx_id


def get_all_transactions(limit: int = 200) -> list[dict]:
    """Returns recent transactions (admin use)."""
    if db:
        # Single collection scan with single-field order — no composite index needed.
        docs = (
            db.collection("transactions")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [d.to_dict() for d in docs]
    return _MOCK_TRANSACTIONS


# ════════════════════════════════════════════════════════════
# ── CSR SPONSORS COLLECTION ──────────────────────────────────
# ════════════════════════════════════════════════════════════

def create_csr_sponsor(data: dict) -> str:
    """Creates a new CSR sponsor record."""
    sponsor_id = str(uuid.uuid4())
    doc = {
        "sponsor_id":       sponsor_id,
        "company_name":     data.get("company_name"),
        "credits_purchased": data.get("credits_purchased", 0),
        "credits_used":     0,
        "logo_url":         data.get("logo_url", ""),
        "contact_email":    data.get("contact_email", ""),
        "created_at":       datetime.now(timezone.utc),
    }
    if db:
        db.collection("csr_sponsors").document(sponsor_id).set(doc)
    else:
        _MOCK_SPONSORS.append(doc)
    return sponsor_id


def get_csr_sponsors(limit: int = 20) -> list[dict]:
    """Returns all CSR sponsors sorted by credits_purchased descending."""
    if db:
        # Fetch all and sort in Python to avoid index requirements.
        docs = db.collection("csr_sponsors").limit(limit).stream()
        results = [d.to_dict() for d in docs]
        results.sort(key=lambda x: x.get("credits_purchased", 0), reverse=True)
        return results
    return sorted(_MOCK_SPONSORS, key=lambda x: x["credits_purchased"], reverse=True)


def get_revenue_stats() -> dict:
    """
    Aggregates revenue statistics for the Admin dashboard.
    In production this would use Firestore aggregation queries.
    """
    if db:
        txs = get_all_transactions(500)
    else:
        txs = _MOCK_TRANSACTIONS

    subscription_revenue = sum(t["amount"] for t in txs if t["type"] == "subscription")
    logistics_revenue    = sum(t["amount"] for t in txs if t["type"] == "logistics_fee")
    csr_revenue          = sum(t["amount"] for t in txs if t["type"] == "csr_credit")
    total_rescues        = len(get_active_rescues(200))

    return {
        "mrr":                subscription_revenue,
        "logistics_revenue":  logistics_revenue,
        "csr_revenue":        csr_revenue,
        "total_revenue":      subscription_revenue + logistics_revenue + csr_revenue,
        "total_rescues":      total_rescues,
        "meals_rescued":      int(total_rescues * 8.3),   # ~8.3 meals per kg average
        "co2_offset_kg":      round(total_rescues * 2.5, 1),
    }


# ════════════════════════════════════════════════════════════
# ── IN-MEMORY MOCK DATA STORE (used when Firebase not configured)
# ════════════════════════════════════════════════════════════
import uuid as _uuid
from datetime import timedelta

def _make_uid(email): return str(_uuid.uuid5(_uuid.NAMESPACE_DNS, email))

_MOCK_USERS = {
    _make_uid("admin@ecolift.com"):    {"uid": _make_uid("admin@ecolift.com"),    "role": "admin",     "name": "Alex Admin",      "email": "admin@ecolift.com",    "subscription_tier": "pro"},
    _make_uid("donor@ecolift.com"):    {"uid": _make_uid("donor@ecolift.com"),    "role": "donor",     "name": "Diana Donor",     "email": "donor@ecolift.com",    "subscription_tier": "basic"},
    _make_uid("receiver@ecolift.com"): {"uid": _make_uid("receiver@ecolift.com"), "role": "receiver",  "name": "Rachel Receiver", "email": "receiver@ecolift.com", "subscription_tier": "basic"},
    _make_uid("logistics@ecolift.com"):{"uid": _make_uid("logistics@ecolift.com"),"role": "logistics", "name": "Leo Logistics",   "email": "logistics@ecolift.com","subscription_tier": "basic"},
}

_now = datetime.now(timezone.utc)

_MOCK_PREDICTIONS = [
    {"prediction_id": "pred-001", "source_system_id": "LOC-101", "waste_data": {"location_id": "LOC-101", "business_name": "Pizza Palace",    "predicted_waste_kg": 15.5, "food_type": "Perishable/Bakery",  "prediction_timestamp": (_now - timedelta(hours=1)).isoformat()}, "confidence": 0.92, "is_converted_to_rescue": False, "created_at": _now - timedelta(hours=1)},
    {"prediction_id": "pred-002", "source_system_id": "LOC-102", "waste_data": {"location_id": "LOC-102", "business_name": "Green Grocers",   "predicted_waste_kg": 22.0, "food_type": "Produce/Vegetables","prediction_timestamp": (_now - timedelta(hours=2)).isoformat()}, "confidence": 0.88, "is_converted_to_rescue": False, "created_at": _now - timedelta(hours=2)},
    {"prediction_id": "pred-003", "source_system_id": "LOC-103", "waste_data": {"location_id": "LOC-103", "business_name": "Sunrise Bakery",  "predicted_waste_kg":  8.3, "food_type": "Bakery/Pastry",    "prediction_timestamp": (_now - timedelta(hours=3)).isoformat()}, "confidence": 0.95, "is_converted_to_rescue": True,  "created_at": _now - timedelta(hours=3)},
    {"prediction_id": "pred-004", "source_system_id": "LOC-104", "waste_data": {"location_id": "LOC-104", "business_name": "Harbor Caterers", "predicted_waste_kg": 31.0, "food_type": "Prepared Meals",   "prediction_timestamp": (_now - timedelta(minutes=30)).isoformat()}, "confidence": 0.91, "is_converted_to_rescue": False, "created_at": _now - timedelta(minutes=30)},
    {"prediction_id": "pred-005", "source_system_id": "LOC-105", "waste_data": {"location_id": "LOC-105", "business_name": "Metro Supermart", "predicted_waste_kg": 45.0, "food_type": "Dairy/Packaged",   "prediction_timestamp": (_now - timedelta(minutes=10)).isoformat()}, "confidence": 0.87, "is_converted_to_rescue": False, "created_at": _now - timedelta(minutes=10)},
]

_MOCK_RESCUES = [
    {"rescue_id": "res-001", "donor_id": _make_uid("donor@ecolift.com"), "receiver_id": None,  "status": "pending",   "food_details": {"type": "Bakery/Pastry",     "description": "Surplus from Sunrise Bakery",  "quantity_kg": 8.3},  "business_name": "Sunrise Bakery",  "confidence_score": 0.95, "premium_delivery": False, "revenue_generated": 0.0,  "created_at": _now - timedelta(hours=3)},
    {"rescue_id": "res-002", "donor_id": _make_uid("donor@ecolift.com"), "receiver_id": None,  "status": "pending",   "food_details": {"type": "Produce/Vegetables","description": "Surplus from Green Grocers",   "quantity_kg": 22.0}, "business_name": "Green Grocers",   "confidence_score": 0.88, "premium_delivery": False, "revenue_generated": 0.0,  "created_at": _now - timedelta(hours=2)},
    {"rescue_id": "res-003", "donor_id": _make_uid("donor@ecolift.com"), "receiver_id": _make_uid("receiver@ecolift.com"), "status": "accepted", "food_details": {"type": "Prepared Meals",  "description": "Surplus from Harbor Caterers","quantity_kg": 31.0}, "business_name": "Harbor Caterers","confidence_score": 0.91, "premium_delivery": True,  "revenue_generated": 4.99, "created_at": _now - timedelta(hours=1)},
    {"rescue_id": "res-004", "donor_id": _make_uid("donor@ecolift.com"), "receiver_id": None,  "status": "pending",   "food_details": {"type": "Dairy/Packaged",    "description": "Surplus from Metro Supermart", "quantity_kg": 45.0}, "business_name": "Metro Supermart", "confidence_score": 0.87, "premium_delivery": False, "revenue_generated": 0.0,  "created_at": _now - timedelta(minutes=10)},
]

_MOCK_TRANSACTIONS = [
    {"transaction_id": "tx-001", "user_id": _make_uid("donor@ecolift.com"),    "amount": 29.0,  "type": "subscription",  "metadata": {"tier": "pro"},         "timestamp": _now - timedelta(days=30)},
    {"transaction_id": "tx-002", "user_id": _make_uid("receiver@ecolift.com"), "amount":  4.99, "type": "logistics_fee", "metadata": {"rescue_id": "res-003"}, "timestamp": _now - timedelta(hours=1)},
    {"transaction_id": "tx-003", "user_id": "csr-sponsor-001",                 "amount": 500.0, "type": "csr_credit",    "metadata": {"credits": 5000},        "timestamp": _now - timedelta(days=5)},
    {"transaction_id": "tx-004", "user_id": _make_uid("donor@ecolift.com"),    "amount": 29.0,  "type": "subscription",  "metadata": {"tier": "pro"},         "timestamp": _now - timedelta(days=60)},
    {"transaction_id": "tx-005", "user_id": "csr-sponsor-002",                 "amount": 200.0, "type": "csr_credit",    "metadata": {"credits": 2000},        "timestamp": _now - timedelta(days=2)},
    {"transaction_id": "tx-006", "user_id": _make_uid("receiver@ecolift.com"), "amount":  4.99, "type": "logistics_fee", "metadata": {"rescue_id": "res-002"}, "timestamp": _now - timedelta(days=1)},
]

_MOCK_SPONSORS = [
    {"sponsor_id": "csr-001", "company_name": "GreenTech Corp",    "credits_purchased": 5000, "credits_used": 1200, "logo_url": "", "contact_email": "esg@greentech.com",   "created_at": _now - timedelta(days=5)},
    {"sponsor_id": "csr-002", "company_name": "NexaBank",          "credits_purchased": 2000, "credits_used":  800, "logo_url": "", "contact_email": "csr@nexabank.com",     "created_at": _now - timedelta(days=2)},
    {"sponsor_id": "csr-003", "company_name": "EarthFirst Foods",  "credits_purchased":  800, "credits_used":  200, "logo_url": "", "contact_email": "impact@earthfirst.io","created_at": _now - timedelta(days=10)},
]
