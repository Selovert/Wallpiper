import objc, threading, re, os, time, subprocess, sys, urllib2, pickle, switcher
from Cocoa import *
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper


### Configs ###
# poach one of the BTT internal images to get things rolling
status_images = {'icon':'wallpiper.png'}
# Settings file path
settingsPath = os.path.expanduser('~/.wallpiper')
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
# screen resolutions
switcher.screens = ['2560x1600', '1920x1200']


class settingsWindow(NSWindowController):
    global settingsWindowPool
    pathBox = objc.IBOutlet()
    sleepBox = objc.IBOutlet()
 
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        self.updateDisplay()

    @objc.IBAction
    def open_(self, sender):
        switcher.savePath = self.openFile()
        self.pathBox.setStringValue_(switcher.savePath)

    @objc.IBAction
    def apply_(self,sender):
        switcher.savePath = self.pathBox.stringValue()
        switcher.sleepTime = self.sleepBox.intValue()
        if switcher.sleepTime == 0:
            switcher.sleepTime = 30
        self.updateDisplay()
        self.saveSettings()
        self.close()
        

    def updateDisplay(self):
        self.pathBox.setStringValue_(switcher.savePath)
        self.sleepBox.setStringValue_(switcher.sleepTime)

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

    def saveSettings(self):
        settings = {'sleepTime':switcher.sleepTime, 'savePath':switcher.savePath}
        with open(os.path.expanduser('~/.wallpiper'), 'wb') as f:
            pickle.dump(settings, f)

class Menu(NSObject):
    images = {}
    statusbar = None
    switcher.run = True

    def applicationDidFinishLaunching_(self, notification):
        statusbar = NSStatusBar.systemStatusBar()
        # Create the statusbar item
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        # Load all images
        for i in status_images.keys():
          self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])
        # Set initial image
        self.statusitem.setImage_(self.images['icon'])
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
        self.menu.addItem_(self.skipItem)
        #Separator for the functions/settings
        self.settingsSeparator = NSMenuItem.separatorItem()
        self.menu.addItem_(self.settingsSeparator)
        # Settings menu
        self.settingsItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Settings', 'settings:', '')
        self.menu.addItem_(self.settingsItem)

        self.debug = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Debug', 'debug:', '')
        self.menu.addItem_(self.debug)

        # Default event
        self.quitItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.addItem_(self.quitItem)
        # Bind it to the status item
        self.statusitem.setMenu_(self.menu)

    def start_(self, sender):
        print "Starting..."
        global e
        global t
        if switcher.run and threading.activeCount() == 1:
            e = threading.Event()
            t = threading.Thread(target=switcher.runLoop, args=(e,))
            t.daemon = True
            t.start()
        else:
            switcher.run = True
        self.menu.removeItem_(self.startItem)
        self.menu.insertItem_atIndex_(self.stopItem, 2)

    def stopSwitcher_(self, sender):
        print "Pausing..."
        switcher.run = False
        self.menu.removeItem_(self.stopItem)
        self.menu.insertItem_atIndex_(self.startItem, 2)


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
        viewController.ReleasedWhenClosed = True;
        # Bring app to top
        NSApp.activateIgnoringOtherApps_(True)

    def debug_(self, sender):
        print"AAAAAHHH"

def loadSettings():
    with open(settingsPath, 'r') as f:
        settings = pickle.load(f)
        switcher.sleepTime = settings['sleepTime']
        switcher.savePath = settings['savePath']

if __name__ == "__main__":
    if os.path.isfile(settingsPath): 
        loadSettings()
    app = NSApplication.sharedApplication()
    delegate = Menu.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

