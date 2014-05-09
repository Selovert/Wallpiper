import objc, threading, re, os, time, subprocess, sys, urllib, urllib2, pickle, switcher, json
from Cocoa import *
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from distutils.version import LooseVersion


### Configs ###
# version number
version = '0.5.3'
shouldUpgrade = False
# poach one of the BTT internal images to get things rolling
status_images = {'icon':'wallpiper.png','icon-dl':'wallpiper-dl.png','icon-dc':'wallpiper-dc.png','icon-gray':'wallpiper-gray.png','icon-alert':'wallpiper-alert.png'}
# Settings file path
settingsPath = os.path.expanduser('~/.wallpiper')
# Start getting wallpapers on app launch
autoLaunch = 0
# Auto Detect Screen Resolutions
autoDetect = 1
# Link to update from
updateUrl = "https://sourceforge.net/projects/wallpiper/files/latest/download"
# number of image files to retain per screen resolution
switcher.archiveImages = 5
# default rotation interval in minutes (can also be provided as first argument)
switcher.sleepTime = 30
# Path for saving wallpapers
switcher.savePath = os.path.expanduser("~/Pictures")
# URL to interfacelift
switcher.baseUrl = 'http://interfacelift.com'
# URL to random background page
switcher.pageUrl = switcher.baseUrl + '/wallpaper/downloads/random/x/'
# What browser to emulate
switcher.userAgent = 'AppleWebKit/537.36'


class settingsWindow(NSWindowController):
    pathBox = objc.IBOutlet()
    sleepBox = objc.IBOutlet()
    screenBox = objc.IBOutlet()
    screenSelector = objc.IBOutlet()
    autoLaunchCheckBox = objc.IBOutlet()
    autoDetectCheckBox = objc.IBOutlet()
    oldIndex = 0
 
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        self.updateDisplay()

    @objc.IBAction
    def open_(self, sender):
        switcher.savePath = self.openFile()
        self.pathBox.setStringValue_(switcher.savePath)

    @objc.IBAction
    def apply_(self,sender):
        self.saveSettings()
        self.close()

    @objc.IBAction
    def autodetectScreens_(self,sender):
        global autoDetect
        if self.autoDetectCheckBox.state() == 1: 
            self.oldIndex = 0
            self.saveSettings()
            loadScreens()
            self.updateDisplay()
            print switcher.screens

    @objc.IBAction
    def updateScreenBox_(self,sender):
        self.updateScreenBox()
        self.saveSettings()

    @objc.IBAction
    def debug_(self,sender):
        if self.autoLaunchCheckBox.state():
            print self.autoLaunchCheckBox.state()

    def updateDisplay(self):
        global autoLaunch
        global autoDetect
        self.populateScreens()
        self.updateScreenBox()
        self.pathBox.setStringValue_(switcher.savePath)
        self.sleepBox.setStringValue_(switcher.sleepTime)
        self.autoLaunchCheckBox.setState_(autoLaunch)
        self.autoDetectCheckBox.setState_(autoDetect)
        

    def openFile(self):
        pool = NSAutoreleasePool.alloc().init()
        panel = NSOpenPanel.openPanel()
        panel.setCanCreateDirectories_(True)
        panel.setCanChooseDirectories_(True)
        panel.setCanChooseFiles_(False)
        #… there are lots of options, you see where this is going…
        if panel.runModal() == NSOKButton:
            return panel.directory()
        return 
        pool.drain()
        del pool

    def populateScreens(self):
        self.screenSelector.removeAllItems()
        i = 1
        for screen in switcher.screens:
            self.screenSelector.addItemWithTitle_(str(i))
            i = i + 1

    def updateScreenBox(self):
        index = int(self.screenSelector.selectedItem().title()) - 1
        if (self.screenBox.stringValue() != '') and (index != self.oldIndex):
            switcher.screens[self.oldIndex] = self.screenBox.stringValue()
        self.screenBox.setStringValue_(switcher.screens[index])
        self.oldIndex = index

    def saveSettings(self):
        global autoLaunch
        global autoDetect
        switcher.savePath = self.pathBox.stringValue()
        switcher.sleepTime = self.sleepBox.intValue()
        autoLaunch = self.autoLaunchCheckBox.state()
        autoDetect = self.autoDetectCheckBox.state()
        if switcher.sleepTime == 0:
            switcher.sleepTime = 30
        index = int(self.screenSelector.selectedItem().title()) - 1
        switcher.screens[index] = self.screenBox.stringValue()
        settings = {'sleepTime':switcher.sleepTime, 'savePath':switcher.savePath, 'screens':switcher.screens, 'autoLaunch':autoLaunch, 'autoDetect':autoDetect}
        with open(os.path.expanduser('~/.wallpiper'), 'wb') as f:
            pickle.dump(settings, f)
        switcher.links = []

class Menu(NSObject):
    images = {}
    statusbar = None
    switcher.run = True

    def applicationDidFinishLaunching_(self, notification):
        global autoLaunch
        global shouldUpgrade
        statusbar = NSStatusBar.systemStatusBar()
        # Create the statusbar item
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        # Load all images
        for i in status_images.keys():
          self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])
        # Set initial image
        self.changeIcon('icon')
        # Let it highlight upon clicking
        self.statusitem.setHighlightMode_(1)
        # Set a tooltip
        self.statusitem.setToolTip_('Wallpiper')
        # Build a very simple menu
        self.menu = NSMenu.alloc().init()
        #Info bits!
        self.infoItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Idle...', '', '')
        self.infoItem.setEnabled_(False)
        self.menu.addItem_(self.infoItem)
        #Separator for the info bits
        self.infoSeparator = NSMenuItem.separatorItem()
        self.menu.addItem_(self.infoSeparator)
        # Start Cylcing
        self.startItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Start', 'start:', '')
        self.menu.addItem_(self.startItem)
        # Start Cylcing
        self.stopItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Pause', 'stopSwitcher:', '')
        # Skip Cycle
        self.skipItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Get new wallpaper now', 'skip:', '')
        #Separator for the functions/settings
        self.settingsSeparator = NSMenuItem.separatorItem()
        self.menu.addItem_(self.settingsSeparator)
        # Settings menu
        self.settingsItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Settings', 'settings:', '')
        self.menu.addItem_(self.settingsItem)
        # App Upgrade
        if shouldUpgrade:
            self.changeIcon('icon-alert')
            self.upgradeItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Upgrade', 'upgrade:', '')
            self.menu.addItem_(self.upgradeItem)

        self.debug = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Debug', 'debug:', '')
        self.menu.addItem_(self.debug)

        # Default event
        self.quitItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.addItem_(self.quitItem)
        # Bind it to the status item
        self.statusitem.setMenu_(self.menu)

        if autoLaunch:
            self.start_('')

    def start_(self, sender):
        print "Starting..."
        global e
        global t
        restart = False
        if switcher.run is False: restart = True
        if switcher.run and threading.activeCount() == 1:
            e = threading.Event()
            t = threading.Thread(target=switcher.runLoop, args=(e,self))
            t.daemon = True
            t.start()
        else:
            switcher.run = True
        self.menu.removeItem_(self.startItem)
        self.menu.insertItem_atIndex_(self.stopItem, 2)
        self.menu.insertItem_atIndex_(self.skipItem, 3)
        if restart:
            e.set()
            time.sleep(.01)
            e.clear()

    def stopSwitcher_(self, sender):
        print "Pausing..."
        switcher.run = False
        self.menu.removeItem_(self.stopItem)
        self.menu.removeItem_(self.skipItem)
        self.menu.insertItem_atIndex_(self.startItem, 2)
        self.changeIcon('icon-gray')


    def skip_(self, sender):
        print "Skipping..."
        global e
        e.set()
        time.sleep(.01)
        e.clear()


    def settings_(self, sender):
        global viewController
        viewController = settingsWindow.alloc().initWithWindowNibName_("Settings")
        # Show the window
        viewController.showWindow_(viewController)
        viewController.ReleasedWhenClosed = True
        # Bring app to top
        NSApp.activateIgnoringOtherApps_(True)

    def upgrade_(self, sender):
        self.statusitem.setEnabled_(False)
        def upgrade(self):
            filePath = os.path.expanduser('~/Downloads/Wallpiper.zip')
            urllib.urlretrieve ("http://sourceforge.net/projects/wallpiper/files/Wallpiper.zip/download", filePath)
            os.chdir("../../../")
            subprocess.call(["rm","-rf","Wallpiper.app"])
            subprocess.call(["unzip",filePath,"-d","."])
            subprocess.call(["rm","-rf","__MACOSX"])
            subprocess.call(["rm","-rf",filePath])
            os.system("sleep 2 && open Wallpiper.app &")
            AppHelper.stopEventLoop()
        t = threading.Thread(target=upgrade, args=(self,))
        t.daemon = True
        t.start()

    def changeIcon(self,iconName):
        self.statusitem.setImage_(self.images[iconName])

    def loadScreens(self):
        loadScreens()

    def checkScreens(self):
        i = 0
        if len(NSScreen.screens()) != len(switcher.screens):
          return True
        for screen in NSScreen.screens():
            screenID = switcher.screenNumbers.append(int(screen.deviceDescription()['NSScreenNumber']))
            if screenID != switcher.screenNumbers[i] and i != 0:
                return True
        return False

    def debug_(self, sender):
        print switcher.screenNumbers
        print "AAAAAHHH"

def loadSettings():
    global autoLaunch
    global autoDetect
    with open(settingsPath, 'r') as f:
        settings = pickle.load(f)
        switcher.screens = settings['screens']
        switcher.sleepTime = settings['sleepTime']
        switcher.savePath = settings['savePath']
        autoLaunch = settings['autoLaunch']
        autoDetect = settings['autoDetect']

def loadScreens():
    switcher.screens = []
    switcher.screenNumbers = []
    x = []; y = []; k = []; i = 0
    for screen in NSScreen.screens():
        x.append(int(screen.frame().size.width))
        y.append(int(screen.frame().size.height))
        k.append(int(screen._.backingScaleFactor))
        switcher.screens.append(str(x[i]*k[i]) + 'x' + str(y[i]*k[i]))
        switcher.screenNumbers.append(int(screen.deviceDescription()['NSScreenNumber']))
        i = i + 1
    print switcher.screenNumbers

def checkForUpgrade():
    global version
    global shouldUpgrade
    try:
        siteVersion = json.loads(urllib2.urlopen("https://sourceforge.net/rest/p/wallpiper/").read())['short_description']
    except:
        seiteVersion = '0'
    if LooseVersion(siteVersion) > LooseVersion(version):
        shouldUpgrade = True

if __name__ == "__main__":
    if os.path.isfile(settingsPath): 
        loadSettings()
        if autoDetect:
            loadScreens()
    else: 
        loadScreens()
    checkForUpgrade()
    app = NSApplication.sharedApplication()
    delegate = Menu.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

