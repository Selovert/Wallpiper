# wallpyper version 0.5.1 for Mac OS
# scrapes random images from interfacelift.com
# author: Greg Berardinelli & Tassilo Selover-Stephan (a bit)
# todo: support multi-monitor images

def fetchLinks():
  for screen in screens:
    resolution = screen['resolution']
    url = pageUrl + resolution + '/'
    request = httpReq(url)
    images = re.findall(r'href=[\'"](/wallpaper?[^\'" >]+.jpg)', request.read())
    screen['urls'] = images
    print '> fetched new listing @ %s' %resolution

def fetchImage(link, index, screen):
  url = baseUrl + link
  filename = os.path.basename(url)
  filename = os.path.splitext(filename)[0] + '_wpy.jpg'
  output = os.path.join(savePath, filename)
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
  for file in os.listdir(savePath):
    match = re.search('_(\d+x\d+)_wpy.jpg', file)
    if match:
      resolution = match.group(1)
      path = os.path.join(savePath, file)
      try:
        images[resolution].append(path)
      except:
        images[resolution] = [path]
  for resolution, files in images.iteritems():
    files.sort(key=lambda x: os.path.getmtime(x))
    while len(files) > archiveImages:
      os.remove(files.pop(0))
    
def httpReq(url):
  req = urllib2.Request(url, headers={'User-Agent' : 'AppleWebKit/537.36'}) 
  con = urllib2.urlopen(req)
  return con

def main():
  while True:
    updateScreens()
    for display, screen in enumerate(screens):
      display += 1
      image = fetchImage(screen['urls'].pop(), len(screen['urls']), display);
      setWallpaper(image, display)
      clean()
    try:
      time.sleep(sleepTime*60)
    except KeyboardInterrupt:
      pass

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    clean()