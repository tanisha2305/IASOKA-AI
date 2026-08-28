"""
IASOKA-AI: Universal Healthcare & Medical Triage Platform
Interactive Python Frontend (Streamlit)
Connects directly to the FastAPI backend at http://localhost:8000
"""
BACKEND_URL = "https://iasoka-ai-backend.onrender.com"
import streamlit as st
import requests
import json
from datetime import datetime

# -----------------------------------------------------------------------------
# Configuration & Backend Base URL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IASOKA-AI | Universal Healthcare Portal",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "https://iasoka-ai-backend.onrender.com"

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "age_mode" not in st.session_state:
    st.session_state.age_mode = "Standard"
if "local_history" not in st.session_state:
    st.session_state.local_history = [
        {
            "id": "demo-1",
            "symptom_text": "Mild headache and dry cough for 2 days",
            "body_part": "Head & Face",
            "severity": 4,
            "duration": "1-2 days",
            "triage": "Home Care & Monitoring",
            "created_at": "Yesterday"
        }
    ]

# -----------------------------------------------------------------------------
# Custom CSS for Multi-Age Accessibility & Theming
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header { font-weight: 900; letter-spacing: -0.5px; }
    .emergency-banner {
        background-color: #dc2626;
        color: white;
        padding: 12px 18px;
        border-radius: 12px;
        font-weight: 700;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .card-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 16px;
    }
    .senior-text {
        font-size: 1.25rem !important;
        line-height: 1.8 !important;
    }
    .kid-bubble {
        background-color: #ecfdf5;
        border: 2px solid #a7f3d0;
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .triage-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-emergency { background-color: #fee2e2; color: #b91c1c; border: 1px solid #f87171; }
    .badge-urgent { background-color: #fef3c7; color: #b45309; border: 1px solid #fbbf24; }
    .badge-doctor { background-color: #e0e7ff; color: #4338ca; border: 1px solid #818cf8; }
    .badge-self { background-color: #d1fae5; color: #047857; border: 1px solid #34d399; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# API Helper Functions
# -----------------------------------------------------------------------------
def check_backend_status():
    try:
        res = requests.get(BACKEND_URL, timeout=1.5)
        return res.status_code == 200
    except Exception:
        return False

def api_login(email, password):
    try:
        res = requests.post(f"{BACKEND_URL}/api/auth/login", json={"email": email, "password": password}, timeout=3)
        if res.status_code == 200:
            data = res.json()
            st.session_state.auth_token = data.get("access_token", "guest-demo-token")
            st.session_state.user_info = data.get("user", {"email": email})
            return True, "Login successful!"
        return False, res.json().get("detail", "Login failed")
    except Exception:
        # Fallback for smooth local demo
        st.session_state.auth_token = "guest-demo-token"
        st.session_state.user_info = {"email": email, "user_metadata": {"full_name": email.split("@")[0]}}
        return True, "Connected in Demo Mode"

def api_signup(email, password, full_name, age_group):
    try:
        res = requests.post(f"{BACKEND_URL}/api/auth/signup", json={
            "email": email, "password": password, "full_name": full_name, "age_group": age_group
        }, timeout=3)
        if res.status_code == 200:
            data = res.json()
            st.session_state.auth_token = data.get("access_token", "guest-demo-token")
            st.session_state.user_info = data.get("user", {"email": email})
            return True, "Signup successful!"
        return False, res.json().get("detail", "Signup failed")
    except Exception:
        st.session_state.auth_token = "guest-demo-token"
        st.session_state.user_info = {"email": email, "user_metadata": {"full_name": full_name}}
        return True, "Registered in Demo Mode"

def api_submit_symptoms(symptom_text, body_part, severity, duration, age_group):
    headers = {"Content-Type": "application/json"}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    
    payload = {
        "symptom_text": symptom_text,
        "body_part": body_part,
        "severity": severity,
        "duration": duration,
        "age_group": age_group.lower()
    }
    
    try:
        res = requests.post(f"{BACKEND_URL}/api/symptoms", json=payload, headers=headers, timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    
    # Save locally to session
    new_entry = {
        "id": f"rep-{len(st.session_state.local_history)+1}",
        "symptom_text": symptom_text,
        "body_part": body_part,
        "severity": severity,
        "duration": duration,
        "created_at": datetime.now().strftime("%b %d, %H:%M")
    }
    st.session_state.local_history.insert(0, new_entry)
    return {"message": "Saved to session", "report": [new_entry]}

def api_get_facilities(facility_type=None):
    mock_facilities = [
        {"name": "St. Jude Children & General Hospital", "type": "Hospital", "address": "742 Evergreen Terrace", "phone": "(555) 019-2831", "emergency_24_7": True, "rating": 4.9, "wait_time": "15 mins"},
        {"name": "Sunrise Senior & Family Urgent Care", "type": "Urgent Care", "address": "1204 Pine Valley Blvd", "phone": "(555) 832-1920", "emergency_24_7": True, "rating": 4.8, "wait_time": "10 mins"},
        {"name": "Little Stars Pediatric Health Clinic", "type": "Pediatrics", "address": "450 Blossom Hill Rd", "phone": "(555) 441-9921", "emergency_24_7": False, "rating": 4.95, "wait_time": "Appointments"},
        {"name": "Metro Health 24/7 Community Pharmacy", "type": "Pharmacy", "address": "880 Central Parkway", "phone": "(555) 302-8811", "emergency_24_7": True, "rating": 4.7, "wait_time": "5 mins"},
        {"name": "Hope Valley Specialized Geriatric Clinic", "type": "Clinic", "address": "301 Wellness Drive", "phone": "(555) 774-0019", "emergency_24_7": True, "rating": 4.85, "wait_time": "20 mins"}
    ]
    
    try:
        url = f"{BACKEND_URL}/api/facilities"
        if facility_type and facility_type != "All":
            url += f"?type={facility_type}"
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            data = res.json().get("facilities", [])
            if data: return data
    except Exception:
        pass
    
    if facility_type and facility_type != "All":
        return [f for f in mock_facilities if facility_type.lower() in f["type"].lower()]
    return mock_facilities


# -----------------------------------------------------------------------------
# Clinical AI Triage Logic
# -----------------------------------------------------------------------------
def evaluate_triage(symptom_text, severity):
    text = symptom_text.lower()
    emergency_keywords = ['chest pain', 'heart attack', 'cannot breathe', 'shortness of breath', 'stroke', 'slurred speech', 'unconscious', 'seizure', 'severe bleeding']
    urgent_keywords = ['high fever', 'deep cut', 'fracture', 'severe migraine', 'vomiting blood', 'burning urination', 'asthma', 'sprain']
    
    if any(k in text for k in emergency_keywords) or severity >= 9:
        return {
            "level": "Emergency",
            "badge_class": "badge-emergency",
            "title": "🚨 Immediate Emergency Medical Attention Required",
            "desc": "Your symptoms indicate acute or life-threatening distress.",
            "action": "Call 911 / 112 immediately or proceed to the nearest Hospital Emergency Room.",
            "care": "Do NOT drive yourself. Sit upright, rest, and keep someone with you.",
            "questions": ["What immediate diagnostic tests (ECG, CT) are being performed?", "What warning signs should family monitor?"]
        }
    elif any(k in text for k in urgent_keywords) or severity >= 7:
        return {
            "level": "Urgent Care",
            "badge_class": "badge-urgent",
            "title": "⚡ Same-Day Urgent Care Visit Recommended",
            "desc": "Your symptoms warrant professional clinical evaluation today.",
            "action": "Visit a nearby Urgent Care center or Walk-in clinic within 4-8 hours.",
            "care": "Stay hydrated with electrolytes, rest in a calm area, avoid physical exertion.",
            "questions": ["Are prescription antibiotics or anti-inflammatories required?", "Is an X-ray or ultrasound recommended?"]
        }
    elif severity >= 4:
        return {
            "level": "Primary Care",
            "badge_class": "badge-doctor",
            "title": "🩺 Consult Your Primary Care Physician / GP",
            "desc": "Your condition is manageable but should be checked by a doctor within 24-48 hours.",
            "action": "Schedule a clinic or telehealth appointment with your doctor.",
            "care": "Monitor temperature and note any symptom triggers.",
            "questions": ["What could be the root cause of these recurring symptoms?", "What lifestyle or OTC medications do you suggest?"]
        }
    else:
        return {
            "level": "Home Care",
            "badge_class": "badge-self",
            "title": "🟢 Home Care & Rest",
            "desc": "Symptoms are currently mild. Supportive home recovery is suitable.",
            "action": "Follow supportive home-care protocols and re-assess in 48 hours.",
            "care": "Get 8+ hours of restful sleep, drink plenty of warm fluids, and stay comfortable.",
            "questions": ["How many days should I wait before seeking an in-person visit if it does not clear?"]
        }


# -----------------------------------------------------------------------------
# Sidebar: Mode Switcher & Patient Profile
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ✚ **IASOKA-AI**")
    st.caption("Universal Healthcare & Triage Portal")
    
    # Age Mode Switcher
    st.markdown("---")
    st.markdown("#### 🎯 **Accessibility & Age Mode**")
    selected_mode = st.radio(
        "Choose Your Preferred Experience:",
        ["🩺 Standard", "👓 Senior Care", "🧸 Kids Mode"],
        index=0 if st.session_state.age_mode == "Standard" else (1 if st.session_state.age_mode == "Senior Care" else 2)
    )
    st.session_state.age_mode = selected_mode.split(" ")[1]
    
    # Backend Status
    st.markdown("---")
    is_online = check_backend_status()
    if is_online:
        st.success("● FastAPI Backend: Connected")
    else:
        st.info("○ Standalone Demo Mode Active (FastAPI offline)")
        
    # User Profile / Auth Section
    st.markdown("---")
    st.markdown("#### 👤 **User Account**")
    if st.session_state.user_info:
        user_name = st.session_state.user_info.get("user_metadata", {}).get("full_name") or st.session_state.user_info.get("email", "Patient")
        st.success(f"Signed in as **{user_name}**")
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.auth_token = None
            st.session_state.user_info = None
            st.rerun()
    else:
        with st.expander("🔐 Sign In / Register", expanded=False):
            auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
            with auth_tab1:
                log_email = st.text_input("Email", key="log_email")
                log_pass = st.text_input("Password", type="password", key="log_pass")
                if st.button("Log In", use_container_width=True):
                    if log_email and log_pass:
                        ok, msg = api_login(log_email, log_pass)
                        if ok: st.rerun()
                        else: st.error(msg)
            with auth_tab2:
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_email = st.text_input("Email", key="reg_email")
                reg_pass = st.text_input("Password", type="password", key="reg_pass")
                if st.button("Create Account", use_container_width=True):
                    if reg_email and reg_pass:
                        ok, msg = api_signup(reg_email, reg_pass, reg_name, st.session_state.age_mode)
                        if ok: st.rerun()
                        else: st.error(msg)


# -----------------------------------------------------------------------------
# Top Emergency SOS Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="emergency-banner">
    <div>🚨 <strong>Life-Threatening Emergency?</strong> Severe chest pain, sudden numbness, or choking?</div>
    <div><a href="tel:911" style="background-color: white; color: #dc2626; padding: 6px 16px; border-radius: 999px; text-decoration: none; font-weight: 900;">CALL 911 / 112</a></div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Dynamic Age Banner
# -----------------------------------------------------------------------------
if st.session_state.age_mode == "Kids":
    st.markdown("""
    <div class="kid-bubble">
        <h3 style="color: #065f46; margin:0;">🦉 Dr. Iasoka the Owl says:</h3>
        <p style="color: #047857; margin: 4px 0 0 0; font-size: 1.1rem;">
            "Hello little friend! Pick where it feels hurt or icky on the body buttons below, and we'll help you feel all better!"
        </p>
    </div>
    """, unsafe_allow_html=True)
elif st.session_state.age_mode == "Senior":
    st.markdown("""
    <div class="card-box senior-text" style="background-color: #fef3c7; border-color: #fde68a;">
        📢 <strong>Senior Care Mode:</strong> High visibility & large typography enabled. Take your time to review each step below.
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Main Application Tabs
# -----------------------------------------------------------------------------
tab_symptoms, tab_facilities, tab_medical_id = st.tabs([
    "📍 1. Symptom Assessment & Body Map",
    "🏥 2. Healthcare Facilities Directory",
    "📇 3. Medical Emergency ID & History"
])

# -----------------------------------------------------------------------------
# TAB 1: Symptom Assessment & Interactive Body Map
# -----------------------------------------------------------------------------
with tab_symptoms:
    st.markdown("## **Interactive Symptom & Pain Visualizer**")
    st.caption("Select your affected body region, adjust the pain scale, and generate your instant AI clinical triage report.")
    
    col_left, col_right = st.columns([5, 7])
    
    with col_left:
        st.markdown("#### 👤 **1. Select Body Region**")
        body_regions = {
            "🧠 Head & Face": ["Throbbing Headache", "Migraine / Light Sensitivity", "Dizziness / Vertigo", "Sinus Congestion"],
            "🗣️ Throat & Neck": ["Sore Throat", "Pain When Swallowing", "Swollen Glands", "Stiff Neck"],
            "🫀 Chest & Heart": ["Chest Tightness", "Shortness of Breath", "Rapid Heart Rate", "Persistent Cough"],
            "🩹 Stomach & Abdomen": ["Stomach Cramps", "Nausea or Vomiting", "Acid Reflux / Heartburn", "Bloating"],
            "🦴 Spine & Back": ["Lower Back Ache", "Upper Back Tension", "Sciatica Nerve Pain", "Stiff Spine"],
            "💪 Arms & Shoulders": ["Shoulder Strain", "Elbow Joint Pain", "Arm Weakness or Numbness"],
            "🦵 Legs & Knees": ["Knee Joint Pain", "Swollen Knee", "Hamstring Soreness", "Leg Cramps"],
            "🦶 Ankles & Feet": ["Ankle Sprain", "Heel Pain / Plantar Fasciitis", "Swollen Ankles"],
            "🌐 Whole Body / General": ["High Fever & Chills", "Extreme Fatigue", "Body Aches / Flu", "Skin Rash"]
        }
        
        selected_region_label = st.selectbox("Choose Affected Area:", list(body_regions.keys()), index=0)
        clean_region_name = selected_region_label.split(" ", 1)[1]
        
        st.markdown("##### **Common Symptoms for this Area:**")
        preset_symptoms = body_regions[selected_region_label]
        selected_presets = []
        preset_cols = st.columns(2)
        for i, symptom in enumerate(preset_symptoms):
            if preset_cols[i % 2].button(f"+ {symptom}", key=f"btn_sym_{i}", use_container_width=True):
                selected_presets.append(symptom)

    with col_right:
        st.markdown("#### 📝 **2. Describe Symptoms & Severity**")
        
        default_text = ", ".join(selected_presets) if selected_presets else ""
        symptom_description = st.text_area(
            "What symptoms are you experiencing?",
            value=default_text,
            placeholder="e.g. I have had a severe throbbing headache since yesterday morning with mild nausea...",
            height=110
        )
        
        # Wong-Baker Pain Scale Slider
        st.markdown("#### 📊 **3. Pain Intensity (Wong-Baker Scale 0–10)**")
        pain_emojis = ["😄", "🙂", "🙂", "😐", "😐", "🙁", "🙁", "😣", "😣", "😭", "😭"]
        pain_labels = [
            "0 - No Hurt", "1 - Very Mild", "2 - Mild Discomfort", "3 - Uncomfortable",
            "4 - Moderate Pain", "5 - Moderately Strong", "6 - Strong", "7 - Very Strong",
            "8 - Intense Pain", "9 - Excruciating", "10 - Worst Pain Possible"
        ]
        
        pain_val = st.slider("Slide to rate pain level:", 0, 10, 4)
        st.markdown(f"### {pain_emojis[pain_val]} **{pain_labels[pain_val]}**")
        
        # Duration selector
        duration_val = st.selectbox(
            "How long have you felt these symptoms?",
            ["Just started (few hours)", "1 – 2 days", "3 – 7 days", "More than 1 week", "Chronic / Recurring"]
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.button("🩺 **Get AI Clinical Assessment & Triage Report**", type="primary", use_container_width=True)

    # Triage Assessment Result Section
    if submit_btn:
        if not symptom_description.strip():
            st.warning("⚠️ Please describe your symptoms before running the assessment.")
        else:
            with st.spinner("Analyzing symptoms & connecting to IASOKA-AI triage engine..."):
                # Call backend API
                api_submit_symptoms(symptom_description, clean_region_name, pain_val, duration_val, st.session_state.age_mode)
                triage = evaluate_triage(symptom_description, pain_val)
                
                st.markdown("---")
                st.markdown("### 📋 **IASOKA-AI Clinical Triage Report**")
                
                st.markdown(f"""
                <div class="card-box" style="border-left: 6px solid #2563eb;">
                    <span class="triage-badge {triage['badge_class']}">{triage['level']}</span>
                    <h3 style="margin-top: 10px;">{triage['title']}</h3>
                    <p style="color: #475569; font-size: 1.05rem;">{triage['desc']}</p>
                    <div style="background-color: #f8fafc; padding: 14px; border-radius: 10px; margin-top: 12px; border: 1px solid #e2e8f0;">
                        <strong>Recommended Next Action:</strong> <span style="color: #2563eb; font-weight: bold;">{triage['action']}</span><br>
                        <strong style="color: #334155;">Supportive Home Care:</strong> {triage['care']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🩺 **Questions to Ask Your Doctor:**")
                for q in triage["questions"]:
                    st.markdown(f"- **{q}**")
                
                st.caption("⚠️ **Medical Disclaimer:** IASOKA-AI provides supportive triage guidance and does not replace professional diagnosis. Call emergency services immediately if you experience chest pain or severe breathing difficulty.")


# -----------------------------------------------------------------------------
# TAB 2: Healthcare Facilities Directory
# -----------------------------------------------------------------------------
with tab_facilities:
    st.markdown("## 🏥 **Healthcare Facilities & Urgent Care Locator**")
    st.caption("Filter hospitals, urgent care centers, pediatric clinics, and 24/7 pharmacies nearby.")
    
    facility_filter = st.radio(
        "Filter by Facility Type:",
        ["All", "Hospital", "Urgent Care", "Pediatrics", "Clinic", "Pharmacy"],
        horizontal=True
    )
    
    facilities_list = api_get_facilities(facility_filter)
    
    f_cols = st.columns(3)
    for idx, fac in enumerate(facilities_list):
        with f_cols[idx % 3]:
            st.markdown(f"""
            <div class="card-box">
                <span class="triage-badge badge-doctor">{fac.get('type', 'Medical Center')}</span>
                <h4 style="margin: 8px 0 4px 0;">{fac['name']}</h4>
                <p style="color: #64748b; font-size: 0.85rem; margin-bottom: 8px;">📍 {fac['address']}</p>
                <div style="font-size: 0.85rem; color: #334155; margin-bottom: 12px;">
                    ⭐ <strong>{fac.get('rating', 4.8)}</strong> • ⏱️ Wait: <strong>{fac.get('wait_time', '15 mins')}</strong>
                    { ' • 🚨 <strong>24/7 ER</strong>' if fac.get('emergency_24_7') else '' }
                </div>
                <a href="tel:{fac.get('phone', '911')}" style="display: block; text-align: center; background-color: #2563eb; color: white; padding: 8px 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.9rem;">📞 Call {fac.get('phone', 'Facility')}</a>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 3: Medical Emergency ID & History
# -----------------------------------------------------------------------------
with tab_medical_id:
    st.markdown("## 📇 **Patient Emergency Medical ID & History**")
    
    col_id, col_hist = st.columns([5, 7])
    
    with col_id:
        st.markdown("#### 🚨 **Emergency Medical ID Badge**")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: white; padding: 22px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.15);">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 14px;">
                <span style="font-weight: 900; letter-spacing: 1px; color: #c7d2fe;">EMERGENCY MEDICAL ID</span>
                <span style="background-color: #dc2626; color: white; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;">SOS</span>
            </div>
            <p style="margin: 6px 0; font-size: 0.9rem;"><strong>Blood Group:</strong> <span style="color: #4ade80;">O Positive (O+)</span></p>
            <p style="margin: 6px 0; font-size: 0.9rem;"><strong>Known Allergies:</strong> <span style="color: #fde047;">Penicillin, Peanuts</span></p>
            <p style="margin: 6px 0; font-size: 0.9rem;"><strong>Current Medications:</strong> Albuterol Inhaler</p>
            <p style="margin: 6px 0; font-size: 0.9rem;"><strong>Emergency Contact:</strong> (555) 912-8834 (Family)</p>
            <p style="margin: 6px 0; font-size: 0.9rem;"><strong>Primary Physician:</strong> Dr. Sarah Jenkins, MD</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_hist:
        st.markdown("#### 📋 **Recent Symptom Logs**")
        for item in st.session_state.local_history:
            st.markdown(f"""
            <div class="card-box" style="padding: 14px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>{item.get('body_part', 'General')}</strong>
                    <span style="color: #64748b; font-size: 0.8rem;">{item.get('created_at', 'Recent')}</span>
                </div>
                <p style="color: #475569; font-size: 0.9rem; margin: 4px 0;">{item.get('symptom_text', '')}</p>
                <span style="font-size: 0.8rem; color: #64748b;">Pain: <strong>{item.get('severity', 4)}/10</strong> • Duration: <strong>{item.get('duration', '1-2 days')}</strong></span>
            </div>
            """, unsafe_allow_html=True)
