import threading, time, os, switcher

# wallpyper version 0.3 for Mac OS
# author: Greg Berardinelli
 
# screen resolutions
switcher.screens = ['2560x1440', '1920x1200']
 
# wallpaper save directory
switcher.targetDir = os.path.abspath(os.path.expanduser('~/Pictures/Wallpaper'))
 
# default rotation interval in minutes (can also be provided as first argument)
switcher.sleepTime = 30
 
# number of image files to retain (must be larger than the number of screens)
switcher.archiveImages = 10
 
#####
 

 
switcher.baseUrl = 'http://interfacelift.com'
switcher.pageUrl = switcher.baseUrl + '/wallpaper/downloads/random/x/'
switcher.userAgent = 'AppleWebKit/537.36'



# ---------------------------------------------------------
e = threading.Event()
t = threading.Thread(target=switcher.runLoop, args=(e,))
t.daemon = True
t.start()

time.sleep(5)
e.set()
time.sleep(.01)
e.clear()
time.sleep(200)


