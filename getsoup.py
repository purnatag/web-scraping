from bs4 import BeautifulSoup
from bs4.element import Comment
from random import randint
from time import sleep
from urllib.error import HTTPError, URLError

import requests
import difflib
import re
import os
   
# global list of pages crawled
urls=[]

# function to recursively find pages from the homepage
# and scrape each page
def scrape(site):
    # sleeping for random amounts of time to prevent getting banned
    #sleep(randint(1, 100))
    print(site)
    # getting the request from url
    try:
        response = requests.get(site)
        response.raise_for_status()
    except HTTPError as hpe:
        print("Error: Website not present.", hpe)
        return
    except URLError as ue:
        print("Error: Cannot find server.", ue)
        return
    
    # converting the text
    soup = BeautifulSoup(response.text, 'lxml')
    if soup is None:
        return
    try:
        getinfo(soup)
    except AttributeError as ae:
        print("Error: Attribute/s not found.", ae)
    
    anchors = soup.find_all('a')
    for i in range(len(anchors)):
        ele = anchors[i]
        if not ele.has_attr('href'):
            continue
        link = ele.attrs['href']
        
        if link.startswith('//'):
            site = 'https:' + link
        elif link.startswith('http'):
            site = link
               
        if "animalcrossing." in site and site not in  urls:
            urls.append(site) 
            # recursive call to scrape
            try:
                scrape(site)
            except KeyboardInterrupt:
                # user wants to stop
                print("Keyboard Interrupt: Exiting program.")
                os._exit(0)
            except Exception as exception:
                print("Error:", exception)
                # exit if there is an error
                continue
    return
    

# function to get text content from a page and update the corresponding file
# if the file has changed
def getinfo(soup):
    if soup.title == None:
        actitle = 'Untitled'+str(randint(1,500))
    else:
        actitle = soup.title.contents[0]
        actitle = re.sub('[^a-zA-Z]+', '-', actitle)

    # get summary from description in the meta tag for a Wiki page
    summary = 'Summary not available.'
    for s in soup.find_all('meta', {'name' : 'description', 'content':True}):
        summary = s.attrs['content']
        if not summary.startswith('#REDIRECT'):
            break
        else:
            summary = 'Summary not available.'

    # The file is saved to a folder, crawled-pages
    acfilepath = "crawled-pages/" + actitle + ".txt"
    acfile = open(acfilepath, 'w+', encoding='utf-8')

    # get content of the Wiki article
    texts = soup.findAll(string = True)
    visible_texts = filter(tag_visible, texts)  
    content = u" ".join(t.strip() for t in visible_texts)

    # rewrite file if there are changes
    newcontent = actitle + '\n\n' + summary + '\n\n' + content
    oldcontent = acfile.read()
    difflist = [li for li in difflib.ndiff(oldcontent, newcontent) if li[0] != ' ']
    if len(difflist) > 0:
        acfile.write(newcontent)
    acfile.close()


# filter function to get visible text only
def tag_visible(element):
    blacklist = ['style', 'script', 'head', 'title', 'meta', '[document]', 'noscript', 'header', 'html', 'input']
    if element.parent.name in blacklist:
        return False
    if isinstance(element, Comment):
        return False
    return True


# main function
if __name__ =="__main__":
    # get the website to be scraped
    homepage="https://animalcrossing.fandom.com/wiki/Animal_Crossing_Wiki"
    urls.append(homepage)
    # calling scraper function
    scrape(homepage)
    print("Finished scraping Animal Crossing Wiki!!")