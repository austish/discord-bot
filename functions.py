import random, json , os
import numpy as np

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
    if os.path.exists(f"C:\\Users\\austi\\OneDrive\\Documents\\CS\\python\\discord bot\\data\\{server_id}.json"):
        print (f'{server_id}.json exists')
    else:
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
    if user_id in user_data:
        return user_data.get(user_id)
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
