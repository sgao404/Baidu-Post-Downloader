__author__ = 'Sida'
# -*- coding: utf-8 -*-

import urllib2
import urllib
import re
from bs4 import BeautifulSoup
import os

class Tiezi:

    def __init__(self,baseURL,onlyLZ,floorTag,alsoPics):

        self.baseURL = baseURL
        self.onlyLZ = '?see_lz='+str(onlyLZ)
        self.file = None
        self.floor = 1
        self.defaultTitle = "Baidu Tieba"
        self.floorTag = floorTag
        self.alsoPics = alsoPics
        self.tool = Tool()
        self.picNum = 1

    def getPage(self,pageNum):
        try:
            url = self.baseURL + self.onlyLZ + '&pn=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8')

        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print "Connection failed. Reason: ", e.reason
                return None

    def getTitle(self,page):
        title = BeautifulSoup(page).find("h3", {"class" : "core_title_txt pull-left text-overflow  "})['title']
        if title:
            return title
        else:
            return None
        
    def getPageNum(self,page):
        pageNums = BeautifulSoup(page).findAll("span", {"class" : "red"})[1].text
        if pageNums:
            return pageNums
        else:
            return None

    def getContent(self,page,title):
        new_contents = []
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>',re.S)
        contents = re.findall(pattern,page)
        for content in contents:
            if self.alsoPics == 1:
                images_src = []
                images = BeautifulSoup(content).findAll("img", {"class" :"BDE_Image"})
                for image in images:
                    images_src.append(image['src'])
                if images_src != None:
                    self.saveImgs(images_src,title)
            item = "\n" + self.tool.replace(content) + "\n"
            new_contents.append(item.encode('utf-8'))
        return new_contents

    def saveImgs(self,images,title):
        for imageURL in images:
            splitPath = imageURL.split('.')
            fTail = splitPath.pop()
            if len(fTail) > 3:
                fTail = "jpg"
            fileName = title + "/" + str(self.picNum) + "." + fTail
            self.saveImg(imageURL,fileName)
            self.picNum += 1

    def saveImg(self,imageURL,filename):
        u = urllib.urlopen(imageURL)
        data = u.read()
        f = open(filename,'wb')
        f.write(data)
        f.close()

    def mkdir(self,path):
        if path is None:
            path = self.defaultTitle
        path = path.strip()
        isExists = os.path.exists(path)
        if not isExists:
            print u"Crated a new directory:",path
            os.makedirs(path)
            return True
        else:
            print u"Directory has already been created:",path
            return False

    def setFileTitle(self,title):
        if title is not None:
            self.file = open(title + "/" + title + ".txt","w+")
        else:
            self.file = open(self.defaultTitle + "/" + self.defaultTitle + ".txt","w+")

    def writeData(self,contents):
        for item in contents:
            print item
            if self.floorTag == '1':
                floorLine = "\n" + str(self.floor) + u"**********************************************************\n"
                self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.mkdir(title)
        self.setFileTitle(title)

        if pageNum == None:
            print "Invalid URL, try again!"
            return
        try:
            print "Page Num: " + str(pageNum)
            for i in range(1,int(pageNum)+1):
                print "Processing page"+str(i)
                page = self.getPage(i)
                contents = self.getContent(page,title)
                self.writeData(contents)
            self.file.close()
        except IOError, e:
            print "Error. Reason: " + e.message
        finally:
            print "Download finished!"

class Tool:

    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    replaceTD= re.compile('<td>')
    replacePara = re.compile('<p.*?>')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')
    
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)

        return x.strip()


again = True
domain = [0,1]
while again:
    print "Enter Tiezi ID"+ u"输入帖子ID"
    baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
    seeLZ = raw_input("Only see LZ 只看楼主 ? Yes:1 No:0\n")
    floorTag = raw_input("Show floor number 是否显示楼层数? Yes:1 No:0\n")
    alsoPics = raw_input("Also download pics 是否下载图片? Yes:1 No:0\n")
    if seeLZ in domain and floorTag in domain and alsoPics in domain:
        again = False
    else:
        print "Invalid parameter inputs. Please enter again!"
bdtb = Tiezi(baseURL,seeLZ,floorTag,alsoPics)
bdtb.start()
