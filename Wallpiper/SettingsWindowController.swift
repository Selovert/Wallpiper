//
//  SettingsWindowController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 11/2/14.
//  Copyright (c) 2014 Tassilo Selover-Stephan. All rights reserved.
//
//  Released under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version. See <http://www.gnu.org/licenses/> for
//  details.

import Cocoa

class SettingsWindowController: NSWindowController {

    @IBOutlet var settingsWindow: NSWindow!
    @IBOutlet weak var savePathPopup: NSPopUpButton!
    @IBOutlet weak var sleepTimeBox: NSTextField!
    @IBOutlet weak var screenSelector: NSPopUpButton!
    @IBOutlet weak var xResolutionBox: NSTextField!
    @IBOutlet weak var yResolutionBox: NSTextField!
    @IBOutlet weak var autoStartCheckBox: NSButton!
    @IBOutlet weak var autoLaunchCheckBox: NSButton!
    @IBOutlet weak var archiveCountBox: NSTextField!
    
    var workSpace: NSWorkspace = NSWorkspace.sharedWorkspace()
    var globals: Globals?
    var tempGlobals: Globals?
    var timerController: TimerController?
    var startupController: StartupController = StartupController()
    var oldIndex: Int = 0
    
    override func windowDidLoad() {
        super.windowDidLoad()

        // Implement this method to handle any initialization after your window controller's window has been loaded from its nib file.
    }
    
    func reveal() {
        self.showWindow(self)
        NSApp.activateIgnoringOtherApps(true)
        tempGlobals = globals!.initCopy(globals!)
        self.updateWindow()
    }
    
    func updateWindow() {
        var savePathImage: NSImage = workSpace.iconForFile(tempGlobals!.savePath.path!)
        savePathImage.size = NSMakeSize(16, 16)
        savePathPopup.itemAtIndex(0)!.title = tempGlobals!.savePath.path!
        savePathPopup.itemAtIndex(0)!.image = savePathImage
        self.savePathPopup.selectItemAtIndex(0)
        
        self.sleepTimeBox.integerValue = Int(tempGlobals!.sleepTime)
        
        autoStartCheckBox.state = tempGlobals!.autoStart
        autoLaunchCheckBox.state = tempGlobals!.autoLaunch
        let state: Int = Int(startupController.applicationIsInStartUpItems())
        if (state != tempGlobals!.autoLaunch) {
            println("Toggling startup...")
            startupController.toggleLaunchAtStartup()
        }
        
        populateScreens()
        
        archiveCountBox.integerValue = tempGlobals!.archiveImages
    }
    
    func populateScreens() {
        screenSelector.removeAllItems()
        for (i, screen) in enumerate(tempGlobals!.screens) {
            screenSelector.addItemWithTitle("\(i+1)")
        }
        updateScreenBox()
    }
    
    func updateScreenBox() {
        let index: Int = screenSelector.indexOfItem(screenSelector.selectedItem!)
        let screen: NSScreen = tempGlobals!.screens[index]
        if (xResolutionBox.stringValue != "") && (index != oldIndex) {
            tempGlobals!.screenOverrides[oldIndex] = [xResolutionBox.integerValue, yResolutionBox.integerValue]
        }
        if (tempGlobals!.screenOverrides[index][0] != 0) && (tempGlobals!.screenOverrides[index][1] != 0) {
            xResolutionBox.integerValue = tempGlobals!.screenOverrides[index][0]
            yResolutionBox.integerValue = tempGlobals!.screenOverrides[index][1]
        } else {
            xResolutionBox.integerValue = Int(screen.frame.width * screen.backingScaleFactor)
            yResolutionBox.integerValue = Int(screen.frame.height * screen.backingScaleFactor)
        }
    }
    
    func saveTemps() {
        let index: Int = screenSelector.indexOfItem(screenSelector.selectedItem!)
        
        tempGlobals!.autoLaunch = autoLaunchCheckBox.state
        tempGlobals!.autoStart = autoStartCheckBox.state
        tempGlobals!.archiveImages = archiveCountBox.integerValue
        tempGlobals!.sleepTime = Double(sleepTimeBox.integerValue)
        tempGlobals!.screenOverrides[oldIndex] = [xResolutionBox.integerValue, yResolutionBox.integerValue]
    }
    
    func saveSettings() {
        self.saveTemps()
        globals!.autoLaunch = tempGlobals!.autoLaunch
        globals!.autoStart = tempGlobals!.autoStart
        globals!.sleepTime = tempGlobals!.sleepTime
        globals!.savePath = tempGlobals!.savePath
        globals!.archiveImages = tempGlobals!.archiveImages
        globals!.screenOverrides = tempGlobals!.screenOverrides
        globals!.saveSettings()
        
    }
    
    @IBAction func autoDetect(sender: AnyObject) {
        tempGlobals?.screenOverrides = []
        for screens in tempGlobals!.screens {
            tempGlobals?.screenOverrides.append([0,0])
        }
        updateScreenBox()
    }
    
    @IBAction func toggleAutoLaunch(sender: AnyObject) {
        self.saveTemps()
        self.updateWindow()
    }
    
    @IBAction func okay(sender: AnyObject) {
        self.saveSettings()
        settingsWindow.close()
        timerController!.restartTimer(fire: false)
        
    }
    
    @IBAction func showFilePicker(sender: AnyObject) {
        let openPanel: NSOpenPanel = NSOpenPanel()
        openPanel.canChooseFiles = false
        openPanel.canChooseDirectories = true
        
        openPanel.beginSheetModalForWindow(settingsWindow) { responseCode in
            if (responseCode == NSFileHandlingPanelOKButton) {
                self.tempGlobals!.savePath = openPanel.URLs[0] as NSURL
                self.savePathPopup.selectItemAtIndex(0)
            }
        }
    }
    
}
