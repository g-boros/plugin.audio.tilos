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

############################################
# Import own requests module
############################################
sys.path.append (xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) ))
# import resources.lib.requests
import requests


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
BASE_URL_DJMIX = BASE_URL_PAGE + '/hangtar'
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

############################################
# Functions
############################################

def log(msg):
    if type(msg) not in (str, unicode):
        xbmc.log("[%s]: %s" % (__plugin__, type(msg)))
        pprint (msg)
    else:
        if type(msg) in (unicode,):
            msg = msg.encode('utf-8')
        xbmc.log("[%s]: %s" % (__plugin__, msg))


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)
    
def getURL(url):
    # log(' > getURL(%s)' % (url))
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
    return Addon.getLocalizedString(stringID)
    
def getUString(string):
    return string.encode('utf8')

def listRootMenu():
    # log(' > listRootMenu()')

    url = build_url({'mode': 'play_%s' % (LIVE_URL_256), 'foldername': getString(30007)})
    li = xbmcgui.ListItem('%s %s' % (getString(30007), getCurrentShowName()), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'play_%s' % (LIVE_URL_128), 'foldername': getString(30008)})
    li = xbmcgui.ListItem('%s %s' % (getString(30008), getCurrentShowName()), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
 
    url = build_url({'mode': 'musicShows', 'foldername': getString(30002)})
    li = xbmcgui.ListItem(getString(30002), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  
    url = build_url({'mode': 'talkShows', 'foldername': getString(30001)})
    li = xbmcgui.ListItem(getString(30001), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
   
    url = build_url({'mode': 'listByToday', 'foldername': getString(30010)})
    li = xbmcgui.ListItem(getString(30010), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'listByYesterday', 'foldername': getString(30011)})
    li = xbmcgui.ListItem(getString(30011), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
 
    url = build_url({'mode': 'listByDateYear', 'foldername': getString(30009)})
    li = xbmcgui.ListItem(getString(30009), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'listSoundStore', 'foldername': getString(30012)})
    li = xbmcgui.ListItem(getString(30012), iconImage = '')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
 
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )    
    xbmcplugin.endOfDirectory(addon_handle)

def listYear(): 
    log(' > listYear()')

    for year in range(datetime.date.today().year, 2008, -1):
        url = build_url({'mode': '%s_%s' % ('listByDateMonth', str(year)), 'foldername': str(year)})
        li = xbmcgui.ListItem(str(year), iconImage = '')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        
    xbmcplugin.endOfDirectory(addon_handle)

def listMonth(year): 
    log(' > listMonth(%s)' % year)

    months = None
    if (str(datetime.date.today().year) == year):
        months = range(datetime.date.today().month, 0, -1)
    else:
        months = range(12, 0, -1) 

    for month in months:
        url = build_url({'mode': '%s_%s_%s' % ('listByDateDay', str(year), str(month)), 'foldername': month})
        li = xbmcgui.ListItem(str(month), iconImage = '')
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
        li = xbmcgui.ListItem(str(day), iconImage = '')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
         
    xbmcplugin.endOfDirectory(addon_handle)

def listShowsByDay(year, month, day):
#    log(' > listShowsByDay(%s,%s,%s)' % (year, month, day))

    startLocal = time.mktime(datetime.datetime(int(year),int(month),int(day),0,0,0).timetuple())
    endLocal = time.mktime(datetime.datetime(int(year),int(month),int(day),23,59,59).timetuple())

#    log(BASE_URL_EPISODES_BY_DATE % (startLocal, endLocal))
    page_data = getURL(BASE_URL_EPISODES_BY_DATE % (startLocal, endLocal))
    jdata = json.loads(page_data)

    startLocal = startLocal - 60 * 60 * 1 
 
    for episode in jdata:
        if (episode['plannedFrom'] < endLocal and
            episode['plannedFrom'] >= startLocal and
            episode.get('m3uUrl')):

            show = episode['show']
            title = '%s - %s' % (datetime.datetime.fromtimestamp(episode['plannedFrom']).strftime('%H:%M'), 
            show['name'])

            url = build_url({'mode': 'play_%s' % episode['m3uUrl'], 'foldername': 'title'})
            li = xbmcgui.ListItem(title, iconImage = '')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
            
   
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )    
    xbmcplugin.endOfDirectory(addon_handle)


#    endDate = calendar.timegm(datetime.datetime.now().utctimetuple())
def listShows(type):
    # log(' > listShows(%s)' % type)
  
    page_data = getURL(BASE_URL_SHOWS)  
    jdata = json.loads(page_data)
 
    for list in jdata:
        if (list['type'] == type):
            url = build_url({'mode': '%s_%s' % ('list', getUString(list['alias'])), 'foldername': getUString(list['name'])})
            li = xbmcgui.ListItem(getUString(list['name']))
            #li.setIconImage('')
            #li.setThumbnailImage(getUString(list['banner']))
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
            
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )    
    xbmcplugin.endOfDirectory(addon_handle)

def listShow(alias):
    # log(' > listShow(%s)' % alias)
    
    # Get Show information
    page_data = getURL(BASE_URL_SHOWS + '/' + alias)
    jdata_list = json.loads(page_data)
    
    artist = ''
    for contributor in jdata_list['contributors']:
        artist += ' %s (%s)' % (getUString(contributor['author']['name'])\
            , getUString(contributor['author']['alias']))
    
    # Get all available episodes since 2009.01.01
    startDate = calendar.timegm(datetime.datetime(2009,01,01,0,0).utctimetuple())
    endDate = calendar.timegm(datetime.datetime.now().utctimetuple())
    page_data = getURL(BASE_URL_EPISODES % (jdata_list['id'], startDate, endDate))
    jdata_episode = json.loads(page_data)
    
    for episode in jdata_episode:
        episode_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(episode['plannedFrom']))
        episode_year = time.strftime('%Y', time.localtime(episode['plannedFrom']))
        
        url = build_url({'mode': 'play_%s' % (episode['m3uUrl']), 'foldername': episode_date})
        li = xbmcgui.ListItem(episode_date)
        li.setInfo('music', {'artist' : artist, 'year' : episode_year, 'title' : 'lofasz' })
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )    
    xbmcplugin.endOfDirectory(addon_handle)

def getCurrentShowName():
    # log(' > getCurrentShowName')

    now =  calendar.timegm(datetime.datetime.utcnow().utctimetuple()) 
    start =  round((now - 3 * 60 * 60) / 10) * 10
    end =  start + (8 * 60 * 60)

#    log(BASE_URL_EPISODES_BY_DATE % (start, end))
    page_data = getURL(BASE_URL_EPISODES_BY_DATE % (start, end))
    jdata = json.loads(page_data)
 
    for episode in jdata:
        if (episode['plannedFrom'] <= now and episode['plannedTo'] > now):
            list = episode['show']
            return ' - %s' % list['name'].strip()

    return ''

def listSoundStore():
    log(' > listSoundStore()')

#    print(getURL(BASE_URL_DJMIX))
#    r = requests.get(BASE_URL_SOUNDSTORE)
#    print(len(r.content))


def playShow(file):
    # log(' > playShow(%s)' % file)

#    li = xbmcgui.ListItem('lofasz')
#    li.setInfo('music', {'artist' : 'eloado', 'year' : 'ev', 'title' : 'lofaszTitle' })
#    xbmcplugin.addDirectoryItem(handle=addon_handle, url=file, listitem=li, isFolder=False)
#
#    xbmcplugin.endOfDirectory(addon_handle)

    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER).play(file)
#    if (xbmc.Player().isPlaying()):
#         log(' Playing..')

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
    listShow(mode[0].split('_')[1])
elif mode[0].startswith('play_'):
    playShow(''.join(mode[0].split('_')[1:]))
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
elif mode[0].startswith('listSoundStore'):
    listSoundStore()
