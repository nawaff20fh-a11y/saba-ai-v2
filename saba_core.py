from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).resolve().parent / "saba_behavior_model.pkl"

FEATURE_COLUMNS = [
    "session_minute",
    "task_difficulty",
    "sleep_quality",
    "hunger_level",
    "sensory_load",
    "preferred_items_available",
    "refusal_count",
    "leaving_seat_count",
]

SELECT_OPTIONS = {
    "task_difficulty": {
        1: "منخفضة",
        2: "متوسطة",
        3: "مرتفعة",
    },
    "hunger_level": {
        1: "منخفض",
        2: "متوسط",
        3: "مرتفع",
    },
    "sleep_quality": {
        1: "جيدة",
        2: "متوسطة",
        3: "ضعيفة",
    },
    "sensory_load": {
        1: "منخفض",
        2: "متوسط",
        3: "مرتفع",
    },
    "preferred_items_available": {
        1: "متوفر",
        2: "متوسط",
        3: "ضعيف",
    },
}

FIELD_LABELS = {
    "session_minute": "مدة العمل بالدقائق",
    "task_difficulty": "صعوبة المهمة",
    "sleep_quality": "جودة النوم",
    "hunger_level": "مستوى الجوع",
    "sensory_load": "الضغط الحسي",
    "preferred_items_available": "توفر المعززات",
    "refusal_count": "عدد مرات الرفض",
    "leaving_seat_count": "عدد مرات ترك الكرسي",
}

DECISION_CONFIG = {
    "give_break": {
        "title": "إعطاء استراحة",
        "recommendation": "يوصى بإعطاء بريك قصير ثم العودة للمهمة بشكل تدريجي.",
        "tone": "error",
    },
    "change_activity": {
        "title": "تعديل النشاط",
        "recommendation": "يوصى بتعديل النشاط أو تقليل صعوبته واستخدام معزز مناسب.",
        "tone": "warning",
    },
    "continue_session": {
        "title": "استمرار الجلسة",
        "recommendation": "يمكن الاستمرار في الجلسة مع مراقبة المؤشرات السلوكية.",
        "tone": "success",
    },
}


def load_model():
    return joblib.load(MODEL_PATH)


def build_input_frame(payload):
    normalized_payload = {column: int(payload.get(column, 0)) for column in FEATURE_COLUMNS}
    return pd.DataFrame([normalized_payload], columns=FEATURE_COLUMNS)


def build_reason_text(payload):
    reasons = []

    if payload["refusal_count"] >= 3:
        reasons.append("ارتفاع عدد مرات الرفض")
    if payload["leaving_seat_count"] >= 2:
        reasons.append("زيادة ترك الكرسي أو الحركة")
    if payload["task_difficulty"] >= 3:
        reasons.append("صعوبة المهمة مرتفعة")
    if payload["hunger_level"] >= 3:
        reasons.append("مستوى الجوع مرتفع")
    if payload["sensory_load"] >= 3:
        reasons.append("الضغط الحسي مرتفع")
    if payload["sleep_quality"] >= 3:
        reasons.append("جودة النوم ضعيفة")
    if payload["preferred_items_available"] >= 3:
        reasons.append("المعززات ضعيفة أو غير كافية")

    return " + ".join(reasons) if reasons else "المؤشرات الحالية مستقرة"


def analyze_session(payload, model=None):
    model = model or load_model()
    input_data = build_input_frame(payload)

    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    confidence = round(max(probabilities) * 100, 1)

    decision_key = prediction if prediction in DECISION_CONFIG else "continue_session"
    decision_meta = DECISION_CONFIG[decision_key]

    return {
        "decision": decision_key,
        "decision_title": decision_meta["title"],
        "recommendation": decision_meta["recommendation"],
        "tone": decision_meta["tone"],
        "confidence": confidence,
        "reason": build_reason_text(payload),
        "input_data": input_data,
    }
