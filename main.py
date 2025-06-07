import aiosqlite
import discord
from discord.ext import commands
from keep_alive import keep_alive
import os, json, re, asyncio, random
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.models import load_model
import aiohttp
TOKEN = "Put discord token here bro"
ownerid = 0
timerlist=[0.0,2.2,1,2.1,1.5,2,0.8,1.1,0.4,0.3,0.2,0.5,2,1,1.1,2,0.1,2,2.0]

bot_prefix = "%"
bot = commands.Bot(command_prefix="blahblah", intents=discord.Intents.all())
loaded_model = load_model('model.h5', compile=False)
with open('classes.json', 'r') as f:
    classes = json.load(f)

with open('pokemon','r', encoding='utf8') as file:
    pokemon_list = file.read()

def solve(message):
    hint = []
    for i in range(15,len(message) - 1):
        if message[i] != '\\':
            hint.append(message[i])
    hint_string = ''
    for i in hint:
        hint_string += i
    hint_replaced = hint_string.replace('_', '.')
    return re.findall('^'+hint_replaced+'$', pokemon_list, re.MULTILINE)
  
async def hint_solver(message: discord.Message):
    c = await bot.loop.run_in_executor(
        None,
        solve,
        message.content
    )
    ch = message.channel
    if not len(c):
        await ch.send("Couldn't find pokemon!")
    else:
        for i in c:       
            await ch.send(f'The Pokémon is {i.lower()}')

@bot.event
async def on_ready():
    activity= activity = discord.Activity(type=discord.ActivityType.watching, name="Pokétwo•FFA")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print('Logged in as {0.user}'.format(bot))
    bot.db = await aiosqlite.connect("pokemon.db")
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS pokies (command str)")
    print("Bot started")
    await bot.db.commit()

@bot.event
async def on_message(message):
    while not hasattr(bot, 'db'):
        await asyncio.sleep(1.0)
    if message.author.id == 716390085896962058:
            if len(message.embeds)>0:
                embed = message.embeds[0]
                if "appeared!" in embed.title :
                    if embed.image:
                            url = embed.image.url
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url=url) as resp:
                                    if resp.status == 200:
                                        content = await resp.read()
                                        image_data = BytesIO(content)
                                        image = Image.open(image_data)
                            preprocessed_image = await preprocess_image(image)
                            predictions = loaded_model.predict(preprocessed_image)
                            classes_x = np.argmax(predictions, axis=1)
                            name= list(classes.keys())[classes_x[0]]
#                    print(f'{name} {message.channel.name}')
                            await asyncio.sleep(random.choice(timerlist))
                            embed = discord.Embed(
                                title=f'{name.lower()}',
                                description="Event Pokémon may not be named correctly",
                                color=discord.Color(value=int("ff6e05", 16))
                                )       
                            await message.channel.send(embed=embed)       
            elif 'The pokémon is' in message.content:
              await catch(message)

async def preprocess_image(image):
    image = image.resize((64, 64))
    image = np.array(image)
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image

keep_alive()
bot.run(TOKEN)
