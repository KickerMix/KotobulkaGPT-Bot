## Telegram Bot with OpenAI Integration

This repository contains a Telegram bot implementation that integrates with OpenAI's GPT-4 model to provide a dynamic and interactive chat experience. The bot supports various functionalities including role management, message history tracking, image processing, and user authentication. 

### Features

- **Role Management**: Users can set and reset their roles. Roles are customizable and can be set to default values.
- **Image Processing**: Users can send images, which are resized to a maximum of 128x128 pixels. The bot handles PNG and JPEG formats, saves images, and maintains usage limits (maximum 2 requests per hour).
- **Message History**: Maintains a history of user and bot interactions, including image handling, for a rich contextual experience.
- **User Authentication**: Requires a secret word for users to gain authorization, ensuring only approved users can access the bot's features.
- **Interactive Commands**: Supports commands like `/start`, `/setrole`, `/resetrole`, and `/help` to interact with the bot.

### Getting Started

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/telegram-bot-openai.git
   ```

2. **Install Dependencies**

   Make sure to install the necessary Python packages. You can use `pip` for this:

   ```bash
   pip install python-telegram-bot requests pillow
   ```

3. **Configuration**

   Create a `config.txt` file in the root directory with the following entries:

   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   SECRET_WORD=your_secret_word
   DEFAULT_ROLE=default_role_description
   ```

   Replace the placeholder values with your actual Telegram bot token, OpenAI API key, secret word, and default role.

4. **Run the Bot**

   Execute the bot using Python:

   ```bash
   python bot.py
   ```

### File Structure

- `bot.py`: Main bot script.
- `user_roles.json`: Stores user-specific roles.
- `user_default_roles.json`: Stores default roles for users.
- `authorized_users.json`: Manages authorized users.
- `History/`: Directory for saving message histories.
- `Images/`: Directory for storing processed images.
- `config.txt`: Configuration file for bot settings.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify this description based on your project's specifics and additional features you may have.