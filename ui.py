import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"   # FastAPI server URL

st.set_page_config(page_title="Churn Prediction UI", layout="centered")

st.title("📊 Customer Churn Prediction")
st.write("Secure Prediction with JWT Authentication")

# -----------------------
# Session state for token
# -----------------------
if "token" not in st.session_state:
    st.session_state.token = None

# -----------------------
# Sidebar Login/Register
# -----------------------
menu = st.sidebar.radio("Menu", ["Login", "Register", "Predict"])

# -----------------------
# Register
# -----------------------
if menu == "Register":
    st.header("📝 Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        payload = {"username": username, "password": password}
        r = requests.post(f"{API_BASE}/register", json=payload)

        if r.status_code == 200:
            data = r.json()
            st.success("Registered successfully!")
            st.session_state.token = data["access_token"]
        else:
            st.error(r.text)

# -----------------------
# Login
# -----------------------
elif menu == "Login":
    st.header("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        payload = {"username": username, "password": password}
        r = requests.post(f"{API_BASE}/login", json=payload)

        if r.status_code == 200:
            data = r.json()
            st.session_state.token = data["access_token"]
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

# -----------------------
# Prediction UI
# -----------------------
elif menu == "Predict":
    st.header("📈 Churn Prediction")

    if not st.session_state.token:
        st.warning("Please login first!")
        st.stop()

    # Customer Form
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.slider("Age", 18, 100, 30)
    tenure = st.slider("Tenure", 0, 100, 10)
    services = st.slider("Services Subscribed", 0, 10, 3)
    contract = st.selectbox("Contract Type", ["Month-to-month", "One Year", "Two year"])
    monthly = st.number_input("Monthly Charges", value=70.5)
    total = st.number_input("Total Charges", value=500.75)
    tech = st.selectbox("Tech Support", ["Yes", "No"])
    security = st.selectbox("Online Security", ["Yes", "No"])
    internet = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])

    if st.button("Predict"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        payload = {
            "customer": {
                "Gender": gender,
                "Age": age,
                "Tenure": tenure,
                "Services_Subscribed": services,
                "Contract_Type": contract,
                "MonthlyCharges": monthly,
                "TotalCharges": total,
                "TechSupport": tech,
                "OnlineSecurity": security,
                "InternetService": internet
            }
        }

        r = requests.post(f"{API_BASE}/predict/auth", json=payload, headers=headers)

        if r.status_code == 200:
            result = r.json()
            st.success(f"Prediction: {result['churn_label']}")
            st.write(f"Probability: {result['churn_probability']}")
        else:
            st.error(r.text)
