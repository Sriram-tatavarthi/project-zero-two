import streamlit as st
import google.generativeai as genai
import os

st.title("🔧 SYSTEM DIAGNOSTIC")

# 1. Check if Key Exists
if "GEMINI_API_KEY" in st.secrets:
    st.success("✅ API Key found in Secrets")
    my_key = st.secrets["GEMINI_API_KEY"]
    st.write(f"Key starts with: `{my_key[:5]}...`") # Security check
    
    # 2. Try Connecting
    genai.configure(api_key=my_key)
    
    st.write("Attempting to contact Google AI...")
    
    try:
        # Try the oldest, most stable model first
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        st.success(f"✅ SUCCESS! Google replied: {response.text}")
        st.balloons()
        
    except Exception as e:
        st.error("❌ CONNECTION CRASHED")
        st.error(f"Error Details: {e}")
        st.write("---")
        st.write("### How to fix this error:")
        err_text = str(e)
        if "400" in err_text or "API key not valid" in err_text:
            st.warning("👉 Your Key is WRONG. Generate a new one at aistudio.google.com")
        elif "404" in err_text or "not found" in err_text:
            st.warning("👉 The Model Name is wrong OR your account is region-locked.")
        elif "quota" in err_text:
            st.warning("👉 You hit the free limit. Wait a few minutes.")
else:
    st.error("❌ No API Key found! Go to Manage App > Settings > Secrets.")
