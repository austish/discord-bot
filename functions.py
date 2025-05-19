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

### PREDICTIONS ###

def add_prediction(server_id, user_id, first_place, second_place, third_place):
    conn = connect(server_id)
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS predictions (user_id integer, first_place text, second_place text, third_place text)")
    
    # Check if prediction already exists for the user
    cur.execute("SELECT rowid FROM predictions WHERE user_id = ?", (user_id,))
    search = cur.fetchall()

    if len(search) == 0:
        # Insert new prediction
        cur.execute("INSERT INTO predictions VALUES (?, ?, ?, ?)", (user_id, first_place, second_place, third_place))
    else:
        # Update existing prediction
        cur.execute("UPDATE predictions SET first_place = ?, second_place = ?, third_place = ? WHERE user_id = ?", 
                    (first_place, second_place, third_place, user_id))

    conn.commit()

def get_predictions(server_id):
    conn = connect(server_id)
    cur = conn.cursor()
    cur.execute("SELECT * FROM predictions")
    predictions = cur.fetchall()
    return predictions

def calculate_odds(server_id):
    predictions = get_predictions(server_id)
    
    first_place_count = {}
    top_3_count = {}
    
    for _, first, second, third in predictions:
        if first in first_place_count:
            first_place_count[first] += 1
        else:
            first_place_count[first] = 1

        if first in top_3_count:
            top_3_count[first] += 1
        else:
            top_3_count[first] = 1
        if second in top_3_count:
            top_3_count[second] += 1
        else:
            top_3_count[second] = 1
        if third in top_3_count:
            top_3_count[third] += 1
        else:
            top_3_count[third] = 1        

    # Convert counts to odds
    first_place_total = sum(first_place_count.values())
    total_predictions = len(predictions)
    
    first_place_odds = {player: round(count / first_place_total, 2) for player, count in first_place_count.items()}
    first_place_odds = dict(sorted(first_place_odds.items(), key=lambda item: item[1], reverse=True))

    top_3_odds = {player: round(count / total_predictions, 2) for player, count in top_3_count.items()}
    top_3_odds = dict(sorted(top_3_odds.items(), key=lambda item: item[1], reverse=True))   
    
    return first_place_odds, top_3_odds

def clear_predictions(server_id):
    conn = connect(server_id)
    cur = conn.cursor()

    #delete all rows
    cur.execute("DELETE FROM predictions")
    conn.commit()