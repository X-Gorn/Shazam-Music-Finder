import os, requests, json
from xgorn_api import NoidAPI
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote

# Environments / Configs
API_HASH = os.environ['API_HASH']
APP_ID = int(os.environ['APP_ID'])
BOT_TOKEN = os.environ['BOT_TOKEN']
API_KEY = os.environ['API_KEY']
OWNER_ID = os.environ['OWNER_ID']

api = NoidAPI()

api.api_key = API_KEY

#Button
START_BUTTONS=[
    [
        InlineKeyboardButton('Source', url='https://github.com/X-Gorn/Shazam-Music-Finder'),
        InlineKeyboardButton('Rest API', url='https://api.xgorn.tech'),
    ],
    [InlineKeyboardButton('Author', url="https://t.me/xgorn")],
]


def shazam_music_finder(update):
    file = update.download()
    if update.audio:
        type_ = 'audio'
    if update.voice:
        type_ = 'audio'
    if update.video:
        type_ = 'video'
    js = api.music.shazam(file=file, type=type_)
    os.remove(file)
    if js['error']:
        return None, js['message']
    track = js['track']
    full_title = track['share']['subject']
    image = track['share']['image']
    text = f'`{full_title}`\n\n[Shazam!]({image})'
    reply_markup = [[InlineKeyboardButton('Google', url='https://www.google.com/search?q='+quote(full_title))]]
    for providers in track['hub']['providers']:
        if providers['type'] == 'SPOTIFY':
            for alt in providers['actions']:
                _, sp_one, sp_two = alt['uri'].split(':')
                url_ = f'https://open.spotify.com/{sp_one}/{sp_two}'
                reply_markup.append([InlineKeyboardButton(f'Spotify {sp_one}', url=url_)])
        elif providers['type'] == 'YOUTUBEMUSIC':
            for alt in providers['actions']:
                reply_markup.append([InlineKeyboardButton(f'YouTube Music', url=alt['uri'])])
    reply_markup = InlineKeyboardMarkup(reply_markup)
    return text, reply_markup


# Running bot
xbot = Client('Shazam-Music-Finder', api_id=APP_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Notify about bot start
with xbot:
    xbot_username = xbot.get_me().username  # Better call it global once due to telegram flood id
    print("Bot started!")
    xbot.send_message(int(OWNER_ID), "Bot started!")


# Start message
@xbot.on_message(filters.command('start') & filters.private)
async def _start(bot, update):
    await update.reply_text(
        f"I'm Shazam-Music-Finder!\nYou can share any telegram files and get the sharing link using this bot!\n\n/help for more details...",
        True, 
        reply_markup=InlineKeyboardMarkup(START_BUTTONS)
    )


# Handle audio and shazam it.
@xbot.on_message((filters.audio | filters.voice | filters.video) & filters.private)
async def _shazam(bot, update):
    await bot.send_chat_action(update.from_user.id, enums.ChatAction.TYPING)
    text, reply_markup = shazam_music_finder(update)
    if text:
        await update.reply(text, reply_markup=reply_markup)
    else:
        await update.reply(reply_markup)


xbot.run()