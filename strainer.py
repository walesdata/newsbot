from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib3.exceptions import HTTPError
import urllib3
import re, string
import json
import html
from io import StringIO
from nltk.stem import PorterStemmer 

class SoupStrainer():
    englishDictionary = {}
    haveHeadline = False
    recHeadline = ''
    locToGet = ''
    extractText = ''
    pageData = None
    errMsg = None
    soup = None
    msgOutput = True

    def init(self):
        with open('newsbot/words_dictionary.json') as json_file:
            self.englishDictionary = json.load(json_file)


    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def find_headline(self, soup):
        reOgTitle = re.compile('og:title', re.IGNORECASE)
        reTwTitle = re.compile('twitter:title', re.IGNORECASE)
        haveHeadline = False
        
        tstLine = soup.title(string=True)
        if(tstLine is not None):
            self.recHeadline = tstLine[0]
            haveHeadline = True
        
        if((not haveHeadline)):
            for meta in soup.find_all('meta'):
                if( ((meta.get('property') is not None) or (meta.get('name') is not None)) and (meta.get('content') is not None)):
                    if(meta.get('property') is not None):
                        prp = meta.get('property')
                    else:
                        prp = meta.get('name')
                
                if(reOgTitle.match(prp)):
                    haveHeadline = True
                    self.recHeadline = meta.get('content')

                if((not self.haveHeadline)):
                    if(reTwTitle.match(prp)):
                        haveHeadline = True
                        self.recHeadline = meta.get('content')
        
                if(haveHeadline):
                    break
                


    def loadAddress(self, address):
        self.locToGet = address
        self.haveHeadline = False

        htmatch = re.compile('.*http.*')
        user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
        ps = PorterStemmer() 

        if(htmatch.match(self.locToGet) is None):
            self.locToGet = "http://" + self.locToGet
        
        if(len(self.locToGet) > 5):
            if(self.msgOutput):
                print("Ready to load page data for: " + self.locToGet + " which was derived from " + address)

            try:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                http = urllib3.PoolManager(2, headers=user_agent)
                r = http.request('GET', self.locToGet)
                self.pageData = r.data
                if(self.msgOutput):
                    print("Page data loaded OK")
                    #print(self.pageData)
            except:
                self.errMsg = 'Error on HTTP request'
                if(self.msgOutput):
                    print("Problem loading the page")
                return False
            self.extractText = ''
            self.recHeadline = self.locToGet
            self.soup = BeautifulSoup(self.pageData, 'html.parser')
            self.find_headline(self.soup)
            ttexts = self.soup.findAll(text=True)
            viz_text = filter(self.tag_visible, ttexts)
            allVisText = u"".join(t.strip() for t in viz_text)
            for word in allVisText.split():
                canonWord = word.lower()
                canonWord = canonWord.translate(str.maketrans('', '', string.punctuation))
                canonWord = canonWord.strip(string.punctuation)
                if(canonWord in self.englishDictionary):
                    canonWord = ps.stem(canonWord)
                    self.extractText = self.extractText + canonWord + " "
#                else:
#                    print("Excluded word: " + canonWord)

            return True
