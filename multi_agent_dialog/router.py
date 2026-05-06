from multi_agent_dialog.state import DialogState, push_task
from multi_agent_dialog.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.trace_service import get_active_trace_collector
import time

def route_intent(state: DialogState) -> DialogState:
    trace_collector = get_active_trace_collector()
    started = time.time()
    llm = get_llm()
    active_task = state.get("active_task", "")
    task_stack = state.get("task_stack", [])
    
    system_prompt = f"""你是一个意图识别助手。根据用户的当前输入和历史对话，判断用户的**当前**意图。
    当前正在进行的任务是: {active_task if active_task else '无'}
    被挂起的任务有: {task_stack if task_stack else '无'}
    
    如果用户正在预订餐厅、讨论吃饭等，返回 "dining"。
    如果用户正在预订酒店、讨论住宿等，返回 "hotel"。
    如果用户正在规划出行、打车、买票等，返回 "travel"。
    如果用户正在讨论休闲娱乐活动（电影、KTV、展览等），返回 "entertainment"。
    如果不属于上述情况（如闲聊、问候等），返回 "unknown"。
    
    注意：
    1. 如果用户是在回复之前的问题（比如回答“是的”、“明天”），请结合历史对话推断所属的意图。
    2. 如果用户突然问了一个不相关的问题（如在订餐时问你能做什么），意图应判断为 "unknown"。
    3. 如果用户主动回到被挂起的任务，返回那个任务对应的意图。
    
    只能返回 "dining" 或 "hotel" 或 "travel" 或 "entertainment" 或 "unknown"，不要包含其他任何字符。"""
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state.get("messages", []))
    
    try:
        response = llm.invoke(messages)
        intent = response.content.strip().lower()
        if intent not in ["dining", "hotel", "travel", "entertainment", "unknown"]:
            intent = "unknown"
    except Exception as e:
        print(f"LLM 路由失败: {e}")
        intent = "unknown"
        
    # 栈式记忆系统：处理意图跳转
    new_state = {**state, "current_intent": intent}
    
    # 如果用户的意图发生了改变，并且之前的任务还没有结束
    if active_task and intent != active_task:
        # 将被打断的 active_task 压入挂起栈
        new_state = push_task(new_state, active_task)
        
    # 如果用户的意图正好是被挂起的某个任务，从栈里把它清理掉
    new_stack = new_state.get("task_stack", [])
    if intent in new_stack:
        new_stack.remove(intent)
        new_state["task_stack"] = new_stack
        
    # 更新当前的 active_task
    new_state["active_task"] = intent

    if trace_collector:
        trace_collector.record(
            "router",
            {
                "intent": intent,
                "active_task_before": active_task,
                "task_stack_before": list(task_stack),
            },
            latency_ms=int((time.time() - started) * 1000),
        )
        
    return new_state
