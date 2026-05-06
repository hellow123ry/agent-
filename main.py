from multi_agent_dialog.graph import run_dialog
from multi_agent_dialog.state import DialogState
from langchain_core.messages import HumanMessage
from app.services.knowledgebase_service import load_knowledgebase

def main():
    print("=======================================")
    print("  欢迎使用生活服务 AI-Agent 智能助理！  ")
    print("  （输入 'q' 或 'quit' 退出聊天）       ")
    print("=======================================\n")
    
    # 初始化对话状态
    state = DialogState(
        messages=[],
        task_stack=[],
        active_task="",
        current_intent="",
        global_blackboard={},
        knowledgebase=load_knowledgebase(),
    )
    
    while True:
        try:
            user_input = input("🧑 提问: ")
            if user_input.strip().lower() in ['q', 'quit', 'exit']:
                print("👋 再见！")
                break
                
            if not user_input.strip():
                continue
                
            # 将用户输入封装为 HumanMessage 加入历史消息
            state["messages"].append(HumanMessage(content=user_input))
            
            # 运行图流转
            print("🤖 Agent 思考中...")
            state = run_dialog(state)
            
            # 打印最新的回复 (AIMessage)
            last_reply = state["messages"][-1].content
            print(f"🤖 回复: {last_reply}\n")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
