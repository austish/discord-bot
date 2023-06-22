"""
Linux/Mac files use / instead of \
"""
import json, os
import numpy as np
import discord

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

###  TEAM GENERATOR  ###

#helper function to create text file with names of members
def create_file(interact, id):
    file = open(f'data/{id}_names.txt', 'w', encoding="utf8")
    for member in interact.guild.members:
        if not member.bot:
            file.write(f'{member.name}\n')
    file.truncate()

#check if name file exists, create it if not, and return file as read mode
def check_txt_file(interact: discord.Interaction, server_id):
    path = f"data/{server_id}_names.txt"
    if not os.path.exists(path):
        create_file(interact, server_id)
    return open(f'data/{server_id}_names.txt', encoding="utf8")