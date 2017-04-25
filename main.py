#coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import spidermethod
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

def get_page_range(html,url):   
    page_range = html.find(class_="hidden-xs desktop")
    page_range = page_range.find_all('li')
    page_list= []
    try:
        url = url.replace('https','http')
    except:
        pass
    try:
        for i in page_range:
            page = i.find('a')
            #通过a标签定位网址位置
            try:
                page_link = page['href'].replace('https','http')
                print page_link
                page_list.append(page_link)
            except:#把页面网址储存成列表
                continue
        page_list = [url]+page_list
    except:
        page_list = [url]
    #pagelist列表中储存网址
    max_page = len(page_list)
    #获取每个地区有多少页，返回页面数量
    print 'get page range successful'
    print 'max_page = '+str(max_page)
    return page_list
    #返回列表


def browse_html(url):
    print 'connecting....'
    browser = webdriver.Chrome()
    browser.get(url)
    page_html = browser.page_source
    page_html = BeautifulSoup(page_html, 'html.parser')
    browser.close()
    print 'connect successful'
    return page_html
    #通过无界面浏览器访问目标网站


def get_phone_number(html):
    try:
        phone = html.find(class_="phone")
        phone_number = (str(phone.get_text()).replace(' ','')).replace('\n','')
    except:
        phone_number = 'N/A'
    return phone_number
    #获取电话号码


def get_address(html):
    try:
        address = html.find(class_="flex_adresse")
        address = address.get_text()
    except:
        address = 'N/A'
    return address.replace('\n','')
    #获取地址


def get_shop_name(html):
    try:
        shop_name = html.find(itemprop="name")
        name = shop_name.get_text()
    except:
        name = 'N/A'
    return (name.strip()).replace('\n','')
    #获取店铺名称


def get_open_time(html):
    try:
        open_time = html.find(class_="oeffnungszeitenanzeige__inhalt geoeffnet")
        open_time = open_time.get_text()
    except:
        open_time = 'N/A'
    return (open_time.strip()).replace('\n',' ')
    #获取营业时间


def get_city_list():
    fh = open('city_name.txt')
    city_list = fh.readlines()
    return city_list
    #读文件，获取城市列表


def get_shop_link(html):
    try:
        link = html.find(class_="m08_teilnehmername teilnehmername entry")
        link = link['href']
    except:
        link = 'N/A'
    return link
    #获取黄页上的店铺链接


def get_shop_site(html):
    url = get_shop_link(html)
    try:
        page_html = spidermethod.get_htmlsoup(url)
        shop_link = page_html.find(class_="website ")
        shop_link = shop_link.find(class_="link")
        shop = shop_link.get_text()
    except:
        shop = 'N/A'
    return shop.replace('\n','')
    #获取店铺的官网地址


def save_contact_info(result_list):
    fh = open('contact_result.txt','a')
    for result in result_list:
        for j in result:
            for i in j:
                fh.write(i.encode('utf-8'))
    fh.close()
    #把每一页的结果保存起来~


def get_result_list(contact_list):
    result_list = []
    for html in contact_list:
        name = get_shop_name(html)
        address = get_address(html)
        phone = get_phone_number(html)
        open_time = get_open_time(html)
        shop_page = get_shop_site(html)
        result = [name]+['\t']+[address]+['\t']+[phone]+['\t']+[open_time]+['\t']+[shop_page]+['\n']
        result_list.append(result)
    return result_list
    #获取整个页面的所有信息，然后保存起来


def get_contact_content(page):
    page_html = browse_html(page)
    contact_list = page_html.find_all(class_="table")
    result_list = get_result_list(contact_list)
    return result_list
    #把主体存成一个专门的对象，等一下专门拿来做多线程用


bad_city = []
fh = open('city_name.txt','r')
city_list = fh.readlines()
for city in city_list:
    city = (city.strip()).replace(' ','')
    url = "http://www.gelbeseiten.de/schuhe/"+city
    print 'getting page range...'
    page_html = spidermethod.get_htmlsoup(url)
    try:
        head = page_html.find(class_="messageHead")
        if str(head.get_text()) == 'Die angeforderte Seite konnte nicht gefunden werden.':
            bad_city.append(city)
            print city
            continue
    except:
        page_list = get_page_range(page_html,url)
        pool = ThreadPool(len(page_list))#建立线程池
        result_list = pool.map(get_contact_content,page_list)
        save_contact_info(result_list)


         
fh = open('bad_city.txt','w')
for i in bad_city:
    fh.write(i+'\n')
fh.close()


