## USED TO OBTAIN A SESSION FOR THE CLIENT ##
import argparse
import asyncio
import os
import shutil
from getpass import getpass

import telethon
from pathlib import Path
from qrcode import QRCode
from rich import print

qr = QRCode()


def gen_qr(token: str):
    qr.clear()
    qr.add_data(token)
    qr.print_ascii()


async def qr_auth(client: telethon.TelegramClient):
    qr_login = await client.qr_login()

    r = False
    while not r:
        gen_qr(qr_login.url)
        print(qr_login.url)
        try:
            r = await qr_login.wait(10)
        except telethon.errors.rpcerrorlist.SessionPasswordNeededError:
            password = getpass("Please, specify 2FA password: ")
            await client.sign_in(password=password)
            r = True
        except Exception:
            await qr_login.recreate()


async def obtain_session(use_qr: bool):
    print(" >>> Initiating...")
    try:
        dir = Path('./misc/session/')
        dir.mkdir(parents=True, exist_ok=True)
        if len(os.listdir('./misc/session/')) <= 2:
            import src.logic.clients as clients
            await clients.userbot.connect()
            if use_qr:
                await qr_auth(clients.userbot)
            else:
                await clients.userbot.start()
            print("[green] >>> Session obtained successfully.[/green]")
            await clients.userbot.disconnect()
            exit(0)
    except Exception as e:
        print(f"[red] >>> Something went wrong: {e}[/red]")
        shutil.rmtree(dir)
        exit(1)
    print("[blue] >>> Session already exists! Exiting[/blue]")

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--qr', action='store_true', help='Login via QR code instead of phone number')
args = parser.parse_args()

asyncio.run(obtain_session(args.qr))