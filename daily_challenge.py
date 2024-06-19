import discord
from config import NCFA_TOKEN, DISCORD_TOKEN, CHANNEL_ID, MAP_ID, OPENAI_KEY, ASSISTANT_ID, THREAD_ID
from browser_side import make_session, get_results, create_challenge
import time
import traceback
import os
import json
os.environ['OPENAI_API_KEY'] = OPENAI_KEY
from openai import OpenAI

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    try:
        channel = client.get_channel(CHANNEL_ID)

        # Sign in to Geoguessr
        session = make_session(NCFA_TOKEN)
        
        # First figure out what the last challenge id was by looking through message history
        last_challenge_id = None
        async for message in channel.history(limit=1000):
            if message.author == client.user:
                if message.embeds is None or len(message.embeds) == 0:
                    continue
                if message.embeds[0].title is None or not "New Daily Challenge" in message.embeds[0].title:
                    continue
                last_challenge_id = message.embeds[0].url.split("/")[-1]
                break

        # Post results of last challenge
        if last_challenge_id:
            results = get_results(session, last_challenge_id)

            # Get ChatGPT analysis of results
            openai_client = OpenAI()
            assistant = openai_client.beta.assistants.retrieve(ASSISTANT_ID)
            thread = openai_client.beta.threads.retrieve(THREAD_ID)

            openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=json.dumps(results, indent=4)
            )

            run = openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            assert run.status == "completed"
            messages = openai_client.beta.threads.messages.list(
                thread_id=thread.id
            )
            analysis = messages.data[0].content[0].text.value

            # Sort players by score to be displayed in the Discord message
            players = []
            for player in results['players']:
                players.append((player['totalScore'], player['playerName']))
            players.sort(reverse=True)
            
            # Send analysis to channel in blocks of 2000 characters. Attach embed in the last block.
            MAX_CHARS = 4096
            desc = analysis if len(analysis) <= MAX_CHARS else analysis[:MAX_CHARS - 3] + "..."
            embed = discord.Embed(
                title=f"Daily Challenge Results",
                description=desc,
                url=f"https://www.geoguessr.com/results/{last_challenge_id}",
                color=2782675
            )
            embed.add_field(name="User", value="\n".join([p[1] for p in players]), inline=True)
            embed.add_field(name="Score", value="\n".join([str(p[0]) for p in players]), inline=True)
            await channel.send(embed=embed)

        # Create new challenge
        challenge_id = create_challenge(session, MAP_ID)
        date = time.strftime("%m/%d/%Y")
        embed = discord.Embed(
            title=f"New Daily Challenge [{date}]",
            description="Good luck!",
            url=f"https://www.geoguessr.com/challenge/{challenge_id}",
            color=5428010
        )
        embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTZus44GbLGe3ivveQmuMkkGtOVF8m0IEvyoQ&s")
        await channel.send(embed=embed)
    except:
        await channel.send(f"An error occurred, WTF fix it @WhaleVomit ```{traceback.format_exc()}```")

    await client.close()

def run_daily_challenge():
    client.run(DISCORD_TOKEN)

# run_daily_challenge()