import os
from dotenv import load_dotenv
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import re

load_dotenv()

SESSION_NAME = os.getenv('SESSION_NAME')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
fetchCount = 0
result = ["oldpfp"]

async def main():
    try:
        await getUserBio()
    except Exception as e:
        if "FloodWaitError" in str(e):
            retryAfter = 10
            await handleRateLimit(retryAfter)
        else:
            print(f"Error: {e}")
    finally:
        await sendListToSavedMessages()
    
async def getUserBio():
    chat = await client.get_entity('fluidchat')
    #                               ^ replace with the target group's username

    async for user in client.iter_participants(chat):
        if user.bot: 
            continue
        
        # get full user details, and then their bio
        member  = await client(GetFullUserRequest(user.id))
        bio = member.full_user.about

        # save the extracted username to a file
        with open('mentions.txt', 'a') as file:
            if bio is not None:
                mentions = re.findall(r'@(\w+)', bio)
                if len(mentions) != 0:
                    #file.write('\n'.join(mentions) + '\n')
                    for name in mentions:
                        global fetchCount
                        global result
                        fetchCount = fetchCount + 1
                        result.append(f"{fetchCount} @{name}")
                        file.write(f"{fetchCount} @{name}\n")

# probably this is not needed, but still just in case
async def handleRateLimit(retryAfter):
    print(f"Cooling down... Retrying after {retryAfter} seconds...")
    await asyncio.sleep(retryAfter)
    await getUserBio()

# send the extracted list to saved messages
async def sendListToSavedMessages():
    await client.send_message('me', '\n'.join(result))

with client:
    client.loop.run_until_complete(main())
