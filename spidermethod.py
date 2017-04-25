#coding=utf-8
import urllib2
from bs4 import BeautifulSoup
import time
import user_agents
import random
import sys
import os

def get_htmlsoup(site):
    randomarry = random.choice(user_agents.user_agent_list)
#随机挑选一个user_agent文件头
    headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.6',
    'X-Requested-With':'XMLHttpRequest',
    'User-Agent':randomarry
    }
#手动添加完整一套文件头，假装是不同的浏览器进行访问
    data = None
    requests = urllib2.Request(site,data,headers)
    response = urllib2.urlopen(requests,timeout=30)
    site_page = response.read()
    soup = BeautifulSoup(site_page, 'html.parser')
    return soup
#获取经过beautifusoup处理过后的结果
def monthexchange(string):
    month = 0
    if string == 'January':
        month = '01'
    elif string == 'February':
        month = '02'
    elif string == 'March':
        month = '03'
    elif string == 'April':
        month = '04'
    elif string == 'May':
        month = '05'
    elif string == 'June':
        month = '06'
    elif string == 'July':
        month = '07'
    elif string == 'August':
        month = '08'
    elif string == 'September':
        month = '09'
    elif string == 'October':
        month = '10'
    elif string == 'November':
        month = '11'
    elif string == 'December':
        month = '12'
    return month

def timeexchange(time):
    time = time.split()
    time = time[1:] #去掉第一个单词on
    year = time[-1] 
    time = time[0:2] 
    time = [year] + time #把年份移到最前面
    time[2] = time[2].replace(',','')#替换掉逗号
    if len(time[2]) == 1:
        time[2] = '0' + time[2]
    time[1] = monthexchange(str(time[1])) #把月份变成数字
    time = '/'.join(time)#组成格式
    return time
#对时间进行格式化处理
def get_author(html):
    comment_author = html.find(class_="a-size-base a-link-normal author")
    comment_author = comment_author.get_text()
    return comment_author.encode('utf-8')
#获取评论作者的信息

def get_title(html):
    comment_title = html.find(class_="a-size-base a-link-normal review-title a-color-base a-text-bold")
    comment_title = comment_title.get_text()
    return comment_title.encode('utf-8')
#获取评论标题

def get_content(html):
    comment_text = html.find(class_="a-size-base review-text")
    comment_text = comment_text.get_text()
    return comment_text.encode('utf-8')
#获取评论内容
def get_userid(html):
    user_id = html.find(class_="a-size-base a-link-normal author")
    user_id = user_id['href']
    return user_id.encode('utf-8')
#获取评论作者的对应id主页
def get_stars(html):
    icon_alt = html.find(class_="a-icon-alt")
    icon_alt = icon_alt.get_text()
    icon_alt = str(icon_alt)[0] 
    return icon_alt.encode('utf-8')
#获取评论星级
def get_comment_date(html):
    comment_date = html.find(class_="a-size-base a-color-secondary review-date")
    comment_date = comment_date.get_text()
    comment_date = timeexchange(comment_date)
    return comment_date.encode('utf-8')
#获取评论发布日期并进行格式化
def get_item_type(html):
    item_type = html.find(class_="a-size-mini a-link-normal a-color-secondary")
    item_type = item_type.get_text()
    return item_type
#获取该商品的规格型号
def get_item_number(html):
    item_number = html.find(class_="a-size-mini a-link-normal a-color-secondary")
    #通过class项目抓取到项目的细分asin码
    item_number = item_number['href']
    #从带有asin码的标签中，抓取href这个网址
    item_number = item_number.split('/')
    #对网址进行根据"/"的切片，获取真实的细分asin内容
    item_number = item_number[3]
    return item_number
#获取细分下的编号
def get_vote(html):
    vote = html.find(class_="review-votes")
    vote = vote.get_text()
    vote = (vote.split())[0]
    #对投票的字符串进行切片，留下第一个元素（投票数量）
    if 'One' in vote:
        vote = str(1)
    vote = filter(str.isdigit,str(vote))
    #如果是投票
    return vote.encode('utf-8')
#获取评论票数
def get_comment_data(html):
    comment = []
    comment.append(get_title(html))
    comment.append('\t')
    comment.append(get_content(html))
    comment.append('\t')
    comment.append(get_author(html))
    comment.append('\t')
    try:
        comment.append(get_item_type(html))
    except:
        comment.append('N/A')
    comment.append('\t')
    try:   
        comment.append(get_item_number(html))
    except:
        comment.append('N/A')
    comment.append('\t')
    comment.append(get_userid(html))
    comment.append('\t')
    try:
        comment.append(get_vote(html))
    except:
        comment.append(str(0))
    comment.append('\t')
    comment.append(get_stars(html))
    comment.append('\t')
    comment.append(get_comment_date(html))
    return comment
#连接成一整条完整的评论列表 
def refresh(count_list,list_array,filename):
    tmp_list = count_list[list_array:]
    config=open(str(filename)+'.txt','w')
    config.write('')
    config=open(str(filename)+'.txt','a')
    for i in tmp_list:
        config.write(i)
#写入缓存文本文件
def reset_list(comment_list):
    count = 0
    result =[]
    for comment in comment_list:
        count = count+1
        if comment not in result:
            result.append(comment)
        else:
            continue
    return result
#去除重复项
def get_page_range(asid):
    print 'try to get page range...'
    page_content = get_htmlsoup('https://www.amazon.com/product-reviews/'+(str(asid).strip())+'/ref=cm_cr_arp_d_paging_btm_1?&sortBy=recent&pageNumber=1')
    print 'connect successful'
    page_range = page_content.find_all(class_="page-button")#通过按钮上的数字查找到整个评论究竟有多少页 
    try:
        page_range = page_range[-1]
        page_range = int(page_range.get_text())
    except:
        page_range = []
    return page_range
#获取页面链接

def cycle_get_page_range(asid):
    count = 0
    while 1:
        page_range = get_page_range(asid)
        try:
            page_range = int(page_range)
            break
        except:
            count = count+1
        if count == 10:
            page_range = 1
            break
    #反复获取总页面数量，获取成功就跳出，获取失败就重新获得，十次失败以后就视为只有一页
    print 'get page_range successful'
    print 'page = '+str(page_range)
    return page_range

def spider_page_logic(asid):
    comment_count = 0
    asin_comment = []
    page_range = cycle_get_page_range(asid)
    for page in range(1,page_range+1):
        url = 'https://www.amazon.com/product-reviews/'+str(asid.strip())+'/ref=cm_cr_arp_d_paging_btm_'+str(page)+'?&sortBy=recent&pageNumber='+str(page)

        page_html = get_htmlsoup(url)

        review_list = page_html.find_all(class_="a-section review")
        #从html代码中获得所有评论的html块，储存成一个列表
        for comment in review_list:
            comment_data = [str(asid.strip()),'\t']
            user_id = get_title(comment)
            comment_data.extend(get_comment_data(comment))
        #对列表中的每一块，依次获取到全部评论细节，组成列表储存起来
            asin_comment.append(comment_data)
            comment_count = comment_count + 1
        print '    '+asid.strip()+' '+str(page)+'/'+str(page_range)+'\r'
        
        time.sleep(random.uniform(1,3))
        #这里显示出来告诉我们现在的进度
    print '    '+asid.strip()+' '+str(page)+'/'+str(page_range)
    return asin_comment
    #每当抓取完一件商品（按照asin区分）后，就立刻写入缓存的txt中    

def write_result_by_asid(asid,address,filename,asin_comment):
    rst = open(address+'/'+str(filename)+'result_comment.txt','a')
    count = 0 
    for i in asin_comment:
        for char in i:
            rst.write(char)
        count = count+1
        rst.write('\n') 
    rst.close()
    print '抓取完'+str(asid.strip())+'抓取到'+str(count)+'条,开始抓取下一件商品'
    #每当抓取完一件商品，就把内容写入到txt文件中










