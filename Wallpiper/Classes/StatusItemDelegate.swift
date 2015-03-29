//
//  StatusItemDelegate.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 24/03/15.
//  Copyright (c) 2015 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class StatusItemDelegate: NSObject, NSMenuDelegate {
    
    @IBOutlet var statusMenu: NSMenu!
    @IBOutlet var latestItem: NSMenuItem!
    @IBOutlet var downloadItem: NSMenuItem!
    @IBOutlet var preferencesItem: NSMenuItem!
    @IBOutlet var loginItem: NSMenuItem!
    @IBOutlet var savePathItem: NSMenuItem!
    @IBOutlet var deleteLastImageItem: NSMenuItem!
    
    let delegate: AppDelegate = NSApplication.sharedApplication().delegate as AppDelegate
    var startupController: StartupController = StartupController()
    var statusItem: NSStatusItem
    var button: NSStatusBarButton
    var currentImage: String
    var defaultImage: String
    var popoverTransiencyMonitor: NSEvent?
    
    override init() {
        statusItem = NSStatusBar.systemStatusBar().statusItemWithLength(-1);
        button = statusItem.button!
        defaultImage = "menubar-icon"
        button.image = NSBundle.mainBundle().imageForResource(defaultImage)
        currentImage = defaultImage
        super.init()
        button.sendActionOn((2 | 8))
//        button.sendActionOn((Int(NSEventType.LeftMouseDown.rawValue) | Int(NSEventType.RightMouseDown.rawValue)))
        button.target = self
        button.action = Selector("clicked")
        
        NSBundle.mainBundle().loadNibNamed("StatusItem", owner: self, topLevelObjects: nil)
    }
    
    // MARK: Click handlers
    
    func clicked() {
        let currentEvent: NSEvent! = NSApp.currentEvent
        let eventType: NSEventType = currentEvent.type
        if eventType == NSEventType.RightMouseDown {
            self.statusItem.highlightMode = false
            self.handleRightClick()
        } else if eventType == NSEventType.LeftMouseDown {
            self.statusItem.highlightMode = true
            self.openMenu()
        }
    }
    
    func openMenu() {
        self.statusMenu.delegate = self
        self.statusItem.popUpStatusItemMenu(self.statusMenu)
    }
    
    func handleRightClick() {
        if self.delegate.downloadController.latestImagePath != "" {
            self.latestWallpaper(self)
        }
    }
    
    func menuWillOpen(menu: NSMenu) {
        self.setUpLogin()
        self.deleteLastImageItem.state = self.delegate.globals.deleteOldImages!
    }
    
    func menuDidClose(menu: NSMenu) {
        
    }
    
    // MARK: Misc Functions
    
    func changeIcon(icon: String, setToDefault: Bool) {
        if (self.currentImage != icon) {
            let image: NSImage = NSBundle.mainBundle().imageForResource(icon)!
            self.statusItem.image = image
            if (setToDefault == true) {
                self.defaultImage = icon
            }
        }
        self.currentImage = icon
    }
    
    func setDownloadState(state: Bool) {
        let setState: Bool = (!state)
        let items: [NSMenuItem] = [
            latestItem,
            downloadItem,
            preferencesItem]
        for item in items {
            item.enabled = setState
        }
    }
    
    func updateLatest() {
        var size: NSSize = NSSize()
        var contentSize: NSSize = NSSize()
        var width: CGFloat
        var height: CGFloat
        var image: NSImage! = NSImage(byReferencingFile: self.delegate.downloadController.latestImagePath)
        let oldWidth: CGFloat = image.size.width
        let oldHeight: CGFloat = image.size.height
        let maxDimension: CGFloat = 500
        if ((oldWidth > maxDimension) || (oldHeight > maxDimension)) {
            if (oldHeight < oldWidth) {
                width = maxDimension
                height = oldHeight / (oldWidth / maxDimension)
            } else {
                height = maxDimension
                width = oldWidth / (oldHeight / maxDimension)
            }
            size.width = width
            size.height = height
            image.size = size
        } else {
            size.width = image.size.width
            size.height = image.size.height
        }
        
        if (size.width < 175) {
            contentSize.width = 175;
        } else {
            contentSize.width = size.width;
        }
        
        if (size.height < 35) {
            contentSize.height = 35;
        } else {
            contentSize.height = size.height;
        }
        
        self.delegate.latestPopoverController.image = image
        self.delegate.latestPopoverController.contentSize = contentSize
        latestItem.enabled = true
    }
    
    func setUpLogin() {
        let state: Int = Int(startupController.applicationIsInStartUpItems())
        loginItem.state = state
    }
    
    
    // MARK: IBActions
    
    @IBAction func latestWallpaper(sender: AnyObject) {
        if self.popoverTransiencyMonitor != nil {
            NSEvent.removeMonitor(self.popoverTransiencyMonitor!)
            self.popoverTransiencyMonitor = nil
        }
        self.delegate.latestPopoverController.popover.showRelativeToRect(button.frame, ofView: button, preferredEdge: NSMinYEdge)
        if self.popoverTransiencyMonitor == nil {
            self.popoverTransiencyMonitor = NSEvent.addGlobalMonitorForEventsMatchingMask(NSEventMask.LeftMouseUpMask, handler: { (event: NSEvent!) -> Void in
                self.delegate.latestPopoverController.popover.close()
            }) as? NSEvent
        }
    }
    
    @IBAction func getNewWallpaper(sender: AnyObject) {
        delegate.downloadController.startDownload()
    }
    
    @IBAction func openSavePath(sender: AnyObject) {
        if delegate.globals.savePath != nil {
            let fileURL: NSURL! = NSURL(fileURLWithPath: delegate.globals.savePath!)
            NSWorkspace.sharedWorkspace().activateFileViewerSelectingURLs([fileURL])
        }
    }
    
    @IBAction func showAboutWindow(sender: AnyObject) {
        self.delegate.aboutWindowController.reveal()
        
    }
    
    @IBAction func toggleLogin(sender: AnyObject) {
        if loginItem.state == NSOnState {
            loginItem.state = NSOffState
        } else if loginItem.state == NSOffState {
            loginItem.state = NSOnState
        }
        
        let state: Int = Int(startupController.applicationIsInStartUpItems())
        if state != loginItem.state {
            println("Toggling startup...")
            startupController.toggleLaunchAtStartup()
        }
    }
    
    @IBAction func deleteLastImageField(sender: AnyObject) {
        if deleteLastImageItem.state == NSOnState {
            deleteLastImageItem.state = NSOffState
        } else if deleteLastImageItem.state == NSOffState {
            deleteLastImageItem.state = NSOnState
        }
        
        delegate.globals.deleteOldImages = deleteLastImageItem.state
        delegate.globals.saveSettings()
    }
    
    @IBAction func changeSavePath(sender: AnyObject) {
        let openPanel: NSOpenPanel = NSOpenPanel()
        openPanel.canChooseFiles = false
        openPanel.canChooseDirectories = true
        openPanel.canCreateDirectories = true
        openPanel.directoryURL = NSURL(fileURLWithPath: delegate.globals.savePath!, isDirectory: true)
        
        NSApplication.sharedApplication().activateIgnoringOtherApps(true)
        openPanel.beginWithCompletionHandler { (result) -> Void in
            if (result == NSFileHandlingPanelOKButton) {
                self.delegate.globals.savePath = openPanel.URL!.path!.stringByReplacingPercentEscapesUsingEncoding(NSUTF8StringEncoding)!
                self.delegate.globals.saveSettings()
            }
        }
    }
}
