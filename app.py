import os
import glob
import json
import logging
import asyncio
import youtube_dl
from pytube import YouTube
from youtube_search import YoutubeSearch
from pytgcalls import PyTgCalls, idle
from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded
from pytgcalls.types import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo
)
from pyrogram import Client, filters
from pyrogram.raw.base import Update
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from helpers.queues import QUEUE, add_to_queue, get_queue, clear_queue, pop_an_item
from helpers.admin_check import *

bot = Client(
    "Music Stream Bot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

client = Client(os.environ["SESSION_NAME"], int(os.environ["API_ID"]), os.environ["API_HASH"])

app = PyTgCalls(client)

OWNER_ID = int(os.environ["OWNER_ID"])

LIVE_CHATS = []

START_TEXT = """
━━━━━━━━━━━━━━━━━━━
**𝙷𝚎𝚕𝚕𝚘**, <b>{}</b> **𝙸'𝚖 𝚂𝚞𝚙𝚎𝚛 𝙵𝚊𝚜𝚝 𝙼𝚞𝚜𝚒𝚌 𝙿𝚕𝚊𝚢𝚎𝚛 𝙱𝚘𝚝 𝙵𝚘𝚛 𝚃𝚎𝚕𝚎𝚐𝚛𝚊𝚖 𝙶𝚛𝚘𝚞𝚙𝚜 𝙰𝚕𝚕𝚘𝚠𝚜 𝚈𝚘𝚞 𝙿𝚕𝚊𝚢 𝙼𝚞𝚜𝚒𝚌 𝙰𝚗𝚍 𝚅𝚒𝚍𝚎𝚘𝚜 𝙾𝚗 𝙶𝚛𝚘𝚞𝚙 𝚃𝚑𝚛𝚘𝚞𝚐𝚑 𝚃𝚑𝚎 𝙽𝚎𝚠 𝚃𝚎𝚕𝚎𝚐𝚛𝚊𝚖 𝚅𝚒𝚍𝚎𝚘 𝙲𝚑𝚊𝚝....**
┏━━━━━━━━━━━━━━━━━┓
┣★ **𝙱𝚊𝚜𝚎𝚍 𝙾𝚗 𝙻𝚊𝚝𝚎𝚜𝚝 𝚅𝚎𝚛𝚜𝚒𝚘𝚗**
┣★ **𝙱𝚎𝚜𝚝 𝙰𝚞𝚍𝚒𝚘 𝚀𝚞𝚊𝚕𝚒𝚝𝚢**
┣★ **𝙵𝚊𝚜𝚝 & 𝙿𝚘𝚠𝚎𝚛𝚏𝚞𝚕 𝙿𝚕𝚊𝚢𝚎𝚛**
┣★ **𝚀𝚞𝚎𝚞𝚎𝚜 𝙰𝚟𝚊𝚒𝚕𝚊𝚋𝚕𝚎**
┣★ **𝙼𝚞𝚕𝚝𝚒 𝙲𝚑𝚊𝚝𝚜 𝚂𝚞𝚙𝚙𝚘𝚛𝚝𝚎𝚍**
┣★ **𝚈𝚃 𝙻𝚒𝚟𝚎 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐 𝚂𝚞𝚙𝚙𝚘𝚛𝚝𝚎𝚍**
┣★ **𝚁𝚎𝚙𝚘𝚛𝚝 𝙱𝚞𝚐𝚜:** @MissCutie_Support
┣★ **𝙿𝚘𝚠𝚎𝚛𝚎𝚍 𝙱𝚢:** @MissCutieBots
┣★**𝙼𝚊𝚗𝚊𝚐𝚎𝚍 𝙱𝚢:** @SAIFALISEW1508 
┗━━━━━━━━━━━━━━━━━┛
━━━━━━━━━━━━━━━━━━━
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("♦️ 𝙰𝚍𝚍 𝚈𝚘𝚞𝚛 𝙶𝚛𝚘𝚞𝚙 ♦️", url=f"https://t.me/MissCutiePlayerBot?startgroup=true")
        ],
        [
            InlineKeyboardButton("📝 𝙼𝚞𝚜𝚒𝚌 𝙲𝚘𝚖𝚖𝚊𝚗𝚍𝚜", callback_data="cbcmds"),
            InlineKeyboardButton("🇮🇳 𝙼𝚊𝚗𝚊𝚐𝚎𝚛", url="https://t.me/saifalisew1508")
        ],
        [
            InlineKeyboardButton("🧞‍♂ 𝚂𝚞𝚙𝚙𝚘𝚛𝚝", url="https://t.me/MissCutie_Support"),
            InlineKeyboardButton("🔔 𝚄𝚙𝚍𝚊𝚝𝚎𝚜", url="https://t.me/MissCutieUpdates")
        ],
        [
            InlineKeyboardButton("↫ 𝚂𝚘𝚞𝚛𝚌𝚎 𝙲𝚘𝚍𝚎 ↬", callback_data="repo_callback")
        ]
    ]
)

BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("⏸", callback_data="pause"),
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏭", callback_data="skip"),
            InlineKeyboardButton("⏹", callback_data="stop"),
            InlineKeyboardButton("🔇", callback_data="mute"),
            InlineKeyboardButton("🔊", callback_data="unmute")
        ],
        [
            InlineKeyboardButton("🗑 Close Menu", callback_data="close")
        ]
    ]
)

GROUP_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="• 𝚂𝚞𝚙𝚙𝚘𝚛𝚝 •", url="https://t.me/MissCutie_Support"),
            InlineKeyboardButton(text="• 𝙲𝚘𝚖𝚖𝚊𝚗𝚍𝚜 •", callback_data="cbcmds")
        ]
    ]
)

BACK_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="• Back •", callback_data="back"),
            InlineKeyboardButton(text="• Source •", callback_data="repo_callback")
        ]
    ]
)

async def skip_current_song(chat_id):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await app.leave_group_call(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            title = chat_queue[1][0]
            duration = chat_queue[1][1]
            link = chat_queue[1][2]
            playlink = chat_queue[1][3]
            type = chat_queue[1][4]
            Q = chat_queue[1][5]
            thumb = chat_queue[1][6]
            if type == "Audio":
                await app.change_stream(
                    chat_id,
                    AudioPiped(
                        playlink,
                    ),
                )
            elif type == "Video":
                if Q == "high":
                    hm = HighQualityVideo()
                elif Q == "mid":
                    hm = MediumQualityVideo()
                elif Q == "low":
                    hm = LowQualityVideo()
                else:
                    hm = MediumQualityVideo()
                await app.change_stream(
                    chat_id, AudioVideoPiped(playlink, HighQualityAudio(), hm)
                )
            pop_an_item(chat_id)
            await bot.send_photo(chat_id, photo = thumb,
                                 caption = f"▶️ <b>Now playing:</b> [{title}]({link}) | `{type}` \n\n⏳ <b>Duration:</b> {duration}",
                                 reply_markup = BUTTONS)
            return [title, link, type, duration, thumb]
    else:
        return 0


async def skip_item(chat_id, lol):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        try:
            x = int(lol)
            title = chat_queue[x][0]
            chat_queue.pop(x)
            return title
        except Exception as e:
            print(e)
            return 0
    else:
        return 0


@app.on_stream_end()
async def on_end_handler(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        await skip_current_song(chat_id)


@app.on_closed_voice_chat()
async def close_handler(client: PyTgCalls, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
        

async def yt_video(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()
    

async def yt_audio(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@bot.on_callback_query(filters.regex("cbcmds"))
async def cbcmds(_, query: CallbackQuery):
    await query.answer("Commands Menu")
    await query.edit_message_text(
        f"""🇮🇳 𝑯𝒆𝒍𝒍𝒐 » **⚜𝑳𝒊𝒔𝒕 𝑶𝒇 𝑨𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔⚜**
» /play (𝚂𝚘𝚗𝚐 𝙽𝚊𝚖𝚎/𝙻𝚒𝚗𝚔) - **𝙿𝚕𝚊𝚢 𝙼𝚞𝚜𝚒𝚌**
» /vplay (𝚟𝚒𝚍𝚎𝚘 𝚗𝚊𝚖𝚎/𝚕𝚒𝚗𝚔) - **𝙿𝚕𝚊𝚢 𝚅𝚒𝚍𝚎𝚘**
» /liveplay (𝚈𝚘𝚞𝚃𝚞𝚋𝚎 𝙻𝚒𝚗𝚔) - **𝙿𝚕𝚊𝚢 𝙻𝚒𝚟𝚎 𝙼𝚞𝚜𝚒𝚌**
» /livestream (𝚈𝚘𝚞𝚃𝚞𝚋𝚎 𝙻𝚒𝚗𝚔) - **𝚂𝚝𝚛𝚎𝚊𝚖 𝙻𝚒𝚟𝚎 𝚅𝚒𝚍𝚎𝚘**
» /pause - **𝙿𝚊𝚞𝚜𝚎 𝚃𝚑𝚎 𝚂𝚘𝚗𝚐**
» /resume - **𝚁𝚎𝚜𝚞𝚖𝚎 𝚃𝚑𝚎 𝚂𝚘𝚗𝚐**
» /skip - **𝚜𝚠𝚒𝚝𝚌𝚑 𝚝𝚘 𝚗𝚎𝚡𝚝 𝚂𝚘𝚗𝚐**
» /end - **𝚂𝚝𝚘𝚙 𝚃𝚑𝚎 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐**
» /join - **𝙸𝚗𝚟𝚒𝚝𝚎 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝 𝚃𝚘 𝚈𝚘𝚞𝚛 𝙶𝚛𝚘𝚞𝚙**
» /mute - **𝙼𝚞𝚝𝚎 𝚃𝚑𝚎 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝 𝙾𝚗 𝚅𝚘𝚒𝚌𝚎 𝙲𝚑𝚊𝚝**
» /unmute - **𝚄𝚗𝙼𝚞𝚝𝚎 𝚃𝚑𝚎 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝 𝙾𝚗 𝚅𝚘𝚒𝚌𝚎 𝙲𝚑𝚊𝚝**
» /playlist - **𝚂𝚑𝚘𝚠 𝚈𝚘𝚞 𝚃𝚑𝚎 𝙿𝚕𝚊𝚢𝚕𝚒𝚜𝚝**
» /restart - **𝚁𝚎𝚜𝚝𝚊𝚛𝚝 𝚃𝚑𝚎 𝙱𝚘𝚝**
⚡  𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚: @MissCutieBots""",
    reply_markup = BACK_BUTTON)

@Client.on_callback_query(filters.regex("back"))
async def back_cb(bot, message):
   await message.answer()
   await start(bot, message, True)

@bot.on_callback_query(filters.regex("repo_callback"))
async def repo_callback(_, CallbackQuery):
 return await CallbackQuery.answer(
                "𝙽𝚒𝚌𝚎 𝚃𝚛𝚢 𝙼𝚊𝚗 𝙱𝚞𝚝 𝙾𝚗𝚎 𝚃𝚑𝚒𝚗𝚐 𝙰𝚛𝚎 𝚈𝚘𝚞 𝙰 𝙱𝚒𝚝𝚌𝚑 𝚃𝚑𝚎𝚢 𝚆𝚘𝚞𝚕𝚍 𝙾𝚗𝚕𝚢 𝙰𝚜𝚔 𝙼𝚎 𝚃𝚑𝚎 𝙰𝚋𝚘𝚞𝚝 𝚂𝚘𝚞𝚛𝚌𝚎 𝙲𝚘𝚍𝚎😏 ©️MissCutieBots@SAIFALISEW1508", show_alert=True
            )

@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    msg = START_TEXT.format(message.from_user.mention)
    await message.reply_photo(photo="https://te.legra.ph/file/ab6eb4c9785d231233c71.jpg",
                              caption = msg,
                              reply_markup = START_BUTTONS)


@bot.on_message(filters.command(["join", "join@MissCutiePlayerBot"]) & filters.group)
async def join_chat(c: Client, m: Message):
    chat_id = m.chat.id
    try:
        invitelink = await c.export_chat_invite_link(chat_id)
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace(
                "https://t.me/+", "https://t.me/joinchat/"
            )
            await client.join_chat(invitelink)
            return await client.send_message(chat_id, "✅ 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝 𝙹𝚘𝚒𝚗𝚎𝚍 𝚃𝚑𝚎 𝙲𝚑𝚊𝚝")
    except UserAlreadyParticipant:
        return await client.send_message(chat_id, "✅ 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝 𝙰𝚕𝚛𝚎𝚊𝚍𝚢 𝙸𝚗 𝙲𝚑𝚊𝚝")
    

@bot.on_message(filters.command("start") & filters.group)
async def start_group(_, message):
    await message.reply_photo(photo="https://te.legra.ph/file/c64734caae40345289712.jpg",
                              caption = f"𝙷𝚎𝚕𝚕𝚘 🚀 {message.from_user.mention} 🥁 𝙼𝚞𝚜𝚒𝚌 𝙱𝚘𝚝 𝙸𝚜 𝙰𝚕𝚒𝚟𝚎🎸.",
                              reply_markup = GROUP_BUTTONS)
    
    
@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
async def video_play(_, message):
    await message.delete()
    user_id = message.from_user.id
    state = message.command[0].lower()
    try:
        query = message.text.split(None, 1)[1]
    except:
        return await message.reply_text(f"<b>Usage:</b> <code>/{state} [query]</code>")
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        return await message.reply_text("❗️𝙿𝚕𝚎𝚊𝚜𝚎 𝚂𝚎𝚗𝚍 <code>/stop</code> 𝚃𝚘 𝙴𝚗𝚍 𝙲𝚞𝚛𝚛𝚎𝚗𝚝 𝙻𝚒𝚟𝚎 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐 𝙱𝚎𝚏𝚘𝚛𝚎 𝙿𝚕𝚊𝚢 𝚂𝚘𝚗𝚐𝚜 𝙾𝚛 𝚅𝚒𝚍𝚎𝚘𝚜.")
    
    m = await message.reply_text("🔄 𝙿𝚛𝚘𝚌𝚎𝚜𝚜𝚒𝚗𝚐...")
    if state == "play":
        damn = AudioPiped
        ded = yt_audio
        doom = "Audio"
    elif state == "vplay":
        damn = AudioVideoPiped
        ded = yt_video
        doom = "Video"
    if "low" in query:
        Q = "low"
    elif "mid" in query:
        Q = "mid"
    elif "high" in query:
        Q = "high"
    else:
        Q = "0"
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        thumb = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        yt = YouTube(link)
        cap = f"▶️ <b>𝙽𝚘𝚠 𝙿𝚕𝚊𝚢𝚒𝚗𝚐:</b> [{yt.title}]({link}) | `{doom}` \n\n⏳ <b>Duration:</b> {duration}"
        try:
            ydl_opts = {"format": "bestvideo[height<=720]+bestaudio/best[height<=720]"}
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            info_dict = ydl.extract_info(link, download=False)
            p = json.dumps(info_dict)
            a = json.loads(p)
            playlink = a['formats'][1]['manifest_url']
        except:
            ice, playlink = await ded(link)
            if ice == "0":
                return await m.edit("❗️YTDL ERROR !!!")               
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if chat_id in QUEUE:
            position = add_to_queue(chat_id, yt.title, duration, link, playlink, doom, Q, thumb)
            caps = f"#️⃣ [{yt.title}]({link}) <b>queued at position {position}</b> \n\n⏳ <b>Duration:</b> {duration}"
            await message.reply_photo(thumb, caption=caps)
            await m.delete()
        else:            
            await app.join_group_call(
                chat_id,
                damn(playlink),
                stream_type=StreamType().pulse_stream
            )
            add_to_queue(chat_id, yt.title, duration, link, playlink, doom, Q, thumb)
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
    except Exception as e:
        return await m.edit(str(e))
    
    
@bot.on_message(filters.command(["liveplay", "livestream"]) & filters.group)
@is_admin
async def stream_func(_, message):
    await message.delete()
    state = message.command[0].lower()
    try:
        link = message.text.split(None, 1)[1]
    except:
        return await message.reply_text(f"<b>Usage:</b> <code>/{state} [link]</code>")
    chat_id = message.chat.id
    
    if state == "liveplay":
        damn = AudioPiped
        emj = "🎵"
    elif state == "livestream":
        damn = AudioVideoPiped
        emj = "🎬"
    m = await message.reply_text("🔄 𝙿𝚛𝚘𝚌𝚎𝚜𝚜𝚒𝚗𝚐...")
    try:
        if chat_id in QUEUE:
            return await m.edit("❗️𝙿𝚕𝚎𝚊𝚜𝚎 𝚂𝚎𝚗𝚍 <code>/stop</code> 𝚃𝚘 𝙴𝚗𝚍 𝚅𝚘𝚒𝚌𝚎 𝙲𝚑𝚊𝚝 𝙱𝚎𝚏𝚘𝚛𝚎 𝙻𝚒𝚟𝚎 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐.")
        elif chat_id in LIVE_CHATS:
            await app.change_stream(
                chat_id,
                damn(link)
            )
            await m.edit(f"{emj} Started streaming: [Link]({link})", disable_web_page_preview=True)
        else:    
            await app.join_group_call(
                chat_id,
                damn(link),
                stream_type=StreamType().pulse_stream)
            await m.edit(f"{emj} Started streaming: [Link]({link})", disable_web_page_preview=True)
            LIVE_CHATS.append(chat_id)
    except Exception as e:
        return await m.edit(str(e))


@bot.on_message(filters.command("skip") & filters.group)
@is_admin
async def skip(_, message):
    await message.delete()
    chat_id = message.chat.id
    if len(message.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await message.reply_text("❗️𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚗 𝚃𝚑𝚎 𝚀𝚞𝚎𝚞𝚎 𝚃𝚘 𝚂𝚔𝚒𝚙.")
        elif op == 1:
            await message.reply_text("❗️𝙴𝚖𝚙𝚝𝚢 𝚀𝚞𝚎𝚞𝚎, 𝚂𝚝𝚘𝚙𝚙𝚎𝚍 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐.")
    else:
        skip = message.text.split(None, 1)[1]
        out = "🗑 <b>Removed the following song(s) from the queue:</b> \n"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        out = out + "\n" + f"<b>#️⃣ {x}</b> - {hm}"
            await message.reply_text(out)
            
            
@bot.on_message(filters.command(["playlist", "queue"]) & filters.group)
@is_admin
async def playlist(_, message):
    chat_id = message.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await message.delete()
            await message.reply_text(
                f"▶️ <b>𝙽𝚘𝚠 𝙿𝚕𝚊𝚢𝚒𝚗𝚐:</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}`",
                disable_web_page_preview=True,
            )
        else:
            out = f"<b>📃 Player queue:</b> \n\n▶️ <b>𝙽𝚘𝚠 𝙿𝚕𝚊𝚢𝚒𝚗𝚐:</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}` \n"
            l = len(chat_queue)
            for x in range(1, l):
                title = chat_queue[x][0]
                link = chat_queue[x][2]
                type = chat_queue[x][4]
                out = out + "\n" + f"<b>#️⃣ {x}</b> - [{title}]({link}) | `{type}` \n"
            await message.reply_text(out, disable_web_page_preview=True)
    else:
        await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
    

@bot.on_message(filters.command("stop") & filters.group)
@is_admin
async def end(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        await app.leave_group_call(chat_id)
        LIVE_CHATS.remove(chat_id)
        return await message.reply_text("⏹ 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐 𝚂𝚝𝚘𝚙𝚙𝚎𝚍.")
        
    if chat_id in QUEUE:
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await message.reply_text("⏹ 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐 𝚂𝚝𝚘𝚙𝚙𝚎𝚍.")
    else:
        await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
        

@bot.on_message(filters.command("pause") & filters.group)
@is_admin
async def pause(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.pause_stream(chat_id)
            await message.reply_text("⏸ 𝙿𝚊𝚞𝚜𝚎𝚍 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐.")
        except:
            await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
    else:
        await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
        
        
@bot.on_message(filters.command("resume") & filters.group)
@is_admin
async def resume(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.resume_stream(chat_id)
            await message.reply_text("⏸ 𝚁𝚎𝚜𝚞𝚖𝚎𝚍 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐.")
        except:
            await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
    else:
        await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
        
        
@bot.on_message(filters.command("mute") & filters.group)
@is_admin
async def mute(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.mute_stream(chat_id)
            await message.reply_text("🔇 𝙼𝚞𝚝𝚎𝚍 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐.")
        except:
            await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
    else:
        await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
        
        
@bot.on_message(filters.command("unmute") & filters.group)
@is_admin
async def unmute(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.unmute_stream(chat_id)
            await message.reply_text("🔊 𝚄𝚗𝚖𝚞𝚝𝚎𝚍 𝚂𝚝𝚛𝚎𝚊𝚖𝚒𝚗𝚐.")
        except:
            await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
    else:
        await message.reply_text("❗𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝙸𝚜 𝙿𝚕𝚊𝚢𝚒𝚗𝚐.")
        
        
@bot.on_message(filters.command("restart"))
async def restart(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    await message.reply_text("🛠 <i>𝚁𝚎𝚜𝚝𝚊𝚛𝚝𝚒𝚗𝚐 𝚃𝚑𝚎 𝙱𝚘𝚝 𝙿𝚕𝚎𝚊𝚜𝚎 𝚆𝚊𝚒𝚝 ✋🏻 𝙸𝚝'𝚜 𝙼𝚊𝚢 𝚃𝚊𝚔𝚎 𝟺-𝟻 𝙼𝚒𝚗𝚞𝚝𝚎𝚜 🤐...</i>")
    os.system(f"kill -9 {os.getpid()} && python3 app.py")
            

app.start()
bot.run()
idle()
