import os
from langchain_openai import ChatOpenAI

def get_llm():
    """获取配置好的 ModelHub 大模型实例"""
    # 优先从环境变量获取，如果没有则使用硬编码的真实 Key
    ak = os.getenv("OPENAI_API_KEY", "HlRoRaHvn9Zbg6HZmbwVjjhgAxeS9Wp7_GPT_AK")
    # 修改 base_url 为字节内部 ModelHub 的标准 OpenAI 兼容网关地址
    base_url = os.getenv("API_BASE_URL", "http://aidp.bytedance.net/api/modelhub/online/v2/crawl/openai/deployments/gpt_openapi")
    
    return ChatOpenAI(
        model="gpt-5.4-2026-03-05", # 更新为用户指定的模型
        openai_api_key=ak,
        base_url=base_url,
        max_tokens=1000,
        temperature=0.7,
        # ModelHub要求
        default_headers={
            "Api-Key": ak,
            "x-tt-logid": "multi_agent_dialog_system_logid"
        },
        model_kwargs={
            "extra_headers": {"x-tt-logid": "multi_agent_dialog_system_logid"}
        }
    )
