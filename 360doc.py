#!/usr/bin/python
# -*- coding:utf-8 -*-
#author:joel 18-5-13

import requests
import time
import random
import re
import pymongo

'''
//*[@id="arti_common_2"]/li/div[2]/a
http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=20&classId=7&subClassId=60&iIscream=0&iSort=1&nPage=1&nType=11
http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=20&classId=7&subClassId=60&iIscream=0&iSort=1&nPage=2&nType=11
'''
class Tool():
    remove1 = re.compile('<p>|<a href=.*?>|<img .*?>|</a>|<blockquote .*?>|</div>|<div style=.*?>|<div>|</p>|<span>|<span .*?>|<tr>|</tr>|<td.*?>|</td>|<tbody>|</tbody>')
    remove2 = re.compile("<div.*?>|<div class='imgcenter'>|<ul>|</ul>|<li>|</li>|<mpvoice .*?>|</mpvoice>|<div .*?>>|<wbr>|</wbr>|<font.*?>|</font>|<table.*?>|</table>")
    remove3 = re.compile('<br>|</br>')
    remove4 = re.compile('<article.*?>|</article>|<b.*?>|</b>|<h1.*?>|</h1>|<p .*?>|<strong.*?>|</span>|</strong>|<section .*?>|<section>|</section>|&nbsp;|<blockquote>|</blockquote>|<em.*?>|</em>')
    def replace(self,html):
        html = re.sub(self.remove1,"",html)
        html = re.sub(self.remove2,"",html)
        html = re.sub(self.remove3, "\n", html)
        html = re.sub(self.remove4, "", html)
        return html.strip()

class Spider():
    def __init__(self):
        self.tool = Tool()
        self.number = int(raw_input('Please input the counts of page : '))
        self.url = 'http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=20&classId=7&subClassId=60&iIscream=0&iSort=1&nPage=1&nType=11'
    def getHtml(self,start_url,i):
        headers = {
            'Accept': '* / *',
            'Accept - Encoding': 'gzip, deflate',
            'Accept - Language': 'zh - CN, zh;q = 0.9',
            'Connection': 'keep - alive',
            'Cookie': 'your cookie',
            'Host': 'www.360doc.com',
            'Referer': 'http://www.360doc.com/index.html',
            'User-Agent': 'your user-agent',
            'X - Requested - With': 'XMLHttpRequest'
        }
        proxies = [
            {"https": "60.255.186.169:8888"},
            {"https": "60.255.186.169:8888"},
            {"https": "121.225.25.134:3128"},
        ]
        proxy = proxies[random.randint(0,2)]
        r = requests.get(start_url,headers = headers,proxies = proxy)
        time.sleep(1)
        result = r.json()
        #print result
        print u'获取第'+str(i)+u'页动态加载的内容...'
        return result

    def getData(self,start_url,i):
        result = self.getHtml(start_url,i)
        page = i
        #print result
        Data = []
        for j in range(0,20):
            l = { }
            l['title'] = result[0]["data"][j]['StrArtidetitle']
            l['author'] = result[0]["data"][j]['StrUserName']
            l['date'] = result[0]["data"][j]['StrSaveDate']
            l['url'] = result[0]["data"][j]['StrUrl']
            l['image'] = result[0]["data"][j]['ImgLis']
            l['source'] = '来源：360doc个人图书馆'
            Data.append(l)
            print u'第'+str(j+1)+u'条获取成功...'
        #print Data
        time.sleep(1)
        print u'已获取第'+str(page)+u'页的20条数据...'
        #print Data
        return Data

    def getContent(self,start_url,i):                       #进入二级文章界面爬取
        page = i
        allData = self.getData(start_url,i)
        #Data = self.getData(start_url, i)
        t = []
        for k in allData:
            try:              #出现文章为doc文件的情况 ，故暂时排除了,其url为：http://www.360doc.cn/document/{}.html
                #url = k['content'][-24:-6]
                url1 = str(k['url']).split('/')
                url2 = url1[7][:-6]
                t.append(url2)
                text_url = 'http://www.360doc.cn/article/{}.html'.format(str(url2))  #通过在这个界面获取文章内容简化操作
                r = requests.get(text_url)
                html = r.text
                pattern = re.compile('<div class="article" id="artcontentdiv" style="clear:both;padding-top:10px;">(.*?)<div class="oactionbox">',re.S)
                result = re.findall(pattern,html)
                content = self.tool.replace(result[0])
                k['content'] = content
                time.sleep(1)
            except IndexError :
                pass
        return allData
        #print u'已获取第'+str(page)+u'页!!!!!!!!!!!!!!!!!!!!!!!'

    def getMore(self):
        p = self.number
        for i in range(1,p+1):
            start_url = 'http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=20&classId=7&subClassId=60&iIscream=0&iSort=1&nPage={}&nType=11'.format(i)
            self.toSave(start_url,i)
            #self.getContent(start_url,i)

    def toSave(self,start_url,i):
        page = i
        item = self.getContent(start_url,i)
        client = pymongo.MongoClient(host = 'localhost',port=port)
        db = client['360doc']
        text = db['360doc Reading experience'+str(page)]
        text.insert(item)
        print  u'第'+str(page)+u'页的20条数据已存到MongoDB...'
        

spider = Spider()
spider.getMore()

