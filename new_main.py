# бот для игры в мафию
#by goldon_cat
from time import sleep
import data_bazes as db
import json
from random import choice
import telebot as tb

gt_id = 0

bot = tb.TeleBot("8046077743:AAGiUNbhKwaoKlj644CEUun3UkJ39-FGD4Q")
bot.send_message(5349993497, 'bot starting')

admins = [5349993497,481408952]
game = False
sleeping = False

def get_kills(sleeping):
    if not sleeping:
        user_w = db.citizens_kill()
        return 'горожане выгнали ' + user_w
    return 'мафия убила ' + db.mafia_kill()

    



def autoplay_citizen(message):
    players_roles = db.get_players_roles()
    for player_id, _ in players_roles:
        usernames = db.get_all_alive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('citizen_vote', vote_username, player_id)
            bot.send_message(
                message.chat.id, f'{name} проголосовал против {vote_username}')
            sleep(0.5)


def autoplay_mafia():
    players_roles = db.get_players_roles()
    for player_id, role in players_roles:
        usernames = db.get_all_alive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames and role == 'mafia':
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('mafia_vote', vote_username, player_id)

def game_loop(message):   
    global sleeping, game
    bot.send_message(        message.chat.id, "Добро пожаловать в игру! Вам дается 1 минута, чтобы познакомиться")
    sleep(40)   
    while True:
        msg = get_kills(sleeping)
        bot.send_message(message.chat.id, msg)
        if not sleeping:
            bot.send_message(
                message.chat.id, "Город засыпает, просыпается мафия. Наступила ночь")
        else:
            bot.send_message(                message.chat.id, "Город просыпается. Наступил день")
        winner = db.check_winner()
        if winner == 'Мафия' or winner == 'Горожане':
            game = False
            bot.send_message(message.chat.id, text=f'Игра окончена победили: {winner}')
            return
        db.reset_users(dead=False)
        sleeping = not sleeping
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, text=f'В игре:\n{alive}')
        sleep(40)
        autoplay_mafia() if sleeping else autoplay_citizen(message)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '  .........//// ')

@bot.message_handler(commands=['add_me'])
def add_me(message):
    bot.send_message(message.chat.id, f'игрок {message.from_user.first_name} играет ')
    bot.send_message(message.from_user.id, f' {message.from_user.first_name} вы добавлены в игру, ожидайте других игроков')
    db.p_add(message.from_user.id, message.from_user.first_name)

@bot.message_handler(commands=['players'])
def show_players(message):
    global tg_id
    tg_id = message.from_user.id
    if tg_id in admins:
        bot.send_message(message.chat.id,str(db.show_names()))
    else:
        bot.send_message(message.chat.id, 'не достаточно прав для совершение каманды, пожалуйсто напишите@cat4087 для получение помощи.')


@bot.message_handler(commands=['game_start'])
def game_start(message):
    global game, sleeping
    players = db.count_players()
    if players >= 6 and not game:
        game = True
        db.set_roles()
        mafias = db.get_mafia()
        players_roles = db.get_roles()
        for id, role in players_roles:
            if id > 5:
                bot.send_message(id, f'вы: {role}')
                if role == 'mafia':
                    bot.send_message(id, f'все члены Мафии: {mafias}')
        bot.send_message(message.chat.id, 'начинаю игру')
        db.reset_users()
        game_loop(message)
        return()
    else:
        bot.send_message(message.chat.id, 'не достаточно игроков, добавляю ботов')
        for i in range(6 - players):
            bot_name = 'bot' + str(i)
            # добавили ботов, для того чтобы можно играть
            db.p_add(i,bot_name)
            bot.send_message(message.chat.id,'бот  : ' + bot_name + ' добавлен.')
            sleep(1)

        game_start(message)

@bot.message_handler(commands=['game_stop'])
def stop_game(message):
    global game
    if game:
        game = False
        db.del_users()
        bot.send_message(message.chat.id, 'Игра остановлена.')
    else:
        bot.send_message(message.chat.id, 'Игра не запущена.')

@bot.message_handler(commands=['kick'])
# это для жителей кильнуть Мафию, надо имя игрока черес пробел/kill goldon
def kick_Mafea(message):
    name = message.text.split(' ')[1:]
    name = ' '.join(name)
    if not sleeping:
        usernames = db.get_alive()
        print(usernames)
        print(name)
        
        if not name in usernames:
            bot.send_message(message.chat.id,' игрок не найден')
            return
        voted = db.vote(type = 'citizen_vote', username = name, player_id = message.from_user.id)
        if voted:
            bot.send_message(message.chat.id,'ваш голос учтён')
        else:
            bot.send_message(message.chat.id,'вы не имеете право голосовать ')
    else:
        bot.send_message(message.chat.id,'спать не голосовать')
        #  end


@bot.message_handler(commands=['kill'])
# это для мафии кильнуть жителя, писать черес пробел имя  надо имя игрока черес пробел/kick goldon
def kick_citizin(message):
    name = message.text.split(' ')[1:]
    name = ' '.join(name)
    mafeas = db.get_mafia()
    if sleeping and message.from_user.first_name in mafeas:
        usernames = db.get_alive()
        
        if not name in usernames:
            bot.send_message(message.chat.id,' игрок не найден')
            return
        voted = db.vote(type = 'mafia_vote', username = name, player_id = message.from_user.id)
        if voted:
            bot.send_message(message.chat.id,'ваш голос учтён')
        else:
            bot.send_message(message.chat.id,'вы не имеете право голосовать ')
    else:
        bot.send_message(message.chat.id,'ты что спалится хочешь? ну ты его днём кильнёшь, и все увидят это')
        # 

@bot.message_handler(content_types=['text'])
def txt(message):
    bot.send_message(message.chat.id, message.text[::-1])

bot.infinity_polling()
    # end
