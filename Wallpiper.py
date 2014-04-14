import objc, threading, re, os, time, subprocess, sys, urllib2, switcher
from Cocoa import *
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper


### Configs ###
# poach one of the BTT internal images to get things rolling
status_images = {'icon':'wallpiper.png'}
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
switcher.screens = ['2560x1440', '1920x1200']


class settingsWindow(NSWindowController):
    pathBox = objc.IBOutlet()
    sleepBox = objc.IBOutlet()
 
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        self.updateDisplay()

    @objc.IBAction
    def open_(self, sender):
        switcher.savePath = self.openFile()
        self.updateDisplay()

    @objc.IBAction
    def apply_(self,sender):
        global sleepTime
        switcher.savePath = self.pathBox.stringValue()
        sleepTime = self.sleepBox.intValue()
        if sleepTime == 0:
            sleepTime = 30
        self.updateDisplay()

    def updateDisplay(self):
        self.pathBox.setStringValue_(switcher.savePath)
        self.sleepBox.setStringValue_(sleepTime)

    def openFile(self):
        panel = NSOpenPanel.openPanel()
        panel.setCanCreateDirectories_(True)
        panel.setCanChooseDirectories_(True)
        panel.setCanChooseFiles_(False)
        #… there are lots of options, you see where this is going…
        if panel.runModal() == NSOKButton:
            return panel.directory()
        return 

class Menu(NSObject):
  images = {}
  statusbar = None

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
    self.statusitem.setToolTip_('Sync Trigger')

    # Build a very simple menu
    self.menu = NSMenu.alloc().init()
    # Run a script
    startItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Start', 'start:', '')
    self.menu.addItem_(startItem)
    # Settings menu
    settingsItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Settings', 'settings:', '')
    self.menu.addItem_(settingsItem)
    # Default event
    quitItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.menu.addItem_(quitItem)
    # Bind it to the status item
    self.statusitem.setMenu_(self.menu)

  def start_(self, sender):
    e = threading.Event()
    t = threading.Thread(target=switcher.runLoop, args=(e,))
    t.daemon = True
    t.start()

    time.sleep(5)
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

    



if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = Menu.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

