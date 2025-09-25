# astrbot_xiuxian_plugin/systems/combat_system.py
import random
from ..database.repositories import player_repository
from . import progression_system
from .monster_generator import Monster

def start_pve_combat(player: "Player", monster: Monster) -> str:
    """
    处理玩家与动态生成的怪物之间的战斗。
    :param player: 玩家对象。
    :param monster: 怪物对象。
    :return: 包含战斗过程和结果的字符串。
    """
    player_hp = player.hp
    monster_hp = monster.hp
    
    combat_log = [f"战斗开始！(HP: {monster_hp}, 攻: {monster.attack}, 防: {monster.defense})"]

    turn = 1
    while player_hp > 0 and monster_hp > 0:
        combat_log.append(f"\n第 {turn} 回合:")
        
        # --- 玩家回合 ---
        player_damage = max(1, player.attack - monster.defense + random.randint(-3, 3))
        monster_hp -= player_damage
        combat_log.append(f"你对【{monster.name}】造成了 {player_damage} 点伤害。【{monster.name}】剩余生命: {max(0, monster_hp)}")

        if monster_hp <= 0:
            break

        # --- 怪物回合 ---
        monster_damage = max(1, monster.attack - player.defense + random.randint(-3, 3))
        player_hp -= monster_damage
        combat_log.append(f"【{monster.name}】对你造成了 {monster_damage} 点伤害。你剩余生命: {max(0, player_hp)}")
        
        turn += 1

    # --- 战斗结束 ---
    player.hp = player_hp
    
    if player_hp <= 0:
        player.hp = 1
        player_repository.update_player(player)
        combat_log.append("\n你被击败了...侥幸保住一命。")
        return "\n".join(combat_log)
    else:
        exp_gain = monster.exp_drop
        stone_gain = monster.spirit_stones_drop
        
        player.experience += exp_gain
        player.spirit_stones += stone_gain
        
        reward_log = [
            "\n你获得了胜利！",
            f"获得奖励:",
            f" - 修为 +{exp_gain}",
            f" - 灵石 +{stone_gain}"
        ]
        combat_log.extend(reward_log)
        
        levelup_message = progression_system._check_and_process_levelup(player)
        if levelup_message:
            combat_log.append("\n" + levelup_message)
            
        player_repository.update_player(player)
        return "\n".join(combat_log)
