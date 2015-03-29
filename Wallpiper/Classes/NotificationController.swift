//
//  NotificationController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 11/16/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//
//  Released under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version. See <http://www.gnu.org/licenses/> for
//  details.

import Cocoa

class NotificationController: NSObject, NSUserNotificationCenterDelegate {
    
    var notificationCenter: NSUserNotificationCenter
    
    override init() {
        notificationCenter = NSUserNotificationCenter.defaultUserNotificationCenter()
        super.init()
        notificationCenter.delegate = self
    }
    
    func notify(title: String, message: String, link: String?) {
        var userInfo: NSDictionary = NSDictionary()
        if ((link) != nil) {
            userInfo = NSDictionary(objects: [link!], forKeys: ["link"])
        }
        var notification: NSUserNotification = NSUserNotification()
        notification.title = title
        notification.informativeText = message
        notification.userInfo = userInfo
        notificationCenter.deliverNotification(notification)
    }
    
    func userNotificationCenter(center: NSUserNotificationCenter,
        didActivateNotification notification: NSUserNotification) {
            let userInfo: NSDictionary = notification.userInfo!
            var link: String? = userInfo.objectForKey("link") as? String
            if ((link) != nil) {
                NSWorkspace.sharedWorkspace().openURL(NSURL(string: link!)!)
            }
            
    }
    
    func userNotificationCenter(center: NSUserNotificationCenter,
        shouldPresentNotification notification: NSUserNotification) -> Bool {
            return true
    }
    
}
