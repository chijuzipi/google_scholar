import urllib2, cookielib, httplib
from bs4 import BeautifulSoup

import os
from selenium import webdriver
import time

from pymongo import MongoClient
from datetime import datetime

import random
from analyzer import Analyzer

class Scholar:
  def __init__(self, url, database):
    chromedriver = "/usr/local/Cellar/chromedriver/2.14/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    self.driver = webdriver.Chrome(chromedriver)

    cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

    client = MongoClient()
    self.db = client[database]
    curr = str(datetime.now()).split('-')
    curr = ''.join(curr)
    curr = 'gs' + curr
    curr = curr.replace(" ", "")
    curr = curr.replace(":", "")
    curr = curr.replace(".", "")
    curr = curr[:14]
    self.collection = self.db[curr]

    self.updateCitation(url)
    self.driver.quit()

   
  def updateCitation(self, url):
    content = urllib2.urlopen(url, timeout=120).read()
    soup = BeautifulSoup(content)
    totalCitations = soup.find('table', {'id':'gsc_rsb_st'}).find('td', {'class':'gsc_rsb_std'}).text

    paperArray = soup.find('tbody', {'id':'gsc_a_b'})
    papers = paperArray.findAll('tr', {'class':'gsc_a_tr'})
    for paper in papers:
      Doc = {}
      Record = {}
      citation = ''
      title    = paper.find('a', {'class':'gsc_a_at'}).text
      cite     = paper.find('a', {'class':'gsc_a_ac'})
      if cite is not None and cite.text != '':
        citation = self.toInt(cite.text)

      citeLink = cite['href']
      pagesNum = citation / 10 + 1
      titleArray = []
      linkArray  = []
      biblArray  = []
      if citation != 0:
        for i in range(pagesNum):
          citePageLink = citeLink + '&start=' + str(i*10)
          #time.sleep(20)
          time.sleep(random.randint(1, 4))
          titleA, linkA = self.getInfoArray(citePageLink)
          titleArray += titleA
          linkArray  += linkA

      Doc['title']     = title
      Doc['citation']  = citation
      Doc['citeTitle'] = titleArray
      Doc['citeLink']  = linkArray
      self.collection.insert(Doc)
    
  def getInfoArray(self, link):
    self.driver.get(link)
    content = self.driver.page_source
    titleArray = [] 
    linkArray  = []
    biblArray  = []
    soup = BeautifulSoup(content)
    Eles   = soup.findAll('div', {'class':'gs_ri'})
    for ele in Eles:
      titEle  = ele.find('h3', {'class':'gs_rt'})
      title   = titEle.find('a')
      if title is None:
        continue
      else:
        link  = title['href']
        title = title.text
        titleArray.append(title)
        linkArray.append(link)
    
    return titleArray, linkArray
  
  def getBib(self, bibs):
    for bib in bibs:
      print bib.text
      if "BibTex" in bib.text:
        return bib 

  def toInt(self, value):
    try:
      x = int(value)
      return x
    except ValueError:
      return 0
  
def main():
  url = ("https://scholar.google.com/citations?hl=en&btnA=1&user=UO984ncAAAAJ")
  scholar = Scholar(url, 'citation')
  analyzer = Analyzer('citation')

if __name__ == '__main__':
  main()
