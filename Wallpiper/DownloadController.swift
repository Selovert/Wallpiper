//
//  DownloadController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 10/19/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class DownloadController: NSObject {
    
    var globals: Globals
    
    init(g: Globals) {
        globals = g
        super.init()
    }
    
    func getList() {
        globals.linkList! = [];
        
    }
}
