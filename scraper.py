
#from __future__ import absolute_import
#from __future__ import division, print_function, unicode_literals
from bs4 import BeautifulSoup, Doctype, Comment
import requests, re
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import os, csv
from difflib import SequenceMatcher

MIN_NUMBER_OF_WORDS_IN_SENTENCE = 2
LANGUAGE = "english"
SENTENCES_COUNT = 5
IMPORTANT_TAG_LIST = ['h1','h2','h3','h4','h5','h6','strong','b','a', 'title', 'blockquote', 'cite', 'em','i','mark','q','pre','u',]
REMOVABLES = ['script','meta','svg','img','path','style','canvas','map','area','form','code','figcaption','picture','audio','source','track','video','link','nav','br','hr','menu','menuitem','table','caption','noscript','embed','object','param']
HEADING_LIST = ['h1','h2','h3','h4','h5','h6']
EMPHASISED_LIST = ['strong','b','a', 'blockquote', 'cite', 'em','i','mark','q','pre','u']
def feature_heading(tag):
    if tag in HEADING_LIST:
        return 1
    else:
        return 0

def feature_emphasised(tag):
    if tag in HEADING_LIST:
        return 1
    else:
        return 0

def feature_istitle(tag):
    if tag == 'title':
        return 1
    else:
        return 0

def similar(a, b): return SequenceMatcher(None, a, b).ratio()

def getHtmlAsSoup(url):
    headers = {'Accept-Encoding': 'identity'}
    r= requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    soup = cleanUp(soup)
    return soup

def cleanUp(soup):
    for removalTag in REMOVABLES:
        [s.extract() for s in soup(removalTag)]
    [s.decompose() for s in soup.find_all('footer')]
    [s.decompose() for s in soup.find_all('header')]
    [s.decompose() for s in soup.find_all("div", {'class':'sidebar'})]
    [s.decompose() for s in soup.find_all("div", {'class':'navigation'})]
    [s.decompose() for s in soup.find_all("a", {'class':'navigation'})]
    [s.decompose() for s in soup.find_all("a", {'class':'sidebar'})]
    [s.decompose() for s in soup.find_all("a", {'class':'js-homeNav'})]
    [s.decompose() for s in soup.find_all("a", {'class':'metabar'})]
    [s.decompose() for s in soup.find_all("div", {'class':'js-homeNav'})]
    [s.decompose() for s in soup.find_all("div", {'class':'metabar'})]
    for item in soup.contents:
        if isinstance(item, Doctype) or isinstance(item, Comment):
            item.extract()
    comments = soup.findAll(text=lambda text:isinstance(text, Comment) 
               and text.find('if') != -1) #This is one line, of course
    [comment.extract() for comment in comments]
    return soup

def cleanText(text):
    # text = replaceAllInstances(text, '\n', '.')
    # text = replaceAllInstances(text, '. ','.')
    # text = replaceAllInstances(text, '..','.')
    # text = replaceAllInstances(text, '  ', ' ')
    text = re.sub(r'[^\x00-\x7F]+','',text).strip()
    text = ' '.join(text.split())
    return text

def replaceAllInstances(text, replaceThis, withThis):
    while text.find(replaceThis)>-1:
        text = text.replace(replaceThis, withThis)
    return text

def sumySummary(url):
   parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
   stemmer = Stemmer(LANGUAGE)
   summarizer = Summarizer(stemmer)
   summarizer.stop_words = get_stop_words(LANGUAGE)
   return [cleanText(str(s)) for s in summarizer(parser.document, SENTENCES_COUNT)]

def extractSentences(url, top_sentences, writer):
    soup = getHtmlAsSoup(url)
    sentences = []
    for tag in soup.descendants:
        if tag.string and len(tag.string.split(' '))>=MIN_NUMBER_OF_WORDS_IN_SENTENCE:
            tagString= cleanText(tag.string)
            if True:
                for tagStringlet in tagString.split('.'):
                    if len(tagStringlet.split(' '))>=MIN_NUMBER_OF_WORDS_IN_SENTENCE:
                        #excel writer
                        # url, sentence, tag, true val
                        #featurise
                        y_true = get_y(tagStringlet, top_sentences)
                        write_to_excel(url, tagStringlet, tag.name, y_true, writer)
                        sentences.append((tagStringlet, tag.name))
    return sentences

def get_y(text, top_sentences):
    ratio = 0
    for i in range(0, len(top_sentences)):
        ratio = max(ratio, similar(text, top_sentences[i]))

    return ratio

def write_to_excel(url, text, tag, y_true, writer):
    writer.writerow([url, text, tag, y_true])



urls = [
    'https://medium.com/@ev/welcome-to-medium-9e53ca408c48',
    'https://medium.com/swlh/how-quitting-my-corporate-job-for-my-startup-dream-f-cked-my-life-up-3b6b3e29b318',
    'https://medium.com/the-mission/8-things-every-person-should-do-before-8-a-m-cc0233e15c8d',
    'https://medium.com/p/a988c17383a6',
    'https://medium.com/p/53c5114c1d3d',
    'https://medium.com/p/1f135f7e1dec',
    'https://medium.com/p/b9b035d39e2d',
    'https://medium.com/p/90c75eb7c5b0',
    'https://medium.com/p/7d894cbaa084',
    'https://medium.com/p/f1611ceb759f',
    'https://medium.com/p/5c5ec7117908',
    'https://medium.com/p/9216e1c9da7d',
    'https://medium.com/p/27b489a39d1a',
    'https://medium.com/p/e07b3cd5fd5b',
    'https://medium.com/p/7af5d5f28038',
    'https://medium.com/p/ea0b02c504cd',
    'https://medium.com/p/62ae4bcbe01b',
    'https://medium.com/p/9eba5eef2976',
    'https://medium.com/p/1df945c09ac6',
    'https://medium.com/p/597cde9ee9d4',
    'https://medium.com/p/dc8526ea9ea8',
    'https://medium.com/p/559d4e805cda',
    'https://medium.com/p/9bf1e69e888c',
    'https://medium.com/p/2c3f948ead98',
    'https://medium.com/p/cf8a2e30907d',
    'https://medium.com/p/263ab694e60e',
    'https://thsppl.com/i-racist-538512462265',
    'https://medium.com/p/328b95c2fd0b',
    'https://medium.com/p/fbe483d3b51e',
    'https://medium.com/p/ead679cb506d',
    'https://medium.com/p/b3d76f963142',
    'https://medium.com/p/8dc34fbe592b',
    'https://medium.com/p/482765ee3503',
    'https://medium.com/p/503c38c131fe',
    'https://medium.com/p/2a1841f1335d',
    'https://medium.com/p/2eb1fe15a426',
    'https://medium.com/p/b8115d6f2361',
    'https://medium.com/p/a387cc0c5db6',
    'https://medium.com/p/26be75072f13',
    'https://medium.com/p/6df13d23689',
    'https://medium.com/p/bad7c34842a2',
    'https://medium.com/p/be8b2dc0677',
    'https://medium.com/p/926eb80d64e3',
    'https://human.parts/a-gentlemens-guide-to-rape-culture-7fc86c50dc4c',
    'https://medium.com/p/fd08c0babb57',
    'https://medium.com/p/15308056cfae',
    'https://medium.com/p/fba93eba6355',
    'https://medium.com/p/1b7372655938',
    'https://medium.com/p/48f36e48d4cb',
    'https://medium.com/p/b81483d2a0e6',
    'https://medium.com/p/4c59524d650d',
    'https://medium.com/p/e53ea8043a85',
    'https://medium.com/p/4191574378',
    'https://medium.com/p/83486f42118c',
    'https://medium.com/p/ee7de959f3fe',
    'https://medium.com/p/124be62f0751',
    'https://medium.com/p/2e953f1c5efb',
    'https://medium.com/p/72c6f8bec7df',
    'https://medium.com/@theonlytoby/history-tells-us-what-will-happen-next-with-brexit-trump-a3fefd154714',
    'https://medium.com/startup-grind/fuck-you-startup-world-ab6cc72fad0e',
    'https://medium.com/an-idea-for-you/the-two-minutes-it-takes-to-read-this-will-improve-your-writing-forever-82a7d01441d1',
    'https://hackernoon.com/how-it-feels-to-learn-javascript-in-2016-d3a717dd577f',
    'https://medium.com/@thatdavidhopkins/how-a-tv-sitcom-triggered-the-downfall-of-western-civilization-336e8ccf7dd0',
    'https://medium.com/@shitHRCcantsay/let-me-remind-you-fuckers-who-i-am-e6e8b297fe47',
    'https://medium.com/swlh/how-technology-hijacks-peoples-minds-from-a-magician-and-google-s-design-ethicist-56d62ef5edf3',
    'https://medium.com/@trentlapinski/dear-democrats-read-this-if-you-do-not-understand-why-trump-won-5a0cdb13c597',
    'https://medium.com/the-mission/what-are-people-working-on-in-coffee-shops-cdf351e28b6',
    'https://medium.com/@maxbraun/my-bathroom-mirror-is-smarter-than-yours-94b21c6671ba',
    'https://medium.com/the-coffeelicious/facebook-turned-me-down-the-job-rejection-letter-that-turned-into-a-4-billion-check-962c658d876c',
    'https://medium.com/the-mission/50-ways-happier-healthier-and-more-successful-people-live-on-their-own-terms-31ba8f482448',
    'https://medium.com/startup-grind/i-got-scammed-by-a-silicon-valley-startup-574ced8acdff',
    'https://medium.com/the-mission/this-is-what-i-do-before-8-am-5ff27fcc985c',
    'https://medium.com/the-mission/the-greatest-sales-deck-ive-ever-seen-4f4ef3391ba0',
    'https://medium.com/the-mission/this-10-minute-routine-will-increase-your-clarity-and-creativity-2082630411d8',
    'https://medium.com/the-mission/the-most-motivational-statement-ever-in-3-words-84854eba5f13',
    'https://m.signalvnoise.com/being-tired-isn-t-a-badge-of-honor-fa6d4c8cff4e',
    'https://medium.com/the-mission/be-a-fucking-weirdo-bb842a0250d',
    'https://medium.com/the-mission/25-things-about-life-i-wish-i-had-known-10-years-ago-61d96e93a028',
    'https://medium.freecodecamp.com/5-key-learnings-from-the-post-bootcamp-job-search-9a07468d2331',
    'https://medium.freecodecamp.com/mark-zuckerberg-is-the-most-powerful-person-on-earth-but-is-he-responsible-5fbcaeb29ee1',
    'https://medium.com/the-mission/your-life-is-tetris-stop-playing-it-like-chess-4baac6b2750d',
    'https://medium.freecodecamp.com/tor-signal-and-beyond-a-law-abiding-citizens-guide-to-privacy-1a593f2104c3',
    'https://blog.heartsupport.com/a-letter-to-my-daughter-about-young-men-2bab2fca4971',
    'https://medium.com/the-mission/lfuck-working-hard-c41baa42b56d',
    'https://medium.com/the-mission/10-incredible-quotes-to-guide-your-life-355aab49fcf4',
    'https://medium.com/better-people/slack-i-m-breaking-up-with-you-54600ace03ea',
    'https://blog.prototypr.io/the-ideal-design-workflow-2c200b8e337d',
    'https://medium.com/chris-messina/silicon-valley-is-all-wrong-about-the-airpods-8204ede08f0f',
    'https://medium.com/re-write/instagram-and-the-cult-of-the-attention-web-how-the-free-internet-is-eating-itself-909b5713055e',
    'https://medium.com/swarm-nyc/complexion-reduction-a-new-trend-in-mobile-design-cef033a0b978',
    'https://medium.com/swlh/the-future-of-design-is-emotional-5789ccde17aa',
    'https://medium.com/desk-of-van-schneider/work-life-balance-is-bullshit-f51bf8b3767',
    ]
with open("webpages.csv", "w") as toWrite:
    writer = csv.writer(toWrite, delimiter=",")
    writer.writerow(["URL", "Sentence", "Tag", "True Value"])
    for url in urls:
        try:
            top_sentences = list(sumySummary(url))
            print 'URL', url
            tagTexts = extractSentences(url, top_sentences, writer)
        except Exception as e:
            print e
            print 'URL IS', url