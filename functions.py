import discord
import sqlite3

### DATABASE ###

def connect(server_id):
    conn = sqlite3.connect(f"data/{server_id}.db")
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS points_table (user_id integer, points integer)")
    cur.execute(f"CREATE TABLE IF NOT EXISTS player_list (username text)")
    conn.commit()
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
        total = get_points(server_id, user_id) + points
        cur.execute(f"UPDATE points_table SET points = {total} WHERE user_id = {user_id}")

    conn.commit()

def get_points(server_id, user_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute(f"SELECT rowid FROM points_table WHERE user_id = ?", (user_id,))
    search = cur.fetchall()
    if len(search) == 0:
        return 0
    else:
        #select user
        cur.execute(f"SELECT points FROM points_table WHERE user_id = ?", (user_id,))
        search = cur.fetchall()
        return search[0][0]

def get_leaderboard(server_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #get all players
    cur.execute("SELECT * FROM points_table ORDER BY points")
    search = cur.fetchall()

    #create list
    leaderboard = []
    for i in range(len(search)):
        leaderboard.append(search[i][0])

    # #convert list of tuples to list of id integers
    # ids = list(map(lambda x: x[0], leaderboard))
    leaderboard.reverse()
    return leaderboard

### PLAYER LIST ###

def get_list(server_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #search for all players in list
    cur.execute("SELECT * FROM player_list")
    search = cur.fetchall()

    #create list
    names = []
    for row in search:
        names.append(row[0])
    
    return names

def clear_list(server_id):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #delete all rows
    cur.execute("DELETE FROM player_list")
    conn.commit()

    return get_list(server_id)

#fills list with all players, returning a list of names
def fill_list(interaction: discord.Interaction):
    #get names
    names = get_list(interaction.guild.id)
    for member in interaction.guild.members:
        #add names that arent already in
        if member not in names and not member.bot:
            add_player(interaction.guild.id, member.display_name)

    return get_list(interaction.guild.id)

#returns false if player already exists
def add_player(server_id, username):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #check if user exists
    cur.execute("SELECT rowid FROM player_list WHERE username = ?", (username,))
    search = cur.fetchall()

    if len(search) != 1:
        # add user
        cur.execute(f"INSERT INTO player_list VALUES (?)", (username,))
        conn.commit()
    
    return get_list(server_id)


def remove_player(server_id, username):
    #establish connection
    conn = connect(server_id)
    cur = conn.cursor()

    #delete player
    cur.execute(f"DELETE FROM player_list WHERE username = ?", (username,))
    conn.commit()

    return get_list(server_id)

### OLD PLAYER POINTS  ###

#check if json file exists
# def check_json_file(id):
#     if not os.path.exists(f"data/{id}.json"):
#         with open((f'data/{id}.json'), 'w') as f:
#             json.dump({}, f)
#         print (f'{id}.json created')

#edit data
# def store_user_data(server_id, user_id, data):
#     #check if file exists:
#     check_json_file(server_id)

#     #read file content
#     with open(f'data/{server_id}.json') as f:
#         user_data = json.load(f)            #store file into dict

#     #check if user in json file
#     if str(user_id) not in user_data:   
#         user_data[str(user_id)] = 0

#     #update data
#     user_data[str(user_id)] += data 

#     #write to json file
#     with open((f'data/{server_id}.json'), 'w') as f:
#         f.seek(0)
#         json.dump(user_data, f)
#         f.truncate()

#returns user data
# def get_user_data(server_id, user_id):
#     #check if file exists:  
#     check_json_file(server_id)

#     #read file content
#     with open(f'data/{server_id}.json') as f:
#         user_data = json.load(f)

#     #return data
#     if str(user_id) in user_data:
#         return user_data.get(str(user_id))
#     else:
#         return 0

#returns sorted dict
# def get_leaderboard(server_id):
#     #check if file exists:  
#     check_json_file(server_id)

#     #get sorted dict
#     with open((f'data/{server_id}.json')) as f:
#         user_data = json.load(f)
    
#     keys = list(user_data.keys())
#     values = list(user_data.values())
#     sorted_value_index = np.argsort(values)[::-1]
#     sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
 
#     return sorted_dict