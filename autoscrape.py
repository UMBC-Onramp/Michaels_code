from bs4 import BeautifulSoup
import requests
import time
import json

def soupify(url):
    req = requests.get(url)
    content = req.text
    soup = BeautifulSoup(content, 'lxml')
    return soup

def source(url):
    #returns name of articles source
    ends = ['com', 'gov']
    phrase = url.split('.')[1][0:3]
    if phrase in ends:
        temp = url.split('.')[0]
        return temp.split('/')[2]
    else:
        return url.split('.')[1]
        
def article_date(soup, source):
    #publicaiton date
    if source == 'fireeye':
        return soup.find('time', class_='entry-date').text

    elif source == 'fortinet':
        date = soup.find('span', class_='b15-blog-meta__date').text
        return date[3:]

    elif source == 'recordedfuture':
        date = soup.find('p', class_='name-date') 
        return date.text.split('•')[0]

    elif source == 'securityintelligence':
        date = soup.find('div', class_='single__date-and-time')
        return date.text

    elif source == 'juniper':
        date = soup.find('span', class_='entry-date')
        return date.text

    elif source == 'kaspersky':
        date = soup.find('time')
        return date.text

    elif source == 'paloaltonetworks':
        date = soup.find('time')
        date = date.text
        date = date.split()
        date = date[:3]
        separator = ' '
        date = separator.join(date)
        return date

    elif source == 'securonix':
        date = soup.find('p', class_='single-pub-date')
        date = date.text
        date = date.split()
        date = date[2:]
        separator = ' '
        date = separator.join(date)
        return date
    
    else: 
        return "not available"
    
       
def date_accessed():
    return time.ctime()

def text(soup, source):
    if source == 'fireeye':
        words = soup.find('div', class_='c00 c00v0')
        return words.text

    elif source == 'fortinet':
        words = soup.find('div', class_='cmp cmp-text aem-GridColumn aem-GridColumn--default--12')  
        return words.text

    elif source == 'recordedfuture':
        words = soup.find('article', class_='col s12 m12 l8 blog-detail')
        return words.text

    elif source =='securityintelligence':
        words = soup.find('div', class_= 'single__content-itself')
        return words.text

    elif source == 'juniper':
        words = soup.find('div', class_='entry-content')
        return words.text

    elif source == 'kaspersky':
        words = soup.find('div', class_='c-article__content')
        return words.text
    
    elif source == 'paloatonetworks':
        words = soup.find('div', class_='entry-conted article-description')
        return words.text

    else:
        #securonix 
        #to scrape text from most articles
        words = soup.find_all('p')
        str = ''
        for ele in words:
            str += ele.text
        return str
    

def jsonify(url):
    #put data scraped in dictionary format
    dict = {}
    soup = soupify(url)
    name = source(url)
    dict['source'] = name 
    dict['url'] = url
    dict['accesed'] = date_accessed()
    dict['date'] = article_date(soup, name)
    dict['text'] = text(soup, name)
    return dict

def get_rss(url):
    #take links from rss page and put them in a list
    name = source(url)
    soup = soupify(url)
    print(name)
    links = []
    
    if name == 'fireeye':
        tags = soup.find_all('link')
        for ele in tags:
            ele = str(ele).split('"')[1]
            links.append(ele)
        links.pop(0)
        links.pop(0)
        
    
    if name == 'feedburner':
        tags = soup.find_all('feedburner:origlink')
        for ele in tags:
            ele = str(ele).split('>')
            ele = ele[1].split('<')
            links.append(ele[0])
    
    
    if name == 'securonix':
        tags = soup.find_all('a')
        for ele in tags:
            ele = str(ele).split('"')
            links.append(ele[1])
        for ele in links:
            if ele == 'https://www.securonix.com':
                links.remove(ele)
        
    
    if name == 'recordedfuture':
        tags = soup.find_all('item')
        for ele in tags:
            ele = ele.find("a")
            url = str(ele).split('"')[1]
            links.append(url)

    
    if name == 'securityintelligence':
        tags = soup.find_all('item')
        for ele in tags:
            ele = ele.find("a")
            url = str(ele).split('"')[1]
            links.append(url)

    
    if name == 'juniper':
        tags = soup.find_all('guid')
        for ele in tags:
            ele = str(ele).split('>')
            ele = str(ele[1]).split('<')
            links.append(ele[0])

       
    if name == 'kaspersky':
        print('running')
        tags = soup.find_all('guid')
        for ele in tags:
            ele = str(ele).split('>')
            ele = str(ele[1]).split('<')
            links.append(ele[0])
        
    return links

def run_one(url):
    #for collecting data from a single url
    json_list = []
    json_list.append(jsonify(url))
    return json_list

def run_list(list):
    #for collecting data from a list of urls
    json_list = []
    for ele in range(len(list)):
        print(list[ele])
        json_list.append(jsonify(list[ele]))
    return json_list
        
def run_rss(url):
    #collects data from all links on an rss page
    links = get_rss(url)
    return run_list(links)

def file_write(data):
    #method for writing to each file
    for ele in data:
        json_data = json.dumps(ele)
        f.write(json_data)
        f.write('\n')
    

#List for testing data collection on different sources
# Not all of these sources scrape the publication date properly
checks = ['https://www.fireeye.com/blog/executive-perspective/2021/01/cti-function-intro-to-primary-source-intelligence.html', 
'https://www.securonix.com/securonix-threat-research-lab/', 'https://towardsdatascience.com/web-scraping-basics-82f8b5acd45c',
'https://realpython.com/python-requests/#the-get-request', 
'https://www.fortinet.com/blog/threat-research/spearphishing-attack-uses-covid-21-lure-to-target-ukrainian-government', 
'https://www.recordedfuture.com/hackmachine-enables-fraud-intrustion/', 'https://securityintelligence.com/posts/zero-trust-why-it-matters-data-security/',
'https://www.netskope.com/blog/cloud-threats-memo-beware-of-leaky-buckets-and-cloud-apps', 'https://www.mcafee.com/blogs/other-blogs/mcafee-labs/tales-from-the-trenches-a-lockbit-ransomware-story/',
'https://blogs.juniper.net/en-us/service-provider-transformation/simplifying-the-enterprise-edge-cloud', 'https://www.kaspersky.co.in/blog/open-tip-updated/22067/',
'https://www.paloaltonetworks.com/blog/prisma-cloud/top-takeaways-from-the-unit-42-cloud-threat-report/'] 


#all sources in this list can have their data scraped properly and can have data taken directly from rss page
works = ['https://www.fortinet.com/blog/threat-research/spearphishing-attack-uses-covid-21-lure-to-target-ukrainian-government', 
'https://www.fireeye.com/blog/executive-perspective/2021/01/cti-function-intro-to-primary-source-intelligence.html', 
 'https://www.securonix.com/securonix-threat-research-lab/', 
 'https://www.recordedfuture.com/hackmachine-enables-fraud-intrustion/', 'https://securityintelligence.com/posts/zero-trust-why-it-matters-data-security/',
 'https://blogs.juniper.net/en-us/service-provider-transformation/simplifying-the-enterprise-edge-cloud', 'https://www.kaspersky.co.in/blog/open-tip-updated/22067/', 
 'https://www.paloaltonetworks.com/blog/prisma-cloud/top-takeaways-from-the-unit-42-cloud-threat-report/']

with open('test.jsonl', 'w') as f:
    #all of these scrape urls from the rss and feed and place data in another file in json format
    fireeye_rss = run_rss('https://www.fireeye.com/blog/threat-research/_jcr_content.feed') 
    file_write(fireeye_rss)
    fortinet_rss = run_rss('http://feeds.feedburner.com/fortinet/blog/threat-research')
    file_write(fortinet_rss)
    securonix_rss = run_rss('https://www.securonix.com/blog/feed/')
    file_write(securonix_rss)
    recorded_rss = run_rss('https://www.recordedfuture.com/blog/feed/')
    file_write(recorded_rss)
    security_rss = run_rss('https://securityintelligence.com/feed/')
    file_write(security_rss)
    palo_rss = run_rss('http://feeds.feedburner.com/PaloAltoNetworks')
    file_write(palo_rss)
    kaspersky_rss = run_rss('https://www.kaspersky.co.in/blog/feed/')
    file_write(kaspersky_rss)
    juniper_rss = run_rss('https://blogs.juniper.net/threat-research/feed')
    file_write(juniper_rss)
    
    

    

