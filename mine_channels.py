# -*- coding: utf-8 -*
import asyncio
import datetime
import json

import telethon
from logger import Logger
from telethon import functions, types
from settings import Settings
from telethon.errors import FloodWaitError, ChannelsTooMuchError, InvalidBufferError, AuthKeyError, AuthKeyNotFound
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest


async def mine_channels(settings: Settings, client: str, channel: str):
    with client:
        result = await client(functions.messages.CreateChatRequest(
            users=['username'],
            title='My awesome title',
            ttl_period=42
        ))
        result = await client(functions.messages.EditChatAboutRequest)
        print(result.stringify())