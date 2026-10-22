import base64
import os
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Financial Health Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Background Image and Styling Configuration
# ------------------------------------------------------------------
APP_DIR = Path(__file__).parent
bg_layers = "linear-gradient(160deg, #061e26, #0f6b52)"
for name, mime in [
    ("bg_image.png", "image/png"),
    ("bg_image.jpg", "image/jpeg"),
    ("bg_image.jpeg", "image/jpeg"),
]:
  f = APP_DIR / name
  if f.exists():
    b64 = base64.b64encode(f.read_bytes()).decode()
    bg_layers = (
        "linear-gradient(100deg, rgba(4,22,30,0.80) 0%,"
        " rgba(4,22,30,0.55) 55%, rgba(4,22,30,0.40) 100%), "
        f"url('data:{mime};base64,{b64}')"
    )
    break

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

.stApp {
    background-color: #061e26;
    background-image: __BG__;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    font-family: 'DM Sans', sans-serif;
}
header[data-testid="stHeader"], div[data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
.block-container { max-width: 1240px; padding-top: 3rem; padding-bottom: 6rem; }

/* ---------- Hero ---------- */
.hero h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700;
    font-size: 4.2rem;
    line-height: 1.08;
    letter-spacing: -1px;
    color: #ffffff !important;
    margin: 18px 0 20px 0;
    text-shadow: 0 4px 30px rgba(0,0,0,0.55);
}
.hero .rule { width: 90px; height: 4px; border-radius: 4px; background: #f0cf7a; margin-bottom: 22px; }
.hero p {
    font-size: 1.35rem;
    line-height: 1.6;
    color: #e6fff3 !important;
    max-width: 500px;
    margin: 0;
    text-shadow: 0 2px 14px rgba(0,0,0,0.7);
}

/* ---------- Glass Container & Forms ---------- */
div[data-testid="stForm"], div.glass-box {
    background: rgba(6,30,38,0.65);
    border: 1px solid rgba(255,255,255,0.22) !important;
    border-radius: 28px;
    padding: 32px 36px 24px 36px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 30px 80px rgba(0,0,0,0.45);
}
.form-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 4px 0;
}
.form-sub { font-size: 1.1rem; color: #b6e9d2; margin: 0 0 16px 0; }

div[data-testid="stWidgetLabel"] p, div[data-testid="stForm"] label p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: #f4fff9 !important;
}
div[data-baseweb="select"] > div, div[data-baseweb="input"] {
    min-height: 50px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.38);
    background: rgba(255,255,255,0.10);
}
div[data-baseweb="select"] *, div[data-testid="stNumberInput"] input {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff !important;
}
div[data-baseweb="select"] svg { fill: #f0cf7a; }
div[data-testid="stNumberInput"] input { background: transparent; }
div[data-testid="stNumberInput"] button { color: #f0cf7a; background: rgba(255,255,255,0.08); }

div[data-baseweb="slider"] div[role="slider"] {
    background-color: #f0cf7a !important;
    border: 3px solid #ffffff !important;
    height: 24px !important;
    width: 24px !important;
}
div[data-testid="stSliderThumbValue"], div[data-testid="stSliderThumbValue"] p {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #f0cf7a !important;
}
div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] { color: #b6e9d2 !important; font-size: 0.95rem; }

/* ---------- Gold Button ---------- */
.stButton > button, div[data-testid="stFormSubmitButton"] > button, div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #f8e19a 0%, #e0b24a 100%) !important;
    color: #1d1604 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 14px 30px !important;
    width: 100% !important;
    margin-top: 10px;
    box-shadow: 0 10px 25px rgba(224,178,74,0.35) !important;
    transition: transform .15s ease, filter .15s ease;
}
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover {
    filter: brightness(1.08);
    transform: translateY(-2px);
}

/* ---------- Results & Cards ---------- */
.result-wrap { display: grid; grid-template-columns: 0.9fr 1.2fr; gap: 24px; margin-top: 40px; }
.glass {
    background: rgba(6,30,38,0.66);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 28px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 30px 80px rgba(0,0,0,0.45);
}
.ring-card { padding: 30px; text-align: center; }
.ring-card .label { font-size: 1.25rem; font-weight: 600; color: #b6e9d2; margin-bottom: 4px; }
.ring-card svg { width: 100%; max-width: 240px; height: auto; }
.ring-num { font-family: 'Playfair Display', serif; font-size: 56px; font-weight: 800; fill: #f0cf7a; }
.ring-sub { font-family: 'DM Sans', sans-serif; font-size: 15px; font-weight: 600; fill: #8ff0c8; }
.ring-note { font-size: 1.1rem; font-weight: 600; color: #ffffff; margin-top: 2px; }

.verdict-card { padding: 32px 36px; border-left: 8px solid var(--tone); }
.verdict-card .head {
    font-family: 'Playfair Display', serif;
    font-size: 2.3rem;
    font-weight: 700;
    line-height: 1.1;
    color: var(--tone);
    margin-bottom: 10px;
}
.verdict-card .body { font-size: 1.2rem; line-height: 1.5; color: #ffffff; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }
.chip {
    font-size: 0.98rem;
    color: #e6fff3;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.28);
    border-radius: 999px;
    padding: 5px 14px;
}
.chip b { color: #f0cf7a; font-weight: 700; margin-left: 4px; }
.tone-low  { --tone: #ff9a62; }
.tone-high { --tone: #7be8b8; }

@media (max-width: 900px) {
    .hero h1 { font-size: 2.8rem; }
    .result-wrap { grid-template-columns: 1fr; }
}
</style>
"""
st.markdown(CSS.replace("__BG__", bg_layers), unsafe_allow_html=True)


def flat(html: str) -> str:
  return " ".join(line.strip() for line in html.splitlines() if line.strip())


# ------------------------------------------------------------------
# Load Model & Imputer Artifacts safely
# ------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
  root_dir = APP_DIR.parent
  # Look inside the 'models' folder
  model_path = root_dir / "models" / "financial_health_model.pkl"
  imputer_path = root_dir / "models" / "imputer.pkl"

  if os.path.exists(model_path) and os.path.exists(imputer_path):
    return joblib.load(model_path), joblib.load(imputer_path)
  return None, None


model, imputer = load_artifacts()
if model is None:
  st.error(
      "Could not find financial_model.pkl and imputer.pkl in the workspace"
      " root directory."
  )
  st.stop()

# ------------------------------------------------------------------
# Navigation Tabs (Main Analyzer vs. Scenario What-If Simulator)
# ------------------------------------------------------------------
tab_main, tab_simulator = st.tabs(
    [" Financial Health Assessment", " Scenario 'What-If' Simulator"]
)

with tab_main:
  left, right = st.columns([1, 1.1], gap="large")

  with left:
    st.markdown(
        flat("""
        <div class="hero">
            <h1>How healthy are your finances, really?</h1>
            <div class="rule"></div>
            <p>Evaluate your financial well-being score out of 100 using advanced machine learning, view algorithmic drivers, compare against benchmarks, and export your report.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )

  with right:
    with st.form("financial_form"):
      st.markdown(
          flat("""
            <div class="form-title">Your money habits</div>
            <div class="form-sub">Hover over fields for detailed indicator guidelines.</div>
            """),
          unsafe_allow_html=True,
      )

      savings_ranges = st.slider(
          "Savings level (1 = little/none, 5 = plenty)",
          1,
          5,
          3,
          help=(
              "Reflects your liquid savings capacity. Scale ranges from 1"
              " (virtually no emergency buffer) to 5 (robust liquid reserves)."
          ),
      )
      ends_meet = st.selectbox(
          "How hard is to cover monthly expenses?",
          [1, 2, 3, 4, 5],
          help=(
              "1 means very easy to cover monthly obligations; 5 indicates"
              " severe chronic difficulty meeting baseline bills."
          ),
      )
      absorb_shock = st.selectbox(
          "Could you absorb a surprise expense?",
          [1, 2, 3],
          help=(
              "1 = Low capacity to handle sudden financial emergencies, 3 ="
              " High financial resilience against sudden shocks."
          ),
      )
      collect = st.selectbox(
          "Debt or collections trouble",
          [1, 2],
          help=(
              "1 = Clean record with no active collection flags, 2 = Active"
              " debt/collection challenges."
          ),
      )
      volatility = st.selectbox(
          "How much do your income & spending swing?",
          [1, 2, 3],
          help=(
              "1 = Highly predictable/stable monthly cash flow, 3 = Extreme"
              " income or expense volatility."
          ),
      )
      earners = st.number_input(
          "Earners in your household",
          min_value=1,
          max_value=5,
          value=1,
          help=(
              "Total count of individuals actively contributing income to your"
              " household."
          ),
      )

      submit_button = st.form_submit_button("Calculate My Score ✨")

  # ------------------------------------------------------------------
  # Prediction & Results Display
  # ------------------------------------------------------------------
  if submit_button:
    user_input = pd.DataFrame(0, index=[0], columns=imputer.feature_names_in_)

    if "SAVINGSRANGES" in user_input.columns:
      user_input["SAVINGSRANGES"] = savings_ranges
    if "ENDSMEET" in user_input.columns:
      user_input["ENDSMEET"] = ends_meet
    if "ABSORBSHOCK" in user_input.columns:
      user_input["ABSORBSHOCK"] = absorb_shock
    if "COLLECT" in user_input.columns:
      user_input["COLLECT"] = collect
    if "VOLATILITY" in user_input.columns:
      user_input["VOLATILITY"] = volatility
    if "EARNERS" in user_input.columns:
      user_input["EARNERS"] = earners

    try:
      user_input_imputed = pd.DataFrame(
          imputer.transform(user_input), columns=user_input.columns
      )
      prediction = float(model.predict(user_input_imputed)[0])
    except Exception as e:
      st.error(f"Prediction calculation failed: {e}")
      st.stop()

    pct = max(3, min(100, prediction))
    circumference = 565.49
    arc = pct / 100 * circumference

    # Benchmark comparison metric calculation (assuming median survey baseline of 60.0)
    benchmark_baseline = 60.0
    delta_pts = prediction - benchmark_baseline
    benchmark_text = (
        f"{delta_pts:+.1f} pts vs National Survey Baseline (60.0)"
    )

    note = (
        "Above Halfway Threshold"
        if prediction >= 50
        else "Below Halfway Threshold"
    )

    if prediction < 50:
      tone, head = "tone-low", "Room to Grow"
      body = (
          "Your indicators point to active financial vulnerabilities. Prioritizing"
          " an emergency cushion and monitoring monthly cash flow swings will"
          " significantly strengthen your score."
      )
    else:
      tone, head = "tone-high", "You're in Great Shape"
      body = (
          "Your profile indicates solid financial resilience and reliable"
          " savings habits. Keep maintaining your safety buffer!"
      )

    answers = [
        ("Savings level", f"{savings_ranges}/5"),
        ("Monthly expenses", ends_meet),
        ("Surprise expense", absorb_shock),
        ("Debt trouble", collect),
        ("Income swings", volatility),
        ("Earners", earners),
    ]
    chips = "".join(
        f'<span class="chip">{k}<b>{v}</b></span>' for k, v in answers
    )

    st.markdown(
        flat(f"""
        <div class="result-wrap">
            <div class="glass ring-card">
                <div class="label">Financial Well-Being Score</div>
                <svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0" stop-color="#8ff0c8"/>
                            <stop offset="1" stop-color="#f0cf7a"/>
                        </linearGradient>
                    </defs>
                    <circle cx="110" cy="110" r="90" fill="none" stroke="rgba(255,255,255,0.16)" stroke-width="16"/>
                    <circle cx="110" cy="110" r="90" fill="none" stroke="url(#ringGrad)" stroke-width="16"
                            stroke-linecap="round" stroke-dasharray="{arc:.1f} {circumference}"
                            transform="rotate(-90 110 110)"/>
                    <text x="110" y="122" text-anchor="middle" class="ring-num">{prediction:.1f}</text>
                    <text x="110" y="150" text-anchor="middle" class="ring-sub">out of 100</text>
                </svg>
                <div class="ring-note">{note}</div>
                <div style="margin-top: 10px; font-size: 0.95rem; color: #f0cf7a; font-weight: 600;">{benchmark_text}</div>
            </div>
            <div class="glass verdict-card {tone}">
                <div class="head">{head}</div>
                <div class="body">{body}</div>
                <div class="chips">{chips}</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Feature Importance (Explainable AI) Section
    # ------------------------------------------------------------------
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Explainable AI: Model Feature Importances")
    st.write(
        "To demystify the machine learning black box, the chart below displays"
        " the relative weight and contribution of each financial feature"
        " driving your assigned prediction score."
    )

    if hasattr(model, "feature_importances_"):
      importances = pd.Series(
          model.feature_importances_, index=imputer.feature_names_in_
      )
      top_drivers = importances.nlargest(6)
      st.bar_chart(top_drivers, color="#f0cf7a")
    else:
      st.info("Feature importance metrics are unavailable for this estimator.")

    # ------------------------------------------------------------------
    # Downloadable Report Feature
    # ------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📥 Export Comprehensive Report")
    st.write(
        "Compile your input profiles, predicted wellness score, and benchmark"
        " performance into a downloadable documentation artifact."
    )

    report_df = pd.DataFrame({
        "Evaluation Metric": [
            "Savings Level Range",
            "Monthly Expense Difficulty",
            "Shock Absorption Capacity",
            "Collections/Debt Flag",
            "Cash Flow Volatility",
            "Household Earners Count",
            "Predicted FWB Score",
            "Benchmark Comparison Delta",
        ],
        "Recorded Input / Output": [
            savings_ranges,
            ends_meet,
            absorb_shock,
            collect,
            volatility,
            earners,
            f"{prediction:.1f} / 100",
            f"{delta_pts:+.1f} pts",
        ],
    })
    csv_bytes = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Financial Health Report (.CSV)",
        data=csv_bytes,
        file_name="financial_health_report.csv",
        mime="text/csv",
    )

# ------------------------------------------------------------------
# Scenario "What-If" Simulator Tab
# ------------------------------------------------------------------
with tab_simulator:
  st.markdown("## 🔮 Interactive Scenario 'What-If' Simulator")
  st.write(
      "Simulate future financial lifestyle changes. Adjust your parameters"
      " below to instantly preview how shifting your savings habits or expense"
      " management impacts your well-being score."
  )

  sim_col1, sim_col2 = st.columns(2, gap="large")

  with sim_col1:
    sim_savings = st.slider("Simulated Savings Level (1-5)", 1, 5, 4)
    sim_ends = st.selectbox("Simulated Expense Difficulty (1-5)", [1, 2, 3, 4, 5], index=1)
    sim_shock = st.selectbox("Simulated Shock Absorption (1-3)", [1, 2, 3], index=2)

  with sim_col2:
    sim_collect = st.selectbox("Simulated Debt Trouble (1-2)", [1, 2], index=0)
    sim_volatility = st.selectbox("Simulated Income Volatility (1-3)", [1, 2, 3], index=0)
    sim_earners = st.number_input("Simulated Earners", 1, 5, 2)

  if st.button("Run Simulation Model 🚀"):
    sim_input = pd.DataFrame(0, index=[0], columns=imputer.feature_names_in_)
    if "SAVINGSRANGES" in sim_input.columns:
      sim_input["SAVINGSRANGES"] = sim_savings
    if "ENDSMEET" in sim_input.columns:
      sim_input["ENDSMEET"] = sim_ends
    if "ABSORBSHOCK" in sim_input.columns:
      sim_input["ABSORBSHOCK"] = sim_shock
    if "COLLECT" in sim_input.columns:
      sim_input["COLLECT"] = sim_collect
    if "VOLATILITY" in sim_input.columns:
      sim_input["VOLATILITY"] = sim_volatility
    if "EARNERS" in sim_input.columns:
      sim_input["EARNERS"] = sim_earners

    sim_imputed = pd.DataFrame(
        imputer.transform(sim_input), columns=sim_input.columns
    )
    sim_pred = float(model.predict(sim_imputed)[0])

    st.success(f"✨ **Simulated Financial Well-Being Score:** `{sim_pred:.1f} / 100`")
    if sim_pred >= 60:
      st.balloons()
      st.info(
          "💡 **Great outlook!** This scenario elevates your standing above the"
          " national survey baseline average."
      )
    else:
      st.warning(
          "💡 **Room for adjustment:** Consider scaling up your savings tier or"
          " reducing cash flow volatility to cross the stability threshold."
      )