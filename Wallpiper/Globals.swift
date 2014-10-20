//
//  Globals.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 10/19/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class Globals: NSObject {
    var autoLaunch: Bool?
    var archiveImages: Int?
    var sleepTime: NSTimeInterval?
    var savePath: NSURL?
    var baseURL: NSURL?
    var pageURL: NSURL?
    var userAgent: String?
    var linkList: [NSURL]?
    
    
    override init() {
        sleepTime = 30
        baseURL = NSURL(string: "http://interfacelift.com")
        pageURL = NSURL(string: baseURL!.absoluteString! + "/wallpaper/downloads/random/x/")
        userAgent = "AppleWebKit/537.36"
        
        super.init()
    }
}
