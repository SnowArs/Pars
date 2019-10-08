from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient

client = MongoClient( 'localhost', 27017 )
client.drop_database( 'unread_messages' )
db = client['unread_messages']

def fill_db( who_sent, date, text):
    db.mail.insert_one( {'сообщение от ': who_sent,
                   'дата получения': date,
                   'текст сообщения': text} )

def time_out(text):
    WebDriverWait( driver, 5 ).until(
        EC.presence_of_element_located( (By.CLASS_NAME, text) )
    )

chrome_options = Options()
# chrome_options.add_argument("--headless")  #Режим без интерфейса
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://mail.yandex.ru/')
assert "Яндекс.Почта — бесплатная и надежная электронная почта" in driver.title
button = driver.find_element_by_class_name('HeadBanner-Button-Enter')
button.click()
login = driver.find_element_by_id('passp-field-login')
login.send_keys("SnowArs2016@yandex.ru")
login.send_keys(Keys.RETURN)
password = WebDriverWait(driver,5).until(
EC.presence_of_element_located((By.ID, 'passp-field-passwd'))
)
password.send_keys("Vnukovo4922")
password.send_keys(Keys.RETURN)
try:
    time_out('is-unread')
except:
    print( 'Нет непрочитанных сообщений ' )

assert "Входящие — Яндекс.Почта" in driver.title[-23:]
links =[]
mails = driver.find_elements_by_class_name('is-unread')
for mail in mails:
    links.append(mail.get_attribute( "href" ))

for link in links:
    try:
        driver.get(link)
        time_out('mail-Message-Sender-Name')
        mail_from = driver.find_element_by_class_name('mail-Message-Sender-Name').text
        receaved = driver.find_element_by_class_name('mail-Message-Date').text
        message = driver.find_element_by_class_name('mail-Message-Body-Content').text

        print(mail_from, receaved, message)
        fill_db( mail_from, receaved, message )
        driver.back()
    except:
         print('Нет непрочитанных сообщений ')

driver.quit()

collections = db.list_collection_names()
for col in collections:
    col_str = str( col )
    for item in db[col_str].find():
        print( item )

