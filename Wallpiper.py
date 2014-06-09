import objc, threading, re, os, time, subprocess, sys, urllib, urllib2, pickle, switcher, json
from Cocoa import *
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from distutils.version import LooseVersion


### Configs ###
# version number
version = '0.5.6'
shouldUpgrade = False
upgradeChecked = False
# All our icons and states of those icons
status_images = {'icon':'wallpiper','icon-dl':'wallpiper-dl','icon-dc':'wallpiper-dc','icon-gray':'wallpiper-gray','icon-alert':'wallpiper-alert'}
# Settings file path
settingsPath = os.path.expanduser('~/.wallpiper')
# Start getting wallpapers on app launch
autoLaunch = 0
# Auto Detect Screen Resolutions
autoDetect = 1
# Link to update from
updateUrl = "https://sourceforge.net/projects/wallpiper/files/latest/download"
# number of image files to retain per screen resolution
switcher.archiveImages = 10
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
# development mode
devMode = True


class settingsWindow(NSWindowController):
    pathBox = objc.IBOutlet()
    sleepBox = objc.IBOutlet()
    screenBox = objc.IBOutlet()
    screenSelector = objc.IBOutlet()
    archiveImagesBox = objc.IBOutlet()
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
        self.populateScreens()
        self.updateScreenBox()
        self.pathBox.setStringValue_(switcher.savePath)
        self.sleepBox.setStringValue_(switcher.sleepTime)
        self.archiveImagesBox.setStringValue_(switcher.archiveImages)
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
        switcher.archiveImages = self.archiveImagesBox.intValue()
        autoLaunch = self.autoLaunchCheckBox.state()
        autoDetect = self.autoDetectCheckBox.state()
        if switcher.sleepTime == 0:
            switcher.sleepTime = 30
        index = int(self.screenSelector.selectedItem().title()) - 1
        switcher.screens[index] = self.screenBox.stringValue()
        settings = {'sleepTime':switcher.sleepTime, 'savePath':switcher.savePath, 'screens':switcher.screens, 'autoLaunch':autoLaunch, 'autoDetect':autoDetect, 'archiveImages':switcher.archiveImages}
        with open(os.path.expanduser('~/.wallpiper'), 'wb') as f:
            pickle.dump(settings, f)
        switcher.links = []
        switcher.titles = []
        switcher.detailURLs = []

class SystemNotification(NSObject):
    def notify(self, title, message, link = 0):
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(message)
        notification.setUserInfo_({'link':link})
     
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.setDelegate_(self)
        center.deliverNotification_(notification)

    def userNotificationCenter_shouldPresentNotification_(self, center, notification):
            return True

    def userNotificationCenter_didActivateNotification_(self, center, notification):
        info = notification.userInfo()
        link = info['link']
        if link:
            subprocess.Popen(['open', link])

class Menu(NSObject):
    # global notification
    images = {}
    statusbar = None
    detailURL = ''
    switcher.run = True
    # Initialize the notification center object
    notification = SystemNotification.alloc().init()
    # The current icon (when not loading or otherwise engaged)
    default_icon = 'icon'

    def applicationDidFinishLaunching_(self, notification):
        statusbar = NSStatusBar.systemStatusBar()
        # Create the statusbar item
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        # Load all images
        for i in status_images.keys():
          self.images[i] = NSImage.imageNamed_(status_images[i])
        # Set initial image
        self.changeIcon('icon', True)
        # Let it highlight upon clicking
        self.statusitem.setHighlightMode_(1)
        # Set a tooltip
        self.statusitem.setToolTip_('Wallpiper')
        # Build a very simple menu
        self.menu = NSMenu.alloc().init()
        self.menu.setDelegate_(self)
        # stop items from becoming selectable when they are not
        self.menu.setAutoenablesItems_(False)
        #Info bits!
        self.infoItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Idle...', 'info:', '')
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
        # Check for app upgrade
        self.checkUpgradeItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Check for Update', 'checkUpgrade:', '')
        self.menu.addItem_(self.checkUpgradeItem)
        # App Upgrade
        self.addUpgradeItem()

        if devMode:
            self.debug = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Debug', 'debug:', '')
            self.menu.addItem_(self.debug)

        # Default event
        self.quitItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.addItem_(self.quitItem)
        # Bind it to the status item
        self.statusitem.setMenu_(self.menu)

        if autoLaunch and not shouldUpgrade:
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

    def checkUpgrade_(self, sender):
        self.checkForUpgrade()
        self.addUpgradeItem()

    def checkForUpgrade(self):
        global shouldUpgrade
        try:
            siteVersion = json.loads(urllib2.urlopen("https://sourceforge.net/rest/p/wallpiper/").read())['short_description']
        except:
            siteVersion = '0'
        if LooseVersion(siteVersion) > LooseVersion(version):
            self.notification.notify('Wallpiper', 'Update available')
            shouldUpgrade = True

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

    def info_(self, sender):
        if self.detailURL is not '':
            subprocess.Popen(['open', self.detailURL])

    def changeIcon(self, iconName, default = False):
        global default_icon
        self.statusitem.setImage_(self.images[iconName])
        if default:
            self.default_icon = iconName

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

    def addUpgradeItem(self):
        global upgradeChecked
        if shouldUpgrade:
            self.changeIcon('icon-alert', True)
            self.upgradeItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Upgrade', 'upgrade:', '')
            self.menu.addItem_(self.upgradeItem)
            self.menu.removeItem_(self.checkUpgradeItem)
        elif upgradeChecked:
            self.notification.notify('Wallpiper', version + ' is the current version!')
        upgradeChecked = True

    def debug_(self, sender):
        print "AAAAAHHH"
        self.changeIcon('pipe')
        pass

def loadSettings():
    global autoLaunch
    global autoDetect
    with open(settingsPath, 'r') as f:
        settings = pickle.load(f)
        switcher.screens = settings['screens']
        switcher.sleepTime = settings['sleepTime']
        switcher.savePath = settings['savePath']
        switcher.archiveImages = settings['archiveImages']
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

if __name__ == "__main__":
    if os.path.isfile(settingsPath): 
        loadSettings()
        if autoDetect:
            loadScreens()
    else: 
        loadScreens()
    app = NSApplication.sharedApplication()
    delegate = Menu.alloc().init()
    delegate.checkForUpgrade()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

