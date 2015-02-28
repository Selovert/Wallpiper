//
//  TimerController.swift
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

class TimerController: NSObject {
    
    var timer: NSTimer?
    var globals: Globals
    var notificationController: NotificationController
    var downloadController: DownloadController?
    var startTime: NSDate = NSDate()
    var fileManager: NSFileManager = NSFileManager.defaultManager()
    
    
    init(g: Globals, n: NotificationController) {
        globals = g
        notificationController = n
        super.init()
        
        downloadController = DownloadController(g: self.globals, t:self, n:notificationController)
        downloadController!.cleanDirectory()
    }
    
    func startTimer(fire: Bool = true) {
        println("Starting timer...")
        if fire { timerLoop() }
        var interval: NSTimeInterval = globals.sleepTime * 60
        timer = NSTimer.scheduledTimerWithTimeInterval(interval, target: self, selector: Selector("timerLoop"), userInfo: nil, repeats: true)
    }
    
    func stopTimer() {
        println("Stopping timer...")
        timer?.invalidate()
        timer = nil
    }
    
    func restartTimer(fire: Bool = true) {
        if (self.timer != nil) {
            self.stopTimer()
            if fire {
                self.startTimer()
            } else {
                self.startTimer(fire: false)
            }
        }
    }
    
    func timerLoop() {
        println(startTime.timeIntervalSinceNow)
        println("Beginning download process...")
        downloadController!.getItemViaAPI()
    }

    
}
