#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import poster # local module
import logging
import time

TOKEN = os.environ.get('BOT_TOKEN')
TARGET_CHANNELS = os.environ.get('TARGET_CHANNELS').split(',')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
  """Send a message when the command /start is issued."""
  update.message.reply_text('Hi!')


def help(bot, update):
  """Send a message when the command /help is issued."""
  update.message.reply_text('Help!')


def download_image(bot, update):
  logger.info('image filter triggered')
  photos = []
  caption = ''

  if update.channel_post:
    # it's a channel post
    photos = update.channel_post.photo
    caption = update.channel_post.caption
  elif update.message:
    # it's a direct message
    photos = update.message.photo
    caption = update.message.caption

  if caption == None: caption = ''

  hq_image_id = photos[-1].file_id
  ifile = bot.get_file(hq_image_id)
  logger.info('downloading image w/ caption ' + caption)
  ifile.download(f'images/to-post/z-channel-{int(time.time())}-{hq_image_id[:10]}.jpg')
  poster.post_one(caption=caption)


def echo(bot, update):
  """Echo the user message."""
  logger.info('text filter')
  update.message.reply_text(update.message.text)


def error(bot, update, error):
  """Log Errors caused by Updates."""
  logger.warning('Update "%s" caused error "%s"', update, error)


def main():
  """Start the bot."""
  # Create the EventHandler and pass it your bot's token.
  updater = Updater(TOKEN)

  # Get the dispatcher to register handlers
  dp = updater.dispatcher

  # on different commands - answer in Telegram
  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("help", help))

  # on noncommand i.e message - echo the message on Telegram
  dp.add_handler(MessageHandler(Filters.text, echo))

  # capture images from the channel
  dp.add_handler(MessageHandler(Filters.chat(username=TARGET_CHANNELS), download_image))


  # log all errors
  dp.add_error_handler(error)

  # Start the Bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C or the process receives SIGINT,
  # SIGTERM or SIGABRT. This should be used most of the time, since
  # start_polling() is non-blocking and will stop the bot gracefully.
  updater.idle()

if __name__ == '__main__':
  main()
