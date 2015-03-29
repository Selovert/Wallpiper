//
//  LatestPopoverController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 26/03/15.
//  Copyright (c) 2015 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class LatestPopoverController: NSViewController {

    @IBOutlet var imageView: NSImageView!
    @IBOutlet var finderButton: NSButton!
    @IBOutlet var browserButton: NSButton!
    
    
    let delegate: AppDelegate = NSApplication.sharedApplication().delegate as AppDelegate
    var popover: NSPopover = NSPopover()
    var contentSize: NSSize = NSSize()
    var image: NSImage?
    
    override init?(nibName nibNameOrNil: String?, bundle nibBundleOrNil: NSBundle?) {
        super.init(nibName: nibNameOrNil, bundle: nibBundleOrNil)
        popover.contentViewController = self
        popover.behavior = NSPopoverBehavior.Transient
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
    }
    
    override func viewWillAppear() {
        imageView.image = self.image
        popover.contentSize = self.contentSize
    }
    
    override func viewDidAppear() {
        NSApplication.sharedApplication().activateIgnoringOtherApps(true)
        super.viewDidAppear()
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        let iconSize: NSSize = NSSize(width: 20, height: 20)
        let buttonSize: NSSize = NSSize(width: 28, height: 28)
        let folder: NSImage! = NSImage(named: "folder")
        let globe: NSImage! = NSImage(named: "globe")
        
        folder.size = iconSize
        globe.size = iconSize
        finderButton.setFrameSize(buttonSize)
        finderButton.image = folder
        browserButton.setFrameSize(buttonSize)
        browserButton.image = globe
    }
    
    @IBAction func finderButton(sender: AnyObject) {
        if delegate.globals.lastImagePath != nil {
            let fileURL: NSURL! = NSURL(fileURLWithPath: delegate.downloadController.latestImagePath)
            NSWorkspace.sharedWorkspace().activateFileViewerSelectingURLs([fileURL])
        }
    }
    
    @IBAction func browserButton(sender: AnyObject) {
        if ((delegate.downloadController.latestDetailURL) != "") {
            NSWorkspace.sharedWorkspace().openURL(NSURL(string: delegate.downloadController.latestDetailURL)!)
        }
    }
    
}
