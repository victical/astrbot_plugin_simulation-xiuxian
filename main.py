from astrbot.api import logger
from astrbot.api.star import Context, Star, register
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api import AstrBotConfig
from .database import db_manager
from .systems import (
    game_start_system,
    player_status_system,
    progression_system,
    sect_system,
    inventory_system,
    exploration_system,
)

# 新增导入
from .systems.elixir_system import use_elixir
from .systems.crafting_system import craft_item, display_crafting_recipes
from .systems.equipment_system import equip_item, unequip_item, show_equipment

# --- 指令常量 ---
CMD_START_XIUXIAN = "开始修仙"
CMD_PLAYER_STATUS = "我的状态"
CMD_MEDITATE = "打坐"
CMD_STOP_MEDITATE = "结束打坐"
CMD_SECT_LIST = "宗门列表"
CMD_JOIN_SECT = "加入宗门"
CMD_SECT_MISSION = "宗门任务"
CMD_COMPLETE_MISSION = "完成任务"
CMD_MY_SECT = "我的宗门"
CMD_INVENTORY = "我的背包"
CMD_SECT_SHOP = "宗门商店"
CMD_EXCHANGE_ITEM = "兑换"
CMD_EXPLORE = "探索"
CMD_USE_ELIXIR = "服用"
CMD_CRAFT_ITEM = "合成"
CMD_CRAFTING_RECIPES = "合成配方"
CMD_EQUIP_ITEM = "装备"
CMD_UNEQUIP_ITEM = "卸下"
CMD_SHOW_EQUIPMENT = "我的装备"


class SimulationXiuxianPlugin(Star):

    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config
        logger.info("SimulationXiuxianPlugin 已实例化")

    async def initialize(self):
        logger.info("模拟修仙插件: 正在加载...")
        db_manager.initialize_database()
        logger.info("模拟修仙插件: 加载完成！")

    async def terminate(self):
        logger.info("模拟修仙插件: 正在终止...")

    # --- 指令处理 ---

    @filter.command(CMD_START_XIUXIAN, "开始你的修仙之路")
    async def handle_start_xiuxian(self, event: AstrMessageEvent):
        logger.info("我要修仙指令已触发，进入 handle_start_xiuxian。")
        user_id = str(event.get_sender_id())
        user_name = event.get_sender_name()
        logger.info(f"用户信息: user_id={user_id}, user_name={user_name}")
        
        message = game_start_system.start_game(user_id, user_name)
        
        logger.info(f"游戏开始系统返回消息: {message}")
        yield event.plain_result(message)

    @filter.command(CMD_PLAYER_STATUS, "查看你的角色信息")
    async def handle_player_status(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = player_status_system.get_player_status(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_MEDITATE, "静心打坐，提升修为")
    async def handle_meditate(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = progression_system.start_meditation(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_STOP_MEDITATE, "结束打坐，查看收益")
    async def handle_stop_meditation(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = progression_system.stop_meditation(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_SECT_LIST, "查看所有可加入的宗门")
    async def handle_sect_list(self, event: AstrMessageEvent):
        message = sect_system.list_all_sects()
        yield event.plain_result(message)

    @filter.command(CMD_JOIN_SECT, "加入一个宗门", args_desc="<宗门名称>")
    async def handle_join_sect(self, event: AstrMessageEvent, sect_name: str = None):
        user_id = str(event.get_sender_id())
        if not sect_name:
            # 用户未提供宗门名称，返回帮助信息和宗门列表
            sect_list_message = sect_system.list_all_sects()
            message = f"请指定要加入的宗门名称，例如：`加入宗门 青云门`\n\n{sect_list_message}"
        else:
            # 用户提供了宗门名称，执行加入逻辑
            message = sect_system.join_sect(user_id, sect_name.strip())
        
        yield event.plain_result(message)

    @filter.command(CMD_SECT_MISSION, "查看当前的宗门任务")
    async def handle_sect_mission(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = sect_system.get_sect_mission(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_COMPLETE_MISSION, "完成宗门任务获取奖励")
    async def handle_complete_mission(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = sect_system.complete_sect_mission(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_MY_SECT, "查看你所在的宗门信息")
    async def handle_my_sect(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = sect_system.get_sect_status(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_INVENTORY, "查看你的背包")
    async def handle_inventory(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = inventory_system.display_inventory(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_SECT_SHOP, "查看宗门商店可兑换的物品")
    async def handle_sect_shop(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = sect_system.list_exchangeable_items(user_id)
        yield event.plain_result(message)

    @filter.command(CMD_EXCHANGE_ITEM, "在宗门商店兑换物品", args_desc="<物品名称>")
    async def handle_exchange_item(self, event: AstrMessageEvent, item_name: str):
        user_id = str(event.get_sender_id())
        message = sect_system.exchange_item(user_id, item_name.strip())
        yield event.plain_result(message)

    @filter.command(CMD_EXPLORE, "外出探索，寻找机缘")
    async def handle_explore(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        provider = self.context.get_using_provider(umo=event.unified_msg_origin)
        message = await exploration_system.explore(user_id, provider)
        yield event.plain_result(message)
    
    @filter.command(CMD_USE_ELIXIR, "服用丹药", args_desc="<丹药名称>")
    async def handle_use_elixir(self, event: AstrMessageEvent, elixir_name: str = None):
        user_id = str(event.get_sender_id())
        if not elixir_name:
            message = "请指定要服用的丹药名称，例如：`服用 养气丹`"
        else:
            message = use_elixir(user_id, elixir_name.strip())
        yield event.plain_result(message)
    
    @filter.command(CMD_CRAFTING_RECIPES, "查看可合成的物品配方")
    async def handle_crafting_recipes(self, event: AstrMessageEvent):
        message = display_crafting_recipes()
        yield event.plain_result(message)
    
    @filter.command(CMD_CRAFT_ITEM, "合成物品", args_desc="<物品名称>")
    async def handle_craft_item(self, event: AstrMessageEvent, item_name: str = None):
        user_id = str(event.get_sender_id())
        if not item_name:
            message = "请指定要合成的物品名称，例如：`合成 养气丹`"
        else:
            message = craft_item(user_id, item_name.strip())
        yield event.plain_result(message)
    
    @filter.command(CMD_EQUIP_ITEM, "装备物品", args_desc="<物品名称>")
    async def handle_equip_item(self, event: AstrMessageEvent, item_name: str = None):
        user_id = str(event.get_sender_id())
        if not item_name:
            message = "请指定要装备的物品名称，例如：`装备 青木剑`"
        else:
            message = equip_item(user_id, item_name.strip())
        yield event.plain_result(message)
    
    @filter.command(CMD_UNEQUIP_ITEM, "卸下装备", args_desc="<物品名称>")
    async def handle_unequip_item(self, event: AstrMessageEvent, item_name: str = None):
        user_id = str(event.get_sender_id())
        if not item_name:
            message = "请指定要卸下的物品名称，例如：`卸下 青木剑`"
        else:
            message = unequip_item(user_id, item_name.strip())
        yield event.plain_result(message)
    
    @filter.command(CMD_SHOW_EQUIPMENT, "查看当前装备")
    async def handle_show_equipment(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        message = show_equipment(user_id)
        yield event.plain_result(message)
