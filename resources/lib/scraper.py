import urllib2
import re
from BeautifulSoup import BeautifulSoup

CATEGORIES = ({'name': 'Videos, Trailer und Teaser', 'path': u'games/videos'},
              {'name': 'Retropolis', 'path': u'games/retropolis/videos'},
              {'name': 'RIP', 'path': u'games/rest-in-peace/videos'})

URL_PREFIX = u'http://www.onlinewelten.com'


def getVideos(path, page):
    url = '%s/%s/seite-%s' % (URL_PREFIX, path, page)
    tree = __getTree(url)
    section = tree.find('div', {'id': 'videos'})
    video_frames = section.findAll('li', {'class': re.compile('c[12]')})
    videos = list()
    r_image = re.compile('background-image:url\((.+?)\);')
    for frame in video_frames:
        link = frame.find('a')
        # title
        if link.span:
            title = '%s - %s' % (link.strong.string, link.span.string)
        else:
            title = link.strong.string
        # url
        url = link['href'][1:]
        # date
        date = frame.find('span', {'class': 'date'}).string
        # image
        image = URL_PREFIX + re.search(r_image,
                                       frame.find('img')['style']).group(1)
        # description
        description = frame.find('p', {'class': 'teaser'}).string
        has_next_page = True
        videos.append({'title': title,
                       'image': image,
                       'url': url,
                       'description': description,
                       'views': '0',
                       'date': '',
                       'length': ''})
    return videos, has_next_page


def __getTree(url, data_dict=None):
    if data_dict:
        post_data = urlencode(data_dict)
    else:
        post_data = ' '
    req = urllib2.Request(url, post_data)
    response = urllib2.urlopen(req).read()
    tree = BeautifulSoup(response, convertEntities=BeautifulSoup.HTML_ENTITIES)
    return tree


def getVideoFile(url):
    full_url = '%s/%s' % (URL_PREFIX, url)
    tree = __getTree(full_url)
    r_stream_url = re.compile('\'(/playvideoflow/[0-9a-f]+?)\';')
    js_code = tree.find('script', text=r_stream_url)
    stream_url = re.search(r_stream_url, js_code).group(1)
    return URL_PREFIX + stream_url


def getCategories():
    return CATEGORIES
