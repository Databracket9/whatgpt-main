import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()
config.read('conf.ini')
token = config['API']['key']
queried_question = []
api_resp = []

def openapi_text_call(question:str):

    header = {"Authorization": "Bearer {}".format(token), 
              "Content-Type": "application/json",
              }
    q = "{}".format(question)
    payload = '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "q"}]}'.replace("q", q)
    req = requests.post('https://api.openai.com/v1/chat/completions', headers=header, data=payload)
    return req.json()

def openapi_image_call(question:str, file_name: str):
    header = {"Authorization": "Bearer {}".format(token), 
              "Content-Type": "application/json",
              }
    q = "{}".format(question)
    payload = '{"prompt": "q", "n": 1, "size": "1024x1024"}'.replace("q", q)
    resp = requests.post('https://api.openai.com/v1/images/generations', data=payload, headers=header)
    resp_return = None
    try:
        image_url = resp.json()['data'][0]['url']
        image_resp = requests.get(image_url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in image_resp.iter_content():
                f.write(chunk)
    except:
        resp_return = resp.json()['error']['message']
    return file_name, resp_return

chrome_opts = webdriver.ChromeOptions()
chrome_opts.add_argument("user-data-dir=C:/Users/jayac/AppData/Local/Google/Chrome/User Data")
chrome_opts.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=chrome_opts)
driver.get('https://web.whatsapp.com/')
wait = WebDriverWait(driver=driver, timeout=100)
time.sleep(15)

while True:
    content = driver.page_source
    soup = BeautifulSoup(content, "lxml")
    recent_question = soup.find("span", {'title':'Aashoto'}).parent.parent.parent
    question = recent_question.find("span", {"dir":"ltr"})
    if question.find(string=True) == None or question == None:
        profile =  wait.until(EC.presence_of_element_located((By.XPATH, "//span[@title='Aashoto']")))
        profile.click()
        send_message_context = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
        sender = wait.until(EC.presence_of_element_located((By.XPATH, send_message_context)))
        sender.send_keys("Make sure to pass input with correct format" + Keys.ENTER)
    elif len(question.find(string=True).split(":")) < 2:
        profile =  wait.until(EC.presence_of_element_located((By.XPATH, "//span[@title='Aashoto']")))
        profile.click()
        send_message_context = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
        sender = wait.until(EC.presence_of_element_located((By.XPATH, send_message_context)))
        sender.send_keys("please pass valid or next prompt for text or image generation" + Keys.ENTER)
    else:
        question = question.find(string=True)
        question_type = question.split(":")[0]
        prompt = question.split(":")[1]
        file_name = question.split(":")[1] + ".png"
        questions = [None, question]
        responses = [None, question]
        if queried_question in questions or queried_question in responses:
            pass
        else:
            if len(queried_question) == 0:
                queried_question.append(question)
            else:
                queried_question[0] = question


            if question_type == 'text':
                response = openapi_text_call(question=str(prompt))
            elif question_type == 'image':
                response, resp_return = openapi_image_call(question=(prompt), file_name=file_name)


            if question_type == 'text':
                try:
                    resp = response["choices"][0]['message']['content']
                except:
                    resp = response['error']['message']
            elif question_type == 'image':
                try:
                    resp = open(response, 'r')
                except:
                    resp = resp_return

            if len(api_resp) == 0:
                api_resp.append(resp)
            else:
                api_resp[0] = resp


            profile =  wait.until(EC.presence_of_element_located((By.XPATH, "//span[@title='Aashoto']")))
            profile.click()
            if question_type == 'text':
                send_message_context = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                sender = wait.until(EC.presence_of_element_located((By.XPATH, send_message_context)))
                sender.send_keys(resp + Keys.ENTER)
            elif question_type == 'image':
                try:
                    cwd = Path.cwd()
                    cwd.as_posix()
                    file_path = "{}/{}".format(cwd, file_name)
                    sender_click = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@data-icon='clip']")))
                    sender_click.click()
                    send_keys = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']")))
                    send_keys.send_keys(file_path)
                    send_click = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@data-icon='send']")))
                    send_click.click()
                except:
                    send_message_context = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                    sender = wait.until(EC.presence_of_element_located((By.XPATH, send_message_context)))
                    sender.send_keys(resp + Keys.ENTER)
    time.sleep(20)