import random, json , os
import numpy as np
import discord

def rps(user_input: str) -> str:
    list = ["rock", "paper", "scissors"]
    bot_input = list[random.randrange(3)]
    if user_input == 'rock':
        print('rock')
        if bot_input == 'rock':
            result = 'tied'
        elif bot_input == 'paper':
            result = 'lost'
        elif bot_input == 'scissors':
            result = 'won'
    elif user_input == 'scissors':
        print('scissors')
        if bot_input == 'rock':
            result = 'lost'
        elif bot_input == 'paper':
            result = 'won'
        elif bot_input == 'scissors':
            result = 'tied'
    elif user_input == 'paper':
        print('paper')
        if bot_input == 'rock':
            result = 'won'
        elif bot_input == 'paper':
            result = 'tied'
        elif bot_input == 'scissors':
            result = 'lost'
    else:
        return 'invalid input'
    return (f'Bot played {bot_input}. You {result}!')

def store_user_data(server_id, user_id, data):
    #check if file exists:
    if not os.path.exists(f"C:\\Users\\austi\\OneDrive\\Documents\\CS\\python\\discord bot\\data\\{server_id}.json"):
        with open((f'data\\{server_id}.json'), 'w') as f:
            json.dump({}, f)
            print (f'{server_id}.json created')

    #read file content
    with open((f'data\\{server_id}.json'), 'r') as f:
        user_data = json.load(f)            #store file into dict

    #check if user in json file
    if str(user_id) not in user_data:   
        user_data[str(user_id)] = 0

    #update data
    user_data[str(user_id)] += data 

    #write to json file
    with open((f'data\\{server_id}.json'), 'w') as f:
        f.seek(0)
        json.dump(user_data, f)
        f.truncate()

def get_user_data(server_id, user_id):
    #read file content
    with open((f'data\\{server_id}.json'), 'r') as f:
        user_data = json.load(f)

    #return data
    if str(user_id) in user_data:
        return user_data.get(str(user_id))
    else:
        return 0

def get_leaderboard(server_id):
    with open((f'data\\{server_id}.json'), 'r') as f:
        user_data = json.load(f)
    
    keys = list(user_data.keys())
    values = list(user_data.values())
    sorted_value_index = np.argsort(values)[::-1]
    sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
 
    return sorted_dict

###  TEAM GENERATOR  ###

#helper function to create text file with names of members
def create_file(interact, path, id):
    file = open(f'data\\{id}_names.txt', 'w', encoding="utf8")
    for member in interact.guild.members:
        if not member.bot:
            file.write(f'{member.name}\n')
    file.truncate()

#check if name file exists, create it if not, add all names, and return file as read mode
def check_file(interact: discord.Interaction, server_id):
    path = f"C:\\Users\\austi\\OneDrive\\Documents\\CS\\python\\discord bot\\data\\{server_id}_names.txt"
    if not os.path.exists(path):
        create_file(interact, path, server_id)
    elif os.stat(path).st_size == 0:
        create_file(interact, path, server_id)
    return open(f'data\\{server_id}_names.txt', 'r', encoding="utf8")