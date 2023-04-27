from time import sleep
from javascript import require, On, AsyncTask
import threading


def fish_bot(mineflayer, pathfinder):
    """
    Fishing bot
    :param mineflayer:
    :param pathfinder:
    :return:
    """
    bot = mineflayer.createBot({
        'host': HOST,
        'username': 'Fisherman',
        'version': MINECRAFT_VERSION
        })

    bot.loadPlugin(pathfinder.pathfinder)

    @On(bot, 'spawn')
    def spawn(*args):
        bot.chat('Fisherman is here!')

        mc_data = require('minecraft-data')(bot.version)
        movements = pathfinder.Movements(bot, mc_data)

        @On(bot, 'chat')
        def message_handler(this, user, message, *args):
            if bot['username'] + ' fish' in message:
                bot.pathfinder.setGoal(None, False)
                bot.equip(bot.registry.itemsByName.fishing_rod.id, 'hand')

                @AsyncTask(start=True)
                def fishing(task):
                    global isFishing
                    while True:
                        if not isFishing:
                            sleep(1)
                            bot.activateItem()
                            isFishing = True

                @On(bot._client, 'sound_effect')
                def sound_handler(this, packet, *args):
                    global isFishing
                    if isFishing:
                        if packet['soundId'] == 417:  # id может отличаться (в зависимости от версии)
                            bot.activateItem()
                            isFishing = False

            elif bot['username'] + ' here' in message:
                global isFishing
                if isFishing:
                    bot.activateItem()

                goal_follow = pathfinder.goals.GoalFollow
                player = bot.players[user]
                target = player.entity
                bot.pathfinder.setMovements(movements)

                bot.pathfinder.setGoal(goal_follow(target, 1), True)

            elif bot['username'] + ' quit' in message:
                bot.quit()


def diamond_bot(mineflayer, pathfinder):
    """
    Diamond mining bot
    :param mineflayer:
    :param pathfinder:
    :return:
    """
    bot = mineflayer.createBot({
        'host': HOST,
        'username': 'Diamondman',
        'version': MINECRAFT_VERSION
    })

    bot.loadPlugin(pathfinder.pathfinder)

    @On(bot, 'spawn')
    def spawn(*args):
        bot.chat('Diamondman is here!')

        mc_data = require('minecraft-data')(bot.version)
        movements = pathfinder.Movements(bot, mc_data)

        @On(bot, 'chat')
        def message_handler(this, user, message, *args):
            if bot['username'] + ' diamonds' in message:
                goal_block = pathfinder.goals.GoalBlock

                block = bot.findBlock({
                    'matching': mc_data.blocksByName.diamond_ore.id,
                    'maxDistance': 256
                })

                print(block.position)
                if block:
                    print('Block = true')
                    bot.pathfinder.setMovements(movements)
                    goal = goal_block(block.position.x, block.position.y + 1, block.position.z)
                    bot.pathfinder.setGoal(goal)

            elif bot['username'] + ' here' in message:
                goal_follow = pathfinder.goals.GoalFollow
                player = bot.players[user]
                target = player.entity
                bot.pathfinder.setMovements(movements)
                goal = goal_follow(target, 1)
                bot.pathfinder.setGoal(goal, True)

            elif bot['username'] + ' quit' in message:
                bot.quit()


def main():
    mineflayer = require('mineflayer')
    pathfinder = require('mineflayer-pathfinder')

    th1 = threading.Thread(fish_bot(mineflayer, pathfinder))
    th2 = threading.Thread(diamond_bot(mineflayer, pathfinder))

    th1.start()
    th2.start()


if __name__ == '__main__':
    isFishing = False
    HOST = 'your server ip'
    MINECRAFT_VERSION = 'your minecraft version'

    main()
