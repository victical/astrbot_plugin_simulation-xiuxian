# astrbot_xiuxian_plugin/main.py

# --- 模拟 AstrBot 环境 ---
# 在真实的 AstrBot 中，Event 类由框架提供
class SimulatedEvent:
    def __init__(self, user_id, user_name, content):
        self.user_id = str(user_id)  # 确保 user_id 是字符串
        self.user_name = user_name
        self.content = content
    
    def reply(self, message):
        """模拟回复消息，直接打印到控制台"""
        print(f"--- [回复给 {self.user_name}] ---\n{message}\n--------------------------")

# --- 插件核心代码 ---

from .database import db_manager
from .systems import game_start_system
from .systems import player_status_system
from .systems import progression_system
from .systems import sect_system
from .systems import inventory_system
from .systems import exploration_system
from .systems import combat_system # <--- 修复：导入战斗系统

def on_load():
    """
    当插件被加载时，AstrBot 会调用此函数。
    我们在这里初始化数据库。
    """
    print("模拟修仙插件: 正在加载...")
    db_manager.initialize_database()
    print("模拟修仙插件: 加载完成！")

def on_message(event):
    """
    当接收到任何消息时，AstrBot 会调用此函数。
    我们在这里处理玩家的命令。
    :param event: 包含消息信息的事件对象
    """
    content = event.content.strip()

    # 命令: 开始修仙
    if content == '!开始修仙':
        # 调用游戏开始系统来处理逻辑
        message = game_start_system.start_game(event.user_id, event.user_name)
        # 将系统返回的消息回复给用户
        event.reply(message)

    # 命令: 我的状态
    elif content == '!我的状态': # <--- 修改这个 elif 块
        # 调用状态系统来处理逻辑
        message = player_status_system.get_player_status(event.user_id)
        # 将返回的状态信息回复给用户
        event.reply(message)
    
    # 命令: 打坐
    elif content == '!打坐': # <--- 新增这个 elif 块
        message = progression_system.meditate(event.user_id)
        event.reply(message)

    elif content == '!宗门列表':
        message = sect_system.list_all_sects()
        event.reply(message)
    
    elif content.startswith('!加入宗门 '):
        # 从命令中解析出宗门名称
        # `split(' ', 1)` 表示最多只分割一次，防止宗门名称带空格(虽然我们目前没有)
        parts = content.split(' ', 1)
        if len(parts) > 1:
            sect_name = parts[1].strip()
            message = sect_system.join_sect(event.user_id, sect_name)
        else:
            message = "指令格式错误。请使用 `!加入宗门 [宗门名称]`，例如：`!加入宗门 青木仙宗`"
        event.reply(message)

    elif content == '!宗门任务':
        message = sect_system.get_sect_mission(event.user_id)
        event.reply(message)

    elif content == '!完成任务':
        message = sect_system.complete_sect_mission(event.user_id)
        event.reply(message)

    elif content == '!我的宗门':
        message = sect_system.get_sect_status(event.user_id)
        event.reply(message)

    elif content == '!我的背包':
        message = inventory_system.display_inventory(event.user_id)
        event.reply(message)

    elif content == '!宗门商店':
        message = sect_system.list_exchangeable_items(event.user_id)
        event.reply(message)

    elif content.startswith('!兑换 '):
        parts = content.split(' ', 1)
        if len(parts) > 1:
            item_name = parts[1].strip()
            message = sect_system.exchange_item(event.user_id, item_name)
        else:
            message = "指令格式错误。请使用 `!兑换 [物品名称]`。"
        event.reply(message)

    elif content == '!探索':
        message = exploration_system.explore(event.user_id)
        event.reply(message)
        
    # 在这里可以添加更多的 elif 来处理其他命令, 如 !打坐, !探索 等

# --- 本地测试代码 ---
# 这段代码允许你直接运行这个文件来测试功能
if __name__ == '__main__':
    on_load()
    print("\n======== 开始模拟用户交互 ========")
    
    from .database.repositories import player_repository

    # --- 测试场景1：遗迹寻宝全流程 ---
    print("\n\n======== 测试场景1：遗迹寻宝全流程 ========")
    # 1. 准备测试用户 "王五"
    print("\n[步骤1: 创建测试用户 '王五' 并给予藏宝图残片]")
    on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!开始修仙"))
    
    wangwu = player_repository.get_player_by_id("3003")
    if wangwu:
        wangwu.inventory["藏宝图残片"] = {"quantity": 2, "type": "material"}
        player_repository.update_player(wangwu)
        print("--- [系统] 已为 '王五' 添加2个藏宝图残片 ---")
    on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!我的背包"))

    # 2. 模拟获得最后一块残片并自动合成
    print("\n[步骤2: 模拟探索获得最后一块残片并触发自动合成]")
    wangwu = player_repository.get_player_by_id("3003")
    if wangwu:
        wangwu.inventory["藏宝图残片"]["quantity"] += 1
        player_repository.update_player(wangwu)
        print("--- [系统] '王五' 获得了第3个藏宝图残片 ---")
    
    on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!探索"))
    on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!我的背包"))

    # 3. 模拟使用完整藏宝图进入遗迹
    print("\n[步骤3: 多次探索，直到触发遗迹事件]")
    has_entered_ruin = False
    for i in range(10):
        print(f"--- 第 {i+1}/10 次尝试 ---")
        wangwu = player_repository.get_player_by_id("3003")
        if wangwu and "完整的藏宝图" not in wangwu.inventory:
            has_entered_ruin = True
            print("--- [系统] 检测到藏宝图已被消耗，判定已进入遗迹！ ---")
            break
        on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!探索"))

    if not has_entered_ruin:
        print("--- [系统] 10次尝试内未进入遗迹，请检查 explore 函数中的概率（当前为30%） ---")

    on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!我的背包"))
    on_message(SimulatedEvent(user_id=3003, user_name="王五", content="!我的状态"))

    # --- 测试场景2：宗门职位晋升全流程 ---
    print("\n\n======== 测试场景2：宗门职位晋升全流程 ========")
    # 1. 准备测试用户 "赵六"
    print("\n[步骤1: 创建测试用户 '赵六' 并加入青木仙宗]")
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!开始修仙"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!加入宗门 青木仙宗"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!我的宗门"))

    # 2. 模拟贡献和等级达标，触发晋升
    print("\n[步骤2: 模拟贡献和等级达标，触发晋升为内门弟子]")
    zhaoliu = player_repository.get_player_by_id("4004")
    if zhaoliu:
        zhaoliu.contribution = 200
        zhaoliu.level = "筑基"
        player_repository.update_player(zhaoliu)
        print("--- [系统] 已将 '赵六' 的贡献提升至200，等级提升至筑基 ---")
    
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!宗门任务"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!完成任务"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!我的宗门"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!我的背包"))

    # 3. 测试晋升后的商店权限
    print("\n[步骤3: 测试内门弟子的商店权限]")
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!宗门商店"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!兑换 筑基丹"))
    on_message(SimulatedEvent(user_id=4004, user_name="赵六", content="!我的背包"))

    # --- 测试场景3：战斗系统 ---
    print("\n\n======== 测试场景3：战斗系统测试 ========")
    print("\n[步骤1: 创建测试用户 '孙七' 并进行战斗]")
    on_message(SimulatedEvent(user_id=5005, user_name="孙七", content="!开始修仙"))
    
    sunqi = player_repository.get_player_by_id("5005")
    if sunqi:
        # 为了确保能打赢，稍微加强一下
        sunqi.attack += 5
        sunqi.defense += 5
        player_repository.update_player(sunqi)
        print("--- [系统] 已为 '孙七' 提升属性 ---")
        
        # 直接调用战斗系统进行测试
        combat_result = combat_system.start_pve_combat(sunqi, "嗜血野狼")
        # 模拟回复
        SimulatedEvent(user_id=5005, user_name="孙七", content="").reply(combat_result)

    print("\n[步骤2: 检查战斗后的状态]")
    on_message(SimulatedEvent(user_id=5005, user_name="孙七", content="!我的状态"))
    on_message(SimulatedEvent(user_id=5005, user_name="孙七", content="!我的背包"))
