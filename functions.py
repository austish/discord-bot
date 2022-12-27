import random

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

