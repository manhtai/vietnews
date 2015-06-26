from bs4 import BeautifulSoup
import httplib2
import re
import urllib.parse as urlparse # Python 3

with open('rss_source.txt') as r:
    rss = []
    for link in r:
        rss.append(link.strip())

with open('test.html') as f:
    test = f.read()

# r = rss[0]

def get_links(rss):
    links = set()
    h = httplib2.Http()
    for r in rss:
        print(r)
        resp, cont = h.request(r)
        soup = BeautifulSoup(cont)
        for link in soup.find_all('a'):
            url = link.get('href')
            if url and re.search(r'^[^?]+\.rss$', url):
                url = urlparse.urljoin(r, url)
                links.add(url)
    return links

def dump_links(links):
    with open('rss_link.txt', 'w') as f:
        for l in links:
            f.write(l+'\n')

if __name__ == '__main__':
    links = get_links(rss)
    dump_links(links)


