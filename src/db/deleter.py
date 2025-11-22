"""
    Helper file; Used to clear database messages in a while
"""
import logging
import asyncio
import datetime

from dateutil.relativedelta import relativedelta 
from db import operations
from db.schema import UserSettings

WAIT_TIME = 666


async def start_message_deleter_service():
    logging.info("[+] Started message deleter service")
    today = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    while True:
        logging.info("[i] Deleter: Polling now")
        user_settings: UserSettings = await operations.get_user_settings()
        delete_after_date_str: str = user_settings.message_deletion_delta
        delete_after_date = today - relativedelta(days=int(delete_after_date_str))

        await operations.delete_messages_by_date(delete_after_date)
        logging.info(f"[i] Deleter: Waiting {WAIT_TIME}")
        await asyncio.sleep(WAIT_TIME)