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
        
    # 在这里可以添加更多的 elif 来处理其他命令, 如 !打坐, !探索 等

# --- 本地测试代码 ---
# 这段代码允许你直接运行这个文件来测试功能
if __name__ == '__main__':
    on_load()
    print("\n======== 开始模拟用户交互 ========")

# 重新创建用户
    on_message(SimulatedEvent(user_id=1001, user_name="张三", content="!开始修仙"))
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!开始修仙"))
    
    # 让李四加入宗门并完成一次任务以获得贡献
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!加入宗门 青木仙宗"))
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!宗门任务"))
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!完成任务"))

    # --- 新增宗门商店和兑换测试场景 ---
    print("\n[场景21: 散修 '张三' 查看背包和商店]")
    on_message(SimulatedEvent(user_id=1001, user_name="张三", content="!我的背包"))
    on_message(SimulatedEvent(user_id=1001, user_name="张三", content="!宗门商店"))

    print("\n[场景22: '李四' 查看宗门商店]")
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!宗门商店"))

    print("\n[场景23: '李四' 贡献不足，尝试兑换'护心玉佩']")
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!兑换 护心玉佩"))
    
    print("\n[场景24: '李四' 贡献足够，成功兑换'养气丹']")
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!兑换 养气丹"))
    
    print("\n[场景25: '李四' 查看兑换后的状态和背包]")
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!我的状态"))
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!我的背包"))
    
    print("\n[场景26: '李四' 再次兑换'养气丹'，测试物品堆叠]")
    # 先让他再做一次任务获得贡献
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!宗门任务"))
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!完成任务"))
    # 再兑换
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!兑换 养气丹"))
    # 查看最终背包
    on_message(SimulatedEvent(user_id=2002, user_name="李四", content="!我的背包"))