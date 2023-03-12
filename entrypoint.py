import os

from dev_assist_bot import DevAssistBot


if __name__ == '__main__':
    TOKEN = os.getenv('TG_TOKEN')
    bot = DevAssistBot(TOKEN)
    bot.run_polling()
