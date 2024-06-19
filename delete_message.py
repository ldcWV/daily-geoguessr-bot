import discord
from config import DISCORD_TOKEN, CHANNEL_ID

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Ready")
    message_id = 1252634263468113983
    # Delete the message
    print("deleting")
    message = await client.get_channel(CHANNEL_ID).fetch_message(message_id)
    await message.delete()
    print("deleted")

client.run(DISCORD_TOKEN)
