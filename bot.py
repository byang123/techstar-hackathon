from slack_bolt import App
from slack_sdk import WebClient
from bs4 import BeautifulSoup
import requests
import os
import json
import random

DIR = os.getcwd()

with open("secret.json", "r") as json_file:
    all_secret = json.load(json_file)
    SLACK_BOT_TOKEN=all_secret["SLACK_BOT_TOKEN"] 
    SLACK_SIGNING_SECRET=all_secret["SLACK_SIGNING_SECRET"] 

with open("user_images.json", 'r') as json_file:
    user_images = json.load(json_file)

with open("api_list.json", 'r') as json_file:
    URL = json.load(json_file)

bot = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
client = WebClient(token=SLACK_BOT_TOKEN)

@bot.command("/animal")
def post_animal(ack, say, body):
    if 'text' not in body: #display help
        ack()
        say(help())
        return
    
    command, *command_list = body['text'].lower().split()
    
    if command == 'list': #list animals
        ack()
        say(f"List of valid animals: {list(URL.keys())}")
        return

    if command == 'user': #pull random user image
        with open("user_images.json", 'r') as json_file:
           temp_user_images = json.load(json_file)

        random_image = random.choice(list(temp_user_images.items()))
        print(random_image)
        ack()
        random_image_user = "Image from " + random_image[1][0] + ": "
        say(f"<{random_image[0]}|{random_image_user}>" + random_image[1][1])
        return

    if command == 'random': #pull random image from API links
        ack()
        pic_url = retrieve_pic(random.choice(list(URL.keys())))
        say(f'{pic_url}')
        return

    print(body['text']) #default case for each command
    ack()
    pic_url = retrieve_pic(command, command_list)
    say(f'{pic_url}')    

@bot.event("app_mention") #adding user images
def mention(ack, say, body):
    print(body)
    if 'files' in body['event']:
        image_url = body['event']['files'][0]['url_private_download']
        
        text = body['event']['text'].split(">", 1)[1]
        
        user_id = body['event']['user']
        result = client.users_info(user=user_id)
        user = result['user']['real_name']

        user_images[image_url] = [user, text]
        with open("user_images.json", 'w') as json_file:
            json.dump(user_images, json_file)
        
        ack()
        say("Added image to database!")
    
    else:
        ack()
        say("Hi!")

def retrieve_pic(command, command_list): #retrieves animal pic of specified command
    if not command in URL:
        return command + " is not a valid animal!" 

    if len(command_list) < 1:
        response = requests.get(URL[command])
    else:
        url1, url2 = URL[command+"-breed"].split("$")
        print(command_list)
        req_url = url1 + command_list[0] + url2
        response = requests.get(req_url)

    if not response.status_code == 200:
        return f"{command} server is not responding :( \n"

    response = response.json()
    if command == 'dog':
        return f"<{response['message']}|{command}>"
    if command == 'cat':
        return f"<{response[0]['url']}|{command}>"
    if command == 'fox':
        return f"<{response['image']}|{command}>"
    if command == 'lizard':
        return f"<{response['url']}|{command}>"
    if command == 'monkey':
        return f"<{response}|{command}>"
    if command in ['bird', 'panda', 'red-panda', 'koala', 'kangaroo', 'raccoon']:
        return f"<{response['link']}|{command}>"


def help(): #help message
    list_of_animals = list(URL.keys())
    help_msg = f"*Animal Bot Help*\nTo use Animal Bot, use command /animal <animal>.\n The list of available animals are {list_of_animals}, or use keyword 'random' to get a random choice.\n You can also @ the bot with an image attached to add to the user collection of animals, viewed with /animal user."

    return help_msg

# def download_pic(input_url):
#     picture_type = input_url.split(".")[-1]
#     filename = f"test.{picture_type}"
#     with open(f'{DIR}/pictures/{filename}', "wb") as f:
#         picture = requests.get(input_url)
#         f.write(picture.content)

if __name__ == "__main__":
    bot.start(port=3000) # replace 3000 with the port ngrok is running on 
    