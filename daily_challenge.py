import discord
from config import EMAIL, PASSWORD, DISCORD_TOKEN, CHANNEL_ID, MAP_URL, MAP_NAME
from browser_side import sign_in_to_geoguessr, take_results_screenshot, create_challenge
import time

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)

    # Sign in to Geoguessr
    page = await sign_in_to_geoguessr(EMAIL, PASSWORD)
    
    # First figure out what the last challenge link was by looking through message history
    last_challenge_url = None
    # last_challenge_url = "https://www.geoguessr.com/challenge/kjNWXIw0mHTrrXRS"
    async for message in channel.history(limit=1000):
        if message.author == client.user:
            if not "DAILY CHALLENGE" in message.content:
                continue
            last_challenge_url = message.content.split("\n")[-1]
            break

    date = time.strftime("%m/%d/%Y")

    # Post results of last challenge
    if last_challenge_url:
        try:
            results_url = last_challenge_url.replace("challenge", "results")
            fname = await take_results_screenshot(page, results_url)
            fname = "trimmed.png"
            await channel.send(f"{date} challenge ended! Results here: {results_url}", file=discord.File(fname))
        except:
            print("Failed to take results screenshot, probably bc Lawrence didn't play")

    # Create new challenge
    challenge_url = await create_challenge(page, MAP_URL)
    # challenge_url = "https://www.geoguessr.com/challenge/kjNWXIw0mHTrrXRS"
    await channel.send(f"**DAILY CHALLENGE [{date}]**\n{challenge_url}")

def run_daily_challenge():
    client.run(DISCORD_TOKEN)

run_daily_challenge()