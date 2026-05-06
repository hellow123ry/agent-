import json
from multi_agent_dialog.tools import book_hotel

def test_book_hotel_blocked_by_filter():
    # 测试未确认价格的情况
    result = book_hotel(
        hotel_name="希尔顿酒店",
        check_in_date="明天",
        check_out_date="后天",
        price_confirmed=False
    )
    result_dict = json.loads(result)
    assert result_dict["status"] == "blocked_by_filter"
    assert "系统安全拦截" in result_dict["message"]

def test_book_hotel_success():
    # 测试已确认价格的情况
    result = book_hotel(
        hotel_name="希尔顿酒店",
        check_in_date="明天",
        check_out_date="后天",
        price_confirmed=True
    )
    result_dict = json.loads(result)
    assert result_dict["status"] == "success"
    assert "成功为您预订" in result_dict["message"]
    
def test_book_hotel_full():
    # 测试已确认价格但满房的情况
    result = book_hotel(
        hotel_name="桔子水晶酒店",
        check_in_date="明天",
        check_out_date="后天",
        price_confirmed=True
    )
    result_dict = json.loads(result)
    assert result_dict["status"] == "error"
    assert "满房" in result_dict["message"]