import streamlit as st
import google.generativeai as genai
import os

st.title("🕵️ GOOGLE MODEL FINDER")

# 1. Check Key
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    st.write("📡 Contacting Google API...")
    
    try:
        # Ask Google what models this key can access
        all_models = list(genai.list_models())
        
        # Filter for models that can chat (generateContent)
        chat_models = []
        for m in all_models:
            # We look for models that support 'generateContent'
            if 'generateContent' in m.supported_generation_methods:
                chat_models.append(m.name)
        
        if chat_models:
            st.success(f"SUCCESS! Found {len(chat_models)} available models.")
            st.write("### ✅ COPY ONE OF THESE EXACT NAMES:")
            
            for name in chat_models:
                st.code(name)
                
            st.info("Paste the first model name in the chat with me, and I will fix your app immediately.")
        else:
            st.error("⚠️ Connection successful, but no Chat models were found for this API Key.")
            st.write("Raw list of available models:")
            st.json([m.name for m in all_models])
            
    except Exception as e:
        st.error("❌ CRITICAL ERROR")
        st.error(str(e))
        st.write("If the error mentions '400' or 'Key', your API Key is still invalid.")

else:
    st.error("❌ API Key not found in Secrets. Please add GEMINI_API_KEY.")
    
