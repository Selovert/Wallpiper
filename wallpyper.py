# wallpyper version 0.5 for Mac OS
# scrapes random images from interfacelift.com
# author: Greg Berardinelli
# todo: support multi-monitor images

# wallpaper save directory
targetDir = '~/Pictures/Wallpapers'

# number of image files to retain per screen resolution
archiveImages = 5

# default rotation interval in minutes (can also be provided as first argument)
sleepTime = 30

#####

import urllib2, os, time, subprocess, re, sys, AppKit

try:
  targetDir = os.path.abspath(os.path.expanduser(targetDir))
  if not os.path.exists(targetDir): raise
except:
  raise Exception('invalid target directory specified')
  
try:
  sleepTime = int(sys.argv[1])
except:
  if len(sys.argv) > 1:
    print '> invalid sleep time specified (expected integer)'

baseUrl = 'http://interfacelift.com'
pageUrl = baseUrl + '/wallpaper/downloads/random/x/'

def fetchLinks():
  sprint('> fetching links...')
  for screen in screens:
    resolution = screen['resolution']
    url = pageUrl + resolution + '/'
    request = httpReq(url)
    images = re.findall(r'href=[\'"](/wallpaper?[^\'" >]+.jpg)', request.read())
    screen['urls'] = images
    print '> fetched new listing @ %s' %resolution

def fetchImage(link, index, screen):
  sprint('> fetching image...')
  url = baseUrl + link
  filename = os.path.basename(url)
  filename = os.path.splitext(filename)[0] + '_wpy.jpg'
  output = os.path.join(targetDir, filename)
  request = httpReq(url)
  with open(output, 'wb') as f:
    while True:
      chunk = request.read(16 * 1024)
      if not chunk: break
      f.write(chunk)
  print '> fetched image %s-%d: %s' %(str(index + 1).zfill(2), screen, filename)
  return output

def updateScreens():
  global screens
  current = ["%sx%s" %(int(screen.frame().size.width), int(screen.frame().size.height)) for screen in AppKit.NSScreen.screens()]
  for display, resolution in enumerate(current):
    try:
      if resolution != screens[display]['resolution']:
        raise
    except:
      screens = [{'resolution': c, 'urls': []} for c in current]
      break
  if len(screens) == 1 & len(screens[0]['urls']) != 0: return
  if reduce(lambda i, j: i * j, [len(screen['urls']) for screen in screens]) != 0: return
  fetchLinks()
screens = []

def setWallpaper(filepath, display):
  subprocess.call(setWallpaper.script %(display, os.path.abspath(filepath)), shell=True)
setWallpaper.script = """/usr/bin/osascript<<END
tell application "System Events" to set picture of desktop %d to "%s"
END"""
  
def clean():
  images = {}
  for file in os.listdir(targetDir):
    match = re.search('_(\d+x\d+)_wpy.jpg', file)
    if match:
      resolution = match.group(1)
      path = os.path.join(targetDir, file)
      try:
        images[resolution].append(path)
      except:
        images[resolution] = [path]
  for resolution, files in images.iteritems():
    files.sort(key=lambda x: os.path.getmtime(x))
    while len(files) > archiveImages:
      os.remove(files.pop(0))
    
def sleep(minutes):
  for i in xrange(minutes, 0, -1):
    suffix = 's' if i != 1 else ''
    sprint('> sleeping for %s minute%s' %(i, suffix))
    time.sleep(60)
    
def httpReq(url):
  req = urllib2.Request(url, headers={'User-Agent' : 'AppleWebKit/537.36'}) 
  con = urllib2.urlopen(req)
  return con

def sprint(string):
  if len(string) > sprint.longest:
    sprint.longest = len(string)
  while len(string) < sprint.longest:
    string = string + ' '
  sys.stdout.write('\r%s\r' %string)
  sys.stdout.flush()
sprint.longest = 0

def main():
  print '> sleep time: %d minutes' %sleepTime
  while True:
    updateScreens()
    for display, screen in enumerate(screens):
      display += 1
      image = fetchImage(screen['urls'].pop(), len(screen['urls']), display);
      setWallpaper(image, display)
      clean()
    try:
      sleep(sleepTime)
    except KeyboardInterrupt:
      pass

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    clean()
    sprint('')