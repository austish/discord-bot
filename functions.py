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
    conn = sqlite3.connect("player_points.db")
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS test (db_id INTEGER PRIMARY KEY, user_id int, points integer)")
    conn.commit()
    # except Exception as e:
    #     print(e)
    return conn

#add points to user, create new entry if user does not exist
def add_points(server_id, user_id, points):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute(f"SELECT db_id FROM test WHERE user_id = {user_id}")
    search = cur.fetchall()

    #if user does not exist
    if len(search) == 0:
        #insert user and points
        cur.execute(f"INSERT INTO test VALUES (NULL, ?, ?)", (user_id, points))
    else:
        #update user's points
        cur.execute(f"UPDATE test SET points = {points} WHERE user_id = {user_id}")

    conn.commit()
    conn.close()

#check user's points
def check_points(server_id, user_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute(f"SELECT db_id FROM test WHERE user_id = {user_id}")
    search = cur.fetchall()
    
    #if user does not exist
    if len(search) == 0:
        #select user
        cur.execute(f"SELECT points FROM test WHERE user_id = {user_id}")
        search = cur.fetchall()
        print(search)
    else:
        print("User has 0 points")
    
    conn.close()

connect(333)
add_points(333, 1, 1)
check_points(333, 1)