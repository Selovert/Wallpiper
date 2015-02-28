//
//  AppDelegate.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 10/19/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//
//  Released under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version. See <http://www.gnu.org/licenses/> for
//  details.

import Cocoa



@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    @IBOutlet weak var window: NSWindow!
    @IBOutlet weak var statusMenu: NSMenu!
    
    @IBOutlet weak var latestItem: NSMenuItem!
    @IBOutlet weak var aboutItem: NSMenuItem!
    @IBOutlet weak var skipItem: NSMenuItem!
    @IBOutlet weak var toggleItem: NSMenuItem!
    @IBOutlet weak var preferencesItem: NSMenuItem!
    
    
    var statusItem: NSStatusItem?
    var globals: Globals = Globals.init()
    var notificationController: NotificationController = NotificationController.init()
    lazy var settingsWindowController: SettingsWindowController = SettingsWindowController(windowNibName: "SettingsWindow")
    lazy var aboutWindowController: AboutWindowController = AboutWindowController(windowNibName: "AboutWindow")
    var timerController: TimerController?
    var downloadController: DownloadController?

    func applicationDidFinishLaunching(aNotification: NSNotification) {
        globals.appDelegate = self
        
        statusItem = NSStatusBar.systemStatusBar().statusItemWithLength(-1)
     
        changeIcon(globals.defaultImage, setToDefault: true)
        statusItem!.alternateImage = NSBundle.mainBundle().imageForResource("menubar-icon-white")!
        statusItem!.menu = statusMenu
        statusItem!.highlightMode = true
        statusMenu.autoenablesItems = false
        
        timerController = TimerController.init(g: globals, n:notificationController)
        if (globals.autoStart == 1) {
            timerController!.startTimer()
        }
        
        downloadController = timerController!.downloadController
        
        settingsWindowController.timerController = timerController!
        settingsWindowController.globals = globals
        
//        Testing down here...
    }

    func applicationWillTerminate(aNotification: NSNotification) {
        globals.saveSettings()
    }
    
    func changeIcon(icon: String, setToDefault: Bool) {
        if (globals.currentImage != icon) {
            let image: NSImage = NSBundle.mainBundle().imageForResource(icon)!
            statusItem!.image = image
            if (setToDefault == true) {
                globals.defaultImage = icon
            }
        }
        globals.currentImage = icon
    }
    
    func updateLatest() {
        latestItem.enabled = true
        latestItem.title = globals.latestTitle
    }
    
    func setDownloadState(state: Bool) {
        let setState: Bool = (!state)
        latestItem.enabled = setState
        aboutItem.enabled = setState
        skipItem.enabled = setState
        toggleItem.enabled = setState
        preferencesItem.enabled = setState
    }
    
    @IBAction func getNewWallpaper(sender: AnyObject) {
        if (timerController!.timer == nil) {
            self.timerController!.timerLoop()
        } else if (timerController!.timer != nil) {
            self.timerController!.restartTimer()
        }
    }
    
    @IBAction func toggleTimer(sender: AnyObject) {
        if (timerController!.timer == nil) {
            self.timerController!.startTimer()
            toggleItem.title = "Stop"
        } else if (timerController!.timer != nil) {
            self.timerController!.stopTimer()
            toggleItem.title = "Start"
        }
    }
    
    @IBAction func showSettingsWindow(sender: AnyObject) {
        settingsWindowController.reveal()
    }
    @IBAction func showAboutWindow(sender: AnyObject) {
        aboutWindowController.reveal()
        
    }
    
    @IBAction func latestWallpaper(sender: AnyObject) {
        if ((globals.latestDetailURL) != "") {
            NSWorkspace.sharedWorkspace().openURL(NSURL(string: globals.latestDetailURL)!)
        }
    }
    


}

