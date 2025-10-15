# astrbot_xiuxian_plugin/systems/crafting_system.py
"""物品合成系统"""

from ..database.db_manager import fetch_query, execute_query
from ..database.repositories import player_repository
from ..systems.item_system import ItemType, generate_item_attributes, generate_item_name
import json
import random

# 合成配方配置
CRAFTING_RECIPES = {
    # 丹药合成配方
    "养气丹": {
        "materials": {"灵草": 3, "木灵石": 1},
        "type": ItemType.ELIXIR,
        "level": "炼气"
    },
    "小还丹": {
        "materials": {"灵草": 5, "千年灵芝": 1},
        "type": ItemType.ELIXIR,
        "level": "炼气"
    },
    "筑基丹": {
        "materials": {"千年灵芝": 3, "玄铁木": 2},
        "type": ItemType.ELIXIR,
        "level": "筑基"
    },
    "生机丹": {
        "materials": {"万年灵芝": 1, "千年灵芝": 5},
        "type": ItemType.ELIXIR,
        "level": "筑基"
    },
    "蕴灵丹": {
        "materials": {"万年灵芝": 3, "星辰铁": 1},
        "type": ItemType.ELIXIR,
        "level": "金丹"
    },
    
    # 武器合成配方
    "青木剑": {
        "materials": {"玄铁木": 2, "木灵石": 3},
        "type": ItemType.WEAPON,
        "level": "炼气"
    },
    "青罡剑": {
        "materials": {"玄铁木": 5, "星辰铁": 1},
        "type": ItemType.WEAPON,
        "level": "筑基"
    },
    "青冥剑": {
        "materials": {"星辰铁": 3, "九天玄铁": 1},
        "type": ItemType.WEAPON,
        "level": "金丹"
    },
    
    # 法宝合成配方
    "护心玉佩": {
        "materials": {"木灵石": 5, "灵草": 3},
        "type": ItemType.ARTIFACT,
        "level": "炼气"
    },
    "碧玉葫芦": {
        "materials": {"万年灵芝": 2, "木灵石": 5},
        "type": ItemType.ARTIFACT,
        "level": "筑基"
    },
    "乾坤袋": {
        "materials": {"星辰铁": 2, "混沌石": 1},
        "type": ItemType.ARTIFACT,
        "level": "金丹"
    }
}

def get_player_materials(user_id: str) -> dict:
    """
    获取玩家拥有的材料
    """
    sql = """
    SELECT i.name, pi.quantity
    FROM player_items pi
    JOIN items i ON pi.item_id = i.id
    WHERE pi.player_id = ? AND i.type = 'material'
    """
    results = fetch_query(sql, (user_id,))
    
    materials = {}
    for result in results:
        materials[result[0]] = result[1]
    
    return materials

def display_crafting_recipes() -> str:
    """
    显示可合成的物品配方
    """
    message_parts = ["═══【可合成物品】═══"]
    
    # 按类型分组显示
    elixir_recipes = {name: recipe for name, recipe in CRAFTING_RECIPES.items() if recipe["type"] == ItemType.ELIXIR}
    weapon_recipes = {name: recipe for name, recipe in CRAFTING_RECIPES.items() if recipe["type"] == ItemType.WEAPON}
    artifact_recipes = {name: recipe for name, recipe in CRAFTING_RECIPES.items() if recipe["type"] == ItemType.ARTIFACT}
    
    if elixir_recipes:
        message_parts.append("【丹药类】")
        for name, recipe in elixir_recipes.items():
            materials_str = ", ".join([f"{mat}x{qty}" for mat, qty in recipe["materials"].items()])
            message_parts.append(f"  {name}({recipe['level']}): {materials_str}")
    
    if weapon_recipes:
        message_parts.append("\n【武器类】")
        for name, recipe in weapon_recipes.items():
            materials_str = ", ".join([f"{mat}x{qty}" for mat, qty in recipe["materials"].items()])
            message_parts.append(f"  {name}({recipe['level']}): {materials_str}")
    
    if artifact_recipes:
        message_parts.append("\n【法宝类】")
        for name, recipe in artifact_recipes.items():
            materials_str = ", ".join([f"{mat}x{qty}" for mat, qty in recipe["materials"].items()])
            message_parts.append(f"  {name}({recipe['level']}): {materials_str}")
    
    message_parts.append("\n══════════════")
    message_parts.append("【合成指令】")
    message_parts.append("使用 `合成 [物品名称]` 来合成物品")
    message_parts.append("通过探索和任务获得材料")
    message_parts.append("══════════════")
    return "\n".join(message_parts)

def craft_item(user_id: str, item_name: str) -> str:
    """
    合成物品
    """
    player = player_repository.get_player_by_id(user_id)
    if not player:
        return "道友，你尚未踏入仙途。"
    
    # 检查是否有这个合成配方
    if item_name not in CRAFTING_RECIPES:
        return f"没有【{item_name}】的合成配方。"
    
    recipe = CRAFTING_RECIPES[item_name]
    
    # 获取玩家拥有的材料
    player_materials = get_player_materials(user_id)
    
    # 检查材料是否足够
    for material, required_qty in recipe["materials"].items():
        if player_materials.get(material, 0) < required_qty:
            return f"材料不足！合成【{item_name}】需要: {material}x{required_qty}，你只有{material}x{player_materials.get(material, 0)}"
    
    # 消耗材料
    for material, required_qty in recipe["materials"].items():
        _consume_material(user_id, material, required_qty)
    
    # 生成物品
    item_type = recipe["type"]
    item_level = recipe["level"]
    
    # 生成属性
    attributes = generate_item_attributes(item_type, item_level)
    
    # 生成名称（如果配方中没有指定名称）
    if item_name not in [item[0] for item in fetch_query("SELECT name FROM items WHERE name = ?", (item_name,))]:
        # 创建物品
        description = f"通过合成获得的{item_type}"
        sql = """
        INSERT INTO items (name, type, level_requirement, description, attributes)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(sql, (
            item_name,
            item_type,
            item_level,
            description,
            json.dumps(attributes)
        ))
    
    # 添加到玩家背包
    from ..systems.item_system import add_item_to_player
    add_item_to_player(user_id, item_name, 1)
    
    # 生成属性描述
    attrs_desc = ", ".join([f"{k}:{v}" for k, v in attributes.items()])
    
    return f"合成成功！你获得了【{item_name}】({attrs_desc})"

def _consume_material(user_id: str, material_name: str, quantity: int):
    """
    消耗玩家的材料
    """
    # 获取物品ID
    item_sql = "SELECT id FROM items WHERE name = ? AND type = 'material'"
    item_result = fetch_query(item_sql, (material_name,), one=True)
    
    if not item_result:
        return
    
    item_id = item_result[0]
    
    # 检查玩家物品数量
    player_item_sql = "SELECT id, quantity FROM player_items WHERE player_id = ? AND item_id = ?"
    player_item_result = fetch_query(player_item_sql, (user_id, item_id), one=True)
    
    if not player_item_result:
        return
    
    player_item_id, current_quantity = player_item_result
    
    if current_quantity <= quantity:
        # 删除记录
        delete_sql = "DELETE FROM player_items WHERE id = ?"
        execute_query(delete_sql, (player_item_id,))
    else:
        # 减少数量
        update_sql = "UPDATE player_items SET quantity = quantity - ? WHERE id = ?"
        execute_query(update_sql, (quantity, player_item_id))