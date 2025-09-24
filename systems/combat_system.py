# astrbot_xiuxian_plugin/systems/combat_system.py
import random
from ..database.repositories import player_repository
from ..config import monsters_data
from . import progression_system

def start_pve_combat(player: "Player", monster_name: str) -> str:
    """
    处理玩家与怪物之间的战斗。
    :param player: 玩家对象。
    :param monster_name: 怪物名称。
    :return: 包含战斗过程和结果的字符串。
    """
    monster = monsters_data.MONSTERS.get(monster_name)
    if not monster:
        return f"遭遇未知妖兽 {monster_name}，你安然无恙。"

    player_hp = player.hp
    monster_hp = monster["hp"]
    
    combat_log = [f"你遭遇了【{monster_name}】(HP: {monster_hp}, 攻: {monster['attack']}, 防: {monster['defense']})！"]

    turn = 1
    while player_hp > 0 and monster_hp > 0:
        combat_log.append(f"\n第 {turn} 回合:")
        
        # --- 玩家回合 ---
        player_damage = max(1, player.attack - monster["defense"] + random.randint(-3, 3))
        monster_hp -= player_damage
        combat_log.append(f"你对【{monster_name}】造成了 {player_damage} 点伤害。【{monster_name}】剩余生命: {max(0, monster_hp)}")

        if monster_hp <= 0:
            break

        # --- 怪物回合 ---
        monster_damage = max(1, monster["attack"] - player.defense + random.randint(-3, 3))
        player_hp -= monster_damage
        combat_log.append(f"【{monster_name}】对你造成了 {monster_damage} 点伤害。你剩余生命: {max(0, player_hp)}")
        
        turn += 1

    # --- 战斗结束 ---
    player.hp = player_hp # 更新玩家战斗后的HP
    
    if player_hp <= 0:
        # 战斗失败
        player.hp = 1 # 死亡惩罚，HP变为1
        player_repository.update_player(player)
        combat_log.append("\n你被击败了...侥幸保住一命。")
        return "\n".join(combat_log)
    else:
        # 战斗胜利
        rewards = monster.get("rewards", {})
        exp_gain = rewards.get("experience", 0)
        stone_gain = rewards.get("spirit_stones", 0)
        
        player.experience += exp_gain
        player.spirit_stones += stone_gain
        
        reward_log = [
            "\n你获得了胜利！",
            f"获得奖励:",
            f" - 修为 +{exp_gain}",
            f" - 灵石 +{stone_gain}"
        ]
        
        # 处理物品掉落
        if "items" in rewards:
            for item_info in rewards["items"]:
                if random.random() < item_info["chance"]:
                    item_name = item_info["name"]
                    quantity = item_info.get("quantity", 1)
                    if item_name in player.inventory:
                        player.inventory[item_name]["quantity"] += quantity
                    else:
                        player.inventory[item_name] = {"quantity": quantity, "type": "材料"} # 假设掉落物都是材料
                    reward_log.append(f" - {item_name} x{quantity}")

        combat_log.extend(reward_log)
        
        # 检查升级
        levelup_message = progression_system._check_and_process_levelup(player)
        if levelup_message:
            combat_log.append("\n" + levelup_message)
            
        player_repository.update_player(player)
        return "\n".join(combat_log)
