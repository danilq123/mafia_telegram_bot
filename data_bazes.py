import random
import sqlite3
def con_open(): 
    global con,cur
    con = sqlite3.connect("db.db")
    cur = con.cursor()
def con_close():
    con.commit()
    con.close()
def  p_add(id,user_name):
    con_open()
    sql = f"INSERT INTO players  (player_id,username) VALUES ({id},'{user_name}')"
    cur.execute(sql)
    con_close()

def show_names():
    con_open()
    sql = "SELECT username FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con_close()
    return data

def show_players():
    con_open()
    sql = "SELECT * FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    print(*data,sep='\n')
    
    con_close()


def del_users():
    con_open()
    sql = 'DELETE FROM players'
    cur.execute(sql)
    con_close()
#end

def reset_users():
    con_open()
    sql = "UPDATE players SET role='',mafia_vote='',citizen_vote='',voted=0,dead=0"
    cur.execute(sql)
    con_close()

def get_alive():
    con_open()
    sql = "SELECT username FROM players WHERE dead = 0 OR dead IS NULL  "
    cur.execute(sql)
    data =  cur.fetchall()
    print(data)
    data = [user[0] for user in data ]
    
    con_close()
    return data
# end

def get_mafia():
    con_open()
    sql = "SELECT username FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    data =  cur.fetchall()
    data = [user[0] for user in data ]
    
    con_close()
    return data
# end

def get_roles():
    con_open()
    sql = "SELECT player_id,role FROM players "
    cur.execute(sql)
    data =  cur.fetchall()   
    con_close()
    return data
# end

def set_roles():
    user_count = count_players()
    roles = ['citezen']*user_count
    mafias = int(user_count*0.3)
    # ищим сколько 30 процентов от всех игроков

    for i in range(mafias):
        roles[i] = 'mafia'
    random.shuffle(roles)   
    # print(roles)
    con_open()
    sql = "SELECT player_id FROM players"
    cur.execute(sql)
    ids = cur.fetchall()
    for role, id in zip(roles, ids):
        sql = f"UPDATE players SET role = '{role}' WHERE player_id = {id[0]}"
        cur.execute(sql)
        print(sql)
    con_close()


    
def count_players():
    con_open()
    sql = "SELECT username FROM players"
    cur.execute(sql)
    data =  len(cur.fetchall())
    
    con_close()
    return(data)
     
def vote(type, username, player_id):
    con_open()
    sql = f'SELECT username FROM players WHERE player_id = {player_id} and dead = 0 and voted = 0 '
    cur.execute(sql)
    can_vote = cur.fetchone()
    if can_vote:
        sql1 = f"UPDATE players SET {type} = {type}+1 WHERE username = '{username}'"
        sql2 = f"UPDATE players SET voted = 1 WHERE player_id = {player_id}"
        cur.execute(sql1)
        cur.execute(sql2)
        con_close()
        return True
    con_close()
    return False
# end

def check_winner():
    con_open()
    sql = "SELECT COUNT (*) FROM players WHERE role = 'mafia' and dead = 0"
    cur.execute(sql)
    mafeas = cur.fetchone()
    sql = "SELECT COUNT (*) FROM players WHERE role != 'mafia' and dead = 0"
    cur.execute(sql)
    citezan = cur.fetchone()
    if mafeas >= citezan:
        con_close()
        return 'выйграла мафиа'
    if mafeas == 0:
        con_close()

        return 'житили победили'
    # end
    

def mafia_kill():
    con_open()
    cur.execute(f"SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    # Выбираем кол-во игроков за мафию, которых не убили
    cur.execute(
    f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia' ")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    # Максимальное кол-во голосов мафии должно быть равно кол-ву мафии
    if max_votes == mafia_alive:        # Получаем имя пользователя, за которого проголосовали
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        # Делаем update БД, ставим, что игрок мертв
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
    con_close()
    return username_killed
# end

def citizens_kill():
    con_open()
    # Выбираем большинство голосов горожан
    cur.execute(f"SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0] or 0
        # Выбираем кол-во живых горожан

    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'    # Проверяем, что только 1 человек с макс. кол-вом голосов
    if max_votes_count == 1:
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
    con_close()
    return username_killed
    

    

# reset_users()
# print(get_alive())
# set_roles()
# del_users()
# show_players()
# get_alive()