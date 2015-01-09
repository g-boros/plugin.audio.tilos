"""
    Plugin to browse the archive and listen to 
    live stream of Radio Tilos
"""

import sys, os, os.path, xbmcaddon
import xbmc, xbmcgui, xbmcplugin
from urllib2 import Request, urlopen, URLError
import urlparse
import urllib
from HTMLParser import HTMLParser
from shutil import rmtree, copy
import traceback
from pprint import pprint
import json
import time
import calendar
import datetime
import re


############################################
# Define required statics
############################################

__plugin__ = "Tilos"
__version__ = '0.0.3'
__author__ = 'Gabor Boros'
__date__ = '2014-07-28'
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')

BASE_URL = 'http://tilos.hu'
BASE_URL_PAGE = 'http://tilos.hu/page'
BASE_URL_SHOWS = BASE_URL + '/api/v0/show'
BASE_URL_EPISODES = BASE_URL_SHOWS + '/%s/episodes?from=%d&to=%d'
BASE_URL_EPISODES_BY_DATE = BASE_URL + '/api/v0/episode?start=%d&end=%d'
BASE_URL_SOUNDSTORE = BASE_URL + '/api/v1/mix'
HEADERS = {'User-Agent' : 'XBMC Plugin v0.0.3'} 
LIVE_URL_256 = 'http://stream.tilos.hu/tilos.m3u'
LIVE_URL_128 = 'http://stream.tilos.hu/tilos_128.mp3.m3u'

dialogProgress = xbmcgui.DialogProgress()
dialog = xbmcgui.Dialog()

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'songs')
Addon = xbmcaddon.Addon("plugin.audio.tilos")

mode = args.get('mode', None)
debug = True

############################################
# Functions
############################################


def log(msg):

    if (debug):
        if type(msg) not in (str, unicode):
            xbmc.log("[%s]: %s" % (__plugin__, type(msg)))
            pprint(msg)
        else:
            if type(msg) in (unicode,):
                msg = msg.encode('utf-8')
            xbmc.log("[%s]: %s" % (__plugin__, msg))


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def getURL(url):
    log(' > getURL(%s)' % (url))
    req = Request(url, None, HEADERS)
     
    try:
        response = urlopen(req)
     
    except URLError, e:
     
        if hasattr(e, 'reason'):
            log(getString(30003))
            log(getString(30004) + str(e.reason))
            xbmcgui.Dialog().ok(__addonname__, getString(30003), '', getString(30004) + str(e.reason))
     
        elif hasattr(e, 'code'):
            log(getString(30005))
            log(getString(30006) + str(e.code))
            xbmcgui.Dialog().ok(__addonname__, getString(30005), '', getString(30006) + str(e.code))
    
    except Exception, e:
        
        if hasattr(e, 'reason'):
            log(e.reason)
        
    else:
        return response.read()
        
    
def getString(stringID):
    return getUString(__addon__.getLocalizedString(stringID))
    

def getUString(string):
    return string.encode('utf8')


def listRootMenu():
    log(' > listRootMenu()')

    name_and_thumb = getCurrentShowName()
    li = xbmcgui.ListItem('%s [I]%s[/I]' % (getString(30007), getUString(name_and_thumb[0])), thumbnailImage=name_and_thumb[1])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=LIVE_URL_256, listitem=li, isFolder=False)

    li = xbmcgui.ListItem('%s [I]%s[/I]' % (getString(30008), getUString(getCurrentShowName()[0])), iconImage='')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=LIVE_URL_128, listitem=li, isFolder=False)

    url = build_url({'mode': 'listByDateYear', 'foldername': getString(30009)})
    li = xbmcgui.ListItem(getString(30009), iconImage='')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'musicShows', 'foldername': getString(30002)})
    li = xbmcgui.ListItem(getString(30002), iconImage='')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  
    url = build_url({'mode': 'talkShows', 'foldername': getString(30001)})
    li = xbmcgui.ListItem(getString(30001), iconImage='')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'listSoundStore', 'foldername': getString(30012)})
    li = xbmcgui.ListItem(getString(30012), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def listYear(): 
    log(' > listYear()')
    
    url = build_url({'mode': 'listByToday', 'foldername': getString(30010)})
    li = xbmcgui.ListItem(getString(30010), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'listByYesterday', 'foldername': getString(30011)})
    li = xbmcgui.ListItem(getString(30011), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    for year in range(datetime.date.today().year, 2008, -1):
        url = build_url({'mode': '%s_%s' % ('listByDateMonth', str(year)), 'foldername': str(year)})
        li = xbmcgui.ListItem(str(year), iconImage = '')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        
    xbmcplugin.endOfDirectory(addon_handle)


def getDayName(day):
    if day == 0:
        return getString(30025)
    if day == 1:
        return getString(30026)
    if day == 2:
        return getString(30027)
    if day == 3:
        return getString(30028)
    if day == 4:
        return getString(30029)
    if day == 5:
        return getString(30030)
    if day == 6:
        return getString(30031)


def getMonthName(month):
    if month == 12:
        return getString(30013)
    if month == 11:
        return getString(30014)
    if month == 10:
        return getString(30015)
    if month == 9:
        return getString(30016)
    if month == 8:
        return getString(30017)
    if month == 7:
        return getString(30018)
    if month == 6:
        return getString(30019)
    if month == 5:
        return getString(30020)
    if month == 4:
        return getString(30021)
    if month == 3:
        return getString(30022)
    if month == 2:
        return getString(30023)
    if month == 1:
        return getString(30024)
    else:
        return str(month)

def listMonth(year): 
    log(' > listMonth(%s)' % year)

    months = None
    if (str(datetime.date.today().year) == year):
        months = range(datetime.date.today().month, 0, -1)
    else:
        months = range(12, 0, -1) 

    for month in months:
        url = build_url({'mode': '%s_%s_%s' % ('listByDateDay', str(year), str(month)), 'foldername': month})
        li = xbmcgui.ListItem(getMonthName(month), iconImage = '')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        
    xbmcplugin.endOfDirectory(addon_handle)


def listDay(year, month): 
    log(' > listDay(%s,%s)' % (year, month))

    days = None
    if (str(datetime.date.today().year) == year and
        str(datetime.date.today().month) == month):
        days = range(datetime.date.today().day + 1, 0, -1)
    else:
        days = calendar.monthrange(int(year), int(month))

    for day in range(days[1], 0, -1):
        url = build_url({'mode': 'showsByDay_%s_%s_%s' % (year, month, str(day)), 
        'foldername': '%s_%s_%s' % (year, month, str(day))})
        li = xbmcgui.ListItem("%d - %s" % (day, getDayName(calendar.weekday(int(year), int(month), day))), iconImage = '')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
         
    xbmcplugin.endOfDirectory(addon_handle)


def listShowsByDay(year, month, day):
    log(' > listShowsByDay(%s,%s,%s)' % (year, month, day))

    startLocal = time.mktime(datetime.datetime(int(year), int(month), int(day), 0, 0, 0).timetuple())
    endLocal = time.mktime(datetime.datetime(int(year), int(month), int(day), 23, 59, 59).timetuple())

    page_data = getURL(BASE_URL_EPISODES_BY_DATE % (startLocal, endLocal))
    jdata = json.loads(page_data)

    startLocal = startLocal-60*60*1

    jdata.reverse()
    print jdata
    for episode in jdata:
        if (episode['plannedFrom'] < endLocal and
            episode['plannedFrom'] >= startLocal and
            episode.get('m3uUrl')):

            show = episode['show']
            title = '%s - %s' % (datetime.datetime.fromtimestamp(episode['plannedFrom']).strftime('%H:%M'),
                                 show['name'])

            li = xbmcgui.ListItem(title)

            li.setInfo('music', {'title': title,
                                 'artist': show['name'],
                                 'year': year})
            li.setProperty('IsPlayable', 'true')

            if show['banner'] is not None:
                li.setThumbnailImage(show['banner'])

            mp3Url = re.sub('.m3u', '.mp3', episode['m3uUrl'])
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=mp3Url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)


def listShows(type):
    log(' > listShows(%s)' % type)
  
    page_data = getURL(BASE_URL_SHOWS)  
    jdata = json.loads(page_data)

    for list in jdata:
        if (list['type'] == type):
            url = build_url({'mode': '%s_%s_%s' % ('list', getUString(list['alias']), getUString(list['name'])), 'foldername': getUString(list['name'])})
            li = xbmcgui.ListItem(getUString(list['name']))
            if list['banner'] is not None:
                li.setThumbnailImage(list['banner'])

            if list['definition'] is not None:
                li.setInfo('music', {'title': list['definition']})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
            
    xbmcplugin.addSortMethod( handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(addon_handle)


def listShow(alias, name):
    log(' > listShow(%s)' % alias)
    
    # Get Show information
    page_data = getURL(BASE_URL_SHOWS + '/' + alias)
    jdata_list = json.loads(page_data)
    
    artist = ''
    for contributor in jdata_list['contributors']:
        artist += ' %s,' % (getUString(contributor['author']['name']))

    page_data = getURL("%s/%s" % (BASE_URL_SHOWS, alias))
    jdata_show = json.loads(page_data)
    thumbnail = jdata_show['banner']

    artist = artist[:-1]
    # Get all available episodes since 2009.01.01
    startDate = calendar.timegm(datetime.datetime(2009,01,01,0,0).utctimetuple())
    endDate = calendar.timegm(datetime.datetime.now().utctimetuple())
    page_data = getURL(BASE_URL_EPISODES % (jdata_list['id'], startDate, endDate))
    jdata_episode = json.loads(page_data)
    
    for episode in jdata_episode:
        episode_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(episode['plannedFrom']))
        episode_year = time.strftime('%Y', time.localtime(episode['plannedFrom']))

        li = xbmcgui.ListItem(episode_date)

        li.setInfo('music', {'title': '%s %s' % (name, episode_date),
                             'artist': artist,
                             'year': episode_year})
        if thumbnail is not None:
            li.setThumbnailImage(thumbnail)

        li.setProperty('IsPlayable', 'true')
        mp3Url = re.sub('.m3u', '.mp3', episode['m3uUrl'])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=mp3Url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

def getCurrentShowName():
    log(' > getCurrentShowName')

    now = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    start = round((now - 3 * 60 * 60) / 10) * 10
    end = start + (8 * 60 * 60)

    page_data = getURL(BASE_URL_EPISODES_BY_DATE % (start, end))
    jdata = json.loads(page_data)
 
    for episode in jdata:
        if (episode['plannedFrom'] <= now and episode['plannedTo'] > now):
            list = episode['show']
            return ' - %s' % list['name'].strip(), list['banner']

    return ''


def listSoundStore():
    log(' > listSoundStore()')

    url = build_url({'mode': 'listSoundStoreTALE', 'foldername': getString(30032)})
    li = xbmcgui.ListItem(getString(30032))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'listSoundStoreDJ', 'foldername': getString(30033)})
    li = xbmcgui.ListItem(getString(30033))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'listSoundStoreGUESTDJ', 'foldername': getString(30034)})
    li = xbmcgui.ListItem(getString(30034))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'listSoundStoreSHOW', 'foldername': getString(30036)})
    li = xbmcgui.ListItem(getString(30036))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )    
    xbmcplugin.endOfDirectory(addon_handle)


def listSoundStoreCategory(category):
    log(' > listSoundStoreCategory(%s)' % category)

    page_data = getURL('%s?category=%s' % (BASE_URL_SOUNDSTORE, category))  
    jdata = json.loads(page_data)
 
    for list in jdata:
        itemDate = list['date'] + ": " if list['date'] is not None else ''
        itemAuthor = list['author'] + ": " if list['author'] != '' else ''

        li = xbmcgui.ListItem('%s[B]%s[/B]%s' % (getUString(itemDate),
                                                 getUString(itemAuthor),
                                                 getUString(list['title'])))

        li.setInfo('music', {'title': list['title'],
                             'artist': list['author'],
                             'year': itemDate})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=list['link'], listitem=li, isFolder=False)
        
    xbmcplugin.endOfDirectory(addon_handle)


def testInfoLabel(play):
    log(' > testInfoLabel()')
    m3uFile = getURL('https://tilos.hu/mp3/tilos-20141224-200000-221500.m3u')
    for line in m3uFile.readlines():
        print line

    return

    # file = '/Users/gabor/Downloads/05 - Pocket Calculator.mp3'

    if not play:
        url = build_url({'mode': 'testInfoLabelPlay', 'foldername': 'testInfoLabelPlay'})
        li = xbmcgui.ListItem(label='[B]%s[/B]' % 'tilos-20141230-100000-123000.mp3', label2='myTitle')
        li.setInfo('music', {'title': 'myTitle', 'artist': 'myArtist'})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=file, listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle)
    # else:
        # xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(file)

############################################
# Start plugin
############################################
# log(' > mode: ' + mode[0] if mode is not None else '')

if mode is None:
    listRootMenu()
elif mode[0] == 'talkShows':
    listShows(1)
elif mode[0] == 'musicShows':
    listShows(0)
elif mode[0].startswith('list_'):
    listShow(mode[0].split('_')[1], mode[0].split('_')[2])
elif mode[0].startswith('listByDateYear'):
    listYear()
elif mode[0].startswith('listByDateMonth'):
    listMonth(mode[0].split('_')[1:][0])
elif mode[0].startswith('listByDateDay'):
    listDay(mode[0].split('_')[1], mode[0].split('_')[2])
elif mode[0].startswith('listByToday'):
    year = str(datetime.date.today().year)
    month = str(datetime.date.today().month)
    day = str(datetime.date.today().day)
    listShowsByDay(year, month, day)    
elif mode[0].startswith('listByYesterday'):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    year = str(yesterday.year)
    month = str(yesterday.month)
    day = str(yesterday.day)
    listShowsByDay(year, month, day)    
elif mode[0].startswith('showsByDay'):
    year = mode[0].split('_')[1]
    month = mode[0].split('_')[2]
    day = mode[0].split('_')[3]
    listShowsByDay(year, month, day)    
elif mode[0] == 'listSoundStore':
    listSoundStore()
elif mode[0] == 'listSoundStoreTALE':
    listSoundStoreCategory('TALE')
elif mode[0] == 'listSoundStoreDJ':
    listSoundStoreCategory('DJ')
elif mode[0] == 'listSoundStoreGUESTDJ':
    listSoundStoreCategory('GUESTDJ')
elif mode[0] == 'listSoundStorePARTY':
    listSoundStoreCategory('PARTY')
elif mode[0] == 'listSoundStoreSHOW':
    listSoundStoreCategory('SHOW')

