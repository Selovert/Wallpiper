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
  titles = []
  detailURLs = []
  for resolution in screens:
    url = pageUrl + resolution + '/'
    con = http_req(url)
    if con is None:
      menu.changeIcon('icon-dc')
      print 'Link fetch failed. Sleeping 5...'
      time.sleep(5)
      return [[],[],[]]
    html = con.read()
    images = re.findall(r'href=[\'"](/wallpaper?[^\'" >]+.jpg)', html)
    details = re.findall(r'<div class="details">.+?<div class="display_actions">', html, re.DOTALL)
    for i, item in enumerate(details):
      rawInfo = re.search(r'<a href="(/wallpaper/details/.+?\.html)">(?!<|Full Info)(.+)?</a>', item).groups()
      title = rawInfo[1]
      detailURL = 'http://interfacelift.com/' + rawInfo[0]
      if len(titles) < len(details):
        titles.append([title])
        detailURLs.append([detailURL])
      else:
        titles[i].append(title)
        detailURLs[i].append(detailURL)

    for i, link in enumerate(images):
      if len(links) < len(images):
        links.append([link])
      else:
        links[i].append(link)
    print '> fetched new listing @ %s' %resolution
  return [links, titles, detailURLs]
 
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
    [links, titles, detailURLs] = fetchLinks(menu)
    while len(links) > 0:
      if run:
        if menu.checkScreens() and (not screensChecked):
          menu.loadScreens()
          print "Reloading Screens"
          screensChecked = True
          break
        menu.changeIcon('icon-dl')
        urls = links.pop()
        imageTitles = titles.pop()
        imageDetailURLs = detailURLs.pop()

        for screen, url in enumerate(urls):
          title = imageTitles[screen]
          detailURL = imageDetailURLs[screen]
          screen += 1
          image = fetchImage(url, len(links), screen, menu);
          if image:
            setWallpaper(image, int(screen))
            menu.notification.notify('Wallpiper: new wallpaper', title, detailURL)
            menu.infoItem.setEnabled_(True)
            menu.infoItem.setTitle_(title)
            menu.detailURL = detailURL
            clean()
      menu.changeIcon(menu.default_icon)
      if image:
        screensChecked = False
        e.wait(sleepTime*60)