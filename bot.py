import discord
import random
from discord import app_commands
from discord.ext import commands

import functions
import tokens

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all(), help_command=commands.DefaultHelpCommand())
TOKEN = tokens.token

#Command Groups
class commandGroup(app_commands.Group):
    ...
randomGroup = commandGroup(name = 'random', description = "random generators")
playerListGroup = commandGroup(name = 'list', description = "manage player list")
predictionGroup = commandGroup(name = 'prediction', description = "manage predictions")

@bot.event
async def on_ready():           #on startup
    print(f'{bot.user} is now running')
    try:
        bot.tree.add_command(randomGroup)
        bot.tree.add_command(playerListGroup)
        bot.tree.add_command(predictionGroup)
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command(name='secret', description='secret')                                   #define bot command
async def hello(interaction: discord.Interaction):                                       #define python command
    await interaction.response.send_message(f"You found the secret!", ephemeral=True)    #return python function

@bot.tree.command(name='help', description='get help')               
async def help(interaction: discord.Interaction):
    message = ""
    message += ":white_check_mark: **PLAYER POINTS:**\n"
    message += "   `/playerpoint` Give player points\n"
    message += "   `/check_points` Check your player points\n"
    message += "   `/leaderboard` View leaderboard\n\n"

    message += ":arrows_counterclockwise: **RANDOMIZERS:**\n"
    message += "   `/random number (num)` Gives random integer between 0 and given (num)\n"
    message += "   `/random user` Gives random user\n\n"

    message += ":1234: **TEAM GENERATOR:**\n"
    message += "   `/generate (amount)` Generate (amount) number of teams\n"
    
    message += "   > /random user and /generate pulls users from player list below\n\n"

    message += ":notepad_spiral: **PLAYER LIST:**\n"
    message += "   `/list view` View list\n"
    message += "   `/list add` Add selected player to list\n"
    message += "   `/list remove` Remove selected player from list\n"
    message += "   `/list clear` Clear all players from list\n"
    message += "   `/list fill` Fill player list with all users\n\n"

    message += ":watch: **PREDICTIONS:**\n"
    message += "   `/prediction place` Place your top 3 predictions.\n"
    message += "   `/prediction odds` View current odds.\n"
    message += "   `/prediction clear` Clear all predictions.\n"



    await interaction.response.send_message(message)

###########################
###  RANDOM GENERATORS  ###
###########################

#random number generator
@randomGroup.command(name='number', description="get random number between 0 and given number, including given number")
@app_commands.describe(num = "maximum number")
async def random_num(interaction: discord.Interaction, num: int):
    num = random.randrange(0,num+1)
    await interaction.response.send_message(num)    

#random user generator
@randomGroup.command(name='user', description="get random user from Player List")
async def random_user(interaction: discord.Interaction):
    #get names
    names = functions.get_list(interaction.guild.id)
    #choose random name
    user = random.choice(names)
    await interaction.response.send_message(user) 

#######################
###  PLAYER POINTS  ###
#######################

#award/remove player points    
@bot.tree.command(name='playerpoint', description="give player points")
async def playerpoint(interaction: discord.Interaction, *, member: discord.Member, amount: float):
    functions.add_points(interaction.guild.id, member.id, amount)
    await interaction.response.send_message(f"{interaction.user.mention} gave {member.mention} {amount} player point(s)! They now have {functions.get_points(interaction.guild.id, member.id)} player points.")    
    
#check player points
@bot.tree.command(name='check_points', description="check player points")
async def check_points(interaction: discord.Interaction):
    points = functions.get_points(interaction.guild.id, interaction.user.id)
    await interaction.response.send_message(f'You have {points} player points.', ephemeral=True)

#player point leaderboard
@bot.tree.command(name='leaderboard', description="display playerpoint leaderboard")
async def leaderboard(interaction: discord.Interaction):
    em = discord.Embed(title = "Player Point Leaderboard")
    ids = functions.get_leaderboard(interaction.guild.id)

    #create embed
    for count, user_id in enumerate(ids):
        user = await bot.fetch_user(user_id)
        em.add_field(name = (f'{count+1}. {user.name}'), value = (f'Points: {functions.get_points(interaction.guild.id, user_id)}'), inline=False)
    await interaction.response.send_message(embed = em)

########################
###  TEAM GENERATOR  ###
########################

#generate teams
@bot.tree.command(name='generate', description="generate teams")
@app_commands.describe(amount = "number of teams")
async def teams(interaction: discord.Interaction, amount: int):
    #get names
    names = functions.get_list(interaction.guild.id)

    #create teams
    random.shuffle(names)
    teams = []
    for i in range(amount):
        teams.append([])
    for count, name in enumerate(names):
        teams[count%amount].append(name)

    #create message
    message = ""
    for count, team in enumerate(teams):
        message += "Team " + str(count+1) + ": "
        for person in team:
            if person != team[-1]:
                message += person + ", "
            else:
                message += person + "\n"
    
    await interaction.response.send_message(message)

#####################
###  PLAYER LIST  ###
#####################

#get player list
@playerListGroup.command(name='view', description="view list of players")
async def view(interaction: discord.Interaction):
    names = functions.get_list(interaction.guild.id)
    await interaction.response.send_message(embed = display_list(names))

#fill player list
@playerListGroup.command(name='fill', description="fill list of players")
async def fill(interaction: discord.Interaction):
    names = functions.fill_list(interaction)
    await interaction.response.send_message(embed = display_list(names))    

#clear list
@playerListGroup.command(name='clear', description="clear list of players")
async def clear(interaction: discord.Interaction):
    names = functions.clear_list(interaction.guild.id)
    await interaction.response.send_message(embed = display_list(names))

#add player
@playerListGroup.command(name='add', description="add player to list")
async def add(interaction: discord.Interaction, member: discord.Member):
    names = functions.add_player(interaction.guild.id, member.display_name)
    await interaction.response.send_message(embed = display_list(names))

#remove player
@playerListGroup.command(name='remove', description="remove player from list")
async def remove(interaction: discord.Interaction, member: discord.Member):
    names = functions.remove_player(interaction.guild.id, member.display_name)
    await interaction.response.send_message(embed = display_list(names))

#helper func to create player list embed
def display_list(names):
    #create embed
    em = discord.Embed(title = "Player List")
    for i in range(len(names)):
        em.add_field(name = (f'{i+1}. {names[i]}'), value='', inline=False)
    return em

#####################
###  PREDICTIONS  ###
#####################

@predictionGroup.command(name='place', description="Place a prediction for the top 3 positions")
async def predict(interaction: discord.Interaction, first_place: discord.Member, second_place: discord.Member, third_place: discord.Member):
    # Check if any of the members are duplicated
    if len({first_place.id, second_place.id, third_place.id}) < 3:
        await interaction.response.send_message(
            f"{interaction.user.mention} You cannot select the same user more than once.",
            ephemeral=True
        )
        return
    
    # Proceed with adding the prediction if all three are unique
    functions.add_prediction(interaction.guild.id, interaction.user.id, first_place.display_name, second_place.display_name, third_place.display_name)
    
    await interaction.response.send_message(
        f"{interaction.user.mention} has placed a prediction: 1st - {first_place.display_name}, 2nd - {second_place.display_name}, 3rd - {third_place.display_name}"
    )

@predictionGroup.command(name='odds', description="Get the current odds for the first place prediction")
async def predict_odds(interaction: discord.Interaction):
    first_place_odds, top_3_odds = functions.calculate_odds(interaction.guild.id)

    if not first_place_odds:
        await interaction.response.send_message("No predictions have been made yet.")
        return

    # Create an embed to display odds
    em = discord.Embed(title="Current Odds")
    players = set()

    # First place
    rank = 1
    for player, odd in first_place_odds.items():
        player_name = f"{rank}. {player} - {odd * 100:g}%"
        odds_text = f"Top 3: {top_3_odds[player] * 100:g}%"
        em.add_field(name=player_name, value=odds_text, inline=False)
        players.add(player)
        rank += 1
    
    # Top 3
    for player, odd in top_3_odds.items():
        if player not in players:
            player_name = f"{rank}. {player} - 0%"
            odds_text = f"Top 3: {top_3_odds[player] * 100:g}%"
            em.add_field(name=player_name, value=odds_text, inline=False)
            rank += 1

    await interaction.response.send_message(embed=em)

@predictionGroup.command(name='clear', description="Clear all predictions")
async def clear_predictions(interaction: discord.Interaction):
    functions.clear_predictions(interaction.guild.id)
    await interaction.response.send_message("All predictions have been cleared.")

bot.run(TOKEN)