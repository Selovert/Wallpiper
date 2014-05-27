import objc, urllib2, os, time, subprocess, re, sys

def http_req(url):
  try:
    req = urllib2.Request(url, headers={'User-Agent' : userAgent})
    con = urllib2.urlopen(req)
  except:
    con = None
  return con


def setWallpaper(filepath, desktop):
  subprocess.call(setWallpaper.ascript %(desktop, os.path.abspath(filepath)), shell=True)
setWallpaper.ascript = """/usr/bin/osascript<<END
tell application "System Events" to set picture of desktop %d to "%s"
END"""

def fetchLinks(menu):
  links = []
  for resolution in screens:
    url = pageUrl + resolution + '/'
    con = http_req(url)
    if con is None:
      menu.changeIcon('icon-dc')
      print 'Link fetch failed. Sleeping 5...'
      time.sleep(5)
      return []
    images = re.findall(r'href=[\'"](/wallpaper?[^\'" >]+.jpg)', con.read())
    for i, link in enumerate(images):
      if len(links) < len(images):
        links.append([link])
      else:
        links[i].append(link)
    print '> fetched new listing @ %s' %resolution
  return links
 
def fetchImage(link, index, screen, menu):
  url = baseUrl + link
  filename = os.path.basename(url)
  filename = os.path.splitext(filename)[0] + '_wpy.jpg'
  output = os.path.join(savePath, filename)
  con = http_req(url)
  if con is None:
    print 'Image fetch failed. Popping...'
    menu.changeIcon('icon-dc')
    return None
  CHUNK = 16 * 1024
  with open(output, 'wb') as fp:
    while True:
      chunk = con.read(CHUNK)
      if not chunk: break
      fp.write(chunk)
  print '> fetched image %s-%d: %s' %(str(index + 1).zfill(2), screen, filename)
  menu.systemNotification('Wallpiper', 'Downloaded ' + filename)
  return output
 
def clean():
  images = []
  for file in os.listdir(savePath):
    if '_wpy.jpg' in file:
      images.append(file)
  images = [os.path.join(savePath, i) for i in images]
  images.sort(key=lambda x: os.path.getmtime(x))
  while len(images) > archiveImages:
    os.remove(images.pop(0))
 
def runLoop(e,menu):
  global run
  global screens
  global links
  print '> sleep time: %d minutes' %sleepTime
  screensChecked = False
  while True:
    if menu.checkScreens() and (not screensChecked):
      menu.loadScreens()
      print "Reloading Screens"
      screensChecked = True
      pass
    links = fetchLinks(menu)
    while len(links) > 0:
      if run:
        if menu.checkScreens() and (not screensChecked):
          menu.loadScreens()
          print "Reloading Screens"
          screensChecked = True
          break
        menu.changeIcon('icon-dl')
        urls = links.pop()
        for screen, url in enumerate(urls):
          screen += 1
          image = fetchImage(url, len(links), screen, menu);
          if image:
            setWallpaper(image, int(screen))
            clean()
      menu.changeIcon('icon')
      if image:
        screensChecked = False
        e.wait(sleepTime*60)