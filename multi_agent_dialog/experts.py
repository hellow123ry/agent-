from multi_agent_dialog.state import DialogState, pop_task
from multi_agent_dialog.llm import get_llm
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from multi_agent_dialog.tools import (
    book_hotel,
    book_hotel_from_knowledgebase,
    search_hotels,
    search_hotels_from_knowledgebase,
    search_restaurants,
    search_restaurants_from_knowledgebase,
    update_blackboard,
)
from app.services.trace_service import get_active_trace_collector
import json

MAX_TOOL_CALL_ROUNDS = 3

def _handle_task_completion(state: DialogState, llm, base_messages, original_response_content) -> DialogState:
    """处理任务完成后的弹栈恢复逻辑"""
    new_state = {**state}
    
    # 清空当前已完成的任务
    new_state["active_task"] = ""
    
    task_stack = new_state.get("task_stack", [])
    if task_stack:
        # 如果栈里有被挂起的任务，弹出它
        new_state, popped_task = pop_task(new_state)
        new_state["active_task"] = popped_task
        
        # 让大模型生成一句“话题转回”的话
        resume_prompt = f"""你刚才已经成功帮用户完成了当前任务。
        但用户之前还有一个被挂起的任务：【{popped_task}】。
        请结合历史对话，在之前的回复后面，加上一句自然的话题过渡，
        提醒用户回到【{popped_task}】任务，并继续询问该任务缺失的信息。
        例如：“顺便提一下，您之前说的订餐厅，需要订几点的？”
        请只输出这句补充的话，不要包含其他内容。"""
        
        resume_messages = base_messages + [
            AIMessage(content=original_response_content),
            SystemMessage(content=resume_prompt)
        ]
        try:
            resume_response = llm.invoke(resume_messages)
            # 拼接最终回复
            final_content = original_response_content + "\n\n" + resume_response.content
            return new_state, AIMessage(content=final_content)
        except Exception as e:
            print(f"恢复任务生成失败: {e}")
            return new_state, AIMessage(content=original_response_content)
            
    return new_state, AIMessage(content=original_response_content)


def _apply_blackboard_updates(state: DialogState, args: dict) -> None:
    blackboard = state.setdefault("global_blackboard", {})
    if args.get("location"):
        blackboard["location"] = args["location"]
    if args.get("people_count"):
        blackboard["people_count"] = args["people_count"]
    if args.get("date"):
        blackboard["date"] = args["date"]

    trace_collector = get_active_trace_collector()
    if trace_collector:
        trace_collector.record("blackboard_update", {"updates": dict(args)})


def _execute_tool_call(tool_call: dict, state: DialogState) -> ToolMessage:
    name = tool_call["name"]
    args = tool_call["args"]
    trace_collector = get_active_trace_collector()
    knowledgebase = state.get("knowledgebase")

    if trace_collector:
        trace_collector.record("tool_call", {"tool_name": name, "args": args})

    if name == "search_restaurants":
        tool_result = search_restaurants_from_knowledgebase(
            restaurant_type=args.get("restaurant_type", ""),
            guests=args.get("guests", 1),
            knowledgebase=knowledgebase,
        )
    elif name == "search_hotels":
        tool_result = search_hotels_from_knowledgebase(
            location=args.get("location", ""),
            hotel_type=args.get("hotel_type", ""),
            knowledgebase=knowledgebase,
        )
    elif name == "book_hotel":
        tool_result = book_hotel_from_knowledgebase(
            hotel_name=args.get("hotel_name", ""),
            check_in_date=args.get("check_in_date", ""),
            check_out_date=args.get("check_out_date", ""),
            price_confirmed=args.get("price_confirmed", False),
            knowledgebase=knowledgebase,
        )
    elif name == "update_blackboard":
        tool_result = update_blackboard(
            location=args.get("location", ""),
            people_count=args.get("people_count"),
            date=args.get("date", ""),
        )
        _apply_blackboard_updates(state, args)
    else:
        tool_result = json.dumps({"status": "error", "message": f"未知工具: {name}"})

    if trace_collector:
        trace_collector.record(
            "tool_result",
            {
                "tool_name": name,
                "result": tool_result,
            },
        )

    return ToolMessage(content=tool_result, tool_call_id=tool_call["id"])


def _run_tool_call_loop(
    llm_with_tools,
    state: DialogState,
    messages: list,
    first_response,
    max_tool_rounds: int = MAX_TOOL_CALL_ROUNDS,
):
    current_response = first_response
    new_state = {**state, "messages": state.get("messages", []) + [current_response]}
    tool_rounds = 0

    while current_response.tool_calls:
        if tool_rounds >= max_tool_rounds:
            trace_collector = get_active_trace_collector()
            if trace_collector:
                trace_collector.record(
                    "error",
                    {"reason": "max_tool_rounds_exceeded", "max_tool_rounds": max_tool_rounds},
                )
            fallback_response = AIMessage(
                content="抱歉，当前请求触发了过多次工具调用。为了避免长时间卡住，我先停止自动执行。请您缩小条件或分步确认。"
            )
            new_state["messages"][-1] = fallback_response
            return new_state, fallback_response, messages

        tool_messages = [
            _execute_tool_call(tool_call, new_state)
            for tool_call in current_response.tool_calls
        ]
        messages.append(current_response)
        messages.extend(tool_messages)
        new_state["messages"].extend(tool_messages)

        current_response = llm_with_tools.invoke(messages)
        new_state["messages"].append(current_response)
        tool_rounds += 1

    return new_state, current_response, messages

def dining_expert(state: DialogState) -> DialogState:
    llm = get_llm()
    # 绑定餐厅查询工具和黑板工具
    llm_with_tools = llm.bind_tools([search_restaurants, update_blackboard])
    
    blackboard_info = state.get("global_blackboard", {})
    
    system_prompt = f"""你是一个专业的、灵活的餐饮预订专家。
    请帮助用户完成餐厅预订，你需要收集的关键信息有：餐厅类型、就餐人数、就餐时间。
    
    【全局信息黑板】：
    系统当前保存的用户长效偏好如下：{blackboard_info if blackboard_info else '无'}
    如果在黑板中找到了相关信息（如人数、日期），你可以直接使用，不要再重复向用户提问！
    如果在对话中用户提供了新的长效信息（如“我们在北京”、“我们一共3个人”），请立即调用 update_blackboard 工具将其写入黑板。
    
    【核心灵活性原则】：
    1. 不要像机器人一样死板地追问！如果用户对餐厅类型没有要求，或者说“随便”、“都行”，你必须理解这种灵活性，将对应的参数设为空字符串 "" 去查询所有餐厅。
    2. 你不必非要等所有信息都收集齐才去查询。如果你已经知道了就餐人数，就可以先去工具查一下目前有哪些餐厅有空位，然后报给用户。
    3. 每次只问一个缺失的**必要**信息（通常人数和时间是必要的，类型可以是随便的）。
    
    当你准备查询时，必须调用 search_restaurants 工具查询是否有空位。
    根据工具返回的结果，向用户推荐有空位的餐厅。如果都满了，请让用户换个类型或时间。
    当用户最终确认了预订（如选定了某家有位的餐厅和时间），请告诉用户预订成功，并总结预订信息。
    **重要指令**：当且仅当预订完全成功、你已经输出总结信息时，请在回复的最后加上标识符 [TASK_COMPLETED]。
    请用专业、友好、灵活的语气回复。"""
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state.get("messages", []))
        
    try:
        first_response = llm_with_tools.invoke(messages)
        new_state, response, messages = _run_tool_call_loop(
            llm_with_tools, state, messages, first_response
        )
            
        # 检查是否完成了任务
        if "[TASK_COMPLETED]" in response.content:
            clean_content = response.content.replace("[TASK_COMPLETED]", "").strip()
            final_state, updated_response = _handle_task_completion(new_state, llm, messages, clean_content)
            final_state["messages"][-1] = updated_response
            return final_state
            
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        error_msg = AIMessage(content="不好意思，我暂时遇到了一些问题，无法为您预订餐厅。")
        new_state = {**state}
        new_state["messages"] = state.get("messages", []) + [error_msg]
        return new_state
        
    return new_state

def hotel_expert(state: DialogState) -> DialogState:
    llm = get_llm()
    # 绑定酒店查询工具、预订工具和黑板工具
    llm_with_tools = llm.bind_tools([search_hotels, book_hotel, update_blackboard])
    
    blackboard_info = state.get("global_blackboard", {})
    
    system_prompt = f"""你是一个专业的、灵活的酒店预订专家。
    请帮助用户完成酒店预订，你需要收集的关键信息有：入住时间、退房时间、酒店位置、酒店类型(如经济/豪华)。
    
    【全局信息黑板】：
    系统当前保存的用户长效偏好如下：{blackboard_info if blackboard_info else '无'}
    如果在黑板中找到了相关信息（如位置、日期），你可以直接使用，不要再重复向用户提问！
    如果在对话中用户提供了新的长效信息（如“我们在北京”、“明天去上海”），请立即调用 update_blackboard 工具将其写入黑板。
    
    【核心灵活性原则】：
    1. 不要像机器人一样死板地追问！如果用户说“随便”、“有什么订什么”、“哪个能订订哪个”，或者用户不愿意提供某个具体条件，你必须理解这种灵活性，将对应的参数设为空字符串 ""，然后直接去查询！
    2. 你不必非要等所有信息都收集齐才去查询。只要用户有了模糊的意向，你就可以先用 search_hotels 工具查一查，然后把结果报给用户供其挑选。
    3. 每次只问一个缺失的**必要**信息（通常时间是必要的，位置和类型可以是随便的）。
    
    【预订流程与安全规则】：
    1. 当你准备查询时，必须调用 search_hotels 工具查询房态和价格，并向用户推荐有房的酒店，告知价格。
    2. **安全规则**：如果你向用户推荐了某家酒店，并且用户同意预订，你必须先确认用户是否知晓并同意该酒店的价格。
    3. 只有在确认用户接受价格后，你才能调用 book_hotel 工具进行真正的预订。
    4. 如果 book_hotel 返回被过滤器拦截的信息，请诚实地按照提示内容向用户确认价格。
    
    当 book_hotel 返回预订成功时，请告诉用户预订成功，并总结预订信息。
    **重要指令**：当且仅当 book_hotel 工具返回预订成功、且你已经输出总结信息时，请在回复的最后加上标识符 [TASK_COMPLETED]。
    请用专业、友好、极其灵活的语气回复。"""
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state.get("messages", []))
        
    try:
        first_response = llm_with_tools.invoke(messages)
        new_state, response, messages = _run_tool_call_loop(
            llm_with_tools, state, messages, first_response
        )
            
        # 检查是否完成了任务
        if "[TASK_COMPLETED]" in response.content:
            clean_content = response.content.replace("[TASK_COMPLETED]", "").strip()
            final_state, updated_response = _handle_task_completion(new_state, llm, messages, clean_content)
            final_state["messages"][-1] = updated_response
            return final_state
            
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        error_msg = AIMessage(content="不好意思，我暂时遇到了一些问题，无法为您预订酒店。")
        new_state = {**state}
        new_state["messages"] = state.get("messages", []) + [error_msg]
        return new_state
        
    return new_state

def travel_expert(state: DialogState) -> DialogState:
    llm = get_llm()
    system_prompt = """你是一个专业的交通出行专家。
    请帮助用户规划或预订交通工具（如打车、买火车票、机票）。
    你需要向用户确认：出发地、目的地、出发时间、交通方式偏好。
    每次只问一个缺失的信息，不要一次性问太多。
    如果所有信息都收集齐了，请告诉用户预订成功（或规划完成），并总结行程信息。
    **重要指令**：当且仅当预订完全成功、你已经输出总结信息时，请在回复的最后加上标识符 [TASK_COMPLETED]。
    请用专业、友好的语气回复。"""
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state.get("messages", []))
        
    try:
        response = llm.invoke(messages)
        new_messages = state.get("messages", []) + [response]
        
        # 检查是否完成了任务
        if "[TASK_COMPLETED]" in response.content:
            clean_content = response.content.replace("[TASK_COMPLETED]", "").strip()
            new_state, updated_response = _handle_task_completion(state, llm, messages, clean_content)
            new_messages[-1] = updated_response
            return {**new_state, "messages": new_messages}
            
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        error_msg = AIMessage(content="不好意思，我暂时遇到了一些问题，无法为您安排出行。")
        new_messages = state.get("messages", []) + [error_msg]
        
    return {**state, "messages": new_messages}

def entertainment_expert(state: DialogState) -> DialogState:
    llm = get_llm()
    system_prompt = """你是一个专业的休闲娱乐专家。
    请帮助用户预订或推荐娱乐活动（如看电影、KTV、剧本杀、密室逃脱、游乐园等）。
    你需要向用户确认：活动类型、参与人数、期望的时间或地点。
    每次只问一个缺失的信息，不要一次性问太多。
    如果所有信息都收集齐了，请告诉用户预订成功，并总结活动信息。
    **重要指令**：当且仅当预订完全成功、你已经输出总结信息时，请在回复的最后加上标识符 [TASK_COMPLETED]。
    请用热情、活泼的语气回复。"""
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state.get("messages", []))
        
    try:
        response = llm.invoke(messages)
        new_messages = state.get("messages", []) + [response]
        
        # 检查是否完成了任务
        if "[TASK_COMPLETED]" in response.content:
            clean_content = response.content.replace("[TASK_COMPLETED]", "").strip()
            new_state, updated_response = _handle_task_completion(state, llm, messages, clean_content)
            new_messages[-1] = updated_response
            return {**new_state, "messages": new_messages}
            
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        error_msg = AIMessage(content="不好意思，我暂时遇到了一些问题，无法为您预订娱乐活动。")
        new_messages = state.get("messages", []) + [error_msg]
        
    return {**state, "messages": new_messages}

def default_expert(state: DialogState) -> DialogState:
    """处理日常闲聊和未明确意图的请求"""
    llm = get_llm()
    system_prompt = """你是一个友好的生活服务 AI 助理。
    你的主要职责是帮助用户解决本地生活服务需求，包括：
    1. 餐饮预订（餐厅、外卖等）
    2. 酒店住宿预订
    3. 交通出行安排（打车、买票）
    4. 休闲娱乐预订（电影、KTV、展览等）
    
    如果用户在闲聊、问候或者问你能做什么，请礼貌地回答，并向他们介绍你可以提供的这4类服务，引导他们使用。
    请保持语气亲切自然。"""
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state.get("messages", []))
        
    try:
        response = llm.invoke(messages)
        new_messages = state.get("messages", []) + [response]
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        error_msg = AIMessage(content="不好意思，我开小差了，能再重复一遍吗？")
        new_messages = state.get("messages", []) + [error_msg]
        
    return {**state, "messages": new_messages}
