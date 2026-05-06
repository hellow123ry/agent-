from __future__ import annotations

import json

# 模拟的餐厅数据库
MOCK_RESTAURANTS = [
    {"name": "全聚德烤鸭", "type": "烤肉店/烤鸭", "capacity": [2, 3, 4, 6, 8], "status": "有位"},
    {"name": "海底捞火锅", "type": "火锅", "capacity": [2, 4, 6], "status": "爆满"},
    {"name": "汉拿山韩式烤肉", "type": "烤肉店", "capacity": [2, 3, 4], "status": "有位"},
]

# 模拟的酒店数据库
MOCK_HOTELS = [
    {"name": "希尔顿酒店", "location": "市中心", "type": "豪华", "price": 1200, "status": "有房"},
    {"name": "如家快捷酒店", "location": "火车站", "type": "经济", "price": 300, "status": "有房"},
    {"name": "桔子水晶酒店", "location": "市中心", "type": "舒适", "price": 600, "status": "满房"},
]


def _get_restaurants(knowledgebase: dict | None = None) -> list[dict]:
    if knowledgebase and isinstance(knowledgebase.get("restaurants"), list):
        return knowledgebase["restaurants"]
    return MOCK_RESTAURANTS


def _get_hotels(knowledgebase: dict | None = None) -> list[dict]:
    if knowledgebase and isinstance(knowledgebase.get("hotels"), list):
        return knowledgebase["hotels"]
    return MOCK_HOTELS


def search_restaurants_from_knowledgebase(
    restaurant_type: str,
    guests: int,
    knowledgebase: dict | None = None,
) -> str:
    results = []
    for restaurant in _get_restaurants(knowledgebase):
        if restaurant_type in restaurant["type"] and guests in restaurant["capacity"]:
            results.append(f"{restaurant['name']} ({restaurant['status']})")

    if not results:
        return json.dumps({"status": "error", "message": f"抱歉，没有找到适合 {guests} 人的 {restaurant_type}。"})
    return json.dumps({"status": "success", "restaurants": results})


def search_hotels_from_knowledgebase(
    location: str,
    hotel_type: str,
    knowledgebase: dict | None = None,
) -> str:
    results = []
    for hotel in _get_hotels(knowledgebase):
        if (location in hotel["location"] or not location) and (hotel_type in hotel["type"] or not hotel_type):
            results.append(f"{hotel['name']} - {hotel['price']}元/晚 ({hotel['status']})")

    if not results:
        return json.dumps({"status": "error", "message": f"抱歉，没有在 {location} 找到合适的 {hotel_type} 酒店。"})
    return json.dumps({"status": "success", "hotels": results})


def book_hotel_from_knowledgebase(
    hotel_name: str,
    check_in_date: str,
    check_out_date: str,
    price_confirmed: bool = False,
    knowledgebase: dict | None = None,
) -> str:
    if not price_confirmed:
        return json.dumps({
            "status": "blocked_by_filter",
            "message": "系统安全拦截：您正在尝试在用户未确认价格的情况下直接下单。请先向用户报价，并询问用户是否接受此价格，然后再尝试调用此工具预订。"
        })

    hotel_info = next((hotel for hotel in _get_hotels(knowledgebase) if hotel["name"] == hotel_name), None)
    if not hotel_info:
        return json.dumps({"status": "error", "message": f"找不到名为 {hotel_name} 的酒店。"})

    if hotel_info["status"] != "有房":
        return json.dumps({"status": "error", "message": f"{hotel_name} 目前已经满房，无法预订。"})

    return json.dumps({
        "status": "success",
        "message": f"成功为您预订了 {hotel_name}，入住时间：{check_in_date}，退房时间：{check_out_date}，总价：{hotel_info['price']}元。"
    })

def search_restaurants(restaurant_type: str, guests: int) -> str:
    """
    根据餐厅类型和就餐人数查询餐厅余位信息。
    
    Args:
        restaurant_type: 餐厅类型，如 "烤肉店"、"火锅" 等。
        guests: 就餐人数。
    """
    return search_restaurants_from_knowledgebase(restaurant_type, guests)

def search_hotels(location: str, hotel_type: str) -> str:
    """
    根据位置和酒店类型查询酒店房态信息。
    
    Args:
        location: 酒店位置，如 "市中心"、"火车站" 等。
        hotel_type: 酒店类型，如 "豪华"、"经济" 等。
    """
    return search_hotels_from_knowledgebase(location, hotel_type)

def book_hotel(hotel_name: str, check_in_date: str, check_out_date: str, price_confirmed: bool = False) -> str:
    """
    预订指定的酒店。这是一个敏感操作，必须确认用户已经知晓并同意了价格。
    
    Args:
        hotel_name: 酒店名称，如 "希尔顿酒店"
        check_in_date: 入住日期
        check_out_date: 退房日期
        price_confirmed: 大模型必须判断用户是否已经明确确认了该酒店的价格。如果用户没有确认过价格，必须传 False。
    """
    return book_hotel_from_knowledgebase(
        hotel_name=hotel_name,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        price_confirmed=price_confirmed,
    )

def update_blackboard(location: str = "", people_count: int = None, date: str = "") -> str:
    """
    更新全局信息黑板。当在对话中发现用户的长效偏好（如所在城市、常用出行人数、日期）时，调用此工具保存。
    
    Args:
        location: 用户提到的地理位置、城市或商圈（如 "北京"、"市中心"）。
        people_count: 用户提到的人数（如 3）。
        date: 用户提到的通用日期（如 "明天"）。
    """
    return json.dumps({
        "status": "success",
        "message": "黑板信息已更新",
        "updates": {
            k: v for k, v in [("location", location), ("people_count", people_count), ("date", date)] if v
        }
    })
