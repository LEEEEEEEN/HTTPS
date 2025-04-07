import requests

def set_bot_avatar(token, photo_path):
    url = f'https://api.telegram.org/bot{token}/setUserProfilePhotos'
    files = {'photo': open(photo_path, 'rb')}
    response = requests.post(url, files=files)
    files.close()
    return response.json()
bot_token = '8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ'
photo_path = 'materials/Healthy habit Customizable Cartoon Illustrations _ Bro Style.jpeg'

response = set_bot_avatar(bot_token, photo_path)
print(response)
