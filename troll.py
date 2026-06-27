from telethon import TelegramClient, events
import asyncio
import os
import random
import json
from datetime import datetime, timedelta
import time
import re
import pickle
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.utils import get_display_name
import psutil
from dateutil.relativedelta import relativedelta
import sys
import getpass
from random import choice
import requests
import hashlib
import aiohttp
from PIL import Image
import io
import shutil
owner_id = 1768107631
name = "Bot Finala"
phone = "+79771713844"
api_id = 21523809
api_hash = "577c0b97ee6a853cd08cda0d7b448508"
PRICE_SERVICE_NAME = "Услуга"
PRICE_CONTACT = "@username"
DATA_DIR = "bot_data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.pkl")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")
MESSAGE_LOGS_FILE = os.path.join(DATA_DIR, "message_logs.json")
MEDIA_DIR = os.path.join(DATA_DIR, "saved_media")
AUTO_FILE = os.path.join(DATA_DIR, "auto.json")
X0_CACHE_FILE = os.path.join(DATA_DIR, "x0_cache.json")
COUNT_POINTS_FILE = os.path.join(DATA_DIR, "count_points.json")
RAS_CHATS_FILE = os.path.join(DATA_DIR, "ras_chats.json")
REPO_CHATS_FILE = os.path.join(DATA_DIR, "repo_chats.json")
CAL_TASKS_FILE = os.path.join(DATA_DIR, "cal_tasks.json")
AFK_FILE = os.path.join(DATA_DIR, "afk.json")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(PROFILES_DIR, exist_ok=True)
EN_TO_RU = {'a':'а','b':'б','c':'с','d':'д','e':'е','f':'ф','g':'г','h':'х','i':'и','j':'й','k':'к','l':'л','m':'м','n':'н','o':'о','p':'р','q':'к','r':'р','s':'с','t':'т','u':'у','v':'в','w':'в','x':'х','y':'у','z':'з','A':'А','B':'В','C':'С','D':'Д','E':'Е','F':'Ф','G':'Г','H':'Х','I':'И','J':'Й','K':'К','L':'Л','M':'М','N':'Н','O':'О','P':'П','Q':'К','R':'Р','S':'С','T':'Т','U':'У','V':'В','W':'В','X':'Х','Y':'У','Z':'З'}
CYRILLIC_TO_LATIN_MAP = {'а':'a','е':'e','о':'o','р':'p','с':'c','у':'y','х':'x','А':'A','В':'B','Е':'E','З':'3','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','У':'Y','Х':'X'}
LATIN_TO_CYRILLIC_MAP = {v:k for k,v in CYRILLIC_TO_LATIN_MAP.items()}
shrift_mode = 0
last_template_index = {}
cal_tasks = {}
ras_chats = []
repo_chats = []
afk_state = False
afk_reason = "хз сплю"
afk_photo = None
afk_start_time = None
afk_users = []
muted_until = {}
def format_text_with_shrift(text):
    global shrift_mode
    if shrift_mode == 0: return text
    elif shrift_mode == 1: return f"<s>{text}</s>"
    elif shrift_mode == 2: return f"<b>{text}</b>"
    elif shrift_mode == 3: return f"<i>{text}</i>"
    elif shrift_mode == 4: return f"<code>{text}</code>"
    elif shrift_mode == 5: return f"<u>{text}</u>"
    elif shrift_mode == 6: return f"<pre>{text}</pre>"
    elif shrift_mode == 7: return f"<tg-spoiler>{text}</tg-spoiler>"
    return text
def get_next_template(task_id):
    global last_template_index, shablon
    if not shablon: return ""
    if task_id not in last_template_index:
        last_template_index[task_id] = random.randint(0, len(shablon)-1)
        return format_text_with_shrift(shablon[last_template_index[task_id]])
    current = last_template_index[task_id]
    new_index = current
    while new_index == current and len(shablon) > 1: new_index = random.randint(0, len(shablon)-1)
    last_template_index[task_id] = new_index
    return format_text_with_shrift(shablon[new_index])
def get_file_extension(message):
    if message.photo: return '.jpg'
    elif message.document:
        if message.file and message.file.name:
            ext = os.path.splitext(message.file.name)[1]
            if ext: return ext
        mime_map = {'video/mp4':'.mp4','video/gif':'.gif','image/gif':'.gif','image/png':'.png','image/jpeg':'.jpg','image/webp':'.webp','audio/mpeg':'.mp3','audio/ogg':'.ogg','application/pdf':'.pdf'}
        return mime_map.get(message.file.mime_type, '.bin')
    elif message.video: return '.mp4'
    elif message.audio: return '.mp3'
    elif message.voice: return '.ogg'
    elif message.sticker: return '.webp'
    elif message.gif: return '.gif'
    else: return '.bin'
def get_media_hash(media_data): return hashlib.md5(media_data).hexdigest()
async def upload_to_catbox(file_path):
    try:
        url = "https://catbox.moe/user/api.php"
        files = {'fileToUpload': open(file_path, 'rb')}
        data = {'reqtype': 'fileupload'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, files=files) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    if text and not text.startswith('<!DOCTYPE'): return text.strip()
        return None
    except: return None
async def upload_to_fileio(file_path):
    try:
        url = "https://file.io"
        files = {'file': open(file_path, 'rb')}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, files=files) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('link')
        return None
    except: return None
async def upload_to_telegraph(file_path):
    try:
        url = "https://telegra.ph/upload"
        files = {'file': open(file_path, 'rb')}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, files=files) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and isinstance(data, list) and len(data) > 0: return f"https://telegra.ph{data[0].get('src','')}"
        return None
    except: return None
async def upload_to_x0(file_path):
    try:
        url = "https://x0.at/"
        files = {'file': open(file_path, 'rb')}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, files=files) as resp:
                if resp.status == 200: return (await resp.text()).strip()
        return None
    except: return None
x0_cache = {}
def load_data():
    data = {'shablon':["я твою мать ебал"],'type_shablon':["раз","два","три","нахуй иди"],'spam_state':{},'spam_state1':{},'autoreply_list':[],'autoreply_time':{},'autoreply_cd':{},'autoreply_photo':{},'autoreply_shpk':{},'tagger_chats':{},'tag_chats':{},'mlist':None,'mh':None,'mid':None,'muted_users':set(),'timer_tasks':{},'message_logs':{},'lesenka_tasks':{},'auto_responses':{},'media_counter':0,'last_activity':{},'command_media':{},'count_points':{'a':None,'b':None}}
    try:
        with open(TEMPLATES_FILE,'r',encoding='utf-8') as f: templates = json.load(f); data.update(templates)
    except: pass
    try:
        with open(TASKS_FILE,'rb') as f: tasks = pickle.load(f); data.update(tasks)
    except: pass
    try:
        with open(MESSAGE_LOGS_FILE,'r',encoding='utf-8') as f: data['message_logs'] = json.load(f)
    except: pass
    try:
        with open(AUTO_FILE,'r',encoding='utf-8') as f:
            auto = json.load(f)
            data['auto_responses'] = auto.get('auto_responses',{})
            data['media_counter'] = auto.get('media_counter',0)
            data['last_activity'] = auto.get('last_activity',{})
    except: pass
    try:
        with open(COUNT_POINTS_FILE,'r',encoding='utf-8') as f: data['count_points'] = json.load(f)
    except: pass
    try:
        with open(RAS_CHATS_FILE,'r',encoding='utf-8') as f: global ras_chats; ras_chats = json.load(f)
    except: ras_chats = []
    try:
        with open(REPO_CHATS_FILE,'r',encoding='utf-8') as f: global repo_chats; repo_chats = json.load(f)
    except: repo_chats = []
    try:
        with open(CAL_TASKS_FILE,'r',encoding='utf-8') as f: global cal_tasks; cal_tasks = json.load(f)
    except: cal_tasks = {}
    try:
        with open(AFK_FILE,'r',encoding='utf-8') as f:
            afk_data = json.load(f)
            global afk_state, afk_reason, afk_photo
            afk_state = afk_data.get('state',False)
            afk_reason = afk_data.get('reason','хз сплю')
            afk_photo = afk_data.get('photo',None)
    except: pass
    global x0_cache
    try:
        with open(X0_CACHE_FILE,'r',encoding='utf-8') as f: x0_cache = json.load(f)
    except: x0_cache = {}
    return data
def save_data(data):
    with open(TEMPLATES_FILE,'w',encoding='utf-8') as f: json.dump({'shablon':data['shablon'],'type_shablon':data['type_shablon']},f,ensure_ascii=False,indent=2)
    with open(TASKS_FILE,'wb') as f: pickle.dump({'spam_state':data['spam_state'],'spam_state1':data['spam_state1'],'autoreply_list':data['autoreply_list'],'autoreply_time':data['autoreply_time'],'autoreply_cd':data['autoreply_cd'],'autoreply_photo':data['autoreply_photo'],'autoreply_shpk':data['autoreply_shpk'],'tagger_chats':data['tagger_chats'],'tag_chats':data['tag_chats'],'mlist':data['mlist'],'mh':data['mh'],'mid':data['mid'],'muted_users':data.get('muted_users',set()),'timer_tasks':data.get('timer_tasks',{}),'lesenka_tasks':data.get('lesenka_tasks',{})},f)
    with open(MESSAGE_LOGS_FILE,'w',encoding='utf-8') as f: json.dump(data.get('message_logs',{}),f,ensure_ascii=False,indent=2)
    with open(AUTO_FILE,'w',encoding='utf-8') as f: json.dump({'auto_responses':data.get('auto_responses',{}),'media_counter':data.get('media_counter',0),'last_activity':data.get('last_activity',{})},f,ensure_ascii=False,indent=2)
    with open(COUNT_POINTS_FILE,'w',encoding='utf-8') as f: json.dump(data.get('count_points',{'a':None,'b':None}),f,ensure_ascii=False,indent=2)
    with open(RAS_CHATS_FILE,'w',encoding='utf-8') as f: json.dump(ras_chats,f,ensure_ascii=False,indent=2)
    with open(REPO_CHATS_FILE,'w',encoding='utf-8') as f: json.dump(repo_chats,f,ensure_ascii=False,indent=2)
    with open(CAL_TASKS_FILE,'w',encoding='utf-8') as f: json.dump(cal_tasks,f,ensure_ascii=False,indent=2)
    with open(X0_CACHE_FILE,'w',encoding='utf-8') as f: json.dump(x0_cache,f,ensure_ascii=False,indent=2)
    with open(AFK_FILE,'w',encoding='utf-8') as f: json.dump({'state':afk_state,'reason':afk_reason,'photo':afk_photo},f,ensure_ascii=False,indent=2)
saved_data = load_data()
menu_photo = "https://t.me/social_trables/3"
shablon = saved_data['shablon']
type_shablon = saved_data['type_shablon']
spam_state = saved_data['spam_state']
spam_state1 = saved_data['spam_state1']
autoreply_list = saved_data['autoreply_list']
autoreply_time = saved_data['autoreply_time']
autoreply_cd = saved_data['autoreply_cd']
autoreply_photo = saved_data['autoreply_photo']
autoreply_shpk = saved_data['autoreply_shpk']
tagger_chats = saved_data['tagger_chats']
tag_chats = saved_data['tag_chats']
mlist = saved_data['mlist']
mh = saved_data['mh']
mid = saved_data['mid']
muted_users = saved_data['muted_users']
timer_tasks = saved_data.get('timer_tasks',{})
message_logs = saved_data.get('message_logs',{})
lesenka_tasks = saved_data.get('lesenka_tasks',{})
auto_responses = saved_data.get('auto_responses',{})
media_counter = saved_data.get('media_counter',0)
last_activity = saved_data.get('last_activity',{})
command_media = saved_data.get('command_media',{})
count_points = saved_data.get('count_points',{'a':None,'b':None})
start_time = time.time()
type_speed = 1
type_active = False
last_reply_time = {}
async def get_all_usernames(client, user):
    usernames = []
    try:
        if hasattr(user,'username') and user.username: usernames.append(f"@{user.username}")
        if hasattr(user,'usernames'):
            if isinstance(user.usernames,list):
                for un in user.usernames:
                    if hasattr(un,'username') and un.username: usernames.append(f"@{un.username}")
    except: pass
    return ', '.join(usernames) if usernames else "нет"
menutext = r"""<b>𝐁𝐨𝐭 𝐅𝐢𝐧𝐚𝐥𝐚</b>
<pre>⛧ 𝐊𝐨𝐦𝐚𝐧𝐝𝐲 𝐬𝐩𝐚𝐦𝐚</pre>
<pre><code>.spam</code> + time + media + reply — 𝐬𝐩𝐚𝐦 𝐯 𝐜𝐡𝐚𝐭
<code>.psp</code> + chat_id + time + media — 𝐬𝐩𝐚𝐦 𝐩𝐨 𝐜𝐡𝐚𝐭 𝐢𝐝
<code>.tag</code> + user_id + time + media + reply — 𝐭𝐞𝐠𝐠𝐞𝐫
<code>.rem</code> + chat_id + user_id + time + media — 𝐭𝐞𝐠𝐠𝐞𝐫 𝐩𝐨 𝐜𝐡𝐚𝐭 𝐢𝐝
<code>.cal</code> + chat_id + user_id + time(sec) + media + текст — 𝐤𝐚𝐥𝐞𝐧𝐝𝐚𝐫𝐲
<code>.ras</code> + reply — 𝐩𝐞𝐫𝐞𝐬𝐥𝐚𝐭𝐲 𝐯𝐨 𝐯𝐬𝐞 𝐠𝐫𝐮𝐩𝐩𝐲
<code>.reply</code> + user_id + задержка(сек) + cd(сек) + media_num — 𝐚𝐯𝐭𝐨𝐨𝐭𝐯𝐞𝐭𝐜𝐡𝐢𝐤
<code>.l</code> — 𝐮𝐩𝐫𝐚𝐯𝐥𝐞𝐧𝐢𝐞 𝐚𝐯𝐭𝐨𝐨𝐭𝐯𝐞𝐭𝐜𝐡𝐢𝐤𝐚𝐦𝐢
<code>.lesenka</code> + time — 𝐥𝐞𝐬𝐞𝐧𝐤𝐚
<code>.offles</code> — 𝐯𝐲𝐤𝐥𝐲𝐮𝐜𝐡𝐢𝐭𝐲 𝐥𝐞𝐬𝐞𝐧𝐤𝐮
<code>.type</code> — 𝐩𝐨𝐬𝐭𝐫𝐨𝐜𝐡𝐧𝐲𝐣 𝐯𝐲𝐯𝐨𝐝
<code>.stoptype</code> — 𝐨𝐬𝐭𝐚𝐧𝐨𝐯𝐢𝐭𝐲 𝐯𝐲𝐯𝐨𝐝
<code>.status</code> — 𝐬𝐭𝐚𝐭𝐮𝐬 𝐛𝐨𝐭𝐚</pre>
<pre>𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐜𝐢𝐨𝐧𝐧𝐲𝐞 𝐤𝐨𝐦𝐚𝐧𝐝𝐲</pre>
<pre>this chat id: <code>{}</code>
your user id: <code>{}</code>
your name: <code>{}</code>
your usernames: {}
bot owner — <a href='tg://user?id=950494880'>final</a></pre>"""
menu2text = r"""<b>𝐁𝐨𝐭 𝐅𝐢𝐧𝐚𝐥𝐚</b>
<pre>⛧ 𝐔𝐩𝐫𝐚𝐯𝐥𝐞𝐧𝐢𝐞 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐚𝐦𝐢</pre>
<pre><code>.ad</code> + reply — 𝐝𝐨𝐛𝐚𝐯𝐢𝐭𝐲 𝐯 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐲
<code>.ad del</code> + номер — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐬𝐡𝐚𝐛𝐥𝐨𝐧
<code>.ad show</code> — 𝐩𝐨𝐤𝐚𝐳𝐚𝐭𝐲 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐲
<code>.set</code> + reply на txt — 𝐳𝐚𝐦𝐞𝐧𝐚 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐨𝐯
<code>.set2</code> — 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐲 𝐝𝐥𝐲𝐚 .𝐭𝐲𝐩𝐞
<code>.file</code> — 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐲 𝐛𝐨𝐭𝐚
<code>.shabl</code> + reply — 𝐩𝐨𝐢𝐬𝐤 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐨𝐯
<code>.shrift</code> + [0-7] — 𝐬𝐡𝐫𝐢𝐟𝐭 𝐝𝐥𝐲𝐚 𝐬𝐡𝐚𝐛𝐥𝐨𝐧𝐨𝐯</pre>
<pre>⛧ 𝐌𝐨𝐝𝐞𝐫𝐚𝐜𝐢𝐲𝐚</pre>
<pre><code>.mute</code> + ID/reply — 𝐥𝐢𝐜𝐡𝐧𝐲𝐣 𝐦𝐮𝐭
<code>.mute list</code> — 𝐬𝐩𝐢𝐬𝐨𝐤 𝐳𝐚𝐦𝐮𝐜𝐡𝐞𝐧𝐧𝐲𝐱
<code>.mute time</code> + ID + время — 𝐯𝐫𝐞𝐦𝐞𝐧𝐧𝐲𝐣 𝐦𝐮𝐭
<code>.mutstop</code> + ID/reply — 𝐮𝐛𝐫𝐚𝐭𝐲 𝐦𝐮𝐭
<code>.delete</code> + количество — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐬𝐯𝐨𝐢 𝐬𝐨𝐨𝐛𝐬𝐡𝐜𝐡𝐞𝐧𝐢𝐲𝐚
<code>.deleteall</code> — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐯𝐬𝐞 𝐢𝐳 𝐥𝐨𝐠𝐨𝐯
<code>.msdel</code> — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐯𝐬𝐞 𝐬𝐨𝐨𝐛𝐬𝐡𝐜𝐡𝐞𝐧𝐢𝐲𝐚 𝐨𝐭 𝐧𝐚𝐜𝐡𝐚𝐥𝐚 𝐜𝐡𝐚𝐭𝐚</pre>
<pre>⛧ 𝐈𝐧𝐬𝐭𝐫𝐮𝐦𝐞𝐧𝐭𝐲</pre>
<pre><code>.afk</code> + on/off/photo/reason — 𝐀𝐅𝐊
<code>.auto</code> + текст + reply — 𝐚𝐯𝐭𝐨𝐨𝐭𝐯𝐞𝐭 𝐩𝐨 𝐤𝐥𝐲𝐮𝐜𝐡𝐮
<code>.calculator</code> + выражение — 𝐤𝐚𝐥𝐲𝐤𝐮𝐥𝐲𝐚𝐭𝐨𝐫
<code>.count a/b</code> + reply — 𝐚𝐧𝐚𝐥𝐢𝐳 𝐭𝐞𝐤𝐬𝐭𝐚
<code>.gif</code> + reply — 𝐤𝐨𝐧𝐯𝐞𝐫𝐭𝐚𝐜𝐢𝐲𝐚 𝐯 𝐆𝐈𝐅
<code>.id</code> + reply — 𝐩𝐨𝐤𝐚𝐳𝐚𝐭𝐲 𝐈𝐃
<code>.mystats</code> + период — 𝐬𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐤𝐚 𝐚𝐤𝐤𝐚𝐮𝐧𝐭𝐚
<code>.ping</code> — 𝐩𝐢𝐧𝐠 𝐛𝐨𝐭𝐚
<code>.price</code> — 𝐩𝐫𝐚𝐣𝐬
<code>.reg</code> — 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐜𝐢𝐲𝐚 𝐨 𝐩𝐨𝐥𝐲𝐳𝐨𝐯𝐚𝐭𝐞𝐥𝐞
<code>.rus</code> + текст — 𝐳𝐚𝐦𝐞𝐧𝐚 𝐚𝐧𝐠𝐥 𝐛𝐮𝐤𝐯
<code>.trans</code> + текст — 𝐩𝐞𝐫𝐞𝐯𝐨𝐝
<code>.uptime</code> — 𝐯𝐫𝐞𝐦𝐲𝐚 𝐫𝐚𝐛𝐨𝐭𝐲
<code>.whois</code> + @username — 𝐢𝐧𝐟𝐨 𝐨 𝐩𝐨𝐥𝐲𝐳𝐨𝐯𝐚𝐭𝐞𝐥𝐞
<code>.x0</code> + имя/цифра — 𝐬𝐨𝐤𝐡𝐫𝐚𝐧𝐢𝐭𝐲 𝐦𝐞𝐝𝐢𝐚</pre>
<pre>⛧ 𝐑𝐚𝐬𝐬𝐲𝐥𝐤𝐚 𝐢 𝐜𝐡𝐚𝐭𝐲</pre>
<pre><code>.addras</code> + reply/chat_id — 𝐝𝐨𝐛𝐚𝐯𝐢𝐭𝐲 𝐯 𝐫𝐚𝐬𝐬𝐲𝐥𝐤𝐮
<code>.delras</code> + chat_id — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐢𝐳 𝐫𝐚𝐬𝐬𝐲𝐥𝐤𝐢
<code>.addrepo</code> + chat_id — 𝐝𝐨𝐛𝐚𝐯𝐢𝐭𝐲 𝐯 𝐫𝐞𝐩𝐨𝐳𝐢𝐭𝐨𝐫𝐢𝐣
<code>.delrepo</code> + chat_id — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐢𝐳 𝐫𝐞𝐩𝐨𝐳𝐢𝐭𝐨𝐫𝐢𝐲𝐚
<code>.addcontacts</code> — 𝐝𝐨𝐛𝐚𝐯𝐢𝐭𝐲 𝐯𝐞𝐬𝐲 𝐜𝐡𝐚𝐭 𝐯 𝐤𝐨𝐧𝐭𝐚𝐤𝐭𝐲
<code>.chats</code> — 𝐯𝐲𝐠𝐫𝐮𝐳𝐢𝐭𝐲 𝐬𝐩𝐢𝐬𝐤𝐢 𝐜𝐡𝐚𝐭𝐨𝐯</pre>
<pre>⛧ 𝐒𝐢𝐬𝐭𝐞𝐦𝐧𝐲𝐞</pre>
<pre><code>.ddk</code> — 𝐯𝐲𝐤𝐥𝐲𝐮𝐜𝐡𝐢𝐭𝐲 𝐯𝐬𝐞 𝐳𝐚𝐝𝐚𝐜𝐡𝐢
<code>.offl</code> — 𝐯𝐲𝐤𝐥𝐲𝐮𝐜𝐡𝐢𝐭𝐲 𝐟𝐥𝐮𝐝𝐞𝐫𝐲
<code>.list</code> + media — 𝐬𝐩𝐢𝐬𝐨𝐤 𝐳𝐚𝐝𝐚𝐜𝐡
<code>.pset</code> + [shapka,media,time,cd] + user_id — 𝐬𝐦𝐞𝐧𝐚 𝐚𝐫𝐠𝐮𝐦𝐞𝐧𝐭𝐨𝐯
<code>.stopcal</code> + chat_id — 𝐨𝐬𝐭𝐚𝐧𝐨𝐯𝐢𝐭𝐲 𝐤𝐚𝐥𝐞𝐧𝐝𝐚𝐫𝐲
<code>.timer</code> + count + [sec/min/hour] + interval + text — 𝐭𝐚𝐣𝐦𝐞𝐫
<code>.stoptimer</code> + ID — 𝐨𝐬𝐭𝐚𝐧𝐨𝐯𝐢𝐭𝐲 𝐭𝐚𝐣𝐦𝐞𝐫</pre>"""
menu3text = r"""<b>𝐁𝐨𝐭 𝐅𝐢𝐧𝐚𝐥𝐚</b>
<pre>⛧ 𝐍𝐨𝐯𝐲𝐞 𝐤𝐨𝐦𝐚𝐧𝐝𝐲</pre>
<pre><code>.top</code> + количество — 𝐭𝐨𝐩 𝐚𝐤𝐭𝐢𝐯𝐧𝐲𝐱 𝐯 𝐜𝐡𝐚𝐭𝐞
<code>.topwords</code> — 𝐭𝐨𝐩 𝐬𝐥𝐨𝐯 𝐯 𝐜𝐡𝐚𝐭𝐞
<code>.hack</code> + @username — 𝐟𝐞𝐣𝐤𝐨𝐯𝐲𝐣 𝐯𝐳𝐥𝐨𝐦
<code>.reverse</code> + текст — 𝐩𝐞𝐫𝐞𝐯𝐞𝐫𝐧𝐮𝐭𝐲 𝐭𝐞𝐤𝐬𝐭
<code>.ss</code> + ссылка — 𝐬𝐤𝐫𝐢𝐧𝐬𝐡𝐨𝐭 𝐬𝐚𝐣𝐭𝐚
<code>.movie</code> + название — 𝐢𝐧𝐟𝐨 𝐨 𝐟𝐢𝐥𝐲𝐦𝐞
<code>.profilesave</code> + номер — 𝐬𝐨𝐤𝐡𝐫𝐚𝐧𝐢𝐭𝐲 𝐩𝐫𝐨𝐟𝐢𝐥𝐲
<code>.profileset</code> + номер — 𝐮𝐬𝐭𝐚𝐧𝐨𝐯𝐢𝐭𝐲 𝐩𝐫𝐨𝐟𝐢𝐥𝐲
<code>.profilelist</code> — 𝐬𝐩𝐢𝐬𝐨𝐤 𝐩𝐫𝐨𝐟𝐢𝐥𝐞𝐣
<code>.profiledel</code> + номер — 𝐮𝐝𝐚𝐥𝐢𝐭𝐲 𝐩𝐫𝐨𝐟𝐢𝐥𝐲</pre>"""
class Userbot:
    def __init__(self):
        self.phone = phone
        self.api_id = api_id
        self.api_hash = api_hash
        self.tg_client = TelegramClient('Grandeur', self.api_id, self.api_hash, device_model="Bot Finala", system_version="1.0", app_version="1.0")
        self._running = False
        self._authorized = False
    async def save_state(self):
        data = {'shablon':shablon,'type_shablon':type_shablon,'spam_state':spam_state,'spam_state1':spam_state1,'autoreply_list':autoreply_list,'autoreply_time':autoreply_time,'autoreply_cd':autoreply_cd,'autoreply_photo':autoreply_photo,'autoreply_shpk':autoreply_shpk,'tagger_chats':tagger_chats,'tag_chats':tag_chats,'mlist':mlist,'mh':mh,'mid':mid,'muted_users':muted_users,'timer_tasks':timer_tasks,'message_logs':message_logs,'lesenka_tasks':lesenka_tasks,'auto_responses':auto_responses,'media_counter':media_counter,'last_activity':last_activity,'command_media':command_media,'count_points':count_points}
        save_data(data)
    async def check_authorization(self):
        try:
            me = await self.tg_client.get_me()
            return me is not None
        except: return False
    async def is_owner(self, user_id): return user_id == owner_id
    async def get_args(self, msg):
        try: return msg.text.split(maxsplit=1)[1]
        except IndexError: return None
    async def parse_time(self, time_str):
        time_str = time_str.lower().strip()
        if time_str.endswith('sec'): return int(time_str.replace('sec','').strip())
        elif time_str.endswith('min'): return int(time_str.replace('min','').strip()) * 60
        elif time_str.endswith('hour'): return int(time_str.replace('hour','').strip()) * 3600
        else:
            try: return int(time_str)
            except ValueError: return 60
    async def parse_period(self, period_str):
        period_str = period_str.lower().strip()
        patterns = {'час':3600,'часа':3600,'часов':3600,'день':86400,'дня':86400,'дней':86400,'месяц':2592000,'месяца':2592000,'месяцев':2592000,'год':31536000,'года':31536000,'лет':31536000}
        for key, value in patterns.items():
            if key in period_str: return value
        return None
    async def send_to_saved(self, text, file=None):
        try: await self.tg_client.send_message('me', text, file=file, parse_mode='html')
        except: pass
    async def detect_language(self, text):
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {'client':'gtx','sl':'auto','tl':'en','dt':'t','q':text}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 2: return data[2]
            return 'unknown'
        except: return 'unknown'
    async def translate_text(self, text, target_lang='ru'):
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {'client':'gtx','sl':'auto','tl':target_lang,'dt':'t','q':text}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0 and len(data[0]) > 0:
                            translated_parts = [part[0] for part in data[0] if part[0]]
                            detected_lang = data[2] if len(data) > 2 else 'unknown'
                            return ' '.join(translated_parts), detected_lang
            return text, 'unknown'
        except: return text, 'unknown'
    async def replace_english_chars(self, text):
        result = []
        for char in text: result.append(EN_TO_RU.get(char, char))
        return ''.join(result)
    async def find_media_by_name(self, name):
        name = str(name)
        if name.isdigit():
            for ext in ['.jpg','.png','.gif','.mp4','.mp3','.ogg','.webp']:
                path = os.path.join(MEDIA_DIR, f"media_{name}{ext}")
                if os.path.exists(path): return path
        else:
            for file in os.listdir(MEDIA_DIR):
                if file.startswith(name + '.') and not file.startswith('media_'): return os.path.join(MEDIA_DIR, file)
        return None
    async def send_with_media(self, chat_id, text, media_name_or_path=None, reply_to=None, parse_mode='html'):
        try:
            media_path = None
            if media_name_or_path:
                if os.path.exists(str(media_name_or_path)): media_path = media_name_or_path
                else: media_path = await self.find_media_by_name(str(media_name_or_path))
            if media_path and os.path.exists(media_path):
                try: return await self.tg_client.send_file(chat_id, media_path, caption=text, reply_to=reply_to, parse_mode=parse_mode)
                except: return await self.tg_client.send_message(chat_id, text, reply_to=reply_to, parse_mode=parse_mode)
            else: return await self.tg_client.send_message(chat_id, text, reply_to=reply_to, parse_mode=parse_mode)
        except Exception as e:
            print(f"Ошибка в send_with_media: {e}")
            return await self.tg_client.send_message(chat_id, text, reply_to=reply_to, parse_mode=parse_mode)
    async def send_with_command_media(self, msg, text, command_name=None):
        global command_media
        if command_name and command_name in command_media and command_media[command_name]:
            media_path = command_media[command_name]
            try:
                await self.send_with_media(msg.chat_id, text, media_path)
                await msg.delete()
                return True
            except Exception as e: print(f"Ошибка отправки с медиа: {e}")
        await msg.edit(text, parse_mode='html')
        return False
    async def help_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .команда help</b>\nПример: <code>.spam help</code>", parse_mode='html')
                return
            cmd = args.lower().replace('.','')
            help_texts = {
                'spam':"<b>⛧ .spam</b>\n<pre>Запуск спама в текущем чате\nИспользование: .spam время [медиа] [текст]\nПримеры:\n.spam 10 — спам шаблонами каждые 10 сек\n.spam 5 1 Привет — спам с медиа #1 и текстом\n.spam 3 https://... — спам с медиа по ссылке\nОстановить: .stop</pre>",
                'psp':"<b>⛧ .psp</b>\n<pre>Спам по ID чата\nИспользование: .psp chat_id время [медиа] [текст]\nПример: .psp -100123456 10 1 Привет\nОстановить: .pstop ID</pre>",
                'tag':"<b>⛧ .tag</b>\n<pre>Теггер в текущем чате\nИспользование: .tag user_id время [медиа] [текст]\nПример: .tag 123456 10 1\nОстановить: .off</pre>",
                'rem':"<b>⛧ .rem</b>\n<pre>Теггер по ID чата\nИспользование: .rem chat_id user_id время [медиа] [текст]\nПример: .rem -100123456 123456 10 1\nОстановить: .goff ID</pre>",
                'cal':"<b>⛧ .cal</b>\n<pre>Календарь - периодический тег\nИспользование: .cal chat_id user_id интервал(сек) [медиа] [текст]\nПример: .cal -100123456 123456 3600 1 Привет\nОстановить: .stopcal ID</pre>",
                'reply':"<b>⛧ .reply</b>\n<pre>Автоответчик\nИспользование: .reply user_id задержка cd [медиа] [шапка]\nПример: .reply 123456 0 5 1 Привет\nОтключить: .l ID</pre>",
                'timer':"<b>⛧ .timer</b>\n<pre>Таймер\nИспользование: .timer количество интервал текст\nИнтервалы: sec, min, hour\nПример: .timer 5 10sec Привет\nОстановить: .stoptimer ID</pre>",
                'lesenka':"<b>⛧ .lesenka</b>\n<pre>Лесенка на сообщение\nИспользование: .lesenka интервал + реплай\nПример: .lesenka 1\nОстановить: .offles + реплай</pre>",
                'type':"<b>⛧ .type</b>\n<pre>Построчный вывод шаблонов\nИспользование: .type [скорость]\nПример: .type 2\nОстановить: .stoptype</pre>",
                'x0':"<b>⛧ .x0</b>\n<pre>Сохранение медиа\nИспользование:\n.x0 5 — сохранить как media_5\n.x0 avatar — сохранить как avatar\n.x0 — залить на файлообменник</pre>",
                'mystats':"<b>⛧ .mystats</b>\n<pre>Статистика сообщений за период\nИспользование: .mystats число период\nПериоды: час(ов), день/дня/дней, месяц(ев), год/года/лет\nПримеры:\n.mystats 1 час\n.mystats 2 дня\n.mystats 3 месяца\n.mystats 1 год</pre>",
                'price':"<b>⛧ .price</b>\n<pre>Показать прайс</pre>",
                'ad':"<b>⛧ .ad</b>\n<pre>Управление шаблонами\nИспользование:\n.ad + реплай — добавить текст\n.ad 5 + реплай — вставить на позицию\n.ad del 5 — удалить шаблон\n.ad show — показать все</pre>",
                'afk':"<b>⛧ .afk</b>\n<pre>AFK режим\nИспользование:\n.afk on — включить\n.afk off — выключить\n.afk причина — установить причину\n.afk photo + реплай — фото из реплая\n.afk photo URL — фото по ссылке\n.afk photo none — убрать фото</pre>",
                'mute':"<b>⛧ .mute</b>\n<pre>Мут пользователя\nИспользование: .mute ID или .mute + реплай\n.mute list — список замученных\n.mute time ID время — временный мут\nСнять: .mutstop ID</pre>",
                'trans':"<b>⛧ .trans</b>\n<pre>Переводчик\nИспользование: .trans [en] текст\nПримеры:\n.trans Привет — на русский\n.trans en Привет — на английский</pre>",
                'calculator':"<b>⛧ .calculator</b>\n<pre>Калькулятор\nИспользование: .calculator выражение\nПример: .calculator 5+3*2</pre>",
                'shrift':"<b>⛧ .shrift</b>\n<pre>Смена шрифта шаблонов\n0 - обычный\n1 - зачеркнутый\n2 - жирный\n3 - курсив\n4 - моноширинный\n5 - подчёркнутый\n6 - цитата (код)\n7 - спойлер</pre>",
                'shabl':"<b>⛧ .shabl</b>\n<pre>Поиск первых 2 строк из реплая по чатам\nИспользование: .shabl + реплай на сообщение</pre>",
                'status':"<b>⛧ .status</b>\n<pre>Показывает статус бота: активные задачи, CPU, RAM, пинг</pre>",
                'whois':"<b>⛧ .whois</b>\n<pre>Информация о пользователе\nИспользование: .whois @username или .whois + реплай</pre>",
                'addcontacts':"<b>⛧ .addcontacts</b>\n<pre>Добавить всех участников чата в контакты</pre>",
                'profilesave':"<b>⛧ .profilesave</b>\n<pre>Сохранить текущий профиль (имя, аватар, био)\nИспользование: .profilesave номер</pre>",
                'profileset':"<b>⛧ .profileset</b>\n<pre>Установить сохранённый профиль\nИспользование: .profileset номер</pre>",
                'profilelist':"<b>⛧ .profilelist</b>\n<pre>Показать список сохранённых профилей</pre>",
                'profiledel':"<b>⛧ .profiledel</b>\n<pre>Удалить сохранённый профиль\nИспользование: .profiledel номер</pre>",
                'top':"<b>⛧ .top</b>\n<pre>Топ активных пользователей в чате\nИспользование: .top количество</pre>",
                'topwords':"<b>⛧ .topwords</b>\n<pre>Топ слов в чате</pre>",
                'hack':"<b>⛧ .hack</b>\n<pre>Фейковый взлом пользователя\nИспользование: .hack @username</pre>",
                'reverse':"<b>⛧ .reverse</b>\n<pre>Перевернуть текст\nИспользование: .reverse текст</pre>",
                'ss':"<b>⛧ .ss</b>\n<pre>Скриншот сайта\nИспользование: .ss ссылка</pre>",
                'movie':"<b>⛧ .movie</b>\n<pre>Информация о фильме\nИспользование: .movie название</pre>",
            }
            if cmd in help_texts: await msg.edit(help_texts[cmd], parse_mode='html')
            else: await msg.edit(f"<b>⛧ Справка для .{cmd} не найдена</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .help: {str(e)}</b>")
    async def status_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            active_tasks = 0
            if spam_state: active_tasks += len([c for c in spam_state if spam_state[c]])
            if spam_state1: active_tasks += len([c for c in spam_state1 if spam_state1[c]])
            if tagger_chats: active_tasks += len([c for c in tagger_chats if tagger_chats[c]])
            if tag_chats: active_tasks += len([c for c in tag_chats if tag_chats[c]])
            if timer_tasks: active_tasks += len([t for t in timer_tasks if timer_tasks[t].get('active',False)])
            if lesenka_tasks: active_tasks += len([t for t in lesenka_tasks if lesenka_tasks[t].get('active',False)])
            if cal_tasks: active_tasks += len(cal_tasks)
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            ping_now = time.perf_counter_ns()
            response = f"<b>⛧ Статус бота</b>\n<pre>Активных задач: {active_tasks}\nCPU: {cpu}%\nRAM: {ram}%\nПинг: вычисляется... ms</pre>"
            message = await msg.edit(response, parse_mode='html')
            ping_time = round((time.perf_counter_ns() - ping_now) / 10**6, 2)
            await message.edit(response.replace('вычисляется...', str(ping_time)), parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .status: {str(e)}</b>")
    async def whois_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args and not msg.is_reply:
                await msg.edit("<b>⛧ Используйте: .whois @username или .whois + реплай</b>", parse_mode='html')
                return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                user = await reply_msg.get_sender()
            else:
                try: user = await self.tg_client.get_entity(args)
                except:
                    await msg.edit("<b>⛧ Пользователь не найден</b>", parse_mode='html')
                    return
            usernames = await get_all_usernames(self.tg_client, user)
            info = f"<b>⛧ Информация о пользователе</b>\n<pre>Имя: {get_display_name(user)}\nID: {user.id}\nUsername: {usernames}</pre>"
            await msg.edit(info, parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .whois: {str(e)}</b>")
    async def addcontacts_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            chat = await event.get_chat()
            if isinstance(chat, types.User):
                await msg.edit("<b>⛧ Команда только для групповых чатов</b>", parse_mode='html')
                return
            await msg.edit("<b>⛧ Добавляю участников в контакты...</b>", parse_mode='html')
            count = 0
            async for user in self.tg_client.iter_participants(chat):
                try:
                    await self.tg_client(functions.contacts.AddContactRequest(
                        id=user.id,
                        first_name=user.first_name or '',
                        last_name=user.last_name or '',
                        phone=''
                    ))
                    count += 1
                    await asyncio.sleep(1)
                except: continue
            await msg.edit(f"<b>⛧ Добавлено {count} контактов</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .addcontacts: {str(e)}</b>")
    async def profilesave_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .profilesave номер</b>", parse_mode='html')
                return
            profile_num = args.split()[0]
            profile_dir = os.path.join(PROFILES_DIR, f"profile_{profile_num}")
            os.makedirs(profile_dir, exist_ok=True)
            me = await self.tg_client.get_me()
            profile_data = {'first_name': me.first_name or '', 'last_name': me.last_name or '', 'bio': ''}
            try:
                full = await self.tg_client(GetFullUserRequest(me.id))
                if full.full_user.about: profile_data['bio'] = full.full_user.about
            except: pass
            with open(os.path.join(profile_dir, 'data.json'), 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            photos = await self.tg_client.get_profile_photos(me.id, limit=1)
            if photos:
                photo_path = os.path.join(profile_dir, 'avatar.jpg')
                try: await self.tg_client.download_media(photos[0], file=photo_path)
                except:
                    try: await self.tg_client.download_profile_photo(me.id, file=photo_path)
                    except: pass
            await msg.edit(f"<b>⛧ Профиль {profile_num} сохранён</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .profilesave: {str(e)}</b>")
    async def profileset_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .profileset номер</b>", parse_mode='html')
                return
            profile_num = args.split()[0]
            profile_dir = os.path.join(PROFILES_DIR, f"profile_{profile_num}")
            data_file = os.path.join(profile_dir, 'data.json')
            if not os.path.exists(data_file):
                await msg.edit(f"<b>⛧ Профиль {profile_num} не найден</b>", parse_mode='html')
                return
            with open(data_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            await self.tg_client(UpdateProfileRequest(
                first_name=profile_data.get('first_name',''),
                last_name=profile_data.get('last_name',''),
                about=profile_data.get('bio','')
            ))
            avatar_path = os.path.join(profile_dir, 'avatar.jpg')
            if os.path.exists(avatar_path):
                try:
                    current_photos = await self.tg_client.get_profile_photos('me', limit=1)
                    if current_photos:
                        await self.tg_client(DeletePhotosRequest([current_photos[0]]))
                    uploaded = await self.tg_client.upload_file(avatar_path)
                    await self.tg_client(UploadProfilePhotoRequest(uploaded))
                except Exception as e: print(f"Ошибка смены аватара: {e}")
            await msg.edit(f"<b>⛧ Профиль {profile_num} установлен</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .profileset: {str(e)}</b>")
    async def profilelist_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            profiles = []
            for folder in os.listdir(PROFILES_DIR):
                if folder.startswith('profile_') and os.path.isdir(os.path.join(PROFILES_DIR, folder)):
                    num = folder.replace('profile_','')
                    data_file = os.path.join(PROFILES_DIR, folder, 'data.json')
                    if os.path.exists(data_file):
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        name = f"{data.get('first_name','')} {data.get('last_name','')}".strip()
                        profiles.append(f"<code>.profileset {num}</code> - {name}")
            if profiles: await msg.edit("<b>⛧ Сохранённые профили:</b>\n" + "\n".join(profiles), parse_mode='html')
            else: await msg.edit("<b>⛧ Нет сохранённых профилей</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .profilelist: {str(e)}</b>")
    async def profiledel_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .profiledel номер</b>", parse_mode='html')
                return
            profile_num = args.split()[0]
            profile_dir = os.path.join(PROFILES_DIR, f"profile_{profile_num}")
            if os.path.exists(profile_dir):
                shutil.rmtree(profile_dir)
                await msg.edit(f"<b>⛧ Профиль {profile_num} удалён</b>", parse_mode='html')
            else: await msg.edit(f"<b>⛧ Профиль {profile_num} не найден</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .profiledel: {str(e)}</b>")
    async def top_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            limit = int(args.split()[0]) if args else 10
            chat = await event.get_chat()
            if isinstance(chat, types.User):
                await msg.edit("<b>⛧ Команда только для групповых чатов</b>", parse_mode='html')
                return
            await msg.edit("<b>⛧ Считаю...</b>", parse_mode='html')
            users_count = {}
            async for message in self.tg_client.iter_messages(chat.id, limit=1000):
                if message.sender_id:
                    users_count[message.sender_id] = users_count.get(message.sender_id, 0) + 1
            sorted_users = sorted(users_count.items(), key=lambda x: x[1], reverse=True)[:limit]
            response = f"<b>⛧ Топ {limit} активных:</b>\n"
            for i, (uid, count) in enumerate(sorted_users, 1):
                try:
                    user = await self.tg_client.get_entity(uid)
                    name = get_display_name(user)
                except: name = str(uid)
                response += f"<pre>{i}. {name} - {count} сообщ.</pre>\n"
            await msg.edit(response, parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .top: {str(e)}</b>")
    async def topwords_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            chat = await event.get_chat()
            if isinstance(chat, types.User):
                await msg.edit("<b>⛧ Команда только для групповых чатов</b>", parse_mode='html')
                return
            await msg.edit("<b>⛧ Считаю слова...</b>", parse_mode='html')
            word_count = {}
            async for message in self.tg_client.iter_messages(chat.id, limit=1000):
                if message.text:
                    for word in message.text.lower().split():
                        if len(word) >= 3:
                            word_count[word] = word_count.get(word, 0) + 1
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:20]
            response = "<b>⛧ Топ слов:</b>\n"
            for i, (word, count) in enumerate(sorted_words, 1):
                response += f"<pre>{i}. {word} - {count} раз</pre>\n"
            await msg.edit(response, parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .topwords: {str(e)}</b>")
    async def hack_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .hack @username</b>", parse_mode='html')
                return
            target = args.split()[0]
            await msg.edit(f"<b>⛧ Взламываю {target}...</b>", parse_mode='html')
            await asyncio.sleep(1)
            hack_lines = [
                f"Поиск {target} в базах данных...",
                f"Перехват IP-адреса... 104.28.31.182",
                f"Подбор пароля... ********",
                f"Доступ к Telegram...",
                f"Поиск переписок...",
                f"Данные карт... 4276 **** **** 1234",
                f"Адрес... ул. Пушкина, д. Колотушкина",
                f"{target} успешно взломан!",
            ]
            for line in hack_lines:
                await asyncio.sleep(0.8)
                try: await msg.edit(f"<b>⛧ Взлом {target}</b>\n<pre>{line}</pre>", parse_mode='html')
                except: break
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .hack: {str(e)}</b>")
    async def reverse_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args and not msg.is_reply:
                await msg.edit("<b>⛧ Используйте: .reverse текст или .reverse + реплай</b>", parse_mode='html')
                return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                text = reply_msg.text
            else: text = args
            if not text:
                await msg.edit("<b>⛧ Нет текста</b>", parse_mode='html')
                return
            reversed_text = text[::-1]
            await msg.edit(f"<b>⛧ Перевёрнутый текст:</b>\n<pre>{reversed_text}</pre>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .reverse: {str(e)}</b>")
    async def ss_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .ss ссылка</b>", parse_mode='html')
                return
            url = args.split()[0]
            if not url.startswith('http'): url = 'https://' + url
            await msg.edit("<b>⛧ Делаю скриншот...</b>", parse_mode='html')
            await msg.edit("<b>⛧ API скриншотов не настроен. Используйте: https://screenshotmachine.com</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .ss: {str(e)}</b>")
    async def movie_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Используйте: .movie название</b>", parse_mode='html')
                return
            movie_name = args
            await msg.edit(f"<b>⛧ Ищу фильм: {movie_name}...</b>", parse_mode='html')
            await msg.edit("<b>⛧ API фильмов не настроен. Используйте: https://omdbapi.com</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .movie: {str(e)}</b>")
    async def uptime_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            bot_runtime = int(time.time() - start_time)
            bot_runtime_formatted = str(timedelta(seconds=bot_runtime))
            try:
                pc_runtime = int(time.time() - psutil.boot_time())
                pc_runtime_formatted = str(timedelta(seconds=pc_runtime))
            except: pc_runtime_formatted = "недоступно"
            ping_now = time.perf_counter_ns()
            response = f"<b>⛧ Аптайм бота:</b> <code>{bot_runtime_formatted}</code>\n<b>⛧ Аптайм ПК:</b> <code>{pc_runtime_formatted}</code>\n<b>⛧ Пинг: <code>вычисляется...</code> ms</b>"
            message = await msg.edit(response, parse_mode='html')
            ping_time = round((time.perf_counter_ns() - ping_now) / 10**6, 2)
            await message.edit(response.replace('вычисляется...', str(ping_time)), parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .uptime: {str(e)}</b>")
    async def ping_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            ping_now = time.perf_counter_ns()
            message = await msg.edit("<b>⛧ Пинг: <code>вычисляется...</code> ms</b>", parse_mode='html')
            ping_time = round((time.perf_counter_ns() - ping_now) / 10**6, 2)
            await message.edit(f"<b>⛧ Пинг: <code>{ping_time}</code> ms</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .ping: {str(e)}</b>")
    async def reg_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            if msg.is_reply: user = (await msg.get_reply_message()).sender
            elif await self.get_args(msg):
                args = await self.get_args(msg)
                try: user = await self.tg_client.get_entity(args)
                except Exception as e:
                    await msg.edit(f"<b>⛧ Ошибка получения пользователя: {str(e)}</b>", parse_mode='html')
                    return
            else: user = await self.tg_client.get_me()
            usernames = await get_all_usernames(self.tg_client, user)
            user_info = [f"<b>⛧ Информация о пользователе:</b>", f"Имя: <code>{get_display_name(user)}</code>", f"ID: <code>{user.id}</code>", f"Юзернеймы: {usernames}"]
            try:
                try:
                    await self.tg_client.delete_dialog('regdatabot')
                    await asyncio.sleep(1)
                except: pass
                await self.tg_client.send_message('regdatabot', f'/reg {user.id}')
                start_time_wait = time.time()
                reg_info = None
                while time.time() - start_time_wait < 10:
                    await asyncio.sleep(1)
                    async for message in self.tg_client.iter_messages('regdatabot', limit=1):
                        if message.text and (str(user.id) in message.text or "Registered on" in message.text):
                            reg_info = self.parse_regdatabot_response(message.text)
                            break
                    if reg_info: break
                if reg_info: user_info.extend(["", f"Дата регистрации: <code>{reg_info['reg_date']}</code>", f"Возраст аккаунта: <code>{reg_info['age_details']}</code>"])
                else: user_info.append("\nНе удалось получить дату регистрации")
            except Exception as e: user_info.append(f"\nОшибка при запросе даты регистрации: {str(e)}")
            await self.send_with_command_media(msg, "\n".join(user_info), "reg")
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .reg: {str(e)}</b>")
    def parse_regdatabot_response(self, text):
        result = {'reg_date':'неизвестно','age_details':'неизвестно'}
        date_patterns = [r'Дата регистрации:\s*(\d{2}\.\d{2}\.\d{4})', r'Registered on:\s*(\d{2}\.\d{2}\.\d{4})', r'(\d{2}\.\d{2}\.\d{4})']
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result['reg_date'] = match.group(1)
                break
        if result['reg_date'] != 'неизвестно':
            try:
                reg_date = datetime.strptime(result['reg_date'], '%d.%m.%Y')
                today = datetime.now()
                delta = relativedelta(today, reg_date)
                years, months, days = delta.years, delta.months, delta.days
                age_parts = []
                if years > 0: age_parts.append(f"{years} год(а/лет)")
                if months > 0: age_parts.append(f"{months} месяц(ев)")
                if days > 0 or not age_parts: age_parts.append(f"{days} день/дней")
                result['age_details'] = ", ".join(age_parts)
            except: pass
        return result
    async def trans_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args and not msg.is_reply:
                await msg.edit("<b>⛧ Использование переводчика:</b>\n\nОсновные команды:\n<code>.trans текст</code> - перевести текст на русский\n<code>.trans en текст</code> - перевести текст на английский\n<code>.trans</code> + реплай - перевести сообщение", parse_mode='html')
                return
            target_lang = 'ru'
            text_to_translate = ""
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                text_to_translate = reply_msg.text
                if args and args.lower() in ['en','eng','english']: target_lang = 'en'
            else:
                if args:
                    parts = args.split(maxsplit=1)
                    if len(parts) > 1 and parts[0].lower() in ['en','eng','english']:
                        target_lang = 'en'
                        text_to_translate = parts[1]
                    else: text_to_translate = args
            if not text_to_translate:
                await msg.edit("<b>⛧ Нет текста для перевода</b>", parse_mode='html')
                return
            translated_text, detected_lang = await self.translate_text(text_to_translate, target_lang)
            lang_flags = {'ru':'🇷🇺','en':'🇺🇸','unknown':'🌐'}
            lang_names = {'ru':'русский','en':'английский'}
            source_flag = lang_flags.get(detected_lang,'🌐')
            target_flag = lang_flags.get(target_lang,'🌐')
            target_name = lang_names.get(target_lang,target_lang)
            result = f"<b>{source_flag} Исходный текст ({detected_lang}):</b>\n<code>{text_to_translate}</code>\n\n<b>{target_flag} Перевод ({target_name}):</b>\n<code>{translated_text}</code>"
            await self.send_with_command_media(msg, result, "trans")
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .trans: {str(e)}</b>")
    async def rus_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            if not msg.is_reply and not await self.get_args(msg):
                await msg.edit("<b>⛧ Замена английских символов на русские:</b>\n\nОсновные команды:\n<code>.rus текст</code> - заменить англ символы на русские\n<code>.rus</code> + реплай - обработать сообщение", parse_mode='html')
                return
            text_to_process = ""
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                text_to_process = reply_msg.text
            else: text_to_process = await self.get_args(msg)
            if not text_to_process:
                await msg.edit("<b>⛧ Нет текста для обработки</b>", parse_mode='html')
                return
            processed_text = await self.replace_english_chars(text_to_process)
            if processed_text == text_to_process: result = f"<b>⛧ Исходный текст:</b>\n<code>{text_to_process}</code>\n\n<b>⛧ В тексте нет английских символов для замены</b>"
            else: result = f"<b>⛧ Исходный текст:</b>\n<code>{text_to_process}</code>\n\n<b>⛧ Обработанный текст:</b>\n<code>{processed_text}</code>"
            await self.send_with_command_media(msg, result, "rus")
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .rus: {str(e)}</b>")
    async def calculator_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args and not msg.is_reply:
                await msg.edit("<b>⛧ Калькулятор</b>\nИспользование: <code>.calculator выражение</code>\n\nПримеры:\n<code>.calculator 5+3</code> → 8\n<code>.calculator 10-4</code> → 6\n<code>.calculator 2*6</code> → 12\n<code>.calculator 15/3</code> → 5\n<code>.calculator 5+3*2</code> → 11\n<code>.calculator (5+3)*2</code> → 16", parse_mode='html')
                return
            expression = args.replace(' ','').replace(',','.')
            allowed_chars = set('0123456789+-*/.()')
            if not all(c in allowed_chars for c in expression):
                await msg.edit("<b>⛧ Ошибка: В выражении содержатся недопустимые символы</b>", parse_mode='html')
                return
            try:
                result = eval(expression)
                if isinstance(result, float):
                    if result.is_integer(): result = int(result)
                    else: result = round(result, 4)
                await msg.edit(f"<b>⛧ Результат:</b> <code>{expression} = {result}</code>", parse_mode='html')
            except ZeroDivisionError: await msg.edit("<b>⛧ Ошибка: Деление на ноль</b>", parse_mode='html')
            except Exception as e: await msg.edit(f"<b>⛧ Ошибка вычисления:</b> <code>{str(e)}</code>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .calculator: {str(e)}</b>")
    async def auto_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                if not auto_responses: await msg.edit("<b>⛧ Нет установленных автоответов</b>", parse_mode='html')
                else:
                    response = "<b>⛧ Автоответы:</b>\n"
                    for text, data in auto_responses.items(): response += f"<code>{text}</code> - медиа: {'есть' if data['media'] else 'нет'}\n"
                    await msg.edit(response, parse_mode='html')
                return
            if args.lower() == "off":
                auto_responses.clear()
                await msg.edit("<b>⛧ Все автоответы удалены</b>", parse_mode='html')
                await self.save_state()
                return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                text = args.split()[0]
                media = None
                if reply_msg.media: media = await reply_msg.download_media(file=os.path.join(MEDIA_DIR, f"auto_{text}"))
                auto_responses[text] = {'response':' '.join(args.split()[1:]) or choice(shablon),'media':media}
                await msg.edit(f"<b>⛧ Автоответ на '{text}' установлен</b>", parse_mode='html')
            else: await msg.edit("<b>⛧ Нужно ответить на сообщение с медиа</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .auto: {str(e)}</b>")
    async def gif_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id) or not msg.is_reply:
                await msg.edit("<b>⛧ Нужно ответить на сообщение с медиа</b>", parse_mode='html')
                return
            reply_msg = await msg.get_reply_message()
            if not reply_msg.media:
                await msg.edit("<b>⛧ В сообщении нет медиа</b>", parse_mode='html')
                return
            await msg.edit("<b>⛧ Конвертирую в GIF...</b>", parse_mode='html')
            media_path = await reply_msg.download_media()
            if not media_path:
                await msg.edit("<b>⛧ Не удалось скачать медиа</b>", parse_mode='html')
                return
            gif_path = media_path + '.gif'
            try:
                img = Image.open(media_path)
                img.save(gif_path, 'GIF', save_all=True)
                global media_counter
                media_counter += 1
                timestamp = int(time.time())
                file_name = f"{media_counter}_{timestamp}_gif.gif"
                final_path = os.path.join(MEDIA_DIR, file_name)
                os.rename(gif_path, final_path)
                await msg.edit(f"<b>⛧ GIF сохранен под номером {media_counter}</b>\nФайл: {file_name}", parse_mode='html')
                await self.save_state()
            except Exception as e: await msg.edit(f"<b>⛧ Ошибка конвертации: {str(e)}</b>", parse_mode='html')
            finally:
                if os.path.exists(media_path): os.remove(media_path)
                if os.path.exists(gif_path) and not os.path.exists(final_path): os.remove(gif_path)
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .gif: {str(e)}</b>")
    async def id_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                user = await reply_msg.get_sender()
                await msg.edit(f"<b>⛧ ID пользователя:</b> <code>{user.id}</code>", parse_mode='html')
            else:
                chat_id = msg.chat_id
                me = await self.tg_client.get_me()
                await msg.edit(f"<b>⛧ ID чата:</b> <code>{chat_id}</code>\n<b>⛧ Ваш ID:</b> <code>{me.id}</code>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .id: {str(e)}</b>")
    async def addras_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message()
                chat_id = reply_msg.chat_id
                if chat_id not in ras_chats: ras_chats.append(chat_id); await msg.edit(f"<b>⛧ Чат {chat_id} добавлен в рассылку</b>", parse_mode='html')
                else: await msg.edit(f"<b>⛧ Чат {chat_id} уже в списке</b>", parse_mode='html')
            else:
                args = await self.get_args(msg)
                if args:
                    try:
                        chat_id = int(args.split()[0])
                        if chat_id not in ras_chats: ras_chats.append(chat_id); await msg.edit(f"<b>⛧ Чат {chat_id} добавлен в рассылку</b>", parse_mode='html')
                        else: await msg.edit(f"<b>⛧ Чат {chat_id} уже в списке</b>", parse_mode='html')
                    except: await msg.edit("<b>⛧ Неверный ID чата</b>", parse_mode='html')
                else: await msg.edit("<b>⛧ Используйте: .addras + реплай или .addras chat_id</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .addras: {str(e)}</b>")
    async def delras_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if args:
                try:
                    chat_id = int(args.split()[0])
                    if chat_id in ras_chats: ras_chats.remove(chat_id); await msg.edit(f"<b>⛧ Чат {chat_id} удален из рассылки</b>", parse_mode='html')
                    else: await msg.edit(f"<b>⛧ Чат {chat_id} не найден</b>", parse_mode='html')
                except: await msg.edit("<b>⛧ Неверный ID чата</b>", parse_mode='html')
            else: await msg.edit("<b>⛧ Используйте: .delras chat_id</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .delras: {str(e)}</b>")
    async def addrepo_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if args:
                try:
                    chat_id = int(args.split()[0])
                    if chat_id not in repo_chats: repo_chats.append(chat_id); await msg.edit(f"<b>⛧ Чат {chat_id} добавлен в репозиторий</b>", parse_mode='html')
                    else: await msg.edit(f"<b>⛧ Чат {chat_id} уже в репозитории</b>", parse_mode='html')
                except: await msg.edit("<b>⛧ Неверный ID чата</b>", parse_mode='html')
            else: await msg.edit("<b>⛧ Используйте: .addrepo chat_id</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .addrepo: {str(e)}</b>")
    async def delrepo_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if args:
                try:
                    chat_id = int(args.split()[0])
                    if chat_id in repo_chats: repo_chats.remove(chat_id); await msg.edit(f"<b>⛧ Чат {chat_id} удален из репозитория</b>", parse_mode='html')
                    else: await msg.edit(f"<b>⛧ Чат {chat_id} не найден</b>", parse_mode='html')
                except: await msg.edit("<b>⛧ Неверный ID чата</b>", parse_mode='html')
            else: await msg.edit("<b>⛧ Используйте: .delrepo chat_id</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .delrepo: {str(e)}</b>")
    async def chats_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            chat_links = []
            if ras_chats:
                chat_links.append("=== СПИСОК РАССЫЛКИ ===\n")
                for chat_id in ras_chats:
                    try:
                        chat = await self.tg_client.get_entity(chat_id)
                        if hasattr(chat,'username') and chat.username: link = f"https://t.me/{chat.username}"
                        else: link = f"https://t.me/c/{str(chat_id).replace('-100','')}"
                        chat_links.append(f"{chat_id}: {link}")
                    except: chat_links.append(f"{chat_id}: ссылка недоступна")
            if repo_chats:
                chat_links.append("\n=== СПИСОК РЕПОЗИТОРИЯ ===\n")
                for chat_id in repo_chats:
                    try:
                        chat = await self.tg_client.get_entity(chat_id)
                        if hasattr(chat,'username') and chat.username: link = f"https://t.me/{chat.username}"
                        else: link = f"https://t.me/c/{str(chat_id).replace('-100','')}"
                        chat_links.append(f"{chat_id}: {link}")
                    except: chat_links.append(f"{chat_id}: ссылка недоступна")
            if not ras_chats and not repo_chats: await msg.edit("<b>⛧ Списки чатов пусты</b>", parse_mode='html'); return
            file_path = os.path.join(DATA_DIR, "chats_list.txt")
            with open(file_path, 'w', encoding='utf-8') as f: f.write('\n'.join(chat_links))
            await self.tg_client.send_file(msg.chat_id, file_path)
            os.remove(file_path)
            await msg.delete()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .chats: {str(e)}</b>")
    async def msdel_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            chat_id = msg.chat_id
            chat = await event.get_chat()
            if isinstance(chat, types.User):
                await msg.edit("<b>⛧ Команда недоступна в личных чатах</b>", parse_mode='html')
                return
            status_msg = await msg.edit("<b>⛧ Начинаю удаление всех сообщений от начала чата...</b>", parse_mode='html')
            deleted_total = 0
            batch_size = 100
            current_msg_id = msg.id - 1
            while True:
                try:
                    message_ids = []
                    async for message in self.tg_client.iter_messages(chat_id, min_id=1, max_id=current_msg_id, limit=batch_size): message_ids.append(message.id)
                    if not message_ids: break
                    await self.tg_client.delete_messages(chat_id, message_ids)
                    deleted_total += len(message_ids)
                    await status_msg.edit(f"<b>⛧ Удалено {deleted_total} сообщений...</b>", parse_mode='html')
                    current_msg_id = min(message_ids) - 1
                    if current_msg_id <= 0 or len(message_ids) < batch_size: break
                    await asyncio.sleep(0.5)
                except Exception as e:
                    await status_msg.edit(f"<b>⛧ Ошибка удаления: {str(e)}</b>", parse_mode='html')
                    return
            await status_msg.edit(f"<b>⛧ Удалено {deleted_total} сообщений от начала чата до команды</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .msdel: {str(e)}</b>")
    async def delete_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            chat = await event.get_chat()
            if isinstance(chat, types.User):
                await msg.edit("<b>⛧ Команда недоступна в личных чатах</b>", parse_mode='html')
                return
            args = await self.get_args(msg)
            if not args:
                await msg.edit("<b>⛧ Укажите количество сообщений для удаления</b>", parse_mode='html')
                return
            limit = int(args.split()[0])
            me = await self.tg_client.get_me()
            deleted = 0
            async for message in self.tg_client.iter_messages(msg.chat_id, from_user=me.id, limit=limit):
                try: await message.delete(); deleted += 1; await asyncio.sleep(0.5)
                except: pass
            await msg.edit(f"<b>⛧ Удалено {deleted} ваших сообщений</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .delete: {str(e)}</b>")
    async def deleteall_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            chat = await event.get_chat()
            if isinstance(chat, types.User):
                await msg.edit("<b>⛧ Команда недоступна в личных чатах</b>", parse_mode='html')
                return
            await msg.edit("<b>⛧ Начинаю удаление всех ваших сообщений из логов...</b>", parse_mode='html')
            total_deleted = 0
            me = await self.tg_client.get_me()
            for chat_id in list(message_logs.keys()):
                try:
                    chat_entity = await self.tg_client.get_entity(chat_id)
                    if isinstance(chat_entity, types.User): continue
                    message_ids = [m['id'] for m in message_logs[chat_id]]
                    if message_ids:
                        await self.tg_client.delete_messages(chat_id, message_ids)
                        total_deleted += len(message_ids)
                        await asyncio.sleep(0.5)
                except: pass
            message_logs.clear()
            await self.save_state()
            await msg.edit(f"<b>⛧ Удалено {total_deleted} сообщений</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .deleteall: {str(e)}</b>")
    async def offl_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global spam_state, spam_state1, tagger_chats, tag_chats, timer_tasks, lesenka_tasks
            spam_state.clear(); spam_state1.clear(); tagger_chats.clear(); tag_chats.clear(); timer_tasks.clear(); lesenka_tasks.clear()
            await msg.edit("<b>⛧ Все флудеры и таймеры остановлены</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .offl: {str(e)}</b>")
    async def mute_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global muted_users, muted_until
            args = await self.get_args(msg)
            if args and args.lower() == 'list':
                if not muted_users: await msg.edit("<b>⛧ Список мута пуст</b>", parse_mode='html')
                else:
                    users_list = []
                    for uid in muted_users:
                        until = muted_until.get(uid, 0)
                        if until:
                            time_left = int(until - time.time())
                            if time_left > 0: users_list.append(f"<code>{uid}</code> - ещё {time_left} сек")
                            else: users_list.append(f"<code>{uid}</code> - истекает")
                        else: users_list.append(f"<code>{uid}</code> - навсегда")
                    await msg.edit("<b>⛧ Замученные:</b>\n" + "\n".join(users_list) if users_list else "<b>⛧ Список мута пуст</b>", parse_mode='html')
                return
            if args and args.startswith('time'):
                parts = args.split()
                if len(parts) < 3:
                    await msg.edit("<b>⛧ Используйте: .mute time ID время</b>\nПример: .mute time 123456 1hour", parse_mode='html')
                    return
                try:
                    user_id = int(parts[1])
                    mute_seconds = await self.parse_time(parts[2])
                except:
                    await msg.edit("<b>⛧ Неверный формат</b>", parse_mode='html')
                    return
                muted_users.add(user_id)
                muted_until[user_id] = time.time() + mute_seconds
                await msg.edit(f"<b>⛧ Пользователь {user_id} замучен на {parts[2]}</b>", parse_mode='html')
                await self.save_state()
                return
            if args:
                try: user_id = int(args.split()[0])
                except:
                    await msg.edit("<b>⛧ Неверный ID</b>", parse_mode='html')
                    return
            elif msg.is_reply:
                reply_msg = await msg.get_reply_message()
                user = await reply_msg.get_sender()
                user_id = user.id
            else:
                await msg.edit("<b>⛧ Используйте: .mute ID / .mute + реплай / .mute list / .mute time ID время</b>", parse_mode='html')
                return
            if user_id in muted_users: await msg.edit(f"<b>⛧ Пользователь {user_id} уже в списке мута</b>", parse_mode='html'); return
            muted_users.add(user_id)
            await msg.edit(f"<b>⛧ Пользователь {user_id} добавлен в список мута</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .mute: {str(e)}</b>")
    async def mutestop_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global muted_users, muted_until
            args = await self.get_args(msg)
            if args:
                try: user_id = int(args.split()[0])
                except:
                    await msg.edit("<b>⛧ Неверный ID пользователя</b>", parse_mode='html')
                    return
            elif msg.is_reply:
                reply_msg = await msg.get_reply_message()
                user = await reply_msg.get_sender()
                user_id = user.id
            else:
                await msg.edit("<b>⛧ Используйте: .mutstop ID или .mutstop + реплай</b>", parse_mode='html')
                return
            if user_id in muted_users:
                muted_users.discard(user_id)
                muted_until.pop(user_id, None)
                await msg.edit(f"<b>⛧ Пользователь {user_id} удален из списка мута</b>", parse_mode='html')
                await self.save_state()
            else: await msg.edit(f"<b>⛧ Пользователь {user_id} не в списке мута</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .mutstop: {str(e)}</b>")
    async def set_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id) or not msg.is_reply: return
            reply_msg = await msg.get_reply_message()
            global shablon
            if reply_msg.file:
                file = await reply_msg.download_media()
                with open(file, 'r', encoding='utf-8') as f: shablon = [line.strip() for line in f if line.strip()]
                os.remove(file)
                await msg.edit(f"<b>⛧ Шаблоны обновлены! Загружено: {len(shablon)} шт.</b>", parse_mode='html')
            elif reply_msg.text:
                shablon = [line.strip() for line in reply_msg.text.split('\n') if line.strip()]
                await msg.edit(f"<b>⛧ Шаблоны обновлены! Загружено: {len(shablon)} шт.</b>", parse_mode='html')
            else: await msg.edit("<b>⛧ Ответьте на файл или сообщение с шаблонами</b>", parse_mode='html'); return
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .set: {str(e)}</b>")
    async def set2_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id) or not msg.is_reply: return
            reply_msg = await msg.get_reply_message()
            global type_shablon
            if reply_msg.file:
                file = await reply_msg.download_media()
                with open(file, 'r', encoding='utf-8') as f: type_shablon = [line.strip() for line in f if line.strip()]
                os.remove(file)
            else: type_shablon = [line.strip() for line in reply_msg.text.split('\n') if line.strip()]
            await msg.edit(f"<b>⛧ Шаблоны для .type обновлены (строк: {len(type_shablon)})</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .set2: {str(e)}</b>")
    async def file_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            with open('texts.txt', 'w', encoding='utf-8') as f:
                for line in shablon: f.write(line + '\n')
            await self.tg_client.send_file(msg.chat_id, 'texts.txt')
            os.remove('texts.txt')
            await msg.delete()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .file: {str(e)}</b>")
    async def list_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if args and args.lower() == "none":
                global mlist; mlist = None
                await msg.edit("<b>⛧ Медиа для списка удалено</b>", parse_mode='html')
                await self.save_state(); return
            response = f"<b>⛧ Список активных задач:</b>\n\n"
            has_tasks = False
            if spam_state:
                has_tasks = True; response += f"<b>⛧ .spam:</b>\n"
                for chat_id in spam_state:
                    if spam_state[chat_id]: response += f"  Чат: <code>{chat_id}</code> - <code>.stop {chat_id}</code>\n"
            if spam_state1:
                has_tasks = True; response += f"<b>⛧ .psp:</b>\n"
                for chat_id in spam_state1:
                    if spam_state1[chat_id]: response += f"  Чат: <code>{chat_id}</code> - <code>.pstop {chat_id}</code>\n"
            if tagger_chats:
                has_tasks = True; response += f"<b>⛧ .tag:</b>\n"
                for chat_id in tagger_chats:
                    if tagger_chats[chat_id]: response += f"  Чат: <code>{chat_id}</code> - <code>.off {chat_id}</code>\n"
            if tag_chats:
                has_tasks = True; response += f"<b>⛧ .rem:</b>\n"
                for chat_id in tag_chats:
                    if tag_chats[chat_id]: response += f"  Чат: <code>{chat_id}</code> - <code>.goff {chat_id}</code>\n"
            if timer_tasks:
                has_tasks = True; response += f"<b>⛧ .timer:</b>\n"
                for task_id in timer_tasks:
                    if timer_tasks[task_id].get('active', False): response += f"  Задача: <code>{task_id}</code> - <code>.stoptimer {task_id}</code>\n"
            if lesenka_tasks:
                has_tasks = True; response += f"<b>⛧ .lesenka:</b>\n"
                for task_id in lesenka_tasks:
                    if lesenka_tasks[task_id].get('active', False):
                        chat_id = lesenka_tasks[task_id].get('chat_id'); user_id = lesenka_tasks[task_id].get('user_id')
                        response += f"  Юзер: <code>{user_id}</code> в чате <code>{chat_id}</code>\n"
            if cal_tasks:
                has_tasks = True; response += f"<b>⛧ .cal:</b>\n"
                for task_id in cal_tasks:
                    if cal_tasks[task_id].get('active', True):
                        chat_id = cal_tasks[task_id].get('chat_id'); user_id = cal_tasks[task_id].get('user_id')
                        response += f"  Чат: <code>{chat_id}</code> юзер: <code>{user_id}</code> - <code>.stopcal {chat_id}</code>\n"
            if muted_users:
                has_tasks = True; response += f"<b>⛧ .mute:</b>\n"
                for uid in muted_users: response += f"  Юзер: <code>{uid}</code> - <code>.mutstop {uid}</code>\n"
            if not has_tasks: response += "  Нет активных задач"
            await self.send_with_command_media(msg, response, "list")
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .list: {str(e)}</b>")
    async def ras_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id) or not msg.is_reply: return
            if not ras_chats:
                await msg.edit("<b>⛧ Список чатов для рассылки пуст. Добавьте чаты через .addras</b>", parse_mode='html'); return
            reply_msg = await msg.get_reply_message()
            await msg.edit("<b>⛧ Начинаю рассылку...</b>", parse_mode='html')
            count = 0
            for chat_id in ras_chats:
                try:
                    if reply_msg.media: await self.tg_client.send_file(chat_id, reply_msg.media, caption=reply_msg.text, parse_mode='html')
                    else: await self.tg_client.send_message(chat_id, reply_msg.text, parse_mode='html')
                    count += 1; await asyncio.sleep(12)
                except Exception as e: print(f"Ошибка отправки в чат {chat_id}: {e}"); continue
            await msg.edit(f"<b>⛧ Сообщение разослано в {count} чатов</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .ras: {str(e)}</b>")
    async def afk_handler(self, event):
        msg = event.message
        global afk_state, afk_users, afk_start_time, afk_reason, afk_photo
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                status = "включен" if afk_state else "выключен"
                photo_status = "установлено" if afk_photo else "не установлено"
                await msg.edit(f"<b>⛧ AFK: {status}</b>\nПричина: {afk_reason}\nФото: {photo_status}", parse_mode='html'); return
            if args.lower() == 'on': afk_state = True; afk_start_time = datetime.now(); afk_users = []; await msg.edit("<b>⛧ AFK включен</b>", parse_mode='html')
            elif args.lower() == 'off': afk_state = False; afk_users = []; afk_start_time = None; await msg.edit("<b>⛧ AFK выключен</b>", parse_mode='html')
            elif args.lower().startswith('photo'):
                photo_args = args[5:].strip()
                if photo_args.lower() == 'none': afk_photo = None; await msg.edit("<b>⛧ Фото AFK убрано</b>", parse_mode='html')
                elif photo_args.startswith('http'): afk_photo = photo_args; await msg.edit("<b>⛧ Фото AFK установлено по ссылке</b>", parse_mode='html')
                elif msg.is_reply:
                    reply_msg = await msg.get_reply_message()
                    if reply_msg and reply_msg.media:
                        file_path = await reply_msg.download_media(file=os.path.join(MEDIA_DIR, f"afk_photo_{int(time.time())}"))
                        if file_path: afk_photo = file_path; await msg.edit("<b>⛧ Фото AFK установлено из реплая</b>", parse_mode='html')
                        else: await msg.edit("<b>⛧ Не удалось сохранить фото</b>", parse_mode='html')
                    else: await msg.edit("<b>⛧ В реплае нет медиа</b>", parse_mode='html')
                else: await msg.edit("<b>⛧ Используйте: .afk photo none / .afk photo URL / .afk photo + реплай</b>", parse_mode='html')
            else: afk_reason = args; await msg.edit(f"<b>⛧ Причина AFK: {afk_reason}</b>", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .afk: {str(e)}</b>")
    async def spam_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Укажите время</b>", parse_mode='html'); return
            chat_id = msg.chat_id
            parts = args.split()
            time_delay = int(parts[0])
            photo = None; text_parts_start = 1
            if len(parts) > 1:
                if parts[1].isdigit(): photo = parts[1]; text_parts_start = 2
                elif 'http://' in parts[1] or 'https://' in parts[1]: photo = parts[1]; text_parts_start = 2
            text = ' '.join(parts[text_parts_start:]) if len(parts) > text_parts_start else get_next_template(f"spam_{chat_id}")
            spam_state[chat_id] = True
            await msg.edit(f"<b>⛧ Спам запущен | стоп: .stop</b>", parse_mode='html')
            while spam_state.get(chat_id, False):
                await self.send_with_media(chat_id, text, photo); await asyncio.sleep(time_delay)
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .spam: {str(e)}</b>")
    async def psp_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global spam_state1
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Укажите chat_id и время</b>", parse_mode='html'); return
            parts = args.split()
            chat_id = int(parts[0]); time_delay = int(parts[1])
            photo = None; text_parts_start = 2
            if len(parts) > 2:
                if parts[2].isdigit(): photo = parts[2]; text_parts_start = 3
                elif 'http://' in parts[2] or 'https://' in parts[2]: photo = parts[2]; text_parts_start = 3
            text = ' '.join(parts[text_parts_start:]) if len(parts) > text_parts_start else get_next_template(f"psp_{chat_id}")
            spam_state1[chat_id] = True
            await msg.edit(f"<b>⛧ Спам запущен в {chat_id} | стоп: .pstop {chat_id}</b>", parse_mode='html')
            while spam_state1.get(chat_id, False):
                await self.send_with_media(chat_id, text, photo); await asyncio.sleep(time_delay)
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .psp: {str(e)}</b>")
    async def tag_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Укажите user_id и время</b>", parse_mode='html'); return
            parts = args.split()
            user_id = int(parts[0]); time_delay = int(parts[1])
            photo = None; text_parts_start = 2
            if len(parts) > 2:
                if parts[2].isdigit(): photo = parts[2]; text_parts_start = 3
                elif 'http://' in parts[2] or 'https://' in parts[2]: photo = parts[2]; text_parts_start = 3
            text = ' '.join(parts[text_parts_start:]) if len(parts) > text_parts_start else ''
            reply_id = (await msg.get_reply_message()).id if msg.is_reply else None
            chat_id = msg.chat_id
            tagger_chats[chat_id] = True
            await msg.edit(f"<b>⛧ Теггер запущен | стоп: .off</b>", parse_mode='html')
            while tagger_chats.get(chat_id, False):
                template = get_next_template(f"tag_{chat_id}")
                message_text = f"{text} <a href='tg://user?id={user_id}'>{template}</a>" if text else f"<a href='tg://user?id={user_id}'>{template}</a>"
                await self.send_with_media(chat_id, message_text, photo, reply_id, parse_mode='html'); await asyncio.sleep(time_delay)
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .tag: {str(e)}</b>")
    async def rem_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Укажите chat_id, user_id и время</b>", parse_mode='html'); return
            parts = args.split()
            chat_id = int(parts[0]); user_id = int(parts[1]); time_delay = int(parts[2])
            photo = None; text_parts_start = 3
            if len(parts) > 3:
                if parts[3].isdigit(): photo = parts[3]; text_parts_start = 4
                elif 'http://' in parts[3] or 'https://' in parts[3]: photo = parts[3]; text_parts_start = 4
            text = ' '.join(parts[text_parts_start:]) if len(parts) > text_parts_start else ''
            tag_chats[chat_id] = True
            await msg.edit(f"<b>⛧ Теггер запущен в {chat_id} | стоп: .goff {chat_id}</b>", parse_mode='html')
            while tag_chats.get(chat_id, False):
                template = get_next_template(f"rem_{chat_id}")
                message_text = f"{text} <a href='tg://user?id={user_id}'>{template}</a>" if text else f"<a href='tg://user?id={user_id}'>{template}</a>"
                await self.send_with_media(chat_id, message_text, photo, parse_mode='html'); await asyncio.sleep(time_delay)
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .rem: {str(e)}</b>")
    async def cal_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: return
            parts = args.split()
            if len(parts) < 3: return
            chat_id = int(parts[0]); user_id = int(parts[1]); time_sec = int(parts[2])
            if time_sec < 1: time_sec = 1
            photo = None; text_parts_start = 3
            if len(parts) > 3:
                if parts[3].isdigit(): photo = parts[3]; text_parts_start = 4
                elif 'http://' in parts[3] or 'https://' in parts[3]: photo = parts[3]; text_parts_start = 4
                else: text_parts_start = 3
            user_text = ' '.join(parts[text_parts_start:]) if len(parts) > text_parts_start else ''
            try: await self.tg_client.get_entity(chat_id)
            except: await msg.edit(f"<b>⛧ Не удалось получить чат {chat_id}</b>", parse_mode='html'); return
            task_id = f"cal_{chat_id}_{user_id}_{int(time.time())}"
            cal_tasks[task_id] = {'chat_id':chat_id,'user_id':user_id,'interval':time_sec,'photo':photo,'user_text':user_text,'active':True}
            await self.save_state()
            await msg.edit(f"<b>⛧ Календарь запущен | стоп: .stopcal {chat_id}</b>", parse_mode='html')
            asyncio.create_task(self.run_cal_task(task_id))
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .cal: {str(e)}</b>")
    async def run_cal_task(self, task_id):
        try:
            task = cal_tasks.get(task_id)
            if not task: return
            while task.get('active', False):
                template = get_next_template(task_id)
                message_text = f"{task['user_text']} {template}" if task['user_text'] else template
                try: await self.send_with_media(task['chat_id'], f"<a href='tg://user?id={task['user_id']}'>{message_text}</a>", task['photo'], parse_mode='html')
                except Exception as e: print(f"Ошибка отправки в календаре: {e}")
                await asyncio.sleep(task['interval'])
            if task_id in cal_tasks: del cal_tasks[task_id]; await self.save_state()
        except Exception as e:
            print(f"Ошибка в календаре {task_id}: {str(e)}")
            if task_id in cal_tasks: del cal_tasks[task_id]; await self.save_state()
    async def stopcal_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                if not cal_tasks: await msg.edit("<b>⛧ Нет активных календарей</b>", parse_mode='html')
                else:
                    tasks_list = []
                    for task_id, task in cal_tasks.items(): tasks_list.append(f"Чат: {task['chat_id']} - юзер: {task['user_id']}")
                    await msg.edit("<b>⛧ Активные календари:</b>\n\n" + "\n".join(tasks_list) + "\n\nДля остановки: .stopcal chat_id", parse_mode='html')
                return
            try:
                chat_id = int(args.split()[0])
                stopped = False
                for task_id in list(cal_tasks.keys()):
                    if cal_tasks[task_id]['chat_id'] == chat_id: cal_tasks[task_id]['active'] = False; del cal_tasks[task_id]; stopped = True
                if stopped: await msg.edit(f"<b>⛧ Календарь в чате {chat_id} остановлен</b>", parse_mode='html'); await self.save_state()
                else: await msg.edit(f"<b>⛧ Нет активного календаря в чате {chat_id}</b>", parse_mode='html')
            except: await msg.edit("<b>⛧ Неверный ID чата</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .stopcal: {str(e)}</b>")
    async def reply_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global autoreply_list, autoreply_time, autoreply_cd, autoreply_photo, autoreply_shpk, last_reply_time
            args = await self.get_args(msg)
            if not args and not msg.is_reply:
                if not autoreply_list: await msg.edit("<b>⛧ Нет активных автоответчиков</b>", parse_mode='html'); return
                users_list = []
                for uid in autoreply_list:
                    time_val = autoreply_time.get(uid,0); cd_val = autoreply_cd.get(uid,0)
                    has_media = "есть" if autoreply_photo.get(uid) else "нет"
                    users_list.append(f"<code>.l {uid}</code> - задержка: {time_val} сек, CD: {cd_val} сек | медиа: {has_media}")
                await msg.edit(f"<b>⛧ Активные автоответчики:</b>\n" + "\n".join(users_list) + "\n\nОтключить: <code>.l ID</code>", parse_mode='html'); return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message(); user_id = reply_msg.sender_id
                if args:
                    parts = args.split()
                    if len(parts) >= 1: autoreply_time[user_id] = int(parts[0])
                    if len(parts) >= 2: autoreply_cd[user_id] = int(parts[1])
                    if len(parts) >= 3: autoreply_photo[user_id] = parts[2]
                    if len(parts) >= 4: autoreply_shpk[user_id] = ' '.join(parts[3:])
                else: autoreply_time[user_id] = 0; autoreply_cd[user_id] = 0
                if user_id not in autoreply_list: autoreply_list.append(user_id)
                await msg.edit(f'<b>⛧ Автоответчик запущен для {user_id}</b>', parse_mode='html')
            elif args:
                try:
                    parts = args.split(); user_id = int(parts[0])
                    if len(parts) >= 2: autoreply_time[user_id] = int(parts[1])
                    else: autoreply_time[user_id] = 0
                    if len(parts) >= 3: autoreply_cd[user_id] = int(parts[2])
                    else: autoreply_cd[user_id] = 0
                    if len(parts) >= 4: autoreply_photo[user_id] = parts[3]
                    if len(parts) >= 5: autoreply_shpk[user_id] = ' '.join(parts[4:])
                    if user_id not in autoreply_list: autoreply_list.append(user_id)
                    await msg.edit(f'<b>⛧ Автоответчик запущен для {user_id}</b>', parse_mode='html')
                except ValueError: await msg.edit("<b>⛧ Неверный формат. Используйте: .reply user_id задержка cd номер_медиа шапка</b>", parse_mode='html'); return
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .reply: {str(e)}</b>")
    async def l_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global autoreply_list, autoreply_time, autoreply_cd, autoreply_photo, autoreply_shpk, last_reply_time
            if msg.is_reply:
                reply_msg = await msg.get_reply_message(); user_id = reply_msg.sender_id
                if user_id in autoreply_list:
                    autoreply_list.remove(user_id); autoreply_time.pop(user_id,None); autoreply_cd.pop(user_id,None); autoreply_photo.pop(user_id,None); autoreply_shpk.pop(user_id,None); last_reply_time.pop(user_id,None)
                    await msg.edit(f'<b>⛧ Автоответчик отключен для {user_id}</b>', parse_mode='html')
                else: await msg.edit(f'<b>⛧ Пользователь {user_id} не в списке</b>', parse_mode='html')
            elif await self.get_args(msg):
                args = await self.get_args(msg)
                try:
                    user_id = int(args.split()[0])
                    if user_id in autoreply_list:
                        autoreply_list.remove(user_id); autoreply_time.pop(user_id,None); autoreply_cd.pop(user_id,None); autoreply_photo.pop(user_id,None); autoreply_shpk.pop(user_id,None); last_reply_time.pop(user_id,None)
                        await msg.edit(f'<b>⛧ Автоответчик отключен для {user_id}</b>', parse_mode='html')
                    else: await msg.edit(f'<b>⛧ Пользователь {user_id} не в списке</b>', parse_mode='html')
                except ValueError: await msg.edit('<b>⛧ Неверный ID пользователя</b>', parse_mode='html')
            else:
                if not autoreply_list: await msg.edit("<b>⛧ Нет активных автоответчиков</b>", parse_mode='html')
                else:
                    users_list = []
                    for uid in autoreply_list:
                        time_val = autoreply_time.get(uid,0); cd_val = autoreply_cd.get(uid,0)
                        has_media = "есть" if autoreply_photo.get(uid) else "нет"
                        users_list.append(f"<code>.l {uid}</code> - задержка: {time_val} сек, CD: {cd_val} сек | медиа: {has_media}")
                    await msg.edit(f"<b>⛧ Активные автоответчики:</b>\n" + "\n".join(users_list) + "\n\n<b>⛧ Отключить:</b>\n<code>.l ID</code> - по ID\n<code>.l</code> + реплай - по сообщению", parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .l: {str(e)}</b>")
    async def pset_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global autoreply_photo, autoreply_time, autoreply_shpk, autoreply_cd
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Укажите действие и user_id</b>", parse_mode='html'); return
            parts = args.split()
            if len(parts) < 2: await msg.edit("<b>⛧ Укажите действие и user_id</b>", parse_mode='html'); return
            action = parts[0]
            try: user_id = int(parts[1])
            except: await msg.edit("<b>⛧ Неверный ID пользователя</b>", parse_mode='html'); return
            if action == 'shapka': autoreply_shpk[user_id] = ' '.join(parts[2:]) if len(parts) > 2 else ''; await msg.edit(f'<b>⛧ Шапка для {user_id} изменена</b>', parse_mode='html')
            elif action == 'media':
                if len(parts) > 2: autoreply_photo[user_id] = parts[2]
                await msg.edit(f'<b>⛧ Медиа для {user_id} изменено</b>', parse_mode='html')
            elif action == 'time': autoreply_time[user_id] = int(parts[2]) if len(parts) > 2 else 0; await msg.edit(f'<b>⛧ Задержка для {user_id} изменена на {autoreply_time[user_id]} сек</b>', parse_mode='html')
            elif action == 'cd': autoreply_cd[user_id] = int(parts[2]) if len(parts) > 2 else 0; await msg.edit(f'<b>⛧ CD для {user_id} изменен на {autoreply_cd[user_id]} сек</b>', parse_mode='html')
            await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .pset: {str(e)}</b>")
    async def lesenka_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id) or not msg.is_reply: await msg.edit("<b>⛧ Нужно ответить на сообщение пользователя</b>", parse_mode='html'); return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Укажите интервал в секундах</b>", parse_mode='html'); return
            try: interval = float(args.split()[0])
            except ValueError: await msg.edit("<b>⛧ Неверный интервал</b>", parse_mode='html'); return
            reply_msg = await msg.get_reply_message(); user = await reply_msg.get_sender()
            chat_id = msg.chat_id; user_id = user.id; reply_id = reply_msg.id
            if not shablon: await msg.edit("<b>⛧ Нет слов для лесенки</b>", parse_mode='html'); return
            task_id = f"lesenka_{chat_id}_{user_id}"
            if task_id in lesenka_tasks: lesenka_tasks[task_id]['active'] = False; lesenka_tasks.pop(task_id); await self.save_state()
            words = []
            for phrase in shablon:
                for word in phrase.split(): words.append(format_text_with_shrift(word))
            lesenka_tasks[task_id] = {'chat_id':chat_id,'user_id':user_id,'reply_id':reply_id,'interval':interval,'active':True,'words':words,'current_index':0}
            await msg.edit(f"<b>⛧ Лесенка запущена | стоп: .offles + реплай</b>", parse_mode='html')
            asyncio.create_task(self.run_lesenka_task(task_id)); await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .lesenka: {str(e)}</b>")
    async def run_lesenka_task(self, task_id):
        try:
            task = lesenka_tasks.get(task_id)
            if not task: return
            while task.get('active', True):
                word = task['words'][task['current_index']]
                await self.tg_client.send_message(task['chat_id'], f"<a href='tg://user?id={task['user_id']}'>{word}</a>", reply_to=task['reply_id'], parse_mode='html')
                task['current_index'] = (task['current_index'] + 1) % len(task['words']); await asyncio.sleep(task['interval'])
            if task_id in lesenka_tasks: lesenka_tasks.pop(task_id); await self.save_state()
        except Exception as e:
            print(f"Ошибка в лесенке {task_id}: {str(e)}")
            if task_id in lesenka_tasks: lesenka_tasks.pop(task_id); await self.save_state()
    async def offles_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            if msg.is_reply:
                reply_msg = await msg.get_reply_message(); user = await reply_msg.get_sender()
                chat_id = msg.chat_id; user_id = user.id
                task_id = f"lesenka_{chat_id}_{user_id}"
                if task_id in lesenka_tasks: lesenka_tasks[task_id]['active'] = False; lesenka_tasks.pop(task_id); await msg.edit(f"<b>⛧ Лесенка для {user_id} остановлена</b>", parse_mode='html'); await self.save_state()
                else: await msg.delete()
            else:
                stopped = 0
                for task_id in list(lesenka_tasks.keys()):
                    if lesenka_tasks[task_id].get('chat_id') == msg.chat_id: lesenka_tasks[task_id]['active'] = False; lesenka_tasks.pop(task_id); stopped += 1
                if stopped > 0: await msg.edit(f"<b>⛧ Остановлено {stopped} лесенок в этом чате</b>", parse_mode='html'); await self.save_state()
                else: await msg.delete()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .offles: {str(e)}</b>")
    async def type_handler(self, event):
        msg = event.message
        global type_active, type_speed
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if args:
                try: type_speed = float(args.split()[0])
                except ValueError: await msg.edit("<b>⛧ Неверная скорость</b>", parse_mode='html'); return
            if not type_shablon: await msg.edit("<b>⛧ Нет шаблонов</b>", parse_mode='html'); return
            type_active = True; chat_id = msg.chat_id; reply_id = msg.reply_to_msg_id if msg.is_reply else None
            await msg.delete()
            while type_active and type_shablon:
                for line in type_shablon:
                    if not type_active: break
                    if line.strip(): await self.tg_client.send_message(chat_id, line, reply_to=reply_id); await asyncio.sleep(1.0 / type_speed)
        except Exception as e: await self.send_to_saved(f"<b>⛧ Ошибка в .type: {str(e)}</b>")
    async def stoptype_handler(self, event):
        msg = event.message
        global type_active
        try:
            if not await self.is_owner(msg.sender_id): return
            type_active = False; await msg.edit("<b>⛧ Построчный вывод остановлен</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .stoptype: {str(e)}</b>")
    async def timer_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Формат: .timer количество интервал текст</b>", parse_mode='html'); return
            parts = args.split()
            if len(parts) < 3: await msg.edit("<b>⛧ Недостаточно аргументов</b>", parse_mode='html'); return
            try: count = int(parts[0]); interval_str = parts[1]; text = ' '.join(parts[2:])
            except: await msg.edit("<b>⛧ Неверный формат аргументов</b>", parse_mode='html'); return
            interval = await self.parse_time(interval_str)
            chat_id = msg.chat_id; reply_id = msg.reply_to_msg_id if msg.is_reply else None
            task_id = f"timer_{chat_id}_{int(time.time())}"
            timer_tasks[task_id] = {'chat_id':chat_id,'count':count,'interval':interval,'text':text,'reply_id':reply_id,'active':True,'start_time':time.time()}
            await msg.edit(f"<b>⛧ Таймер запущен | стоп: .stoptimer {task_id}</b>", parse_mode='html')
            asyncio.create_task(self.run_timer_task(task_id)); await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .timer: {str(e)}</b>")
    async def run_timer_task(self, task_id):
        try:
            task = timer_tasks.get(task_id)
            if not task: return
            chat_id = task['chat_id']; count = task['count']; interval = task['interval']; text = task['text']; reply_id = task['reply_id']
            for i in range(count):
                task = timer_tasks.get(task_id)
                if not task or not task.get('active', False): break
                await self.tg_client.send_message(chat_id, text, reply_to=reply_id)
                if i < count - 1: await asyncio.sleep(interval)
            if task_id in timer_tasks: timer_tasks.pop(task_id); await self.save_state(); await self.send_to_saved(f"<b>⛧ Таймер {task_id} завершён</b>\nЧат: {chat_id}\nСообщений: {count}\nТекст: {text}")
        except Exception as e:
            print(f"Ошибка в таймере {task_id}: {str(e)}")
            if task_id in timer_tasks: timer_tasks.pop(task_id); await self.save_state()
    async def stoptimer_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args:
                if not timer_tasks: await msg.edit("<b>⛧ Нет активных таймеров</b>", parse_mode='html'); return
                tasks_list = []
                for task_id, task in timer_tasks.items():
                    elapsed = int(time.time() - task['start_time'])
                    tasks_list.append(f"ID: {task_id}\n   {task['count']} сообщ. | {task['interval']} сек | Работает: {elapsed} сек")
                await msg.edit("<b>⛧ Активные таймеры:</b>\n\n" + "\n".join(tasks_list) + "\n\nДля остановки: .stoptimer ID", parse_mode='html'); return
            task_id = args.split()[0]
            if task_id in timer_tasks: timer_tasks[task_id]['active'] = False; timer_tasks.pop(task_id); await msg.edit(f"<b>⛧ Таймер {task_id} остановлен</b>", parse_mode='html'); await self.save_state()
            else: await msg.edit(f"<b>⛧ Таймер {task_id} не найден</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .stoptimer: {str(e)}</b>")
    async def count_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Используйте: .count a или .count b</b>", parse_mode='html'); return
            if args.lower() not in ['a','b']: await msg.edit("<b>⛧ Используйте: .count a или .count b</b>", parse_mode='html'); return
            if not msg.is_reply: await msg.edit("<b>⛧ Нужно ответить на сообщение</b>", parse_mode='html'); return
            reply_msg = await msg.get_reply_message(); point_type = args.lower()
            count_points[point_type] = {'chat_id':msg.chat_id,'message_id':reply_msg.id,'user_id':reply_msg.sender_id}
            await self.save_state(); await msg.edit(f"<b>⛧ Точка {point_type.upper()} установлена</b>", parse_mode='html')
            if count_points['a'] and count_points['b']:
                point_a = count_points['a']; point_b = count_points['b']
                if point_a['chat_id'] != point_b['chat_id']:
                    await msg.edit("<b>⛧ Точки должны быть в одном чате</b>", parse_mode='html'); count_points['a'] = None; count_points['b'] = None; await self.save_state(); return
                if point_a['user_id'] != point_b['user_id']:
                    await msg.edit("<b>⛧ Точки должны быть от одного пользователя</b>", parse_mode='html'); count_points['a'] = None; count_points['b'] = None; await self.save_state(); return
                await msg.edit("<b>⛧ Анализирую...</b>", parse_mode='html')
                msg_a = await self.tg_client.get_messages(point_a['chat_id'], ids=point_a['message_id'])
                msg_b = await self.tg_client.get_messages(point_b['chat_id'], ids=point_b['message_id'])
                if not msg_a or not msg_b:
                    await msg.edit("<b>⛧ Не удалось найти сообщения</b>", parse_mode='html'); count_points['a'] = None; count_points['b'] = None; await self.save_state(); return
                if msg_a.date < msg_b.date: start_msg, end_msg = msg_a, msg_b
                else: start_msg, end_msg = msg_b, msg_a
                all_text = ""; message_count = 0
                if start_msg.text: all_text += start_msg.text + "\n"; message_count += 1
                if end_msg.id != start_msg.id and end_msg.text: all_text += end_msg.text + "\n"; message_count += 1
                async for message in self.tg_client.iter_messages(point_a['chat_id'], min_id=start_msg.id-1, max_id=end_msg.id+1, from_user=point_a['user_id']):
                    if message.id == start_msg.id or message.id == end_msg.id: continue
                    if message.text:
                        words = len(message.text.split())
                        if words >= 50: all_text += message.text + "\n"; message_count += 1
                if message_count == 0:
                    await msg.edit("<b>⛧ Нет сообщений для анализа</b>", parse_mode='html'); count_points['a'] = None; count_points['b'] = None; await self.save_state(); return
                total_words = len(all_text.split()); report = await self.analyze_text(all_text, total_words, message_count)
                file_content = report['full_report']; file_bytes = io.BytesIO(file_content.encode('utf-8'))
                file_name = f"analysis_{total_words}words_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt"
                await self.tg_client.send_file(msg.chat_id, file_bytes, caption=f"<b>⛧ Анализ завершён</b>\n<pre>{report['summary']}</pre>", parse_mode='html', attributes=[types.DocumentAttributeFilename(file_name)])
                await msg.delete(); count_points['a'] = None; count_points['b'] = None; await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .count: {str(e)}</b>")
    async def analyze_text(self, text, total_words, message_count):
        words = text.split(); unique_words = set(words); chars = len(text); sentences = len(re.split(r'[.!?]+', text))
        phrases = {}; words_list = text.lower().split()
        for i in range(len(words_list)):
            for j in range(i+2, min(i+8, len(words_list)+1)):
                phrase = ' '.join(words_list[i:j]); phrases[phrase] = phrases.get(phrase, 0) + 1
        repetitions = {p:c for p,c in phrases.items() if c >= 2}
        sorted_reps = sorted(repetitions.items(), key=lambda x: x[1], reverse=True)[:10]
        hidden_chars = []
        hidden_pattern = re.compile(r'[a-zA-Z]|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\u00ad\u200b-\u200f\u2028-\u202f\u205f-\u206f\ufeff]')
        for match in hidden_pattern.finditer(text):
            char = match.group(); pos = match.start(); start = max(0, pos-30); end = min(len(text), pos+30)
            fragment = text[start:end].replace('\n',' ').replace('\r','')
            if ord(char) < 32 or ord(char) in [0x200B,0xFEFF,0x00AD,0x200C,0x200D,0x200E,0x200F]: desc = f"Скрытый символ (U+{ord(char):04X})"
            else: desc = f"Английская буква '{char}'"
            hidden_chars.append({'desc':desc,'fragment':fragment})
        homoglyphs = []; lines = text.split('\n')
        for line in lines:
            if not line.strip(): continue
            found_replacements = []
            for char in line:
                if char in CYRILLIC_TO_LATIN_MAP: found_replacements.append(f"{char}→{CYRILLIC_TO_LATIN_MAP[char]}")
            if found_replacements: homoglyphs.append({'line':line[:200],'replacements':', '.join(found_replacements)})
        mentions = []
        mention_keywords = ['лс','личку','личке','лички','личная','конфа','конфу','конфе','сронф','элэс']
        text_lower = text.lower()
        for kw in mention_keywords:
            for match in re.finditer(kw, text_lower):
                pos = match.start(); start = max(0, pos-30); end = min(len(text), pos+30)
                fragment = text[start:end].replace('\n',' '); mentions.append({'word':kw,'fragment':fragment})
        full_report = f"""=== АНАЛИЗ ТЕКСТА ===
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

СТАТИСТИКА:
- Сообщений: {message_count}
- Всего слов: {total_words}
- Уникальных слов: {len(unique_words)}
- Всего символов: {chars}
- Всего предложений: {sentences}

ПОВТОРЕНИЯ ФРАЗ:
"""
        if sorted_reps:
            for phrase, count in sorted_reps: full_report += f"- \"{phrase}\" (x{count})\n"
        else: full_report += "- Нет повторений\n"
        full_report += "\nСКРЫТЫЕ СИМВОЛЫ:\n"
        if hidden_chars:
            for h in hidden_chars[:20]: full_report += f"- {h['desc']}\n  Фрагмент: ...{h['fragment']}...\n"
        else: full_report += "- Не найдено\n"
        full_report += "\nЗАМЕНА КИРИЛЛИЦЫ:\n"
        if homoglyphs:
            for h in homoglyphs[:20]: full_report += f"- \"{h['line']}\"\n  Замены: {h['replacements']}\n"
        else: full_report += "- Не найдено\n"
        full_report += "\nУПОМИНАНИЯ:\n"
        if mentions:
            for m in mentions[:20]: full_report += f"- \"{m['word']}\"\n  Фрагмент: ...{m['fragment']}...\n"
        else: full_report += "- Не найдено\n"
        summary = f"Сообщений: {message_count}\nВсего слов: {total_words}\nПовторений: {len(sorted_reps)}\nСкрытий: {len(hidden_chars)}\nЗамен: {len(homoglyphs)}\nУпоминаний: {len(mentions)}"
        return {'full_report':full_report,'summary':summary}
    async def mystats_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Используйте: .mystats число период</b>\nПериоды: час, день, месяц, год", parse_mode='html'); return
            parts = args.split()
            if len(parts) < 2: await msg.edit("<b>⛧ Укажите число и период</b>", parse_mode='html'); return
            try: num = int(parts[0])
            except: await msg.edit("<b>⛧ Неверное число</b>", parse_mode='html'); return
            period_str = ' '.join(parts[1:]); period_sec = await self.parse_period(period_str)
            if not period_sec: await msg.edit("<b>⛧ Неверный период. Используйте: час, день, месяц, год</b>", parse_mode='html'); return
            total_sec = num * period_sec; await msg.edit("<b>⛧ Считаю статистику...</b>", parse_mode='html')
            me = await self.tg_client.get_me(); cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(seconds=total_sec)
            total_messages = 0; total_words = 0; total_chars = 0
            async for dialog in self.tg_client.iter_dialogs():
                try:
                    async for message in self.tg_client.iter_messages(dialog.id, from_user=me.id, limit=None):
                        if message.date.replace(tzinfo=None) < cutoff_date: break
                        if message.text: total_messages += 1; total_words += len(message.text.split()); total_chars += len(message.text)
                except: continue
            days = total_sec / 86400; avg_per_day = round(total_messages / days, 1) if days > 0 else 0
            await msg.edit(f"<b>⛧ Статистика за {num} {period_str}</b>\n<pre>Сообщений: {total_messages}\nСлов: {total_words}\nСимволов: {total_chars}\nСреднее в день: {avg_per_day}</pre>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .mystats: {str(e)}</b>")
    async def price_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            text = """<b>⛧ Прайс</b>
<pre>Услуга: Trolling Bot
Цена: 200₽ Crypto, NFT, Stars
Срок: месяц
Контакты: @xolizm</pre>"""
            await msg.edit(text, parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .price: {str(e)}</b>")
    async def ad_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global shablon
            args = await self.get_args(msg)
            if not args:
                if msg.is_reply:
                    reply_msg = await msg.get_reply_message()
                    if reply_msg.text: shablon.append(reply_msg.text.strip()); await msg.edit(f"<b>⛧ Добавлено в шаблоны! Всего: {len(shablon)}</b>", parse_mode='html'); await self.save_state()
                    else: await msg.edit("<b>⛧ В сообщении нет текста</b>", parse_mode='html')
                else: await msg.edit("<b>⛧ Используйте: .ad + реплай на текст</b>", parse_mode='html')
                return
            parts = args.split()
            if parts[0] == 'del':
                if len(parts) > 1:
                    try:
                        idx = int(parts[1]) - 1
                        if 0 <= idx < len(shablon): deleted = shablon.pop(idx); await msg.edit(f"<b>⛧ Шаблон удалён: {deleted[:50]}...</b>", parse_mode='html'); await self.save_state()
                        else: await msg.edit(f"<b>⛧ Неверный индекс. Всего шаблонов: {len(shablon)}</b>", parse_mode='html')
                    except: await msg.edit("<b>⛧ Неверный индекс</b>", parse_mode='html')
                else: await msg.edit("<b>⛧ Укажите номер для удаления: .ad del 5</b>", parse_mode='html')
            elif parts[0] == 'show':
                if shablon: show_text = "\n".join([f"{i+1}. {t[:100]}" for i, t in enumerate(shablon[:20])]); await msg.edit(f"<b>⛧ Шаблоны (первые 20):</b>\n<pre>{show_text}</pre>", parse_mode='html')
                else: await msg.edit("<b>⛧ Шаблоны пусты</b>", parse_mode='html')
            else: await msg.edit("<b>⛧ Используйте: .ad del/show или .ad + реплай</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .ad: {str(e)}</b>")
    async def x0_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if args:
                if not msg.is_reply: await msg.edit("<b>⛧ Нужно ответить на сообщение с медиа</b>", parse_mode='html'); return
                reply_msg = await msg.get_reply_message()
                if not reply_msg.media: await msg.edit("<b>⛧ В сообщении нет медиа</b>", parse_mode='html'); return
                name = args.split()[0]; file_ext = get_file_extension(reply_msg)
                if name.isdigit(): file_path = os.path.join(MEDIA_DIR, f"media_{name}{file_ext}")
                else:
                    for ext in ['.jpg','.png','.gif','.mp4','.mp3','.ogg','.webp']:
                        old_path = os.path.join(MEDIA_DIR, f"{name}{ext}")
                        if os.path.exists(old_path): os.remove(old_path)
                    file_path = os.path.join(MEDIA_DIR, f"{name}{file_ext}")
                await reply_msg.download_media(file=file_path); await msg.edit(f"<b>⛧ Медиа сохранено как {name}</b>", parse_mode='html'); return
            if not msg.is_reply: await msg.edit("<b>⛧ Нужно ответить на сообщение с медиа</b>", parse_mode='html'); return
            reply_msg = await msg.get_reply_message()
            if not reply_msg.media: await msg.edit("<b>⛧ В сообщении нет медиа</b>", parse_mode='html'); return
            temp_path = os.path.join(DATA_DIR, f"temp_{int(time.time())}.tmp")
            try:
                media_data = await self.tg_client.download_media(reply_msg, file=bytes)
                if not media_data: await msg.edit("<b>⛧ Не удалось скачать медиа</b>", parse_mode='html'); return
                with open(temp_path, 'wb') as f: f.write(media_data)
                url = await upload_to_catbox(temp_path); service = "catbox.moe"
                if not url: url = await upload_to_fileio(temp_path); service = "file.io"
                if not url: url = await upload_to_telegraph(temp_path); service = "telegra.ph"
                if not url: url = await upload_to_x0(temp_path); service = "x0.at"
                if url: await msg.edit(f"<b>⛧ Медиа загружено на {service}</b>\n<code>{url}</code>", parse_mode='html')
                else: await msg.edit("<b>⛧ Не удалось загрузить медиа</b>", parse_mode='html')
            finally:
                if os.path.exists(temp_path): os.remove(temp_path)
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .x0: {str(e)}</b>")
    async def shabl_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            if not msg.is_reply: await msg.edit("<b>⛧ Нужно ответить на сообщение с текстом</b>", parse_mode='html'); return
            replied_msg = await msg.get_reply_message()
            raw_text = replied_msg.raw_text or replied_msg.message or ""
            lines = raw_text.strip().split('\n')
            search_lines = []
            for line in lines[:2]:
                clean = line.strip()
                if clean: search_lines.append(clean)
            if not search_lines: await msg.edit("<b>⛧ В сообщении нет текста</b>", parse_mode='html'); return
            search_text = '\n'.join(search_lines)
            await msg.edit(f"<b>⛧ Ищу 2 строки...</b>\n<pre>{search_text[:100]}</pre>", parse_mode='html')
            found_count, results = 0, []
            chats_to_search = repo_chats if repo_chats else []
            if not chats_to_search:
                async for dialog in self.tg_client.iter_dialogs():
                    if dialog.is_group or dialog.is_channel: chats_to_search.append(dialog.id)
            for chat_id in chats_to_search:
                try:
                    async for message in self.tg_client.iter_messages(chat_id, search=search_lines[0], limit=100):
                        if message.text:
                            msg_lines = message.text.strip().split('\n')
                            msg_first_lines = [l.strip() for l in msg_lines[:2] if l.strip()]
                            msg_search = '\n'.join(msg_first_lines)
                            if msg_search == search_text:
                                found_count += 1
                                try:
                                    chat_entity = await self.tg_client.get_entity(chat_id)
                                    if hasattr(chat_entity,'username') and chat_entity.username: link = f"https://t.me/{chat_entity.username}/{message.id}"
                                    else:
                                        chat_id_str = str(chat_id)
                                        if chat_id_str.startswith('-100'): chat_id_str = chat_id_str[4:]
                                        elif chat_id_str.startswith('-'): chat_id_str = chat_id_str[1:]
                                        link = f"https://t.me/c/{chat_id_str}/{message.id}"
                                    results.append(f"{found_count}. {link}")
                                except: results.append(f"{found_count}. чат {chat_id}")
                                if found_count >= 20: break
                    if found_count >= 20: break
                except: continue
            if not results: await msg.edit("<b>⛧ Совпадений не найдено</b>", parse_mode='html')
            else: await msg.edit(f"<b>⛧ Найдено: {found_count}</b>\n\n" + "\n".join(results), parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .shabl: {str(e)}</b>")
    async def cmd_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            chat_id = msg.chat_id; me = await self.tg_client.get_me(); usernames = await get_all_usernames(self.tg_client, me)
            if args and args.strip() == '2': await msg.edit(menu2text, parse_mode='html')
            elif args and args.strip() == '3': await msg.edit(menu3text, parse_mode='html')
            else: await msg.edit(menutext.format(chat_id, me.id, me.first_name, usernames), parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .cmd: {str(e)}</b>")
    async def stop_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global spam_state
            args = await self.get_args(msg)
            chat_id = int(args.split()[0]) if args else msg.chat_id
            if chat_id in spam_state: spam_state[chat_id] = False; await msg.edit(f"<b>⛧ Спам остановлен в чате {chat_id}</b>", parse_mode='html'); await self.save_state()
            else: await msg.edit(f"<b>⛧ Чат {chat_id} не найден</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .stop: {str(e)}</b>")
    async def pstop_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global spam_state1
            args = await self.get_args(msg)
            chat_id = int(args.split()[0]) if args else msg.chat_id
            if chat_id in spam_state1: spam_state1[chat_id] = False; await msg.edit(f"<b>⛧ Спам остановлен в чате {chat_id}</b>", parse_mode='html'); await self.save_state()
            else: await msg.edit(f"<b>⛧ Чат {chat_id} не найден</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .pstop: {str(e)}</b>")
    async def off_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global tagger_chats
            args = await self.get_args(msg)
            chat_id = int(args.split()[0]) if args else msg.chat_id
            if chat_id in tagger_chats: tagger_chats.pop(chat_id); await msg.edit(f"<b>⛧ Теггер остановлен в чате {chat_id}</b>", parse_mode='html'); await self.save_state()
            else: await msg.edit(f"<b>⛧ Чат {chat_id} не найден</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .off: {str(e)}</b>")
    async def goff_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global tag_chats
            args = await self.get_args(msg)
            chat_id = int(args.split()[0]) if args else msg.chat_id
            if chat_id in tag_chats: tag_chats.pop(chat_id); await msg.edit(f"<b>⛧ Теггер остановлен в чате {chat_id}</b>", parse_mode='html'); await self.save_state()
            else: await msg.edit(f"<b>⛧ Чат {chat_id} не найден</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .goff: {str(e)}</b>")
    async def ddk_handler(self, event):
        msg = event.message
        try:
            if not await self.is_owner(msg.sender_id): return
            global spam_state, spam_state1, tagger_chats, tag_chats, timer_tasks, lesenka_tasks, cal_tasks, type_active
            spam_state.clear(); spam_state1.clear(); tagger_chats.clear(); tag_chats.clear(); timer_tasks.clear(); lesenka_tasks.clear(); type_active = False
            for task_id in list(cal_tasks.keys()): cal_tasks[task_id]['active'] = False; del cal_tasks[task_id]
            await msg.edit("<b>⛧ Все задачи остановлены</b>", parse_mode='html'); await self.save_state()
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .ddk: {str(e)}</b>")
    async def shrift_handler(self, event):
        msg = event.message
        global shrift_mode
        try:
            if not await self.is_owner(msg.sender_id): return
            args = await self.get_args(msg)
            if not args: await msg.edit("<b>⛧ Выберите шрифт:</b>\n<code>.shrift 0</code> - обычный\n<code>.shrift 1</code> - зачеркнутый\n<code>.shrift 2</code> - жирный\n<code>.shrift 3</code> - курсив\n<code>.shrift 4</code> - моноширинный\n<code>.shrift 5</code> - подчёркнутый\n<code>.shrift 6</code> - цитата (код)\n<code>.shrift 7</code> - спойлер", parse_mode='html'); return
            try:
                mode = int(args.split()[0])
                if 0 <= mode <= 7: shrift_mode = mode; modes = ["обычный","зачеркнутый","жирный","курсив","моноширинный","подчёркнутый","цитата","спойлер"]; await msg.edit(f"<b>⛧ Шрифт изменен на: {modes[mode]}</b>", parse_mode='html')
                else: await msg.edit("<b>⛧ Используйте цифры от 0 до 7</b>", parse_mode='html')
            except ValueError: await msg.edit("<b>⛧ Неверный формат</b>", parse_mode='html')
        except Exception as e:
            await msg.delete()
            await self.send_to_saved(f"<b>⛧ Ошибка в .shrift: {str(e)}</b>")
    async def watcher(self, event):
        msg = event.message
        global afk_state, afk_users, afk_start_time, afk_reason, afk_photo, autoreply_list, autoreply_time, last_reply_time, autoreply_shpk, autoreply_photo, autoreply_cd
        try:
            me = await self.tg_client.get_me()
            if msg.sender_id == me.id: return
            my_usernames = []
            if me.username: my_usernames.append(f"@{me.username.lower()}")
            if hasattr(me,'usernames') and me.usernames:
                for un in me.usernames:
                    if hasattr(un,'username') and un.username: my_usernames.append(f"@{un.username.lower()}")
            if afk_state:
                should_reply = False
                if msg.is_private: should_reply = True
                elif msg.text:
                    text_lower = msg.text.lower()
                    for un in my_usernames:
                        if un in text_lower: should_reply = True; break
                    if msg.is_reply:
                        reply_msg = await msg.get_reply_message()
                        if reply_msg and reply_msg.sender_id == me.id: should_reply = True
                if should_reply and msg.sender_id not in afk_users:
                    afk_users.append(msg.sender_id)
                    if afk_start_time: time_string = str(datetime.now() - afk_start_time).split('.')[0]
                    else: time_string = "неизвестно"
                    reply_text = f"<b>⛧ Я в АФК уже {time_string}</b>\nПричина: {afk_reason}"
                    try:
                        if afk_photo and os.path.exists(afk_photo): await msg.reply(reply_text, file=afk_photo, parse_mode='html')
                        elif afk_photo and afk_photo.startswith('http'): await msg.reply(reply_text, file=afk_photo, parse_mode='html')
                        else: await msg.reply(reply_text, parse_mode='html')
                    except: await msg.reply(reply_text, parse_mode='html')
            if msg.sender_id in autoreply_list:
                current_time = time.time(); last_reply = last_reply_time.get(msg.sender_id, 0)
                delay = autoreply_time.get(msg.sender_id, 0); cd = autoreply_cd.get(msg.sender_id, 0)
                if cd > 0:
                    time_since_last = current_time - last_reply
                    if time_since_last < cd: return
                if current_time - last_reply >= delay:
                    last_reply_time[msg.sender_id] = current_time; await asyncio.sleep(delay)
                    caption = (autoreply_shpk.get(msg.sender_id,'') + " " + get_next_template(f"reply_{msg.sender_id}")) if autoreply_shpk.get(msg.sender_id) else get_next_template(f"reply_{msg.sender_id}")
                    media_name = autoreply_photo.get(msg.sender_id)
                    media_file = await self.find_media_by_name(str(media_name)) if media_name else None
                    try:
                        if media_file and os.path.exists(media_file): await msg.reply(caption, file=media_file, parse_mode='html')
                        elif media_name and media_name.startswith('http'): await msg.reply(caption, file=media_name, parse_mode='html')
                        else: await msg.reply(caption, parse_mode='html')
                    except: await msg.reply(caption, parse_mode='html')
        except Exception as e: print(f"Ошибка в watcher: {e}")
    async def message_watcher(self, event):
        try:
            global muted_users
            if not muted_users: return
            if event.sender_id in muted_users:
                try: await event.delete()
                except: pass
        except Exception as e: print(f"Ошибка в message_watcher: {str(e)}")
    async def disconnect(self):
        if self.tg_client.is_connected(): await self.tg_client.disconnect()
    async def cleanup(self):
        global spam_state, spam_state1, tagger_chats, tag_chats, type_active, timer_tasks, lesenka_tasks, cal_tasks
        spam_state.clear(); spam_state1.clear(); tagger_chats.clear(); tag_chats.clear(); type_active = False; timer_tasks.clear(); lesenka_tasks.clear()
        for task_id in list(cal_tasks.keys()): cal_tasks[task_id]['active'] = False; del cal_tasks[task_id]
        await self.save_state(); await self.disconnect()
    def run(self):
        async def main():
            try:
                print("Запуск бота...")
                print(f"Используется номер: {self.phone}")
                if os.path.exists('Grandeur.session'):
                    print("Пытаемся подключиться с существующей сессией...")
                    await self.tg_client.start(phone=lambda: self.phone)
                    if not await self.check_authorization(): print("Ошибка: не удалось проверить авторизацию!"); await self.tg_client.disconnect(); return
                else:
                    print("Создаем новую сессию...")
                    await self.tg_client.start(phone=lambda: self.phone, code_callback=lambda: input('Введите код из Telegram: '), password=lambda: getpass.getpass('Введите пароль (если есть): '))
                    if not await self.check_authorization(): print("Ошибка: не удалось проверить авторизацию!"); await self.tg_client.disconnect(); return
                print("Бот успешно авторизован и запущен")
                self._running = True
                self.tg_client.add_event_handler(self.help_handler, events.NewMessage(pattern=r'\.help'))
                self.tg_client.add_event_handler(self.uptime_handler, events.NewMessage(pattern=r'\.uptime'))
                self.tg_client.add_event_handler(self.ping_handler, events.NewMessage(pattern=r'\.ping'))
                self.tg_client.add_event_handler(self.reg_handler, events.NewMessage(pattern=r'\.reg'))
                self.tg_client.add_event_handler(self.trans_handler, events.NewMessage(pattern=r'\.trans'))
                self.tg_client.add_event_handler(self.rus_handler, events.NewMessage(pattern=r'\.rus'))
                self.tg_client.add_event_handler(self.calculator_handler, events.NewMessage(pattern=r'\.calculator'))
                self.tg_client.add_event_handler(self.auto_handler, events.NewMessage(pattern=r'\.auto'))
                self.tg_client.add_event_handler(self.gif_handler, events.NewMessage(pattern=r'\.gif'))
                self.tg_client.add_event_handler(self.id_handler, events.NewMessage(pattern=r'\.id'))
                self.tg_client.add_event_handler(self.addras_handler, events.NewMessage(pattern=r'\.addras'))
                self.tg_client.add_event_handler(self.delras_handler, events.NewMessage(pattern=r'\.delras'))
                self.tg_client.add_event_handler(self.addrepo_handler, events.NewMessage(pattern=r'\.addrepo'))
                self.tg_client.add_event_handler(self.delrepo_handler, events.NewMessage(pattern=r'\.delrepo'))
                self.tg_client.add_event_handler(self.chats_handler, events.NewMessage(pattern=r'\.chats'))
                self.tg_client.add_event_handler(self.msdel_handler, events.NewMessage(pattern=r'\.msdel'))
                self.tg_client.add_event_handler(self.delete_handler, events.NewMessage(pattern=r'\.delete'))
                self.tg_client.add_event_handler(self.deleteall_handler, events.NewMessage(pattern=r'\.deleteall'))
                self.tg_client.add_event_handler(self.offl_handler, events.NewMessage(pattern=r'\.offl'))
                self.tg_client.add_event_handler(self.mute_handler, events.NewMessage(pattern=r'\.mute'))
                self.tg_client.add_event_handler(self.mutestop_handler, events.NewMessage(pattern=r'\.mutstop'))
                self.tg_client.add_event_handler(self.set_handler, events.NewMessage(pattern=r'\.set'))
                self.tg_client.add_event_handler(self.set2_handler, events.NewMessage(pattern=r'\.set2'))
                self.tg_client.add_event_handler(self.file_handler, events.NewMessage(pattern=r'\.file'))
                self.tg_client.add_event_handler(self.list_handler, events.NewMessage(pattern=r'\.list'))
                self.tg_client.add_event_handler(self.ras_handler, events.NewMessage(pattern=r'\.ras'))
                self.tg_client.add_event_handler(self.afk_handler, events.NewMessage(pattern=r'\.afk'))
                self.tg_client.add_event_handler(self.spam_handler, events.NewMessage(pattern=r'\.spam'))
                self.tg_client.add_event_handler(self.psp_handler, events.NewMessage(pattern=r'\.psp'))
                self.tg_client.add_event_handler(self.tag_handler, events.NewMessage(pattern=r'\.tag'))
                self.tg_client.add_event_handler(self.rem_handler, events.NewMessage(pattern=r'\.rem'))
                self.tg_client.add_event_handler(self.cal_handler, events.NewMessage(pattern=r'\.cal'))
                self.tg_client.add_event_handler(self.stopcal_handler, events.NewMessage(pattern=r'\.stopcal'))
                self.tg_client.add_event_handler(self.reply_handler, events.NewMessage(pattern=r'^\.reply\b'))
                self.tg_client.add_event_handler(self.l_handler, events.NewMessage(pattern=r'^\.l\b'))
                self.tg_client.add_event_handler(self.pset_handler, events.NewMessage(pattern=r'\.pset'))
                self.tg_client.add_event_handler(self.lesenka_handler, events.NewMessage(pattern=r'\.lesenka'))
                self.tg_client.add_event_handler(self.offles_handler, events.NewMessage(pattern=r'\.offles'))
                self.tg_client.add_event_handler(self.type_handler, events.NewMessage(pattern=r'\.type'))
                self.tg_client.add_event_handler(self.stoptype_handler, events.NewMessage(pattern=r'\.stoptype'))
                self.tg_client.add_event_handler(self.timer_handler, events.NewMessage(pattern=r'\.timer'))
                self.tg_client.add_event_handler(self.stoptimer_handler, events.NewMessage(pattern=r'\.stoptimer'))
                self.tg_client.add_event_handler(self.count_handler, events.NewMessage(pattern=r'\.count'))
                self.tg_client.add_event_handler(self.mystats_handler, events.NewMessage(pattern=r'\.mystats'))
                self.tg_client.add_event_handler(self.price_handler, events.NewMessage(pattern=r'\.price'))
                self.tg_client.add_event_handler(self.ad_handler, events.NewMessage(pattern=r'\.ad'))
                self.tg_client.add_event_handler(self.x0_handler, events.NewMessage(pattern=r'\.x0'))
                self.tg_client.add_event_handler(self.shabl_handler, events.NewMessage(pattern=r'\.shabl'))
                self.tg_client.add_event_handler(self.cmd_handler, events.NewMessage(pattern=r'\.cmd'))
                self.tg_client.add_event_handler(self.stop_handler, events.NewMessage(pattern=r'\.stop'))
                self.tg_client.add_event_handler(self.pstop_handler, events.NewMessage(pattern=r'\.pstop'))
                self.tg_client.add_event_handler(self.off_handler, events.NewMessage(pattern=r'\.off'))
                self.tg_client.add_event_handler(self.goff_handler, events.NewMessage(pattern=r'\.goff'))
                self.tg_client.add_event_handler(self.ddk_handler, events.NewMessage(pattern=r'\.ddk'))
                self.tg_client.add_event_handler(self.shrift_handler, events.NewMessage(pattern=r'\.shrift'))
                self.tg_client.add_event_handler(self.status_handler, events.NewMessage(pattern=r'\.status'))
                self.tg_client.add_event_handler(self.whois_handler, events.NewMessage(pattern=r'\.whois'))
                self.tg_client.add_event_handler(self.addcontacts_handler, events.NewMessage(pattern=r'\.addcontacts'))
                self.tg_client.add_event_handler(self.profilesave_handler, events.NewMessage(pattern=r'\.profilesave'))
                self.tg_client.add_event_handler(self.profileset_handler, events.NewMessage(pattern=r'\.profileset'))
                self.tg_client.add_event_handler(self.profilelist_handler, events.NewMessage(pattern=r'\.profilelist'))
                self.tg_client.add_event_handler(self.profiledel_handler, events.NewMessage(pattern=r'\.profiledel'))
                self.tg_client.add_event_handler(self.top_handler, events.NewMessage(pattern=r'\.top'))
                self.tg_client.add_event_handler(self.topwords_handler, events.NewMessage(pattern=r'\.topwords'))
                self.tg_client.add_event_handler(self.hack_handler, events.NewMessage(pattern=r'\.hack'))
                self.tg_client.add_event_handler(self.reverse_handler, events.NewMessage(pattern=r'\.reverse'))
                self.tg_client.add_event_handler(self.ss_handler, events.NewMessage(pattern=r'\.ss'))
                self.tg_client.add_event_handler(self.movie_handler, events.NewMessage(pattern=r'\.movie'))
                self.tg_client.add_event_handler(self.watcher, events.NewMessage())
                self.tg_client.add_event_handler(self.message_watcher, events.NewMessage())
                print("=== Запущен обработчик команд ===")
                print("Скрипт запущен и ожидает команды. (Нажмите Ctrl+C для выхода)")
                await self.tg_client.run_until_disconnected()
            except Exception as e: print(f"Ошибка при запуске: {e}")
            finally: self._running = False; await self.cleanup()
        if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        try: loop.run_until_complete(main())
        except KeyboardInterrupt: print("\nБот останавливается...")
        except Exception as e: print(f"Неожиданная ошибка: {e}")
        finally:
            pending = asyncio.all_tasks(loop=loop)
            for task in pending: task.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens()); loop.close()
if __name__ == "__main__":
    bot = Userbot(); bot.run()
