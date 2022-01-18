import os
import time
from selenium import webdriver
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging as logger
import requests

DEV_ID = "SLACK DEVELOPER ID"
USER_ID = "USER SLACK ID"
TOKEN = "YOUR TOKEN"
CHANNEL_ID = "YOUR CHANNEL ID"

while True:
    def sendMessage(id, text):
        url = "https://slack.com/api/chat.postMessage"
        r = requests.post(url, params={
            "token": TOKEN,
            "channel": id,
            "text": text})


    def extract(link, fz):
        driver = webdriver.Chrome(
            executable_path="YOUR PATH")
        driver.get(link)
        if fz == 44:
            elems = driver.find_elements_by_xpath("/html/body/div[2]/div/div[2]/div/div[1]/table/tbody/tr")
            result = []
            for i in elems:
                result.append(i.text)
        else:
            elems = driver.find_elements_by_xpath(
                "/html/body/div[3]/div/div/div[2]/div/div/div[2]/div[2]/div/div/table/tbody/tr")
            result = []
            for i in elems:
                result.append(i.text)
        driver.close()
        driver.quit()
        return result


    """Получение номера закупки"""
    client = WebClient(token=TOKEN)
    conversation_history = []

    try:
        result = client.conversations_history(channel=CHANNEL_ID, limit=1)
        conversation_history = result["messages"]
        logger.info("{} messages found in {}".format(len(conversation_history), id))
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

    """Находим номер заказа"""
    conversation_history = str(conversation_history)
    toBeAdded = True
    if '$' in conversation_history:
        start = conversation_history.find("'$") + 2
        end = conversation_history.find("'", start)
        toBeAdded = False
    else:
        start = conversation_history.find("'&amp;") + 6
        end = conversation_history.find("'", start)
    number = conversation_history[start:end]
    isNewNumber = False
    with open('povtor.txt', 'r') as povtor:
        line = ''
        for foo in povtor:
            line = foo
        if number != line:
            isNewNumber = True
    with open('reestr.txt', 'r') as reestr:
        reestr_list = []
        for line in reestr:
            reestr_list.append(line)

    if not toBeAdded and number + '\n' not in reestr_list and isNewNumber:
        sendMessage(USER_ID, 'Номер ' + str(number) + ' отсутствует в реестре!!!')
        sendMessage(DEV_ID, 'Пользователь пытается удалить несуществующую в реестре запись-_-')
    if isNewNumber or (not isNewNumber and not toBeAdded):
        with open('povtor.txt', 'w', encoding="UTF-8") as povtor:
            povtor.write(number)
        if toBeAdded and number + '\n' not in reestr_list:
            reestr_list.append(number)
        elif not toBeAdded and number + '\n' in reestr_list:
            reestr_list.remove(number + '\n')
            os.remove(number + '.txt')
            with open('povtor.txt', 'w') as dick:
                pass
        with open('reestr.txt', 'w') as reestr:
            for foo in reestr_list:
                reestr.write(foo.strip() + '\n')

    for reestrNumber in reestr_list:
        if len(reestrNumber) > 1:
            fz = 0
            if len(reestrNumber) > 15:
                dr = 'https://zakupki.gov.ru/epz/order/notice/ea44/view/event-journal.html?regNumber=' + reestrNumber
                fz = 44
            else:
                fz = 223
                dr = 'https://zakupki.gov.ru/223/purchase/public/purchase/info/journal.html?regNumber=' + reestrNumber

            result = extract(dr, fz)
            if len(result) == 0:
                sendMessage(DEV_ID, 'Не смог открыть ' + dr)
                pass
            """Достаем из файла все данные и находим разницу с полученными"""
            try:
                with open(str(reestrNumber).strip() + '.txt', 'r', encoding='utf-8') as f:
                    l = [line.strip() for line in f]
            except:
                with open(str(reestrNumber).strip() + ".txt", 'w', encoding='utf-8') as res:
                    for i in result:
                        i = i.replace("\n", " ")
                        res.write(i + '\n')
                l = []
            result1 = []
            for i in result:
                j = i.replace("\n", " ")
                result1.append(j)
            raznica = list(set(result1) - set(l))
            if len(raznica) > 0:
                with open(str(reestrNumber).strip() + ".txt", 'w', encoding='utf-8') as res:
                    for i in result:
                        i = i.replace("\n", " ")
                        res.write(i + '\n')
                sms = 'Есть изменения: \n'
                for i in raznica:
                    sms += i + '\n'
                sms += dr
                sendMessage(USER_ID, sms)
                sendMessage(DEV_ID, sms)
    time.sleep(300)
