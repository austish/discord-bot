import interactions
from functions import rps

bot = interactions.Client(token='MTA0MDg3NzA0MDM1OTk4MTA5Ng.GPmMVh.9C_oN9zDzAxGN9TiqyEnSfXdjOgi3Fnw8PcbpI')



@bot.command(name = "rps",
    description="Play rock, paper, scissors with the bot",
    options = [
        interactions.Option("member"),
        interactions.Option(name = "Paper", value = 2),
        interactions.Option(name = "Scissors", value = 3)
    ]
)
async def r_p_s(ctx: interactions.CommandContext, text: str):    #define python command
    result = f'You selected: `{text.name}` \n{rps(text.name.lower())}'
    await ctx.send(result)          

bot.start()