# coding: utf8
import time
import urllib3
import sys
import telebot

TOKEN = "YOUR TOKEN"
bot = telebot.TeleBot(TOKEN)
USERS_ID = ["YOUR TELEGRAM ID"]
user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) ..'}
http = urllib3.PoolManager(10, headers=user_agent)

url = 'https://zakupki.gov.ru/epz/complaint/search/search_eis.html?morphology=on&fz94=on&considered=on&issuedStatus=0&subjectViolations=-1&complaintObject_0=on&complaintObject_1=on&complaintObject_2=on&complaintObject=0%2C1%2C2&pageNumber=1&sortDirection=false&recordsPerPage=_20&showLotsInfoHidden=false&sortBy=PUBLISH_DATE'

resp = http.request('GET', url)
s = resp.data.decode('utf-8')
if len(s) == 1960:
    print('Failed')
    sys.exit()


def read_current_numbers():
    my_list = []
    with open("reestr_nomerov.txt", 'r') as reestr_nomerow:
        for line in reestr_nomerow:
            my_list.append(line.replace('\n', ''))
    return my_list


def find_comlains_numbers(s):
    myList = []
    current_pos = s.find('№ 2021')
    if current_pos > 0:
        for foo in range(20):
            myList.append(s[current_pos + 2: current_pos + 20])
            current_pos = s.find('№ 2021', current_pos + 20)
    return myList


def write_changes(complains, numbers):
    with open('reestr_jalob.txt', 'w') as fuck:
        pass
    for i in complains:
        with open('reestr_jalob.txt', 'a') as jaloba:
            jaloba.write(str(i) + '\n')
    for i in numbers:
        with open("reestr_nomerov.txt", 'a') as reestr_nomerov:
            reestr_nomerov.write(str(i) + '\n')


def find_comlains_links(s):
    myList = []
    link_to_complain = 'https://zakupki.gov.ru/epz/complaint/card/complaint-information.html?id='
    current_pos = s.find('-information.html?id=')
    for _ in range(20):
        myList.append(link_to_complain + s[current_pos + 21: current_pos + 28])
        current_pos = s.find('-information.html?id=', current_pos + 28)
    return myList


while True:
    if __name__ == '__main__':
        reestr = []
        reestr_nomerov_new = []
        reestr_nomerov_current = read_current_numbers()
        reestr_nomerov_new_current = find_comlains_numbers(s)
        reestr_links = find_comlains_links(s)
        for foo in range(20):
            if reestr_nomerov_new_current[foo] in reestr_nomerov_current:
                pass
            else:
                time.sleep(1)
                reestr_nomerov_new.append(reestr_nomerov_new_current[foo])
                resp = http.request('GET', reestr_links[foo])
                s1 = resp.data.decode('utf-8')
                if len(s1) > 1960:
                    reestr.append(reestr_links[foo])
                    curr_pos1 = s1.find('regNumber=')
                    reg_number = s1[curr_pos1 + 10: curr_pos1 + 29]
                    reestr.append(s1[curr_pos1 + 10: curr_pos1 + 29])
                    curr_pos2 = s1.find('Наименование закупки')
                    curr_pos3 = s1.find('</div>', curr_pos2 + 29)
                    reestr.append(s1[curr_pos2 + 98: curr_pos3])
                    time.sleep(4)
                    resp = http.request('GET','https://zakupki.gov.ru/epz/order/notice/ea44//view/common-info.html?regNumber=' + reg_number)
                    s2 = resp.data.decode('utf-8')
                    curr_pos = s2.find('cardMainInfo__content cost')
                    curr_pos2 = s2.find('&#8381;')
                    price = int((s2[curr_pos + 54: curr_pos2 - 4].replace(' ', '')))
                    if price < 2000000:
                        del reestr[-3:]
                    else:
                        reestr.append(price)
                else:
                    print(reestr_links[foo])
                    print('OOps')

        write_changes(reestr, reestr_nomerov_new)
        sms = []
        messsage = ''
        j = 0
        for i in reestr:
            j += 1
            messsage += str(i) + '\n'
            if j % 4 == 0:
                sms.append(messsage)
                messsage = ''
        users = open('usersId.txt','r')
        USERS_ID = [line.rstrip() for line in users]
        users.close()
        for text in sms:
            for user in USERS_ID:
                ret_msg = bot.send_message(user, text)
                assert ret_msg.message_id
    time.sleep(300)


# USERS_ID = []
# with open("usersId.txt",'r') as usersID:
#     for i in usersID:
#         USERS_ID.append(int(i))
#         print(USERS_ID)
