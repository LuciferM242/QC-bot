from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import threading
import time
import re
from revChatGPT.V1 import Chatbot

chatbot = Chatbot(config={"access_token": "Your access token"})

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)

def main():
    url = 'https://www.qcsalon.net/en/game?connectbox'
    try:
        driver.get(url)
        time.sleep(3)
        login_qcsalon()
        history_thread = threading.Thread(target=display_events)
        history_thread.start()
        interact()

    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

def login_qcsalon():
    driver.find_element('id', 'login').send_keys('username')
    driver.find_element('id', 'password').send_keys('Your Password')
    driver.find_element("xpath", "//button[contains(text(), 'Sign-in')]").click()
    time.sleep(5)

def display_events():
    prev_history = ''
    while True:
        curr_history = driver.find_element('id', 'history').text
        if curr_history != prev_history:
            new_events = curr_history[len(prev_history):]
            print(new_events)
            prev_history = curr_history
            process_events(new_events)

def process_events(events):
    lines = events.split('\n')
    for line in lines:
        if re.search(r" says: q ", line, re.IGNORECASE):
            parts = re.split(r" says: q ", line, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) >= 2:
                text = parts[1].strip()
                cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
                if cleaned_text:
                    try:
                        response = generate_response(cleaned_text)
                        send_reply(response)
                    except Exception as e:
                        print("Error generating or sending response:", e)
                else:
                    print("ignoring line with only non BMP characters:", line)
            else:
                print("invalid line format:", line)

def send_reply(reply):
    try:
        cmd_box = driver.find_element('id', 'chatBox')
        cmd_box.send_keys(reply)
        cmd_box.send_keys(Keys.RETURN)
        time.sleep(4)
    except Exception as e:
        print("Error sending reply:", e)

def generate_response(prompt):
    response = ""
    try:
        for data in chatbot.ask(prompt):
            response = data["message"]
        response = response.replace("\n", " ").replace("\r", "")
    except Exception as e:
        print("Error generating response:", e)
    return response

def interact():
    while True:
        cmd = input("Enter a command (or quit to exit): ")
        if cmd.lower() == 'quit':
            break
        cmd_box = driver.find_element('id', 'chatBox')
        cmd_box.send_keys(cmd)
        cmd_box.send_keys(Keys.RETURN)
        time.sleep(2)

if __name__ == "__main__":
    main()
