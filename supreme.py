import platform
import sys
import requests
import json
import random
import datetime
import time
from lxml import etree
from concurrent import futures as cf
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class Supreme(object):

    def __init__(self, category, name, color, size, delay):
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B202'}
        self.proxies = [line.rstrip('\n') for line in open('proxies.txt', 'r')]
        self.urls = []

        self.category = category.lower() if category else None
        self.prodName = name.lower() if name else None
        self.color = color.lower() if color else None
        self.size = size[0].upper() + size[1:].lower() if size else None
        self.delay = delay if delay else 0

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        if platform.system() == 'Darwin':
            self.driver = webdriver.Chrome('./bin/chromedriver', chrome_options=options)
        else:
            self.driver = webdriver.Chrome('./bin/chromedriver.exe', chrome_options=options)
        self.driver.get('https://www.google.com')
        for cookie in json.load(open('gmail.json')):
            self.driver.add_cookie(cookie)
        self.wait = WebDriverWait(self.driver, 10)

        with open('billing.json') as billing_json:
            billing = json.load(billing_json)
            self.name = billing['name']
            self.email = billing['email']
            self.tel = billing['tel']
            self.address1 = billing['address1']
            self.address2 = billing['address2']
            self.zip = billing['zip']
            self.city = billing['city']
            self.state = billing['state']
            self.ccNum = billing['ccNum']
            self.expMon = billing['expMon']
            self.expYear = billing['expYear']
            self.ccCVV = billing['ccCVV']

    def search(self):
        def checkMatch(url):
            try:
                r = requests.get(url, headers=self.headers, proxies={'http': random.choice(self.proxies)} if self.proxies else None)
                tree = etree.HTML(r.content)
                return tree.xpath('/html/head/title')[0].text, url
            except Exception as e:
                print(e)
                return None

        while True:
            try:
                print(datetime.datetime.now().strftime('%x %X'), 'Searching')
                r = requests.get('http://www.supremenewyork.com/shop/all/{}'.format(self.category), headers=self.headers,
                                 proxies={'http': random.choice(self.proxies)} if self.proxies else None)
                tree = etree.HTML(r.content)
                if not self.urls:
                    for products in tree.xpath('//*[@id="container"]/article/div/a'):
                        self.urls.append('http://www.supremenewyork.com'+products.get('href'))
                    print(self.urls)
                else:
                    with cf.ThreadPoolExecutor() as pool:
                        futures = []
                        for products in tree.xpath('//*[@id="container"]/article/div/a'):
                            if 'http://www.supremenewyork.com'+products.get('href') not in self.urls:
                                futures.append(pool.submit(checkMatch, 'http://www.supremenewyork.com'+products.get('href')))
                        if futures:
                            for x in futures:
                                if x.result():
                                    if self.prodName in x.result()[0].lower() and self.color in x.result()[0].lower():
                                        return x.result()[1]
                time.sleep(0.5)
            except Exception as e:
                print(e)

    def restock(self, url):
            while True:
                try:
                    print(datetime.datetime.now().strftime('%x %X'), 'Waiting for restock')
                    r = requests.get(url, headers=self.headers, proxies={'http': random.choice(self.proxies)} if self.proxies else None)
                    tree = etree.HTML(r.content)
                    if tree.xpath('//*[@id="add-remove-buttons"]/input'):
                        avlSz = [sizes for sizes in tree.xpath('//*[@id="s"]/option/text()')] if tree.xpath('//*[@id="s"]/option/text()') else ['N/A']
                        if avlSz:
                            return url
                    time.sleep(0.5)
                except Exception as e:
                    print(e)

    def addToCart(self, url):
        print(datetime.datetime.now().strftime('%x %X'), 'Adding to cart')
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'button')))
            try:
                select = Select(self.driver.find_element_by_xpath('//*[@id="s"]'))
                select.select_by_visible_text(self.size)
            except:
                pass
            self.driver.find_element_by_name('commit').click()
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'subtotal-container')))
            print(datetime.datetime.now().strftime('%x %X'), 'Finish adding to cart')
            time.sleep(0.1)
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit(1)

    def checkOut(self):
        print(datetime.datetime.now().strftime('%x %X'), 'Beginning checkout')
        try:
            self.driver.get('https://www.supremenewyork.com/checkout')
            self.driver.find_element_by_name('order[billing_name]').send_keys(self.name)
            self.driver.find_element_by_name('order[email]').send_keys(self.email)
            self.driver.find_element_by_name('order[tel]').click()
            for i in self.tel:
                self.driver.find_element_by_name('order[tel]').send_keys(i)
            self.driver.find_element_by_name('order[billing_address]').send_keys(self.address1)
            self.driver.find_element_by_name('order[billing_address_2]').send_keys(self.address2)
            self.driver.find_element_by_name('order[billing_zip]').send_keys(self.zip)
            try:
                self.driver.find_element_by_name('credit_card[nlb]').click()
                for i in self.ccNum:
                    self.driver.find_element_by_name('credit_card[nlb]').send_keys(i)
            except:
                self.driver.find_element_by_id('cnb').click()
                for i in self.ccNum:
                    self.driver.find_element_by_name('credit_card[cnb]').send_keys(i)
            self.driver.find_element_by_xpath('//*[@id="credit_card_month"]').send_keys(self.expMon)
            self.driver.find_element_by_xpath('//*[@id="credit_card_year"]').send_keys(self.expYear)
            try:
                self.driver.find_element_by_name('credit_card[rvv]').click()
                self.driver.find_element_by_name('credit_card[rvv]').send_keys(self.ccCVV)
            except:
                self.driver.find_element_by_name('credit_card[vval]').click()
                self.driver.find_element_by_name('credit_card[vval]').send_keys(self.ccCVV)
            self.driver.find_element_by_xpath('//*[@id="cart-cc"]/fieldset/p[2]/label').click()
            time.sleep(self.delay)
            self.driver.find_element_by_name('commit').send_keys('\n')  # Remove hashtag for complete auto checkout
            print(datetime.datetime.now().strftime('%x %X'), 'Done submitting billing info, check email for order confirmation')
            try:
                self.wait.until(EC.visibility_of_any_elements_located((By.ID, 'confirmation')))
                print(datetime.datetime.now().strftime('%x %X'), '\n' + self.driver.find_element_by_id('confirmation').text)
            except:
                pass
            screenShot = datetime.datetime.now().strftime('%x_%X').replace(':', '-').replace('/', '-')
            self.driver.save_screenshot('./orders/order_{}.png'.format(screenShot))
            self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit(1)
