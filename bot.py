import requests
import json
from googletrans import Translator
from downloadvideo import get_video
from bottle import (
    run, post, response, request as bottle_request
)
import logging
import threading
import os
import time
import datetime
from Extract import Create_Frames, Extract_Text
from Chat import Chat_class
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, filename='bot.log',
                    datefmt="%H:%M:%S")


lock = threading.Lock()
translator = Translator()

bot_url = 'https://api.telegram.org/bot<token>/'

chats = Chat_class()


def get_ngrok_url():
    url = "http://localhost:4040/api/tunnels"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    return res_json["tunnels"][0]["public_url"]


def set_webhook():
    # first check the existing webhook
    check_webhook_url = bot_url+'getWebHookinfo'
    webhook_response = requests.get(check_webhook_url).json()
    webhook_url = webhook_response['result']['url']

    ngrok_url = get_ngrok_url()

    if not ngrok_url[-17:].__eq__(webhook_url[-17:]):
        print("Previous Webhook: "+webhook_url)
        print("New Webhook: "+ngrok_url)

        method = 'deleteWebHook'
        requests.get(bot_url + method)
        ngrok_url = ngrok_url[-17:]
        method = 'setWebHook' + '?url=https://{}'.format(ngrok_url)
        response = requests.get(bot_url + method)


def get_chatid(data):
    chatid = data['message']['chat']['id']
    return chatid


def get_text(data):
    text = 'Hello'
    sender = data['message']['from']['first_name']
    try:
        text = data['message']['text']
    except:
        try:
            video = data['message']['video']
            if video:
                return sender, 'video'
        except:
            text = 'I accept Text and Videos!'
    return sender, text


def reply(message, chat_id):

    json_data = {
        "chat_id": chat_id,
        "text": message
    }

    message_url = bot_url+'sendMessage'
    requests.post(message_url, json=json_data)


def download_video(file_path, sender, chat_id):
    logging.info("Thread for downloading video from %s Started", sender)
    download_file_url = f'https://api.telegram.org/file/bot1291011387:AAEDG2wqE0t4XHbe_9RurkcJHJ_Fdw99rf8/{file_path}'
    response = requests.get(download_file_url)

    try:
        os.chdir('/home/chaser/telegram/python-bot/Downloaded_Files')
    except:
        print('Error Saving the video')

    FILE_NAME = f'Attendance_{sender}.mp4'

    with open(FILE_NAME, 'wb') as file:
        file.write(response.content)

    logging.info("Thread for downloading video from %s Finished", sender)
    global lock

    extract_thread = threading.Thread(
        target=Create_Frames, args=(FILE_NAME, sender, chat_id, lock,))
    extract_thread.start()


def get_video(video, sender, chat_id):

    duration = video['duration']
    size = video['file_size']
    video_id = video['file_id']

    size = round(size / (1024 * 1024), 1)
    reply_message = f'Video Received\nDuration: {duration} seconds of size: {size} MB'

    # get the file path
    get_file_path_url = f'https://api.telegram.org/bot1291011387:AAEDG2wqE0t4XHbe_9RurkcJHJ_Fdw99rf8/getFile?file_id={video_id}'
    response = requests.get(get_file_path_url)
    try:
        file_path = response.json()['result']['file_path']
    except:
        reply_message = "Error Occured!Contact Narayan"
        return reply_message

    t = threading.Thread(target=download_video,
                         args=(file_path, sender, chat_id))
    t.start()

    return reply_message


@post('/')
def main():
    data = bottle_request.json

    chat_id = get_chatid(data)
    sender, text = get_text(data)

    if text.__eq__('video'):
        log_message = f'Video From {sender} chat_id:{chat_id}'
        logging.info(log_message)
        video = data['message']['video']
        message = get_video(video, sender, chat_id)
        reply(message, chat_id)
        return response

    else:
        log_message = f'Text:{text} From {sender} chat_id:{chat_id}'
        logging.info(log_message)
        if text.__eq__('/start'):
            message = "You seem to be new here. I'm here to guide.Send me Something and I will convert it to Spanish(Yeah LCDP fans) "
            message += "or send me a video of attendance and I will extract the names from it"
        else:
            translated_text = translator.translate(text, dest='es', src='en')
            message = translated_text.text
        reply(message, chat_id)
        return response


if __name__ == '__main__':
    set_webhook()
    logging.info("Started server at port 8080")
    run(host='localhost', port=8080, debug=True)
