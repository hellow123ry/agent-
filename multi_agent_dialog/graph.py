from langgraph.graph import StateGraph, END
from multi_agent_dialog.state import DialogState
from multi_agent_dialog.router import route_intent
from multi_agent_dialog.experts import dining_expert, hotel_expert, default_expert, travel_expert, entertainment_expert

def get_next_node(state: DialogState) -> str:
    intent = state.get("current_intent")
    if intent == "dining":
        return "dining_node"
    elif intent == "hotel":
        return "hotel_node"
    elif intent == "travel":
        return "travel_node"
    elif intent == "entertainment":
        return "entertainment_node"
    # 当意图是 unknown 或者其他时，交给默认闲聊节点处理
    return "default_node"

def run_dialog(initial_state: DialogState) -> DialogState:
    workflow = StateGraph(DialogState)
    
    workflow.add_node("router", route_intent)
    workflow.add_node("dining_node", dining_expert)
    workflow.add_node("hotel_node", hotel_expert)
    workflow.add_node("travel_node", travel_expert)
    workflow.add_node("entertainment_node", entertainment_expert)
    workflow.add_node("default_node", default_expert)
    
    workflow.set_entry_point("router")
    workflow.add_conditional_edges("router", get_next_node)
    
    workflow.add_edge("dining_node", END)
    workflow.add_edge("hotel_node", END)
    workflow.add_edge("travel_node", END)
    workflow.add_edge("entertainment_node", END)
    workflow.add_edge("default_node", END)
    
    app = workflow.compile()
    return app.invoke(initial_state)
