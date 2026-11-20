import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
# Load the API Key to Environment Variable
load_dotenv()
DATA_FILE = Path(__file__).parent / "data" / "responses" / "employees.json"
print(os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",temperature=0)

# Define a MCP Tool
@tool
def check_employee_asset(employee_id:str)->str:
    """Look for an Employee's Laptop and Asset Details"""
    if not DATA_FILE.exists():
        return f"Error: Employee database file not found at {DATA_FILE}."
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            employees = json.load(f)
        record = employees.get(employee_id.strip().upper())
        if not record:
            return f"No asset record found for employee ID '{employee_id}'."

        return f"Asset record for {employee_id}: {json.dumps(record)}"
    except json.JSONDecodeError:
        return "Error: employees.json contains invalid JSON formatting."
    except Exception as e:
        return f"Error reading employee database: {str(e)}"

# Define the Pydantic JSON Schema
class TriageDecision(BaseModel):
    employee_id: str = Field(description="Extracted employee ID, or 'UNKNOWN'.")
    category: Literal["Network", "Hardware", "Access", "Other"]
    priority: Literal["Low", "Medium", "High"]
    recommended_action: str

def run_triage(
user_input: str, context_rules: str, on_step) -> dict:
    def log_step(msg: str):
        if on_step:
            on_step(msg)

    log_step("1️⃣ Binding tools to Gemini...")
    llm_with_tools = llm.bind_tools([check_employee_asset])

    messages = [
        SystemMessage(content=(
            "You are an enterprise IT triage assistant.\n"
            "RULES:\n"
            "1. Always call `check_employee_asset` if an employee ID is present.\n"
            "2. Base priority strictly on the provided Policy. Do not guess."
        )),
        HumanMessage(content=f"Policy:\n{context_rules}\n\nTicket:\n{user_input}")
    ]

    log_step("2️⃣ Analyzing input and checking tool requirements...")
    ai_msg = llm_with_tools.invoke(messages)

    tool_trace = None
    if ai_msg.tool_calls:
        messages.append(ai_msg)
        for call in ai_msg.tool_calls:
            log_step(f"3️⃣ Executing tool `{call['name']}` ({call['args']})...")
            tool_output = check_employee_asset.invoke(call["args"])
            tool_trace = tool_output
            messages.append(ToolMessage(content=tool_output, tool_call_id=call["id"]))
    else:
        log_step("3️⃣ No external tool lookup required.")

    log_step("4️⃣ Enforcing Pydantic structured output schema...")
    messages.append(HumanMessage(content="Return the final structured TriageDecision JSON."))
    structured_llm = llm.with_structured_output(TriageDecision)
    decision = structured_llm.invoke(messages)

    # Return a standardized envelope that any UI boilerplate can render
    return {
        "metrics": {
            "Employee ID": decision.employee_id,
            "Category": decision.category,
            "Priority": decision.priority,
            #"Confidence": f"{decision.confidence_score}%",
        },
        "primary_message": decision.recommended_action,
        "tool_trace": tool_trace,
        "raw_payload": decision.model_dump(),
    }
