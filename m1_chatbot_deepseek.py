import streamlit as st
import pandas as pd
import openai
import plotly.express as px  # Plotly for graphing
import plotly.graph_objects as go
from PIL import Image
import io  # For capturing printed output
from contextlib import redirect_stdout  # Corrected import
# Ensure that kaleido is installed before using it
import plotly.graph_objects as go
from openai import OpenAI
import openai
import os
import re

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("m1_data.csv")

df = load_data()

# Set up DeepSeek API via Kluster AI
client = OpenAI(
    api_key="7556ec59-95e1-4ede-b6cf-b8d25dc54339",  # Replace with your actual Kluster API key #Shadeer's api key
    base_url="https://api.kluster.ai/v1"
)

def query_deepseek(prompt):
    """
    Send a query to DeepSeek LLM via Kluster AI and get Python code as a response.
    """
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1",  # Using DeepSeek model
        messages=[
            {"role": "system", "content": "You are a helpful data assistant that generates Python code to process data."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=2000,
        temperature=0.6,
        top_p=1
    )
    return response.choices[0].message.content.strip()

def main():
    # Streamlit App UI
    st.title("M1 Dynamic Data Bot")
    st.write("Interact with your M1 data dynamically!")

    # Initialize session state to store conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Show dataset preview
    st.subheader("Dataset Preview")
    st.dataframe(df.head(3))  # Display the first 5 rows
    
    # User Input
    query = st.text_input("What insights are you seeking? (e.g., What’s the total value of orders in 2024?)")

    if st.button("Submit"):
        if query:
            st.write(f"Your query: **{query}**")

            # Store the user's query in the conversation history
            st.session_state.conversation.append({"role": "user", "content": query})

            # Generate Python code based on the user query
            deepseek_prompt = f"""
            You are a helpful assistant that generates Python code for data analysis. 
            The dataset contains the following columns:{', '.join(df.columns)}

            please ensure that the 'Advertiser' and 'Status' columns are cleaned by replacing specific values as follows if user query asks about advertiser or status, if needed:

            1. **For the 'Advertiser' column**:
                - 'Samsung Singapore' -> 'Samsung SG'
                - 'Lazada (SG)' -> 'Lazada SG'
                - 'FairPrice Online' -> 'Fairprice ON'
                - 'Shopee Singapore' -> 'Shopee SG'
                - 'Shopee SG - CPS' -> 'Shopee SG'
                - 'tripcom' -> 'Trip.com'
                - 'Decathlon' -> 'Decathlon SG'
                - 'Nike (APAC)' -> 'Nike APAC'
                - 'Klook' -> 'Klook Travel (CPS)'
                - 'Watsons SG' -> 'Watsons Singapore'

            2. **For the 'Status' column**:
                - 'APR' -> 'Approved'
                - 'pending' -> 'Pending'
                - 'rejected' -> 'Rejected'

            Replace the values in the 'Advertiser' and 'Status' column as per the above mappings if needed.

            ### **Important Instructions:**
            - Do **NOT** include `<think>` tags or any other meta-content.  
            **Why?** Because we need a **clean Python script** that runs directly in our system without extra formatting or reasoning text.  
            - Do **NOT** include explanations, reasoning steps, or additional comments—only return the **pure Python code**.  
            **Why?** Because we are integrating this response into a **Streamlit app**, and any extra text will break the execution. 
            

            The relevant columns for specific terms are as follows:
            - "cashback", "total cashback", or similar terms refer to "Estimate Optimise Cashback Value".
            - "order amount", "total order amount", or similar terms refer to "Estimate Order Value".

            The 'Conversion Time' column uses the format `dd/mm/yyyy hh:mm`. 
            Please ensure that the 'Conversion Time' column is parsed with the correct format (`%d/%m/%Y %H:%M`), and handle any errors during the parsing process by using the `errors='coerce'` option so that any invalid date values are converted to `NaT`.
            If a column uses the to_period() function (e.g., for months), ensure that the result is converted to a string using .astype(str) to avoid serialization errors when plotting with Plotly or processing JSON data. 
            The user has requested the following:
            {query}

            **Important:** 
            - Return only the Python code. 
            - Do not include any additional text, explanations, or tags.
            - Skip all reasoning steps. Do not include `<think>` or any other meta-content.

            Generate Python code that can process this request and provide the answer.
            The Python code should use the pandas library to process the dataset.If the query involves generating a graph or plot, use Plotly for visualization,
            and ensure to display the plot using st.plotly_chart(fig) for integration with a Streamlit app instead of using fig.show().
            Return only the Python code, no explanations or extra text.
            Please generate Python code that can process this request and provide the answer. Do **not include** any markdown or code block formatting (` ```python` or ` ``` `). Just give the Python code directly.
            my dataset file name is: m1_data.csv
            when generating Python code, ensure the result is displayed first using Streamlit functions (`st.write()`, `st.dataframe()`, etc.). Once the result is displayed, store it in the variable 'output_data' in the last line of the code. Ensure that the result is properly displayed **before** being assigned to the 'output_data' variable.
            If the result is not a graph or fig, ensure that `output_data` stores the result incluing both the description and the calculated result.
            Only if the result is a graph or plot, do not include any descriptive text in `output_data`.
            
            Generate the **pure Python code** that processes this request.  
            DO NOT include `<think>`</think>, reasoning steps, or explanations in the output.  
            Return only the **Python code**, nothing else.
            
            """

            python_code = query_deepseek(deepseek_prompt)

            #st.write("Generated Python Code:")
            #st.code(python_code)

            #added
            raw_output = query_deepseek(deepseek_prompt)
            cleaned_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL).strip()
            python_code = cleaned_output
            

            #st.write("Generated Python Code after cleaned:")
            #st.code(python_code)

            try:
                # Define a dictionary for the code execution environment
                exec_globals = {"df": df, "pd": pd, "px": px, "st": st}

                # Execute the generated Python code
                exec(python_code, exec_globals)

                # Check if the output is a Plotly figure
                if isinstance(exec_globals.get('fig'), go.Figure):
                    explanation_prompt = f"""
                    You are a helpful data analyst who can explain data insights in a meaningful manner.
                    Analyze the following graph:
                    {exec_globals.get('fig')}
                    Provide insights focusing on:
                    - Any significant trends, low/high points, and potential implications.
                    - Key observations and their impact on business decision-making.
                    """
                else:
                    output_data = exec_globals.get('output_data', None)
                    explanation_prompt = f"""
                    You are a helpful data analyst who can explain data insights in a meaningful manner.
                    Analyze the following output:
                    {output_data}
                    Provide insights focusing on:
                    - Key observations and their significance.
                    - Any notable trends or patterns and their implications.
                    """

                # Get insights using DeepSeek LLM
                explanation = query_deepseek(explanation_prompt)

                #added
                # Remove <think> tags from the explanation output
                cleaned_explanation = re.sub(r"<think>.*?</think>", "", explanation, flags=re.DOTALL).strip()
                explanation = cleaned_explanation

                # Display only the explanation in Streamlit
                st.write("Explanation:")
                st.write(explanation)

                # Store assistant's response in the conversation history
                st.session_state.conversation.append({"role": "assistant", "content": explanation})

            except SyntaxError as e:
                st.error("Oops! The generated code had a syntax issue. Please try again.")
                st.error(f"Syntax Error in generated code: {e}")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again.")
                st.error(f"An error occurred while executing the code: {e}")



# Run the app
if __name__ == "__main__":
    main()