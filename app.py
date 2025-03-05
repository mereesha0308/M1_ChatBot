import streamlit as st
import importlib

# Mapping of dropdown options to file names
model_mapping = {
    "M1 ChatBot - OpenAI": "m1_chatbot_openai",
    "M1 ChatBot - LLaMA": "m1_chatbot_llama",
    "M1 ChatBot - DeepSeek": "m1_chatbot_deepseek"
}

# Set default model on first run
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "M1 ChatBot - OpenAI"  # Default selection

# Sidebar dropdown for model selection
selected_option = st.sidebar.selectbox(
    "Select ChatBot Model:", 
    list(model_mapping.keys()), 
    index=list(model_mapping.keys()).index(st.session_state.selected_model)
)

# Update session state
st.session_state.selected_model = selected_option

# Get the corresponding script name
script_name = model_mapping[selected_option]

# Display the running model
st.write(f"🔹 Running: `{script_name}.py`")

# Import and run the selected script
try:
    module = importlib.import_module(script_name)
    module.main()  # Ensure each script has a `main()` function
except Exception as e:
    st.error(f"⚠️ Error running `{script_name}.py`: {e}")
