import os
import json
import logging
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
import base64
import re
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode

# Constants
USER_ROLES_FILE = 'user_roles.json'
USER_DEFAULT_ROLES_FILE = 'user_default_roles.json'
AUTHORIZED_USERS_FILE = 'authorized_users.json'
MAX_IMAGE_SIZE = (128, 128)  # (width, height)
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MAX_HISTORY_LENGTH = 5  # Maximum number of message contexts
MAX_IMAGE_REQUESTS_PER_HOUR = 2  # Maximum number of image requests per hour
HISTORY_DIR = 'History'
IMAGES_DIR = 'Images'

# Logger settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creating folders (Need to fix)
def create_dirs():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
 
 # Saving message history
def save_message_history(user_id, role, user_message, bot_message=None):
    history_file = os.path.join(HISTORY_DIR, f'{user_id}_history.txt')
    with open(history_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {role}:\n{user_message}\n")
        if bot_message:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Assistant:\n{bot_message}\n")
        f.write("\n")
        
# Markdown for telegram
def escape_markdown(text: str) -> str:
    escape_chars = r'[_*~|]'
    return re.sub(r'([_*~|])', r'\\\1', text)

# Loading config
def load_config(config_file):
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

# Loading user roles
def load_user_roles():
    if os.path.exists(USER_ROLES_FILE):
        try:
            with open(USER_ROLES_FILE, 'r', encoding='utf-8') as f:
                roles = json.load(f)
                return roles
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in a file {USER_ROLES_FILE}: {e}")
            return {}
    else:
        with open(USER_ROLES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        logger.info(f"File {USER_ROLES_FILE} created.")
        return {}
    
# Loading user default roles
def load_user_default_roles():
    if os.path.exists(USER_DEFAULT_ROLES_FILE):
        try:
            with open(USER_DEFAULT_ROLES_FILE, 'r', encoding='utf-8') as f:
                roles = json.load(f)
                return roles
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in a file {USER_DEFAULT_ROLES_FILE}: {e}")
            return {}
    else:
        with open(USER_DEFAULT_ROLES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        logger.info(f"File {USER_DEFAULT_ROLES_FILE} created.")
        return {}

# Save user default roles
def save_user_default_roles(roles):
    try:
        with open(USER_DEFAULT_ROLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(roles, f, ensure_ascii=False, indent=4)
        logger.info(f"User roles saved to {USER_DEFAULT_ROLES_FILE}")
    except (TypeError, IOError) as e:
        logger.error(f"Error saving roles in a {USER_DEFAULT_ROLES_FILE}: {e}")

# Save user roles
def save_user_roles(roles):
    try:
        with open(USER_ROLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(roles, f, ensure_ascii=False, indent=4)
    except (TypeError, IOError) as e:
        logger.error(f"Error saving roles in a {USER_ROLES_FILE}: {e}")

# Loading auth users
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        try:
            with open(AUTHORIZED_USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
                return users
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in a file {AUTHORIZED_USERS_FILE}: {e}")
            return set()
    else:
        with open(AUTHORIZED_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        logger.info(f"File {AUTHORIZED_USERS_FILE} created.")
        return set()

# Saving auth users
def save_authorized_users(users):
    try:
        with open(AUTHORIZED_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(users), f, ensure_ascii=False, indent=4)
    except (TypeError, IOError) as e:
        logger.error(f"Error saving auth users in a {AUTHORIZED_USERS_FILE}: {e}")

# Loading cfg
config = load_config('config.txt')

TELEGRAM_BOT_TOKEN = config.get('TELEGRAM_BOT_TOKEN')  # Telegram token
OPENAI_API_KEY = config.get('OPENAI_API_KEY')
SECRET_WORD = config.get('SECRET_WORD')
DEFAULT_ROLE = config.get('DEFAULT_ROLE')

user_roles = load_user_roles()
user_default_roles = load_user_default_roles()
authorized_users = set(load_authorized_users())

logger.info(f"User roles loaded: {user_roles}")
logger.info(f"Authorized users loaded: {authorized_users}")

# Keeping context and track image counter
message_histories = {}
image_request_counters = {}

# Check auth
def is_authorized(user_id: str) -> bool:
    return user_id in authorized_users

# Processing /start
async def start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)

    if is_authorized(user_id):
        await update.message.reply_text("You are already authorized and can use the bot.\nBut if you want to change your default role, please choose it below.")

    welcome_message = (
        "Text\n"

        "Text\n\n"
        
        "Text"
        
        "Text"
        "Text"
    )


    # Creating buttons
    keyboard = [
        [InlineKeyboardButton("Role 1", callback_data='Role1'),
            InlineKeyboardButton("Role 2", callback_data='Role2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Sending welcome message
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Logging for button pressed
    logger.info(f"Button pressed by user {user_id}, data: {query.data}")
    
    await query.answer()

    selected_role = query.data
    if selected_role == 'Role1':
        user_default_roles[user_id] = {'role': 'Role description'}
    elif selected_role == 'Role2':
        user_default_roles[user_id] = {'role': 'Role description'}

    save_user_default_roles(user_default_roles)
    logger.info(f"User {user_id} role set to {selected_role.replace('_', ' ').title()}")

    if is_authorized(user_id):
        await query.edit_message_text(text=f"You've choosed: {selected_role}.")
    else:
        await query.edit_message_text(text=f"You've choosed: {selected_role}.\n\nEnter the secret word:")

# Proccesing secret word
async def handle_start_secret_word(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if not is_authorized(user_id):
        user_input = update.message.text.strip()

        if user_input == SECRET_WORD:
            authorized_users.add(user_id)
            save_authorized_users(authorized_users)
            await update.message.reply_text("You have successfully authorized! Now you can use the bot.")
            logger.info(f"User {user_id} successfully authorized.")
        else:
            await update.message.reply_text("Incorrect secret word. Please try entering it again without any commands.")


# Processing /setrole
async def set_role(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    
    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized. Please start with the /start command.")
        return

    new_role_text = ' '.join(context.args)
    
    if new_role_text:
        user_roles[user_id] = {'role': new_role_text}
        save_user_roles(user_roles)
        escaped_role = escape_markdown(new_role_text)
        await update.message.reply_text(f'Your role has been changed to: {escaped_role}')
        logger.info(f"User {user_id} set a new role: {new_role_text}")
    else:
        await update.message.reply_text('Please specify a new role.')

# Processing /resetrole
async def reset_role(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)

    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized. Please start with the /start command.")
        return

    if user_id in user_roles:
        del user_roles[user_id]
        save_user_roles(user_roles)
        await update.message.reply_text(f'Your role has been reset to the default role: {user_default_roles.get(user_id, {})}')
        logger.info(f"User {user_id} reset their role to default.")
    else:
        await update.message.reply_text('Your role is already set to the default value.')

# Processing messages
async def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)

    if not is_authorized(user_id):
        user_input = update.message.text.strip()

        if user_input == SECRET_WORD:
            authorized_users.add(user_id)
            save_authorized_users(authorized_users)
            await update.message.reply_text("You have successfully authorized! Now you can use the bot. Type /help if you want to learn about the bot's full functionality.")
            logger.info(f"User {user_id} successfully authorized.")
        else:
            await update.message.reply_text("You are not authorized. Please start with the /start command.")
        return

    role_text = user_roles.get(user_id, {}).get('role', user_default_roles.get(user_id, {}).get('role', DEFAULT_ROLE))

    # Init user message history
    if user_id not in message_histories:
        message_histories[user_id] = []

    # Init image counter
    if user_id not in image_request_counters:
        image_request_counters[user_id] = []

    # Check limit image requests
    now = datetime.now()

    # Prune old image requests
    image_request_counters[user_id] = [timestamp for timestamp in image_request_counters[user_id] if now - timestamp < timedelta(hours=1)]

    logger.info(f"User {user_id} has {len(image_request_counters[user_id])} image requests in the last hour.")

    if update.message.photo:
        logger.info(f"Current image request count for user {user_id}: {len(image_request_counters[user_id])}. Limit: {MAX_IMAGE_REQUESTS_PER_HOUR}")

        if len(image_request_counters[user_id]) >= MAX_IMAGE_REQUESTS_PER_HOUR:
            next_allowed_time = image_request_counters[user_id][0] + timedelta(hours=1)
            remaining_time = next_allowed_time - now
            remaining_minutes = int(remaining_time.total_seconds() // 60)  # Left time to minutes convertation
            logger.warning(f"User {user_id} exceeded the image request limit. They can try again in {remaining_minutes} minutes.")

            await update.message.reply_text(
                f"{update.message.from_user.mention_html()}, You have exceeded the image request limit. ({MAX_IMAGE_REQUESTS_PER_HOUR} in hour). You send next image not before then {remaining_minutes} minutes.",
                parse_mode=ParseMode.HTML
            )
            return
        else:
            # Adding requset to list
            image_request_counters[user_id].append(now)
            logger.info(f"Image request for user {user_id} added at {now}. Total requests: {len(image_request_counters[user_id])}")

        # Get image and check format
        file = await update.message.photo[-1].get_file()
        file_name = file.file_path.split('/')[-1]
        if not file_name.lower().endswith(('png', 'jpg', 'jpeg')):
            await update.message.reply_text(f"{update.message.from_user.mention_html()}, please, send image in PNG or JPEG format.", parse_mode=ParseMode.HTML)
            return

        # Loading image and resampling it if needed
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(BytesIO(photo_bytes))

        if image.size[0] > MAX_IMAGE_SIZE[0] or image.size[1] > MAX_IMAGE_SIZE[1]:
            image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            logger.info(f"Image resized to {image.size}.")

        # Save user message for image in history
        user_message = update.message.caption
        
        # Image path for saving
        image_path = os.path.join(IMAGES_DIR, f'{user_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.jpg')

        # Saving image
        image.save(image_path, format="JPEG")  # Save in JPEG

        # Save image path in history
        save_message_history(user_id, "Image", f"Image saved in: {image_path}")
        
        # Encoding image to base64
        buffered = BytesIO()
        image.save(buffered, format=image.format)
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Add to context only text message
        if update.message.caption:
            text = update.message.caption
        else:
            text = "[User sent image without description]"

        message_histories[user_id].append({"role": "user", "content": text})

        if len(message_histories[user_id]) > MAX_HISTORY_LENGTH:
            message_histories[user_id] = message_histories[user_id][-MAX_HISTORY_LENGTH:]

        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": role_text}] + message_histories[user_id] + [
                {"role": "user", "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]}
            ]
        }
    else:
        # Adding message to history
        text = update.message.text
        
        # Save message to history
        user_message = update.message.text
        
        message_histories[user_id].append({"role": "user", "content": text})

        if len(message_histories[user_id]) > MAX_HISTORY_LENGTH:
            message_histories[user_id] = message_histories[user_id][-MAX_HISTORY_LENGTH:]

        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": role_text}] + message_histories[user_id]
        }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        bot_response = response_data['choices'][0]['message']['content']

        message_histories[user_id].append({"role": "assistant", "content": bot_response})
        if len(message_histories[user_id]) > MAX_HISTORY_LENGTH:
            message_histories[user_id] = message_histories[user_id][-MAX_HISTORY_LENGTH:]
        
        # Saving history to file
        save_message_history(user_id, role_text, user_message, bot_response)

        await update.message.reply_text(f"{update.message.from_user.mention_html()}, {bot_response}", parse_mode=ParseMode.HTML)
    else:
        logger.error(f"Failed to get response from OpenAI. Status code: {response.status_code}")
        await update.message.reply_text(f"{update.message.from_user.mention_html()}, failed to get response from OpenAI. Try later.", parse_mode=ParseMode.HTML)

# Processing /help
async def help_command(update: Update, context: CallbackContext):
    help_text = (
    "Help text" 
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# Main function for bot start
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))  
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler('setrole', set_role))
    application.add_handler(CommandHandler('resetrole', reset_role))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(CallbackQueryHandler(button))  # Button handler

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())