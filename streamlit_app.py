import streamlit as st

from saba_core import FIELD_LABELS, SELECT_OPTIONS, analyze_session, load_model


st.set_page_config(page_title="SABA", page_icon="🧠", layout="centered")


@st.cache_resource
def get_model():
    return load_model()


def render_select(field_name, default=1):
    options = list(SELECT_OPTIONS[field_name].keys())
    default_index = options.index(default)
    return st.selectbox(
        FIELD_LABELS[field_name],
        options=options,
        index=default_index,
        format_func=lambda value: SELECT_OPTIONS[field_name][value],
    )


def result_color(decision_key):
    if decision_key == "give_break":
        return "#dc2626"
    if decision_key == "change_activity":
        return "#f59e0b"
    return "#16a34a"


st.markdown(
    """
    <style>
    .stApp {
        background: #f4f7fb;
        color: #111827;
    }
    .block-container {
        max-width: 440px;
        padding-top: 1.4rem;
        padding-bottom: 1.6rem;
    }
    h1, h2, h3, p, label {
        direction: rtl;
    }
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label {
        color: #64748b;
        font-size: 13px;
        font-weight: 400;
    }
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        min-height: 52px;
    }
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: #2563eb;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.08);
    }
    div.stButton > button {
        width: 100%;
        border: none;
        min-height: 54px;
        border-radius: 18px;
        background: #2563eb;
        color: white;
        font-size: 16px;
        font-weight: 700;
    }
    div.stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }
    .top {
        background: linear-gradient(135deg, #0f172a, #1e40af);
        color: white;
        padding: 26px;
        border-radius: 28px;
        margin-bottom: 22px;
        box-shadow: 0 18px 40px rgba(30,64,175,0.25);
    }
    .brand {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }
    .logo {
        font-size: 26px;
        font-weight: 800;
    }
    .ai-badge {
        background: rgba(255,255,255,0.18);
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 13px;
    }
    .top h2 {
        margin: 22px 0 8px;
        font-size: 22px;
        color: white;
    }
    .top p {
        margin: 0;
        color: #dbeafe;
        font-size: 14px;
        line-height: 1.7;
    }
    .card, .result-card {
        background: white;
        border-radius: 26px;
        padding: 22px;
        box-shadow: 0 14px 35px rgba(15,23,42,0.08);
        margin-bottom: 18px;
    }
    .section-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 18px;
        direction: rtl;
    }
    .status-label {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 8px;
        text-align: center;
    }
    .decision-title {
        font-size: 28px;
        font-weight: 800;
        margin: 8px 0 16px;
        text-align: center;
    }
    .info-box {
        margin-top: 14px;
        background: #f8fafc;
        padding: 14px;
        border-radius: 18px;
        text-align: right;
        color: #475569;
        line-height: 1.7;
        font-size: 14px;
    }
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        margin-top: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="top" dir="rtl">
      <div class="brand">
        <div class="logo">SABA</div>
        <div class="ai-badge">AI Model Active</div>
      </div>
      <h2>Smart ABA Assistant</h2>
      <p>نظام ذكي يساعد الأخصائي على تحليل بيانات الجلسة واقتراح القرار المناسب.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

model = get_model()

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">بيانات الجلسة</div>', unsafe_allow_html=True)

    session_minute = st.number_input(FIELD_LABELS["session_minute"], min_value=0, value=10, step=1)
    refusal_count = st.number_input(FIELD_LABELS["refusal_count"], min_value=0, value=0, step=1)
    leaving_seat_count = st.number_input(FIELD_LABELS["leaving_seat_count"], min_value=0, value=0, step=1)
    task_difficulty = render_select("task_difficulty", default=2)
    hunger_level = render_select("hunger_level", default=1)
    sleep_quality = render_select("sleep_quality", default=1)
    sensory_load = render_select("sensory_load", default=1)
    preferred_items_available = render_select("preferred_items_available", default=1)

    analyze_clicked = st.button("تحليل الحالة", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

payload = {
    "session_minute": session_minute,
    "task_difficulty": task_difficulty,
    "sleep_quality": sleep_quality,
    "hunger_level": hunger_level,
    "sensory_load": sensory_load,
    "preferred_items_available": preferred_items_available,
    "refusal_count": refusal_count,
    "leaving_seat_count": leaving_seat_count,
}

if analyze_clicked:
    st.session_state["latest_result"] = analyze_session(payload, model=model)

latest_result = st.session_state.get("latest_result")

decision_title = "—"
decision_reason = "أدخل بيانات الجلسة ثم اضغط تحليل الحالة."
decision_recommendation = "—"
bar_color = "#2563eb"

if latest_result:
    decision_title = latest_result["decision_title"]
    decision_reason = latest_result["reason"]
    decision_recommendation = latest_result["recommendation"]
    bar_color = result_color(latest_result["decision"])

st.markdown('<div class="result-card" dir="rtl">', unsafe_allow_html=True)
st.markdown('<div class="status-label">القرار المقترح</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="decision-title" style="color:{bar_color};">{decision_title}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="info-box">
      <b>سبب القرار:</b>
      <div>{decision_reason}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="info-box">
      <b>التوصية:</b>
      <div>{decision_recommendation}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">SABA Prototype — AI Decision Support</div>', unsafe_allow_html=True)
