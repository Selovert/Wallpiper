//
//  AppDelegate.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 10/19/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa



@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    @IBOutlet weak var window: NSWindow!
    @IBOutlet weak var statusMenu: NSMenu!
    
    var statusItem: NSStatusItem?
    var globals: Globals = Globals.init()
    var timerController: TimerController?
    var downloadController: DownloadController?

    func applicationDidFinishLaunching(aNotification: NSNotification) {
        statusItem = NSStatusBar.systemStatusBar().statusItemWithLength(-1);
     
        statusItem!.title = "W"
        statusItem!.menu = statusMenu
        statusItem!.highlightMode = true
        
        timerController = TimerController.init(g: globals)
        timerController!.startTimer()
        
        downloadController = DownloadController.init(g: globals)
        
        println(globals.pageURL!)
    }

    func applicationWillTerminate(aNotification: NSNotification) {
        // Insert code here to tear down your application
    }
    
    @IBAction func getNewWallpaper(sender: AnyObject) {
        
        timerController!.timer!.fire()
        timerController!.stopTimer()
        timerController!.startTimer()
    }
    @IBAction func stopTimer(sender: AnyObject) {
        timerController!.stopTimer()
    }


}

