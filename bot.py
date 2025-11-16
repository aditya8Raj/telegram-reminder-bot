from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from datetime import datetime
import pytz
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TOKEN")
TIMEZONE = pytz.timezone('Asia/Kolkata')
REMINDERS_FILE = "reminders.json"

# Conversation states
TASK, DATES, TIMES = range(3)

# Load/Save reminders
def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f, indent=2)

reminders_db = load_reminders()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    welcome_msg = """
🤖 **Welcome to Reminder Bot!**

I can help you set up reminders for any task. Here's what I can do:

📝 `/addreminder` - Create a new reminder
📋 `/myreminders` - View all your reminders
🗑️ `/delete [id]` - Delete a reminder by ID
❓ `/help` - Show this help message

Let's get started! Use /addreminder to create your first reminder.
"""
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg = """
📚 **How to use Reminder Bot:**

**Creating a Reminder:**
1. Send `/addreminder`
2. Tell me what task you want to be reminded about
3. Select the dates (format: 13,17,21 or single date: 25)
4. Select times (6am, 12pm, 9pm format)

**Managing Reminders:**
• `/myreminders` - See all active reminders
• `/delete [id]` - Remove a specific reminder

**Examples:**
`/addreminder` → "Upload YouTube Video" → "13,17,21,25,29" → "6,12,21"
This creates reminders on those dates at 6 AM, 12 PM, and 9 PM.
"""
    await update.message.reply_text(help_msg, parse_mode='Markdown')


async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 What task do you want to be reminded about?\n\n"
        "Example: Upload YouTube Video 💥"
    )
    return TASK


async def receive_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['task'] = update.message.text
    await update.message.reply_text(
        f"✅ Task: *{update.message.text}*\n\n"
        "📅 Now, enter the dates (day of month) when you want reminders.\n\n"
        "Format examples:\n"
        "• Single date: `25`\n"
        "• Multiple dates: `13,17,21,25,29`\n"
        "• Range: `1-5` (days 1 through 5)",
        parse_mode='Markdown'
    )
    return DATES


async def receive_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dates_input = update.message.text.strip()
    
    try:
        dates = []
        # Handle range (e.g., "1-5")
        if '-' in dates_input:
            start, end = map(int, dates_input.split('-'))
            dates = list(range(start, end + 1))
        # Handle comma-separated (e.g., "13,17,21")
        elif ',' in dates_input:
            dates = [int(d.strip()) for d in dates_input.split(',')]
        # Handle single date
        else:
            dates = [int(dates_input)]
        
        # Validate dates
        dates = [d for d in dates if 1 <= d <= 31]
        
        if not dates:
            await update.message.reply_text("❌ Invalid dates. Please enter valid day numbers (1-31).")
            return DATES
        
        context.user_data['dates'] = dates
        await update.message.reply_text(
            f"✅ Dates: {', '.join(map(str, dates))}\n\n"
            "⏰ Now, enter the times (hours in 24-hour format).\n\n"
            "Format examples:\n"
            "• Morning only: `6`\n"
            "• Multiple times: `6,12,21` (6 AM, 12 PM, 9 PM)\n"
            "• All day: `6,12,18,21`"
        )
        return TIMES
        
    except ValueError:
        await update.message.reply_text("❌ Invalid format. Please use numbers only (e.g., 13,17,21).")
        return DATES


async def receive_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    times_input = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    try:
        times = [int(t.strip()) for t in times_input.split(',')]
        times = [t for t in times if 0 <= t <= 23]
        
        if not times:
            await update.message.reply_text("❌ Invalid times. Please enter hours (0-23).")
            return TIMES
        
        task = context.user_data['task']
        dates = context.user_data['dates']
        
        # Create reminders
        chat_reminders = reminders_db.get(str(chat_id), [])
        reminder_count = 0
        
        job_queue = context.application.job_queue
        
        for day in dates:
            for hour in times:
                # Determine the correct month/year
                now = datetime.now(TIMEZONE)
                year = now.year
                month = now.month
                
                # If day is in the past this month, schedule for next month
                reminder_dt = datetime(year, month, day, hour, 0, 0, tzinfo=TIMEZONE)
                if reminder_dt <= now:
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
                    reminder_dt = datetime(year, month, day, hour, 0, 0, tzinfo=TIMEZONE)
                
                # Create reminder entry
                reminder_id = f"{chat_id}_{reminder_dt.timestamp()}"
                reminder_entry = {
                    'id': reminder_id,
                    'task': task,
                    'datetime': reminder_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'chat_id': chat_id
                }
                chat_reminders.append(reminder_entry)
                
                # Schedule job
                job_queue.run_once(
                    send_reminder,
                    when=reminder_dt,
                    data={'task': task, 'chat_id': chat_id},
                    name=reminder_id
                )
                reminder_count += 1
        
        reminders_db[str(chat_id)] = chat_reminders
        save_reminders(reminders_db)
        
        time_labels = [f"{t}:00" for t in times]
        await update.message.reply_text(
            f"✅ **Reminder Created!**\n\n"
            f"📝 Task: {task}\n"
            f"📅 Dates: {', '.join(map(str, dates))}\n"
            f"⏰ Times: {', '.join(time_labels)}\n"
            f"📊 Total reminders: {reminder_count}\n\n"
            f"Use /myreminders to see all your reminders.",
            parse_mode='Markdown'
        )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Invalid format. Please use numbers only (e.g., 6,12,21).")
        return TIMES


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    task = job_data['task']
    chat_id = job_data['chat_id']
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏰ **REMINDER**\n\n{task}",
        parse_mode='Markdown'
    )


async def my_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_reminders = reminders_db.get(str(chat_id), [])
    
    if not chat_reminders:
        await update.message.reply_text("📭 You don't have any active reminders.\n\nUse /addreminder to create one!")
        return
    
    # Sort by datetime
    chat_reminders.sort(key=lambda x: x['datetime'])
    
    msg = "📋 **Your Active Reminders:**\n\n"
    for i, reminder in enumerate(chat_reminders, 1):
        dt = datetime.strptime(reminder['datetime'], '%Y-%m-%d %H:%M:%S')
        msg += f"{i}. **{reminder['task']}**\n"
        msg += f"   📅 {dt.strftime('%B %d, %Y at %I:%M %p')}\n\n"
    
    msg += "\nUse `/delete [number]` to remove a reminder."
    await update.message.reply_text(msg, parse_mode='Markdown')


async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("❌ Please specify reminder number.\n\nUsage: `/delete 1`", parse_mode='Markdown')
        return
    
    try:
        index = int(context.args[0]) - 1
        chat_reminders = reminders_db.get(str(chat_id), [])
        
        if 0 <= index < len(chat_reminders):
            removed = chat_reminders.pop(index)
            reminders_db[str(chat_id)] = chat_reminders
            save_reminders(reminders_db)
            
            # Remove scheduled job
            current_jobs = context.application.job_queue.get_jobs_by_name(removed['id'])
            for job in current_jobs:
                job.schedule_removal()
            
            await update.message.reply_text(f"✅ Reminder deleted: {removed['task']}")
        else:
            await update.message.reply_text("❌ Invalid reminder number. Use /myreminders to see your list.")
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Reminder creation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


# Build application
app = ApplicationBuilder().token(TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("myreminders", my_reminders))
app.add_handler(CommandHandler("delete", delete_reminder))

# Conversation handler for adding reminders
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("addreminder", add_reminder)],
    states={
        TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_task)],
        DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_dates)],
        TIMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_times)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
app.add_handler(conv_handler)

# Load existing reminders on startup
def load_existing_reminders(application):
    job_queue = application.job_queue
    now = datetime.now(TIMEZONE)
    
    loaded_count = 0
    for chat_id, chat_reminders in reminders_db.items():
        valid_reminders = []
        for reminder in chat_reminders:
            reminder_dt = datetime.strptime(reminder['datetime'], '%Y-%m-%d %H:%M:%S')
            reminder_dt = TIMEZONE.localize(reminder_dt)
            
            # Only schedule future reminders
            if reminder_dt > now:
                job_queue.run_once(
                    send_reminder,
                    when=reminder_dt,
                    data={'task': reminder['task'], 'chat_id': int(chat_id)},
                    name=reminder['id']
                )
                valid_reminders.append(reminder)
                loaded_count += 1
        
        reminders_db[chat_id] = valid_reminders
    
    save_reminders(reminders_db)
    print(f"✅ Loaded {loaded_count} existing reminders from database")

print("🤖 Reminder Bot is running...")
print("📝 Available commands: /start, /addreminder, /myreminders, /delete, /help")

# Load existing reminders
load_existing_reminders(app)

app.run_polling()
