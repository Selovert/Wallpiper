import objc, re, os
from Cocoa import *
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

# class Bar(NSObject):
#     def applicationDidFinishLaunching_(self, notification):
#         statusbar = NSStatusBar.systemStatusBar()
#         self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
#         self.statusitem.setHighlightMode_(1)
#         self.statusitem.setToolTip_('Da bar')
#         self.menu = NSMenu.alloc().init()

# poach one of the BTT internal images to get things rolling
status_images = {'idle':'oldsize.png'}

class settingsWindow(NSWindowController):
    pathBox = objc.IBOutlet()
    path = "placeholder"
 
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)

    @objc.IBAction
    def save_(self, sender):
        path = self.pathBox.stringValue()
        print path


class Menu(NSObject):
  images = {}
  statusbar = None
  state = 'idle'

  def applicationDidFinishLaunching_(self, notification):
    statusbar = NSStatusBar.systemStatusBar()
    # Create the statusbar item
    self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
    # Load all images
    for i in status_images.keys():
      self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])
    # Set initial image
    self.statusitem.setImage_(self.images['idle'])
    # Let it highlight upon clicking
    self.statusitem.setHighlightMode_(1)
    # Set a tooltip
    self.statusitem.setToolTip_('Sync Trigger')

    # Build a very simple menu
    self.menu = NSMenu.alloc().init()
    # Sync event is bound to sync_ method
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Sync...', 'sync:', '')
    self.menu.addItem_(menuitem)
    # Run a script
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Start', 'start:', '')
    self.menu.addItem_(menuitem)
    # Settings menu
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Settings', 'settings:', '')
    self.menu.addItem_(menuitem)
    # Default event
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.menu.addItem_(menuitem)
    # Bind it to the status item
    self.statusitem.setMenu_(self.menu)

    # Get the timer going
    # self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(start_time, 5.0, self, 'tick:', None, True)
    # NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
    # self.timer.fire()

  def sync_(self, notification):
    print "sync"

  def tick_(self, notification):
    print self.state

  def start_(self, sender):
    print settingsWindow.path
  
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

