## USED TO OBTAIN A SESSION FOR THE CLIENT ##
import asyncio
import os

from pathlib import Path
from rich import print


async def obtain_session():
    print(" >>> Initiating...")
    try:
        dir = Path('./misc/session/')
        dir.mkdir(parents=True, exist_ok=True)
        if len(os.listdir('./misc/session/')) <= 1:
            import src.logic.clients as clients
            await clients.userbot.start()
            print("[green] >>> Session obtained successfully.[/green]")
            await clients.userbot.disconnect()
            exit(0)
    except Exception as e:
        print(f"[red] >>> Something went wrong: {e}[/red]")
        os.rmdir('./misc/session/')
        exit(1)
    print("[blue] >>> Session already exists! Exiting[/blue]")

asyncio.run(obtain_session())