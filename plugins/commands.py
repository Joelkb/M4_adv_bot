import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, LOG_CHANNEL, PICS
from utils import get_size, is_subscribed, temp
import re
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start"))
async def start(client, message):
    if message.chat.type in ['group', 'supergroup']:
        buttons = [[
                    InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'https://t.me/auto_m4_mallumovies_bot?startgroup=true')
                ],[
                    InlineKeyboardButton('🤴ʙᴏᴛ ᴏᴡɴᴇʀ🤴', url=f'https://t.me/creatorbeatz'),
                    InlineKeyboardButton('🍿ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ🍿', url='https://t.me/filmy_harbour')
                ],[
                    InlineKeyboardButton('ℹ️ Help', callback_data='help'),
                    InlineKeyboardButton('😊 About', callback_data='about')
                ],[
                    InlineKeyboardButton('💥 ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ 💥', url='https://t.me/+LJRsBp82HiJhNDhl')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
                        InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'https://t.me/auto_m4_mallumovies_bot?startgroup=true')
                    ],[
                        InlineKeyboardButton('🤴ʙᴏᴛ ᴏᴡɴᴇʀ🤴', url=f'https://t.me/creatorbeatz'),
                        InlineKeyboardButton('🍿ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ🍿', url='https://t.me/filmy_harbour')
                    ],[
                        InlineKeyboardButton('ℹ️ Help', callback_data='help'),
                        InlineKeyboardButton('😊 About', callback_data='about')
                    ],[
                        InlineKeyboardButton('💥 ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ 💥', url='https://t.me/+LJRsBp82HiJhNDhl')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "🍿ᴊᴏɪɴ ᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇsᴛ ɢʀᴏᴜᴘ🍿", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            btn.append([InlineKeyboardButton("🔄 Try Again", callback_data=f"checksub#{message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**താഴെ കാണുന്ന ഞങ്ങളുടെ ഗ്രൂപ്പിൽ നിങ്ങൾ ഇല്ല അതുകൊണ്ട് നിങ്ങൾക്ക് സിനിമ കിട്ടില്ല...\n\nസിനിമ വേണമെങ്കിൽ താഴെ കാണുന്ന '🍿ᴊᴏɪɴ ᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇsᴛ ɢʀᴏᴜᴘ🍿' എന്ന ബട്ടണിൽ ക്ലിക്ക് ചെയ്ത് ജോയിൻ ചെയ്ത ശേഷം ഈ താഴെ കാണുന്ന '🔄 Try Again' എന്ന ബട്ടണിൽ ക്ലിക്ക് ചെയ്യുക...\n\nഅപ്പോൾ നിങ്ങൾക്ക് file ലഭിക്കുന്നതാണ്...\n\nYou are not in the group below so you do not get the movie...\n\n If you want the movie, click on the '🍿ᴊᴏɪɴ ᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇsᴛ ɢʀᴏᴜᴘ🍿' button below to join and then click on the '🔄 Try Again' button below...\n\nThen you will get the movie files...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="markdown"
            )
        return
    if len(message.command) ==2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                        InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'https://t.me/auto_m4_mallumovies_bot?startgroup=true')
                    ],[
                        InlineKeyboardButton('🤴ʙᴏᴛ ᴏᴡɴᴇʀ🤴', url=f'https://t.me/creatorbeatz'),
                        InlineKeyboardButton('🍿ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ🍿', url='https://t.me/filmy_harbour')
                    ],[
                        InlineKeyboardButton('ℹ️ Help', callback_data='help'),
                        InlineKeyboardButton('😊 About', callback_data='about')
                    ],[
                        InlineKeyboardButton('💥 ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ 💥', url='https://t.me/+LJRsBp82HiJhNDhl')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        return
    file_id = message.command[1]
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup(
             [
                 [
                     InlineKeyboardButton("⚡ ᴊᴏɪɴ ɢʀᴏᴜᴘ ⚡", url="https://t.me/filmy_harbour"),
                     InlineKeyboardButton("💥 ꜱʜᴀʀᴇ 💥", url="https://t.me/share/url?url=%F0%9F%A4%A9%20FILMY%20HARBOUR%20%F0%9F%A4%A9%0A%0A%E0%B4%8F%E0%B4%A4%E0%B5%8D%20%E0%B4%85%E0%B5%BC%E0%B4%A7%E0%B4%B0%E0%B4%BE%E0%B4%A4%E0%B5%8D%E0%B4%B0%E0%B4%BF%20%E0%B4%9A%E0%B5%8B%E0%B4%A6%E0%B4%BF%E0%B4%9A%E0%B5%8D%E0%B4%9A%E0%B4%BE%E0%B4%B2%E0%B5%81%E0%B4%82%20%E0%B4%AA%E0%B4%9F%E0%B4%82%20%E0%B4%95%E0%B4%BF%E0%B4%9F%E0%B5%8D%E0%B4%9F%E0%B5%81%E0%B4%82%2C%20%E0%B4%B2%E0%B5%8B%E0%B4%95%E0%B4%A4%E0%B5%8D%E0%B4%A4%E0%B4%BF%E0%B4%B2%E0%B5%86%20%E0%B4%92%E0%B4%9F%E0%B5%8D%E0%B4%9F%E0%B5%81%E0%B4%AE%E0%B4%BF%E0%B4%95%E0%B5%8D%E0%B4%95%20%E0%B4%AD%E0%B4%BE%E0%B4%B7%E0%B4%95%E0%B4%B3%E0%B4%BF%E0%B4%B2%E0%B5%81%E0%B4%AE%E0%B5%81%E0%B4%B3%E0%B5%8D%E0%B4%B3%20%E0%B4%B8%E0%B4%BF%E0%B4%A8%E0%B4%BF%E0%B4%AE%E0%B4%95%E0%B4%B3%E0%B5%81%E0%B4%9F%E0%B5%86%20%E0%B4%95%E0%B4%B3%E0%B4%95%E0%B5%8D%E0%B4%B7%E0%B5%BB..%20%E2%9D%A4%EF%B8%8F%0A%0A%F0%9F%91%87%20GROUP%20LINK%20%F0%9F%91%87%0A%40filmy_harbour%0A%40filmy_harbour%0A%40filmy_harbour")
                 ],[
                     InlineKeyboardButton("🔖 ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴜʙᴛɪᴛʟᴇ 🔖", url="https://telegra.ph/DOWNLOAD-SUBTITLES-01-05")
                   ]
             ]
        )
        )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_one({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_one({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer()
    await message.message.edit('Succesfully Deleted All The Indexed Files.')

