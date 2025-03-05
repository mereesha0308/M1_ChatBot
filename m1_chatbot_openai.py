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

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("m1_data.csv")

df = load_data()

import openai
import os

# Set your API key securely
openai.api_key = "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"
 # Replace with your actual key
# Alternatively, you can use an environment variable:
# os.environ["OPENAI_API_KEY"] = "your-api-key"
# Then use: openai.api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI

client = OpenAI(api_key=openai.api_key)  # Initialize the client with API key

def query_openai(prompt):
    """
    Send a query to OpenAI and get Python code as a response.
    """
    response = client.chat.completions.create(
        model="gpt-4o",  # Use the latest available model
        messages=[
            {"role": "system", "content": "You are a helpful data assistant that generates Python code to process data."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    # Streamlit app starts here
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

            # Use OpenAI to generate Python code based on the user query
            openai_prompt = f"""
            You are a helpful assistant that generates Python code for data analysis. The dataset contains the following columns:
            {', '.join(df.columns)}

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

            The relevant columns for specific terms are as follows:
            - "cashback", "total cashback", or similar terms refer to "Estimate Optimise Cashback Value".
            - "order amount", "total order amount", or similar terms refer to "Estimate Order Value".

            The 'Conversion Time' column uses the format `dd/mm/yyyy hh:mm`. 
            Please ensure that the 'Conversion Time' column is parsed with the correct format (`%d/%m/%Y %H:%M`), and handle any errors during the parsing process by using the `errors='coerce'` option so that any invalid date values are converted to `NaT`.
            If a column uses the to_period() function (e.g., for months), ensure that the result is converted to a string using .astype(str) to avoid serialization errors when plotting with Plotly or processing JSON data. 
            The user has requested the following:
            {query}

            Generate Python code that can process this request and provide the answer.
            The Python code should use the pandas library to process the dataset.If the query involves generating a graph or plot, use Plotly for visualization,
            and ensure to display the plot using st.plotly_chart(fig) for integration with a Streamlit app instead of using fig.show().
            Return only the Python code, no explanations or extra text.
            Please generate Python code that can process this request and provide the answer. Do **not include** any markdown or code block formatting (` ```python` or ` ``` `). Just give the Python code directly.
            my dataset file name is: m1_data.csv
            when generating Python code, ensure the result is displayed first using Streamlit functions (`st.write()`, `st.dataframe()`, etc.). Once the result is displayed, store it in the variable 'output_data' in the last line of the code. Ensure that the result is properly displayed **before** being assigned to the 'output_data' variable.
            If the result is not a graph or fig, ensure that `output_data` stores the result incluing both the description and the calculated result.
            Only if the result is a graph or plot, do not include any descriptive text in `output_data`.
            """

            python_code = query_openai(openai_prompt)

            #st.write("Generated Python Code:")
            #st.code(python_code)

            try:
                # Define a dictionary for the code execution environment
                exec_globals = {"df": df, "pd": pd, "px": px, "st": st}

                # Execute the Python code in the given environment
                exec(python_code, exec_globals)

                # Check if the output is a Plotly figure
                if isinstance(exec_globals.get('fig'), go.Figure):
                    # Generate explanation prompt for the graph
                    explanation_prompt = f"""
                    You are a data analyst working on business insights for M1 based in Singapore in a meaningful manner.
                    M1 partners with a set of merchants to offer cashback promotions to its customers. These offers are designed to increase engagement and encourage more transactions and to satisfied the customer with the M1 business.

                    Analyze the following graph:
                    {exec_globals.get('fig')}
                    Provide insights focusing on:
                    - Any significant trends, low/high points, and potential implications.
                    - Key observations and their impact on business decision-making.
                    """

                else:
                    # Handle other output types (DataFrame, list, dict, or generic text)
                    output_data = exec_globals.get('output_data', None)

                    # Generate explanation prompt without displaying the data in Streamlit
                    explanation_prompt = f"""
                    You are a data analyst working on business insights for M1 based in Singapore in a meaningful manner.
                    M1 partners with a set of merchants to offer cashback promotions to its customers. These offers are designed to increase engagement and encourage more transactions and to satisfied the customer with the M1 business.

                    You are a helpful data analyst who can explain data insights in a meaningful manner.
                    Analyze the following output:
                    {output_data}
                    Provide insights focusing on:
                    - Key observations and their significance.
                    - Any notable trends or patterns and their implications.
                    """

                # Pass the explanation prompt to the LLM
                explanation = query_openai(explanation_prompt)

                # Display only the explanation in Streamlit
                st.write("Explanation:")
                st.write(explanation)

                # Store assistant's response in the conversation history
                st.session_state.conversation.append({"role": "assistant", "content": explanation})

                # Now show results progressively
                #if len(st.session_state.conversation) > 1:
                    # Show first response first and second after that
                    #st.write("First Query Result:")
                    #st.write(st.session_state.conversation[0]["content"])

                    # Then show the second response (current one)
                    #st.write("Second Query Result:")
                    #st.write(explanation)

            except SyntaxError as e:
                st.error("Oops! The generated code had a syntax issue. Please try again.")
                st.error(f"Syntax Error in generated code: {e}")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again.")
                st.error(f"An error occurred while executing the code: {e}")


# Run the app
if __name__ == "__main__":
    main()