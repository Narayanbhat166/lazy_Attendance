import requests
import os


def get_video(video,sender):

    duration = video['duration']
    size = video['file_size']
    video_id = video['file_id']

    size = round(size /(1024 * 1024),1)
    reply_message=f'Video Received\nDuration: {duration} seconds of size: {size} MB'

    #get the file path
    get_file_path_url = f'https://api.telegram.org/bot1291011387:AAEDG2wqE0t4XHbe_9RurkcJHJ_Fdw99rf8/getFile?file_id={video_id}'
    response = requests.get(get_file_path_url)

    file_path = response.json()['result']['file_path']
    print(f'Path of the file {file_path}')

    download_file_url = f'https://api.telegram.org/file/bot1291011387:AAEDG2wqE0t4XHbe_9RurkcJHJ_Fdw99rf8/{file_path}'
    response = requests.get(download_file_url)

    try:
        os.chdir('./Downloaded_Files/')
    except:
        try:
            os.mkdirs('./Downloaded_Files/')
            os.chdir('./Downloaded_Files/')
        except:
            print('Couldnt Save video Due to error')
            reply_message+= '\nCouldnt Save video. Try Again Later!!'
            return reply_message


    FILE_NAME =  f'Attendance_{sender}.mp4'

    with open(FILE_NAME,'wb') as file:
        file.write(response.content)

    return reply_message