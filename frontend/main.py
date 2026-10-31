
import streamlit as st
import requests
from datetime import datetime
from urllib.parse import quote_plus

# ============================================================
# IASOKA-AI | INDIA EDITION
# Patient-facing healthcare assistance prototype
# ============================================================

BACKEND_URL = "https://iasoka-ai-backend.onrender.com"

st.set_page_config(
    page_title="IASOKA-AI | Healthcare Assistant",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- SESSION STATE -------------------------

defaults = {
    "age_mode": "Standard",
    "location": "",
    "history": [],
    "last_triage": None,
    "last_symptoms": "",
    "last_specialty": "General Physician",
    "patient_name": "",
    "blood_group": "Not provided",
    "allergies": "",
    "medications": "",
    "emergency_contact": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- DESIGN -------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #f5f8fc;
    color: #172b4d;
}
section[data-testid="stSidebar"] {
    background: #10243b;
}
section[data-testid="stSidebar"] * {
    color: #edf5ff !important;
}
.main-title {
    font-family: 'Manrope', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    color: #10243b;
    letter-spacing: -1.5px;
    margin-bottom: 0;
}
.sub-title {
    color: #64748b;
    font-size: 1rem;
    margin-top: 4px;
}
.hero {
    background: linear-gradient(115deg,#10243b,#164e63);
    padding: 28px;
    border-radius: 20px;
    color: white;
    margin: 12px 0 22px 0;
}
.hero h2 {color:white; margin:0; font-size:1.8rem;}
.hero p {color:#d7e9f3; margin:8px 0 0 0;}
.emergency {
    background: #fff0f0;
    border: 1px solid #fecaca;
    border-left: 5px solid #dc2626;
    border-radius: 14px;
    padding: 16px 18px;
    margin: 16px 0;
}
.emergency h3 {color:#991b1b; margin:0 0 5px 0;}
.emergency p {color:#7f1d1d; margin:0;}
.metric-card {
    background:white;
    border:1px solid #e5edf5;
    border-radius:16px;
    padding:18px;
    min-height:110px;
    box-shadow:0 4px 15px rgba(16,36,59,.04);
}
.metric-label {color:#64748b; font-size:.85rem;}
.metric-value {color:#10243b; font-size:1.5rem; font-weight:800;}
.panel {
    background:white;
    border:1px solid #e5edf5;
    border-radius:18px;
    padding:20px;
    margin-bottom:14px;
}
.small-muted {color:#64748b; font-size:.88rem;}
.result-emergency {
    background:#fff1f2;
    border-left:5px solid #dc2626;
    padding:20px;
    border-radius:14px;
}
.result-urgent {
    background:#fff7ed;
    border-left:5px solid #ea580c;
    padding:20px;
    border-radius:14px;
}
.result-doctor {
    background:#eff6ff;
    border-left:5px solid #2563eb;
    padding:20px;
    border-radius:14px;
}
.result-self {
    background:#ecfdf5;
    border-left:5px solid #059669;
    padding:20px;
    border-radius:14px;
}
.stButton>button {
    border-radius:10px;
    font-weight:700;
    min-height:42px;
}
div[data-testid="stMetric"] {
    background:white;
    border:1px solid #e5edf5;
    padding:14px;
    border-radius:14px;
}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------- HELPERS -------------------------------

def backend_status():
    try:
        r = requests.get(BACKEND_URL, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def save_symptom(symptoms, region, severity, duration):
    payload = {
        "symptom_text": symptoms,
        "body_part": region,
        "severity": severity,
        "duration": duration,
        "age_group": st.session_state.age_mode.lower()
    }
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/symptoms",
            json=payload,
            timeout=8
        )
        if r.status_code == 200:
            return True
    except Exception:
        pass
    return False


def identify_specialty(text):
    t = text.lower()

    rules = [
        (["chest pain", "palpitation", "heart", "heartbeat"], "Cardiologist"),
        (["headache", "migraine", "seizure", "numbness", "stroke", "dizziness"], "Neurologist"),
        (["skin", "rash", "acne", "itch", "eczema", "hair fall"], "Dermatologist"),
        (["stomach", "abdomen", "gas", "bloating", "diarrhoea", "constipation", "acidity"], "Gastroenterologist"),
        (["cough", "asthma", "breathing", "lungs", "wheezing"], "Pulmonologist"),
        (["bone", "joint", "fracture", "knee", "back pain", "sprain"], "Orthopedic Doctor"),
        (["eye", "vision", "blurred vision"], "Ophthalmologist"),
        (["ear", "nose", "throat", "sinus"], "ENT Specialist"),
        (["fever", "infection", "weakness", "fatigue"], "General Physician"),
        (["period", "pregnancy", "menstrual", "reproductive"], "Gynaecologist")
    ]

    for keywords, specialty in rules:
        if any(word in t for word in keywords):
            return specialty

    return "General Physician"


def assess_symptoms(text, severity):
    t = text.lower()

    emergency_terms = [
        "chest pain", "heart attack", "cannot breathe",
        "can't breathe", "difficulty breathing",
        "shortness of breath", "unconscious",
        "severe bleeding", "stroke", "slurred speech",
        "face drooping", "sudden weakness", "seizure",
        "overdose", "choking"
    ]

    urgent_terms = [
        "high fever", "vomiting blood", "blood in stool",
        "severe abdominal pain", "fracture",
        "severe dehydration", "persistent vomiting"
    ]

    if any(term in t for term in emergency_terms):
        return {
            "level": "Emergency",
            "class": "result-emergency",
            "title": "Immediate emergency assistance may be needed",
            "description": "Some reported symptoms can indicate a time-critical condition.",
            "action": "Call 112 now or seek the nearest emergency department. Do not drive yourself."
        }

    if severity >= 9:
        return {
            "level": "Emergency",
            "class": "result-emergency",
            "title": "Severe pain reported",
            "description": "Very severe pain needs prompt professional assessment.",
            "action": "Seek urgent emergency assessment. Call 112 if you cannot safely travel or have other emergency symptoms."
        }

    if any(term in t for term in urgent_terms) or severity >= 7:
        return {
            "level": "Urgent",
            "class": "result-urgent",
            "title": "Prompt medical assessment recommended",
            "description": "Your reported symptoms or pain level suggest that you should be assessed promptly.",
            "action": "Contact a qualified doctor or visit an appropriate hospital today."
        }

    if severity >= 4:
        return {
            "level": "Doctor consultation",
            "class": "result-doctor",
            "title": "Consider consulting a doctor",
            "description": "A healthcare professional can assess persistent or worsening symptoms.",
            "action": "Arrange a consultation with a general physician or relevant specialist."
        }

    return {
        "level": "Self-care guidance",
        "class": "result-self",
        "title": "Monitor symptoms and take care",
        "description": "The information entered does not indicate an obvious emergency trigger in this prototype.",
        "action": "Monitor your symptoms and seek medical advice if they persist or worsen."
    }


def maps_url(query, location):
    search = f"{query} near {location}" if location.strip() else query
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(search)


def doctor_url(specialty, location):
    return maps_url(specialty, location)


# -------------------- SIDEBAR -------------------------------

with st.sidebar:
    st.markdown("## ✚ IASOKA-AI")
    st.caption("Intelligent Healthcare Assistance")
    st.markdown("---")

    st.markdown("### Patient preferences")
    st.session_state.age_mode = st.radio(
        "Experience mode",
        ["Standard", "Senior Care", "Kids Mode"]
    )

    st.markdown("---")
    st.markdown("### 📍 Your location")
    st.session_state.location = st.text_input(
        "City / Area / PIN code",
        value=st.session_state.location,
        placeholder="e.g. Vaishali, Ghaziabad"
    )
    st.caption("Your location is entered manually. IASOKA-AI does not automatically track GPS.")

    st.markdown("---")
    if backend_status():
        st.success("Backend connected")
    else:
        st.warning("Demo mode: backend unavailable")

    st.markdown("---")
    st.markdown("### Emergency contacts")
    st.markdown("**112 — All-in-one emergency**")
    st.markdown("[📞 Call 112](tel:112)")
    st.markdown("**108 — Ambulance emergency service**")
    st.markdown("[📞 Call 108](tel:108)")
    st.markdown("**102 — National Ambulance Service**")
    st.markdown("[📞 Call 102](tel:102)")
    st.caption("Ambulance service availability and eligibility may vary by state. Use 112 for immediate emergencies.")

# -------------------- HEADER --------------------------------

st.markdown('<div class="main-title">IASOKA-AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Multimodal AI for Intelligent Healthcare Assistance · India Edition</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="hero">
    <h2>Your health. Better understood.</h2>
    <p>Describe symptoms, review general urgency guidance and discover healthcare options near your location.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="emergency">
    <h3>🚨 Medical emergency?</h3>
    <p>For severe chest pain, serious breathing difficulty, unconsciousness, stroke symptoms or life-threatening injury, call <b>112</b> immediately.</p>
    <p style="margin-top:10px;">
        <a href="tel:112" style="background:#dc2626;color:white;padding:9px 18px;border-radius:9px;text-decoration:none;font-weight:800;">CALL 112</a>
        &nbsp;&nbsp;
        <a href="tel:108" style="background:#7f1d1d;color:white;padding:9px 18px;border-radius:9px;text-decoration:none;font-weight:800;">AMBULANCE 108</a>
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------- TOP METRICS ---------------------------

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown('<div class="metric-card"><div class="metric-label">Emergency response</div><div class="metric-value">112</div><div class="small-muted">Pan-India emergency number</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-card"><div class="metric-label">Ambulance support</div><div class="metric-value">108 / 102</div><div class="small-muted">State-dependent services</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-card"><div class="metric-label">Your selected area</div><div class="metric-value" style="font-size:1.2rem;">' + (st.session_state.location or "Not entered") + '</div><div class="small-muted">Used for map searches</div></div>', unsafe_allow_html=True)

st.write("")

# -------------------- MAIN TABS -----------------------------

tab_assess, tab_care, tab_history, tab_profile = st.tabs([
    "🩺 Symptom Assessment",
    "🏥 Find Healthcare",
    "📋 Health History",
    "🪪 Medical ID"
])

# ============================================================
# TAB 1: SYMPTOM ASSESSMENT
# ============================================================

with tab_assess:
    st.markdown("## Symptom assessment")
    st.caption("Share what you are experiencing. This prototype provides general urgency guidance, not a diagnosis.")

    left, right = st.columns([1, 1])

    with left:
        regions = [
            "Head & Face",
            "Throat & Neck",
            "Chest & Heart",
            "Stomach & Abdomen",
            "Back & Spine",
            "Arms & Shoulders",
            "Legs & Knees",
            "Feet & Ankles",
            "Whole Body"
        ]

        region = st.selectbox("Where are you experiencing symptoms?", regions)

        symptom_text = st.text_area(
            "Describe your symptoms",
            placeholder="Example: I have had a headache and mild nausea since yesterday...",
            height=150
        )

    with right:
        severity = st.slider("Pain / discomfort level", 0, 10, 3)
        duration = st.selectbox(
            "How long have you experienced this?",
            [
                "Just started",
                "1–2 days",
                "3–7 days",
                "More than a week",
                "Recurring / chronic"
            ]
        )

        age = st.selectbox(
            "Age group",
            ["Under 18", "18–40", "41–60", "Above 60", "Prefer not to say"]
        )

        st.info("If you are experiencing a medical emergency, do not wait for this assessment. Call 112.")

    if st.button("Generate my assessment", type="primary", use_container_width=True):
        if not symptom_text.strip():
            st.warning("Please describe your symptoms first.")
        else:
            triage = assess_symptoms(symptom_text, severity)
            specialty = identify_specialty(symptom_text)

            st.session_state.last_triage = triage
            st.session_state.last_symptoms = symptom_text
            st.session_state.last_specialty = specialty

            entry = {
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "region": region,
                "symptoms": symptom_text,
                "severity": severity,
                "duration": duration,
                "level": triage["level"],
                "specialty": specialty
            }
            st.session_state.history.insert(0, entry)

            save_symptom(symptom_text, region, severity, duration)

    if st.session_state.last_triage:
        triage = st.session_state.last_triage
        st.markdown("---")
        st.markdown("### Your assessment summary")

        st.markdown(
            f"""
            <div class="{triage['class']}">
                <div style="font-size:.8rem;font-weight:800;text-transform:uppercase;letter-spacing:1px;">
                    {triage['level']}
                </div>
                <h3>{triage['title']}</h3>
                <p>{triage['description']}</p>
                <b>Suggested next step:</b> {triage['action']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        st.markdown("#### Suggested doctor specialty")
        st.info(
            f"Based on the words entered, you may wish to search for a **{st.session_state.last_specialty}**."
        )
        st.caption("This is a keyword-based suggestion, not a medical diagnosis or a determination of which specialist you need.")

        if st.session_state.location:
            st.link_button(
                f"Find {st.session_state.last_specialty}s near {st.session_state.location}",
                doctor_url(st.session_state.last_specialty, st.session_state.location),
                use_container_width=True
            )
        else:
            st.warning("Enter your city or area in the sidebar to find relevant doctors.")

        st.caption(
            "Important: This prototype uses predefined symptom rules. It is not a trained or clinically validated diagnostic model. A qualified healthcare professional must assess medical concerns."
        )

# ============================================================
# TAB 2: HEALTHCARE DISCOVERY
# ============================================================

with tab_care:
    st.markdown("## Healthcare discovery")
    st.caption("Search for hospitals, emergency departments, clinics and specialists around your selected area.")

    location = st.text_input(
        "Search location",
        value=st.session_state.location,
        placeholder="Enter area, city or PIN code"
    )
    if location != st.session_state.location:
        st.session_state.location = location

    if not location.strip():
        st.warning("Enter a location to generate nearby healthcare searches.")
    else:
        st.markdown("### Hospitals and emergency care")
        st.write("Use these live map searches to see current facilities, directions, contact details and reviews.")

        c1, c2 = st.columns(2)
        with c1:
            st.link_button(
                "🏥 Nearby hospitals",
                maps_url("Hospitals", location),
                use_container_width=True
            )
            st.link_button(
                "🚑 Emergency departments",
                maps_url("24 hour emergency hospital", location),
                use_container_width=True
            )
            st.link_button(
                "🧪 Diagnostic centres",
                maps_url("Diagnostic laboratory and imaging centre", location),
                use_container_width=True
            )

        with c2:
            st.link_button(
                "💊 Pharmacies",
                maps_url("Pharmacy", location),
                use_container_width=True
            )
            st.link_button(
                "🩺 General physicians",
                maps_url("General physician", location),
                use_container_width=True
            )
            st.link_button(
                "🩻 Multispeciality hospitals",
                maps_url("Multispeciality hospital", location),
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### Specialist discovery")

        specialties = [
            "Cardiologist",
            "Neurologist",
            "Dermatologist",
            "Gastroenterologist",
            "Pulmonologist",
            "Orthopedic Doctor",
            "Ophthalmologist",
            "ENT Specialist",
            "Gynaecologist",
            "Paediatrician",
            "General Physician"
        ]

        selected_specialty = st.selectbox(
            "Choose a doctor specialty",
            specialties,
            index=specialties.index(st.session_state.last_specialty)
            if st.session_state.last_specialty in specialties else 10
        )

        st.link_button(
            f"Find {selected_specialty}s near {location}",
            doctor_url(selected_specialty, location),
            use_container_width=True
        )

        if st.session_state.last_symptoms:
            st.markdown("#### Based on your last assessment")
            st.success(
                f"Suggested specialty: {st.session_state.last_specialty}"
            )
            st.link_button(
                "Find suggested specialists on Maps",
                doctor_url(st.session_state.last_specialty, location),
                use_container_width=True
            )

        st.caption("Map results are supplied by Google Maps. Check the hospital's emergency availability, services, distance and contact details directly before travelling. IASOKA-AI does not rank or certify hospitals.")

    st.markdown("---")
    st.markdown("### Emergency helplines in India")

    e1, e2, e3 = st.columns(3)
    with e1:
        st.markdown("#### 112")
        st.write("Integrated emergency response")
        st.link_button("Call 112", "tel:112", use_container_width=True)
    with e2:
        st.markdown("#### 108")
        st.write("Emergency ambulance service")
        st.link_button("Call 108", "tel:108", use_container_width=True)
    with e3:
        st.markdown("#### 102")
        st.write("National Ambulance Service")
        st.link_button("Call 102", "tel:102", use_container_width=True)

    st.caption("112 is the primary pan-India emergency number. 108 and 102 services vary in availability and function across states. In a life-threatening emergency, call 112.")

# ============================================================
# TAB 3: HEALTH HISTORY
# ============================================================

with tab_history:
    st.markdown("## Your symptom history")
    st.caption("Reports entered during this browser session.")

    if not st.session_state.history:
        st.info("No symptom reports yet. Complete an assessment to see it here.")
    else:
        for item in st.session_state.history:
            with st.expander(
                f"{item['date']} · {item['level']} · Pain {item['severity']}/10"
            ):
                st.write("**Affected area:**", item["region"])
                st.write("**Symptoms:**", item["symptoms"])
                st.write("**Duration:**", item["duration"])
                st.write("**Suggested specialty:**", item["specialty"])

    if st.button("Clear session history"):
        st.session_state.history = []
        st.session_state.last_triage = None
        st.session_state.last_symptoms = ""
        st.rerun()

    st.caption("Session history is temporary and may be lost when the session ends. Do not enter sensitive medical information into this demonstration.")

# ============================================================
# TAB 4: MEDICAL ID
# ============================================================

with tab_profile:
    st.markdown("## Patient medical ID")
    st.caption("Add optional information for a demonstration medical profile. Do not use this as a substitute for an official medical ID.")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.patient_name = st.text_input(
            "Patient name",
            value=st.session_state.patient_name
        )
        st.session_state.blood_group = st.selectbox(
            "Blood group",
            [
                "Not provided", "A+", "A-", "B+", "B-",
                "AB+", "AB-", "O+", "O-"
            ],
            index=[
                "Not provided", "A+", "A-", "B+", "B-",
                "AB+", "AB-", "O+", "O-"
            ].index(st.session_state.blood_group)
        )

    with col2:
        st.session_state.emergency_contact = st.text_input(
            "Emergency contact number",
            value=st.session_state.emergency_contact,
            placeholder="+91 XXXXX XXXXX"
        )
        st.session_state.allergies = st.text_input(
            "Known allergies",
            value=st.session_state.allergies
        )

    st.session_state.medications = st.text_area(
        "Current medications (optional)",
        value=st.session_state.medications
    )

    st.markdown("---")
    st.markdown("### Emergency medical ID preview")

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(130deg,#10243b,#164e63);
            color:white;padding:26px;border-radius:18px;
            border:1px solid #31536c;
        ">
            <div style="font-size:.8rem;letter-spacing:2px;color:#b8d8e8;font-weight:800;">
                IASOKA-AI · MEDICAL ID
            </div>
            <h2 style="color:white;margin-top:12px;">
                {st.session_state.patient_name or "Patient Name"}
            </h2>
            <p style="color:#d7e9f3;">
                Blood group: <b>{st.session_state.blood_group}</b>
            </p>
            <p style="color:#d7e9f3;">
                Allergies: <b>{st.session_state.allergies or "Not provided"}</b>
            </p>
            <p style="color:#d7e9f3;">
                Medications: <b>{st.session_state.medications or "Not provided"}</b>
            </p>
            <p style="color:#d7e9f3;">
                Emergency contact: <b>{st.session_state.emergency_contact or "Not provided"}</b>
            </p>
            <div style="background:#dc2626;padding:10px 14px;border-radius:9px;display:inline-block;margin-top:10px;">
                <b>Emergency in India: 112</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("This preview is stored only in the current Streamlit session. It is not a verified medical record or a secure emergency service.")

# -------------------- FOOTER --------------------------------

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#64748b;font-size:.85rem;'>"
    "<b>IASOKA-AI</b> · Intelligent Healthcare Assistance<br>"
    "Academic prototype · Not a medical device · Not a diagnosis · "
    "Not clinically validated<br>"
    "For emergencies in India, call 112."
    "</div>",
    unsafe_allow_html=True
)
