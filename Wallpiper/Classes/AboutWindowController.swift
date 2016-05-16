//
//  AboutWindowController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 26/03/15.
//  Copyright (c) 2015 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class AboutWindowController: NSWindowController, NSWindowDelegate {
    
    @IBOutlet var aboutWindow: NSWindow!
    @IBOutlet weak var versionLabel: NSTextField!
    
    let version: String = NSBundle.mainBundle().objectForInfoDictionaryKey("CFBundleShortVersionString")! as! String
    
    override func windowDidLoad() {
        
        aboutWindow.delegate = self
        super.windowDidLoad()
    }
    
    func windowDidResignKey(notification: NSNotification) {
        self.close()
    }
    
    func reveal() {
        NSBundle.mainBundle().loadNibNamed("AboutWindow", owner: self, topLevelObjects: nil)
        self.centerWindow()
        versionLabel.stringValue = "Version: \(version)"
        self.showWindow(self)
        NSApp.activateIgnoringOtherApps(true)
        aboutWindow.makeKeyAndOrderFront(self)
    }
    
    func centerWindow() {
        let mainScreen: NSScreen! = NSScreen.mainScreen()
        let x: CGFloat = ceil(mainScreen.frame.origin.x + (mainScreen.frame.width/2) - (aboutWindow.frame.width/2))
        let y: CGFloat = ceil(mainScreen.frame.origin.y + (mainScreen.frame.height/1.5) - (aboutWindow.frame.height/2))
        self.window!.setFrame(CGRectMake(x, y, aboutWindow.frame.width, aboutWindow.frame.height), display: true)
    }
    
    @IBAction func viewSource(sender: AnyObject) {
        NSWorkspace.sharedWorkspace().openURL(NSURL(string: "https://github.com/Selovert/Wallpiper")!)
    }
}
