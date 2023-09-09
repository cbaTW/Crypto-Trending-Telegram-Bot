import os, time, signal, sys
from telegram.ext import Updater, CommandHandler

def start(update, context):
    id = update.message.chat_id
    update.message.reply_text('安安 你的id是 '+ str(id))
def main():
    pid = os.fork()
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    if pid == 0:
        updater.start_polling()
        updater.idle()
    else:
        time.sleep(6)
        updater.stop()
        updater.is_idle = False
        os.kill(pid, signal.SIGKILL)


if __name__ == '__main__':
    TOKEN = sys.argv[1]
    updater = Updater(TOKEN)
    main()


