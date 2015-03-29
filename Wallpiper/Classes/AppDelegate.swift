//
//  AppDelegate.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 24/03/15.
//  Copyright (c) 2015 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {
    
    var statusItemDelegate: StatusItemDelegate!
    var globals: Globals!
    var downloadController: DownloadController!
    var notificationController: NotificationController!
    var aboutWindowController: AboutWindowController!
    var latestPopoverController: LatestPopoverController!

    func applicationDidFinishLaunching(aNotification: NSNotification) {
        globals = Globals()
        statusItemDelegate = StatusItemDelegate()
        downloadController = DownloadController()
        notificationController = NotificationController.init()
        aboutWindowController = AboutWindowController(windowNibName: "AboutWindow")
        latestPopoverController = LatestPopoverController(nibName: "LatestPopover", bundle: NSBundle.mainBundle())
    }

    func applicationWillTerminate(notification: NSNotification) {
        globals.saveSettings()
    }
}

