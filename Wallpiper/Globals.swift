//
//  Globals.swift
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

class Globals: NSObject {
    
    var appDelegate: AppDelegate?
    var autoLaunch: Int
    var autoStart: Int
    var archiveImages: Int
    var sleepTime: NSTimeInterval
    var savePath: NSURL
    var screens: [NSScreen]
    var screenOverrides: [[Int]]
    var latestTitle: String
    var latestDetailURL: String
    var defaultImage: String
    var currentImage: String
    var appKey: String
    
    var defaults: NSUserDefaults = NSUserDefaults.standardUserDefaults()
    
    
    override init() {
        autoLaunch = 0
        autoStart = 0
        sleepTime = 30
        savePath = NSURL(string: "\(NSHomeDirectory())/Pictures/Wallpapers")!
        archiveImages = 10
        screens = NSScreen.screens() as [NSScreen]
        screenOverrides = []
        latestTitle = "Idle..."
        latestDetailURL = ""
        defaultImage = "menubar-icon"
        currentImage = ""
        var keyDict:NSDictionary = NSDictionary(contentsOfFile: NSBundle.mainBundle().pathForResource("AppKeys", ofType: "plist")!)!
        appKey = keyDict.objectForKey("X-IFL-API-Key") as String
        for screen in screens {
            screenOverrides.append([Int(screen.frame.width * screen.backingScaleFactor),Int(screen.frame.height * screen.backingScaleFactor)])
        }
        super.init()
        self.loadSettings()
    }
    
    func initCopy(g: Globals) -> Globals {
        var copy: Globals = Globals.init()
        copy.autoLaunch = g.autoLaunch
        copy.autoStart = g.autoStart
        copy.sleepTime = g.sleepTime
        copy.savePath = g.savePath
        copy.archiveImages = g.archiveImages
        copy.screens = g.screens
        copy.screenOverrides = g.screenOverrides
        return copy
    }
    
    func copyWithZone(zone: NSZone) -> Globals! {
        return Globals.init()
    }
    
    func saveSettings() {
        defaults.setInteger(self.autoLaunch, forKey: "autoLaunch")
        defaults.setInteger(self.autoStart, forKey: "autoStart")
        defaults.setObject(self.sleepTime, forKey: "sleepTime")
        defaults.setInteger(self.archiveImages, forKey: "archiveImages")
        defaults.setURL(self.savePath, forKey: "savePath")
        defaults.setObject(screenOverrides, forKey: "screenOverrides")
        println("Saving settings...")
        defaults.synchronize()
    }
    
    func loadSettings() {
        autoLaunch = defaults.integerForKey("autoLaunch")
        autoStart = defaults.integerForKey("autoStart")
        sleepTime = defaults.objectForKey("sleepTime")! as NSTimeInterval
        archiveImages = defaults.integerForKey("archiveImages")
        savePath = defaults.URLForKey("savePath")!
        screenOverrides = defaults.objectForKey("screenOverrides") as Array

    }
}
