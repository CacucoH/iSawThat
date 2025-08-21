## USED TO OBTAIN A SESSION FOR THE CLIENT ##
import asyncio
import os

async def obtain_session():
    if len(os.listdir('./misc/session/')) <= 1:
        import src.logic.clients as clients
        await clients.userbot.start()
        print("Session obtained successfully.")
        await clients.userbot.disconnect()
        exit(0)

    print("Session already exists. Exiting")

asyncio.run(obtain_session())