# Telegram Reminder Bot 🤖⏰

A fully functional Telegram bot for managing reminders with scheduling capabilities. Set custom reminders for any task, choose specific dates and times, and never miss important deadlines!

## ✨ Features

- 📝 Create custom reminders with interactive setup
- 📅 Schedule reminders for specific dates and times
- 🔄 Support for multiple dates (comma-separated, ranges)
- ⏰ Multiple time slots per day
- 📋 View all active reminders
- 🗑️ Delete reminders easily
- 💾 Persistent storage (reminders survive bot restarts)
- 🌍 Timezone support

## 🚀 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and bot introduction |
| `/addreminder` | Create a new reminder (interactive) |
| `/myreminders` | View all your active reminders |
| `/delete [number]` | Delete a specific reminder |
| `/help` | Get help on using the bot |

## 📖 How to Use

### Creating a Reminder

1. Send `/addreminder` to the bot
2. Enter your task (e.g., "Upload YouTube Video 💥")
3. Enter dates in one of these formats:
   - Single date: `25`
   - Multiple dates: `13,17,21,25,29`
   - Date range: `1-5`
4. Enter times in 24-hour format:
   - Single time: `6` (6 AM)
   - Multiple times: `6,12,21` (6 AM, 12 PM, 9 PM)
5. Done! You'll receive reminders at the scheduled times ✅

### Example
```
You: /addreminder
Bot: What task do you want to be reminded about?
You: Upload YouTube Video 💥
Bot: Enter the dates...
You: 13,17,21,25,29
Bot: Enter the times...
You: 6,12,21
Bot: ✅ Reminder Created! Total reminders: 15
```

## 🛠️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/telegram-reminder-bot.git
   cd telegram-reminder-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   ```env
   TOKEN=your_telegram_bot_token_here
   ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## 🚂 Deployment on Railway

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variable: `TOKEN` = `your_telegram_bot_token`
   - Deploy! 🚀

3. **Railway will automatically:**
   - Detect Python project
   - Install dependencies from `requirements.txt`
   - Run the bot using the `Procfile`

## 📦 Project Structure

```
telegram-reminder-bot/
├── bot.py              # Main bot logic
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment config
├── runtime.txt        # Python version specification
├── .env               # Environment variables (local only)
├── .gitignore         # Git ignore rules
├── reminders.json     # Persistent reminder storage
└── README.md          # This file
```

## 🔧 Configuration

- **Timezone**: Edit `TIMEZONE` in `bot.py` (default: `Asia/Kolkata`)
- **Token**: Set via environment variable `TOKEN`

## 🐛 Troubleshooting

**Bot not responding?**
- Check if the bot is running
- Verify your bot token is correct
- Ensure you've sent `/start` to the bot

**Reminders not sending?**
- Make sure the bot is running continuously
- Check that dates/times are in the future
- Verify timezone settings

## 📝 Requirements

- Python 3.12+
- python-telegram-bot[job-queue]
- pytz
- python-dotenv

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

MIT License - feel free to use this project however you'd like!

## 👨‍💻 Author

Created with ❤️ by [Your Name]

---

⭐ If you found this helpful, consider giving it a star on GitHub!
