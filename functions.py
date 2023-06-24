"""
Linux/Mac files use / instead of \
"""
import json, os
import numpy as np
import discord
import sqlite3

###  PLAYER POINTS  ###

#check if json file exists
def check_json_file(id):
    if not os.path.exists(f"data/{id}.json"):
        with open((f'data/{id}.json'), 'w') as f:
            json.dump({}, f)
        print (f'{id}.json created')

#edit data
def store_user_data(server_id, user_id, data):
    #check if file exists:
    check_json_file(server_id)

    #read file content
    with open(f'data/{server_id}.json') as f:
        user_data = json.load(f)            #store file into dict

    #check if user in json file
    if str(user_id) not in user_data:   
        user_data[str(user_id)] = 0

    #update data
    user_data[str(user_id)] += data 

    #write to json file
    with open((f'data/{server_id}.json'), 'w') as f:
        f.seek(0)
        json.dump(user_data, f)
        f.truncate()

#returns user data
def get_user_data(server_id, user_id):
    #check if file exists:  
    check_json_file(server_id)

    #read file content
    with open(f'data/{server_id}.json') as f:
        user_data = json.load(f)

    #return data
    if str(user_id) in user_data:
        return user_data.get(str(user_id))
    else:
        return 0

#returns sorted dict
def get_leaderboard(server_id):
    #check if file exists:  
    check_json_file(server_id)

    #get sorted dict
    with open((f'data/{server_id}.json')) as f:
        user_data = json.load(f)
    
    keys = list(user_data.keys())
    values = list(user_data.values())
    sorted_value_index = np.argsort(values)[::-1]
    sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
 
    return sorted_dict

###  PLAYER LIST  ###

#helper function to create text file with names of members
def create_file(interact, server_id):
    file = open(f'data/{server_id}_names.txt', 'w', encoding="utf8")
    for member in interact.guild.members:
        if not member.bot:
            file.write(f'{member.name}\n')
    file.truncate()
    return open(f'data/{server_id}_names.txt', encoding="utf8")

#check if name file exists, create it if not, and return file as read mode
def check_txt_file(interact: discord.Interaction, server_id):
    path = f"data/{server_id}_names.txt"
    if not os.path.exists(path):
        create_file(interact, server_id)
    return open(f'data/{server_id}_names.txt', encoding="utf8")

### DATABASE ###

def connect(server_id):
    # try:
    conn = sqlite3.connect(f"data/{server_id}.db")
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS points_table (user_id integer, points integer)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS player_list (username text)")
    conn.commit()
    # except Exception as e:
    #     print(e)
    return conn

### PLAYER POINTS ###

#add points to user, create new entry if user does not exist
def add_points(server_id, user_id, points):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute(f"SELECT rowid FROM points_table WHERE user_id = {user_id}")
    search = cur.fetchall()

    #if user does not exist
    if len(search) == 0:
        #insert user and points
        cur.execute(f"INSERT INTO points_table VALUES (?, ?)", (user_id, points))
    else:
        #update user's points
        total = check_points(server_id, user_id) + points
        cur.execute(f"UPDATE points_table SET points = {total} WHERE user_id = {user_id}")

    conn.commit()

def check_points(server_id, user_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute(f"SELECT rowid FROM points_table WHERE user_id = {user_id}")
    search = cur.fetchall()

    if len(search) == 0:
        return 0
    else:
        #select user
        cur.execute(f"SELECT points FROM points_table WHERE user_id = {user_id}")
        search = cur.fetchall()
        return search[0][0]

def get_ldrboard(server_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #get all players
    cur.execute("SELECT * FROM points_table")
    search = cur.fetchall()

    #create list
    ldrboard = []
    for row in search:
        ldrboard.append(row)
    ldrboard.sort(key=lambda a: a[1], reverse=True)

    #convert list of tuples to list of only id numbers
    ldrboard_list = list(map(lambda x: x[0], ldrboard))

    return ldrboard_list

### PLAYER LIST ###

def get_list(server_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #search for all players in list
    cur.execute("SELECT * FROM player_list")
    search = cur.fetchall()

    final = []
    for row in search:
        final.append(row[0])
    
    return final

def clear_list(server_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #delete all rows
    cur.execute("DELETE FROM player_list")
    conn.commit()

#returns false if player already exists
def add_player(server_id, username):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute(f"SELECT rowid FROM player_list WHERE username = {username}")
    search = cur.fetchall()

    # false is user is already in list
    if len(search) == 1:
        return False
    else:
        # add user
        cur.execute(f"INSERT INTO player_list VALUES (?)", (f"{username}",))
        conn.commit()
        return True


def remove_player(server_id, username):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #delete player
    cur.execute(f"DELETE FROM player_list WHERE username = {username}")
    conn.commit()