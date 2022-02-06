"""
MIT License

Copyright (c) 2021 Janindu Malshan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import glob
import json
import logging
import asyncio
import youtube_dl
from pytgcalls import StreamType
from pytube import YouTube
from youtube_search import YoutubeSearch
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pyrogram.raw.base import Update
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo
)
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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
━━━━━━━━━━━━━━━━━━━━━━━━
**𝙷𝚎𝚕𝚕𝚘**, <b>{}</b> **𝙸'𝚖 𝚂𝚞𝚙𝚎𝚛 𝙵𝚊𝚜𝚝 𝙼𝚞𝚜𝚒𝚌 𝙿𝚕𝚊𝚢𝚎𝚛 𝙱𝚘𝚝 𝙵𝚘𝚛 𝚃𝚎𝚕𝚎𝚐𝚛𝚊𝚖 𝙶𝚛𝚘𝚞𝚙𝚜 𝙰𝚕𝚕𝚘𝚠𝚜 𝚈𝚘𝚞 𝙿𝚕𝚊𝚢 𝙼𝚞𝚜𝚒𝚌 𝙰𝚗𝚍 𝚅𝚒𝚍𝚎𝚘𝚜 𝙾𝚗 𝙶𝚛𝚘𝚞𝚙 𝚃𝚑𝚛𝚘𝚞𝚐𝚑 𝚃𝚑𝚎 𝙽𝚎𝚠 𝚃𝚎𝚕𝚎𝚐𝚛𝚊𝚖 𝚅𝚒𝚍𝚎𝚘 𝙲𝚑𝚊𝚝....**
┏━━━━━━━━━━━━━━━━━┓
┣★ **𝙱𝚊𝚜𝚎𝚍 𝙾𝚗 𝙻𝚊𝚝𝚎𝚜𝚝 𝚅𝚎𝚛𝚜𝚒𝚘𝚗**
┣★ **𝚂𝚞𝚙𝚎𝚛𝙵𝚊𝚜𝚝 𝙰𝚗𝚍 𝙱𝚎𝚜𝚝 𝙰𝚞𝚍𝚒𝚘 𝚀𝚞𝚊𝚕𝚒𝚝𝚢**
┣★ **𝙰𝚍𝚍 𝚃𝚘 𝚈𝚘𝚞𝚛 𝙶𝚛𝚘𝚞𝚙 𝙰𝚗𝚍 𝙼𝚊𝚔𝚎 𝚂𝚞𝚛𝚎 𝙼𝚎 𝙰𝚍𝚖𝚒𝚗**
┣★ **𝙰𝚗𝚢 𝚀𝚞𝚎𝚛𝚢 𝙰𝚗𝚍 𝙱𝚞𝚐 𝚁𝚎𝚙𝚘𝚛𝚝:** @MissCutie_Support
┣★**𝙼𝚊𝚗𝚊𝚐𝚎𝚍 𝙱𝚢:** @SAIFALISEW1508 
┗━━━━━━━━━━━━━━━━━┛
━━━━━━━━━━━━━━━━━━━━━━━━
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("♦️ 𝙰𝚍𝚍 𝚈𝚘𝚞𝚛 𝙶𝚛𝚘𝚞𝚙 ♦️", url=f"https://t.me/MissCutiePlayerBot?startgroup=true")
        ],
        [
            InlineKeyboardButton("📝 𝙼𝚞𝚜𝚒𝚌 𝙲𝚘𝚖𝚖𝚊𝚗𝚍𝚜", callback_data="cbcmds"),
            InlineKeyboardButton("🇮🇳 𝙳𝚎𝚟𝚕𝚘𝚙𝚎𝚛", url="https://t.me/saifalisew1508")
        ],
        [
            InlineKeyboardButton("🧞‍♂ 𝚂𝚞𝚙𝚙𝚘𝚛𝚝", url="https://t.me/MissCutie_Support"),
            InlineKeyboardButton("🔔 𝚄𝚙𝚍𝚊𝚝𝚎𝚜", url="https://t.me/MissCutieUpdates")
        ],
        [
            InlineKeyboardButton("↫ 𝚁𝚎𝚙𝚘 ↬", callback_data="get_repo")
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


@bot.on_callback_query()
async def callbacks(_, cq: CallbackQuery):
    user_id = cq.from_user.id
    try:
        user = await cq.message.chat.get_member(user_id)
        admin_strings = ("creator", "administrator")
        if user.status not in admin_strings:
            is_admin = False
        else:
            is_admin = True
    except ValueError:
        is_admin = True        
    if not is_admin:
        return await cq.answer("You aren't an admin.")   
    chat_id = cq.message.chat.id
    data = cq.data
    if data == "close":
        return await cq.message.delete()
    if not chat_id in QUEUE:
        return await cq.answer("Nothing is playing.")

    if data == "pause":
        try:
            await app.pause_stream(chat_id)
            await cq.answer("Paused streaming.")
        except:
            await cq.answer("Nothing is playing.")
      
    elif data == "resume":
        try:
            await app.resume_stream(chat_id)
            await cq.answer("Resumed streaming.")
        except:
            await cq.answer("Nothing is playing.")   

    elif data == "stop":
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await cq.answer("Stopped streaming.")  

    elif data == "mute":
        try:
            await app.mute_stream(chat_id)
            await cq.answer("Muted streaming.")
        except:
            await cq.answer("Nothing is playing.")
            
    elif data == "unmute":
        try:
            await app.unmute_stream(chat_id)
            await cq.answer("Unmuted streaming.")
        except:
            await cq.answer("Nothing is playing.")
            
    elif data == "skip":
        op = await skip_current_song(chat_id)
        if op == 0:
            await cq.answer("Nothing in the queue to skip.")
        elif op == 1:
            await cq.answer("Empty queue, stopped streaming.")
        else:
            await cq.answer("Skipped.")


@bot.on_callback_query(filters.regex("cbcmds"))
async def cbcmds(_, query: CallbackQuery):
    await query.answer("Commands Menu")
    await query.edit_message_text(
        f"""🗡️🇮🇳🗡️ 𝘏𝘦𝘭𝘭𝘰 » **𝘓𝘪𝘴𝘵 𝘖𝘧 𝘈𝘷𝘢𝘪𝘭𝘢𝘣𝘭𝘦 𝘊𝘰𝘮𝘮𝘢𝘯𝘥𝘴 🗡️🇮🇳🗡️**
» /play (Song Name/Link) - Play Music
» /vplay (video name/link) - Play Video
» /pause - Pause The Song
» /resume - Resume The Song
» /skip - switch to next Song
» /end - Stop The Streaming
» /join - Invite Assistant To Your Group
» /mute - Mute The Assistant On Voice Chat
» /unmute - UnMute The Assistant On Voice Chat
» /playlist - Show You The Playlist
» /restart - Restart The Bot
⚡  `𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚:` @MissCutie_Support")


@app.on_callback_query(filters.regex("get_repo"))
async def get_repo(_, CallbackQuery):
    text = await why so pro bazzi bhaiya()
    await app.answer_callback_query(CallbackQuery.id, text, show_alert=True)


@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    msg = START_TEXT.format(message.from_user.mention)
    await message.reply_text(text = msg,
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
    await message.reply_text("🎧 <i>Music player is running.</i>")
    
    
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
        return await message.reply_text("❗️Please send <code>/stop</code> to end current live streaming before play songs or videos.")
    
    m = await message.reply_text("🔄 Processing...")
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
        cap = f"▶️ <b>Now playing:</b> [{yt.title}]({link}) | `{doom}` \n\n⏳ <b>Duration:</b> {duration}"
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
    
    
@bot.on_message(filters.command(["saudio", "svideo"]) & filters.group)
@is_admin
async def stream_func(_, message):
    await message.delete()
    state = message.command[0].lower()
    try:
        link = message.text.split(None, 1)[1]
    except:
        return await message.reply_text(f"<b>Usage:</b> <code>/{state} [link]</code>")
    chat_id = message.chat.id
    
    if state == "saudio":
        damn = AudioPiped
        emj = "🎵"
    elif state == "svideo":
        damn = AudioVideoPiped
        emj = "🎬"
    m = await message.reply_text("🔄 Processing...")
    try:
        if chat_id in QUEUE:
            return await m.edit("❗️Please send <code>/stop</code> to end voice chat before live streaming.")
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
            await message.reply_text("❗️Nothing in the queue to skip.")
        elif op == 1:
            await message.reply_text("❗️Empty queue, stopped streaming.")
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
                f"▶️ <b>Now playing:</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}`",
                disable_web_page_preview=True,
            )
        else:
            out = f"<b>📃 Player queue:</b> \n\n▶️ <b>Now playing:</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}` \n"
            l = len(chat_queue)
            for x in range(1, l):
                title = chat_queue[x][0]
                link = chat_queue[x][2]
                type = chat_queue[x][4]
                out = out + "\n" + f"<b>#️⃣ {x}</b> - [{title}]({link}) | `{type}` \n"
            await message.reply_text(out, disable_web_page_preview=True)
    else:
        await message.reply_text("❗Nothing is playing.")
    

@bot.on_message(filters.command("stop") & filters.group)
@is_admin
async def end(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        await app.leave_group_call(chat_id)
        LIVE_CHATS.remove(chat_id)
        return await message.reply_text("⏹ Stopped streaming.")
        
    if chat_id in QUEUE:
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await message.reply_text("⏹ Stopped streaming.")
    else:
        await message.reply_text("❗Nothing is playing.")
        

@bot.on_message(filters.command("pause") & filters.group)
@is_admin
async def pause(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.pause_stream(chat_id)
            await message.reply_text("⏸ Paused streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("resume") & filters.group)
@is_admin
async def resume(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.resume_stream(chat_id)
            await message.reply_text("⏸ Resumed streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("mute") & filters.group)
@is_admin
async def mute(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.mute_stream(chat_id)
            await message.reply_text("🔇 Muted streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("unmute") & filters.group)
@is_admin
async def unmute(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.unmute_stream(chat_id)
            await message.reply_text("🔊 Unmuted streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("restart"))
async def restart(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    await message.reply_text("🛠 <i>Restarting Music Player...</i>")
    os.system(f"kill -9 {os.getpid()} && python3 app.py")
            

app.start()
bot.run()
idle()
