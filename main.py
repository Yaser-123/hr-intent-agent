from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from uipath.models import CreateAction
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.fake_chat_models import FakeChatModel
import json, re
import os
# ===== 1. LLM Setup =====
# Using a mock LLM for testing without API key
class MockHRLLM(FakeChatModel):
    """Mock LLM that detects HR intents from keywords"""
    def _call(self, messages, stop=None, **kwargs):
        # Get the last message content
        user_message = messages[-1].content if messages else ""
        
        # Simple keyword-based intent detection
        intents = []
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['leave', 'vacation', 'pto', 'time off', 'holiday']):
            intents.append("LeaveRequest")
        if any(word in user_lower for word in ['laptop', 'phone', 'equipment', 'asset', 'device']):
            intents.append("AssetRequest")
        if any(word in user_lower for word in ['address', 'move', 'relocation', 'location']):
            intents.append("AddressUpdate")
        if any(word in user_lower for word in ['expense', 'reimbursement', 'receipt', 'claim']):
            intents.append("ExpenseReimbursement")
        
        response = {
            "intents": intents,
            "confidence": 0.9 if intents else 0.0
        }
        return json.dumps(response)
llm = MockHRLLM()
# ===== 2. Define State (combined input/output) =====
class GraphState(BaseModel):
    user_prompt: str = Field(..., title="User Prompt")
    intents: list[str] = Field(default_factory=list, title="Detected HR Intents")
# ===== 3. Nodes =====
def extract_intents(state: GraphState) -> GraphState:
    prompt = f"""
    You are an HR assistant. Identify all HR-related intents from this message.
    Possible intents: LeaveRequest, AssetRequest, AddressUpdate, ExpenseReimbursement.
    Respond strictly as JSON: {{ "intents": [...], "confidence": 0.0–1.0 }}
    Message: "{state.user_prompt}"
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    print('Response', response.content)
    match = re.search(r"\{.*\}", response.content, re.S)
    result = json.loads(match.group(0)) if match else {"intents": []}
    print(result)
    return GraphState(user_prompt=state.user_prompt, intents=result.get("intents", []))
def validate_with_human(state: GraphState) -> Command:
    """
    Escalates to Action Center if no intents were found.
    Waits for human input and updates state upon completion.
    """
    user_prompt = state.user_prompt
    intents = state.intents or []
    if not intents:
        #  Create Action for Human Validation
        action_data = interrupt(
            CreateAction(
                app_name="MultiIntentIdentification_App",
                title="Please identify all intents (comma separated)",
                data={
                    "User_Prompt": user_prompt,
                    "Intents": ",".join(intents)
                },
                app_version=1,
                app_folder_path="Shared"
            )
        )
        print(" Raw Action Center return:", action_data)
        #  Parse returned Action Center data (robust handling)
        updated_intents_str = ""
        if isinstance(action_data, dict):
            # Case 1: returned as dict with nested output
            if "output" in action_data:
                updated_intents_str = action_data["output"].get("Intents", "")
            else:
                updated_intents_str = action_data.get("Intents", "")
        elif hasattr(action_data, "output"):
            # Case 2: returned as object
            updated_intents_str = action_data.output.get("Intents", "")
        print(" Extracted Intents from Action Center:", updated_intents_str)
        updated_intents = [
            i.strip() for i in updated_intents_str.split(",") if i.strip()
        ]
        #  Return Command to update state after resume
        return Command(
            update={
                "intents": updated_intents or state.intents,
                "user_prompt": user_prompt
            }
        )
    # If intents already exist, just continue
    # return Command(update={"intents": intents, "user_prompt": user_prompt})
def route_intents(state: GraphState) -> GraphState:
    print("Intents identified:", ", ".join(state.intents))
    return state
# ===== 4. Build Graph =====
graph = StateGraph(GraphState)
graph.add_node("ExtractIntents", extract_intents)
graph.add_node("ValidateWithHuman", validate_with_human)
graph.add_node("RouteIntents", route_intents)
graph.add_edge(START, "ExtractIntents")
graph.add_edge("ExtractIntents", "ValidateWithHuman")
graph.add_edge("ValidateWithHuman", "RouteIntents")
graph.add_edge("RouteIntents", END)
# ===== 5. Compile App =====
app = graph.compile()