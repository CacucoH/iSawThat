"""
    Helper file; Used to clear database messages in a while
"""
import logging
import asyncio
import datetime

from dateutil.relativedelta import relativedelta 
from db.operations import delete_messages_by_date, get_user_settings
from logic.helper_funcs import beautify_logger_name
from db.schema import UserSettings

logger = logging.getLogger(beautify_logger_name(__name__))
WAIT_TIME = 666 # why not? i'd say it's a nice number


async def start_message_deleter_service():
    logger.info("[+] Started message deleter service")
    today = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    while True:
        logger.info("[i] Polling now")
        user_settings: UserSettings = await get_user_settings()
        delete_after_date_str: str = user_settings.message_deletion_delta
        delete_after_date = today - relativedelta(days=int(delete_after_date_str))

        await delete_messages_by_date(delete_after_date)
        # await delete_old_attachments(delete_after_date)
        
        logger.info(f"[i] Done; Waiting {WAIT_TIME} seconds until next poll...")
        await asyncio.sleep(WAIT_TIME)