# astrbot_xiuxian_plugin/systems/exploration_area_system.py
"""探索区域系统，处理玩家选择探索区域的逻辑"""

from ..database.repositories import player_repository
from ..config.cultivation_levels import LEVEL_ORDER

# 探索区域配置
EXPLORATION_AREAS = {
    "凡人": [
        {"name": "新手村周边", "description": "安全的修炼区域，适合初学者", "min_level": "凡人", "max_level": "凡人"},
        {"name": "凡人山脉", "description": "普通的山脉地带，偶尔能遇到低级妖兽", "min_level": "凡人", "max_level": "炼气"},
        {"name": "低阶灵矿外围", "description": "灵气稀薄的矿场外围，有一些基础材料", "min_level": "凡人", "max_level": "炼气"}
    ],
    "炼气": [
        {"name": "中低阶修士历练区", "description": "专门为炼气期修士准备的历练场所", "min_level": "炼气", "max_level": "筑基"},
        {"name": "普通山林", "description": "适合炼气期修士的山林地带", "min_level": "炼气", "max_level": "筑基"},
        {"name": "筑基期宗门后山", "description": "筑基期宗门的后山，有一定危险性", "min_level": "炼气", "max_level": "筑基"}
    ],
    "筑基": [
        {"name": "高阶修士试炼地", "description": "为筑基期修士准备的试炼场所", "min_level": "筑基", "max_level": "金丹"},
        {"name": "灵矿深处", "description": "灵矿的深处，有更丰富的资源和更强的妖兽", "min_level": "筑基", "max_level": "金丹"},
        {"name": "筑基期宗门内门", "description": "筑基期宗门的核心区域", "min_level": "筑基", "max_level": "金丹"}
    ],
    "金丹": [
        {"name": "金丹期禁地", "description": "金丹期修士的专属禁地", "min_level": "金丹", "max_level": "元婴"},
        {"name": "秘境入口", "description": "通往秘境的入口，机遇与危险并存", "min_level": "金丹", "max_level": "元婴"},
        {"name": "宗门核心区域", "description": "宗门的核心区域，有大量资源", "min_level": "金丹", "max_level": "元婴"}
    ],
    "元婴": [
        {"name": "元婴修士禁地", "description": "元婴期修士的专属禁地", "min_level": "元婴", "max_level": "化神"},
        {"name": "深海区域", "description": "神秘的深海地带，有强大的海族妖兽", "min_level": "元婴", "max_level": "化神"},
        {"name": "上古战场外围", "description": "上古战场的外围区域", "min_level": "元婴", "max_level": "化神"}
    ],
    "化神": [
        {"name": "化神期险地", "description": "化神期修士的专属险地", "min_level": "化神", "max_level": "炼虚"},
        {"name": "界域裂缝边缘", "description": "界域裂缝的边缘地带，空间不稳定", "min_level": "化神", "max_level": "炼虚"},
        {"name": "高浓度灵气山谷", "description": "灵气浓度极高的山谷", "min_level": "化神", "max_level": "炼虚"}
    ],
    "炼虚": [
        {"name": "炼虚修士专属秘境", "description": "炼虚期修士的专属秘境", "min_level": "炼虚", "max_level": "合体"},
        {"name": "灵界通道附近", "description": "通往灵界的通道附近", "min_level": "炼虚", "max_level": "合体"},
        {"name": "星空古路外围", "description": "星空古路的外围区域", "min_level": "炼虚", "max_level": "合体"}
    ]
}

def get_available_areas(player_level: str) -> list:
    """
    获取玩家当前等级可探索的区域
    :param player_level: 玩家当前等级
    :return: 可探索区域列表
    """
    available_areas = []
    
    # 获取玩家等级索引
    player_level_index = LEVEL_ORDER.index(player_level)
    
    # 添加当前等级和前两个等级的区域（如果存在）
    for i in range(max(0, player_level_index - 1), player_level_index + 1):
        level = LEVEL_ORDER[i]
        if level in EXPLORATION_AREAS:
            available_areas.extend(EXPLORATION_AREAS[level])
    
    # 添加下一个等级的区域（如果存在）
    if player_level_index + 1 < len(LEVEL_ORDER):
        next_level = LEVEL_ORDER[player_level_index + 1]
        if next_level in EXPLORATION_AREAS:
            available_areas.extend(EXPLORATION_AREAS[next_level])
    
    return available_areas

def show_exploration_areas(user_id: str) -> str:
    """
    显示玩家可探索的区域
    :param user_id: 玩家ID
    :return: 区域列表消息
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    areas = get_available_areas(player.level)
    
    if not areas:
        return "当前没有可探索的区域。"
    
    message = f"═══【{player.level}可探索区域】═══\n"
    for i, area in enumerate(areas, 1):
        message += f"{i}. {area['name']}\n"
        message += f"   {area['description']}\n"
        message += f"   适合等级: {area['min_level']} - {area['max_level']}\n\n"
    
    message += "请输入 `探索 [区域编号]` 选择区域进行探索。"
    
    return message

async def explore_area(user_id: str, area_index: int, provider=None) -> str:
    """
    探索指定区域
    :param user_id: 玩家ID
    :param area_index: 区域编号
    :param provider: 大模型提供者（可选）
    :return: 探索结果消息
    """
    from . import exploration_system
    
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    areas = get_available_areas(player.level)
    
    if area_index < 1 or area_index > len(areas):
        return "无效的区域编号。请输入正确的区域编号。"
    
    # 获取选择的区域
    selected_area = areas[area_index - 1]
    
    # 检查玩家等级是否符合区域要求
    player_level_index = LEVEL_ORDER.index(player.level)
    min_level_index = LEVEL_ORDER.index(selected_area['min_level'])
    max_level_index = LEVEL_ORDER.index(selected_area['max_level'])
    
    if player_level_index < min_level_index:
        return f"你的境界过低，无法进入{selected_area['name']}。最低要求境界: {selected_area['min_level']}"
    
    # 消耗灵力
    spirit_cost = 10
    if player.spirit_power < spirit_cost:
        return "你的灵力不足，无法继续探索。请先打坐恢复灵力。"
    
    player.spirit_power -= spirit_cost
    player_repository.update_player(player)
    
    # 执行探索
    result = await exploration_system.explore(user_id, provider)
    
    # 在结果前添加区域信息
    area_info = f"你在{selected_area['name']}探索...\n\n"
    
    return area_info + result