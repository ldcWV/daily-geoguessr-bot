import discord
from config import EMAIL, PASSWORD, DISCORD_TOKEN, CHANNEL_ID, MAP_URL, OPENAI_KEY, ASSISTANT_ID, THREAD_ID
from browser_side import sign_in_to_geoguessr, take_results_screenshot, create_challenge
import time
import traceback
import os
os.environ['OPENAI_API_KEY'] = OPENAI_KEY
from openai import OpenAI

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    try:
        channel = client.get_channel(CHANNEL_ID)

        # Sign in to Geoguessr
        page = await sign_in_to_geoguessr(EMAIL, PASSWORD)
        
        # First figure out what the last challenge link was by looking through message history
        last_challenge_url = None
        async for message in channel.history(limit=1000):
            if message.author == client.user:
                if not "DAILY CHALLENGE" in message.content:
                    continue
                last_challenge_url = message.content.split("\n")[-1]
                break

        date = time.strftime("%m/%d/%Y")

        # Post results of last challenge
        if last_challenge_url:
            print("Posting results of last challenge...")
            results_url = last_challenge_url.replace("challenge", "results")
            results_message = f"{date} challenge ended! Results here: {results_url}"
            await channel.send(results_message)
            try:
                print("Taking results screenshot...")
                fname = await take_results_screenshot(page, results_url)
                # fname = "trimmed.png"
                message = await channel.send("", file=discord.File(fname))
                screenshot_url = message.attachments[0].url

                print("Accessing OpenAI API...")
                openai_client = OpenAI()
                assistant = openai_client.beta.assistants.retrieve(ASSISTANT_ID)
                thread = openai_client.beta.threads.retrieve(THREAD_ID)

                message = openai_client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": screenshot_url
                            }
                        }
                    ]
                )

                run = openai_client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )

                if run.status == "completed":
                    print("Run succeeded, sending message to channel")
                    messages = openai_client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    analysis = messages.data[0].content[0].text.value
                    
                    # Send analysis to channel in blocks of 2000 characters
                    for i in range(0, len(analysis), 2000):
                        await channel.send(analysis[i:i+2000])
                else:
                    print(run.status)
            except:
                print("Failed to take results screenshot or access OpenAI API, probably bc Lawrence didn't play")

        # Create new challenge
        challenge_url = await create_challenge(page, MAP_URL)
        # challenge_url = "https://www.geoguessr.com/challenge/kjNWXIw0mHTrrXRS"
        await channel.send(f"**DAILY CHALLENGE [{date}]**\n{challenge_url}")
    except:
        await channel.send(f"An error occurred, WTF fix it @WhaleVomit ```{traceback.format_exc()}```")

    await client.close()

def run_daily_challenge():
    client.run(DISCORD_TOKEN)

# run_daily_challenge()