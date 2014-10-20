//
//  TimerController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 10/19/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class TimerController: NSObject {
    
    var timer: NSTimer?
    var globals: Globals?
    var startTime: NSDate = NSDate()
    
    init(g: Globals) {
        globals = g
        super.init()
    }
    
    func startTimer() {
        var interval: NSTimeInterval = globals!.sleepTime! * 60
        timer = NSTimer.scheduledTimerWithTimeInterval(interval, target: self, selector: Selector("timerLoop"), userInfo: nil, repeats: true)
    }
    
    func stopTimer() {
        timer?.invalidate()
        timer = nil
    }
    
    func timerLoop() {
        println(startTime.timeIntervalSinceNow)
        println("ping")
    }
    
    
}
