# astrbot_xiuxian_plugin/systems/game_start_system.py

from ..models.player import Player
from ..database.repositories import player_repository
from ..config import settings

def start_game(user_id: str, user_name: str) -> str:
    """
    处理用户的游戏开始请求。

    - 检查玩家是否已存在。
    - 如果不存在，则根据初始设置创建一个新角色。
    - 返回一个相应的消息给用户。
    
    :param user_id: 用户的唯一ID
    :param user_name: 用户的昵称
    :return: 一条将要回复给用户的消息字符串
    """
    # 1. 检查玩家是否已经存在
    if player_repository.player_exists(user_id):
        player = player_repository.get_player_by_id(user_id)
        if player:
            return f"道友 {player.user_name}，你已在仙途中，当前境界为【{player.level}】。无需重新开始。使用 `!我的状态` 查看详情。"
        else:
            # 这是一个理论上的边缘情况，以防万一
            return "系统出现异常，无法获取您的角色信息，请联系管理员。"

    # 2. 如果玩家不存在，创建新角色
    print(f"新玩家加入: user_id={user_id}, user_name={user_name}")

    # 从配置文件获取初始属性
    initial_stats = settings.INITIAL_PLAYER_STATS

    # 创建一个新的 Player 对象
    new_player = Player(
        user_id=user_id,
        user_name=user_name,
        level=initial_stats['level'],
        experience=initial_stats['experience'],
        spirit_stones=initial_stats['spirit_stones'],
        hp=initial_stats['hp'],
        mp=initial_stats['mp'],
        attack=initial_stats['attack'],
        defense=initial_stats['defense'],
        sect=initial_stats['sect'],
        sect_rank=initial_stats['sect_rank'],
        contribution=initial_stats['contribution'],
        inventory='{}',  # 初始为空的 JSON 对象
        learned_skills='[]' # 初始为空的 JSON 数组
    )

    # 3. 将新玩家存入数据库
    player_repository.create_player(new_player)

    # 4. 构造欢迎消息
    welcome_message = (
        f"欢迎道友 {user_name}！\n"
        f"你已成功踏入修仙世界，成为一名【凡人】。\n"
        f"你的旅程从此开始，愿你早日证道长生！\n"
        f"输入 `!我的状态` 来查看你的当前信息。"
    )
    
    return welcome_message