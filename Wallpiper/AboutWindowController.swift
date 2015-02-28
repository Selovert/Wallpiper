//
//  AboutWindowController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 11/22/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//
//  Released under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version. See <http://www.gnu.org/licenses/> for
//  details.

import Cocoa

class AboutWindowController: NSWindowController {

    @IBOutlet var AboutWindow: NSWindow!
    @IBOutlet weak var versionLabel: NSTextField!
    
    override func windowDidLoad() {
        super.windowDidLoad()
        let version: String = NSBundle.mainBundle().objectForInfoDictionaryKey("CFBundleVersion")! as String
        versionLabel.stringValue = "Version: \(version)"
    }
    
    func reveal() {
        self.showWindow(self)
        NSApp.activateIgnoringOtherApps(true)
    }
    
    @IBAction func viewSource(sender: AnyObject) {
        NSWorkspace.sharedWorkspace().openURL(NSURL(string: "https://github.com/Selovert/Wallpiper")!)
    }
}
