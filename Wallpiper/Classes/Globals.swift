//
//  Globals.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 24/03/15.
//  Copyright (c) 2015 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class Globals: NSObject {
    
    var appKey: String
    var savePath: String?
    var deleteOldImages: Int?
    var lastImagePath: String?

    var defaults: NSUserDefaults = NSUserDefaults.standardUserDefaults()

    override init() {
        var keyDict:NSDictionary = NSDictionary(contentsOfFile: NSBundle.mainBundle().pathForResource("AppKeys", ofType: "plist")!)!
        appKey = keyDict.objectForKey("X-IFL-API-Key") as String
        
        let defaultValues = [
            "deleteOldImages" : 1,
            "savePath"        : "\(NSHomeDirectory())/Pictures/Wallpapers"
        ]
        defaults.registerDefaults(defaultValues)
        super.init()
        self.loadSettings()
    }
    
    func saveSettings() {
        defaults.setObject(self.savePath, forKey: "savePath")
        defaults.setInteger(self.deleteOldImages!, forKey: "deleteOldImages")
        if self.lastImagePath != nil {
            defaults.setObject(self.lastImagePath!, forKey: "lastImagePath")
        }
        println("Saving settings...")
        defaults.synchronize()
    }
    
    func loadSettings() {
        savePath = defaults.stringForKey("savePath")
        deleteOldImages = defaults.integerForKey("deleteOldImages")
        lastImagePath = defaults.stringForKey("lastImagePath")
    }

}
