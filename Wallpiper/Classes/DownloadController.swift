//
//  DownloadController.swift
//  Wallpiper
//
//  Created by Tassilo Selover-Stephan on 24/03/15.
//  Copyright (c) 2015 Tassilo Selover-Stephan. All rights reserved.
//

import Cocoa

class DownloadController: NSObject {
    let delegate: AppDelegate = NSApplication.sharedApplication().delegate as AppDelegate
    var error: NSError?
    var fileManager: NSFileManager = NSFileManager.defaultManager()
    
    var mainScreen: NSScreen! = NSScreen.mainScreen()
    var x: Int = 0
    var y: Int = 0
    var outputPath: String = ""
    var data: NSMutableData? = NSMutableData()
    var response : NSHTTPURLResponse? = nil
    var downloadSize: Float = 0
    var downloadProgress: Float = 0
    var latestTitle: String = ""
    var latestDetailURL: String = ""
    var latestImagePath: String = ""
    
    class imageFile  {
        var filePath: String = String()
        var lastModDate: NSDate = NSDate()
    }

    func startDownload() {
        delegate.statusItemDelegate.setDownloadState(true)
        mainScreen = NSScreen.mainScreen()
        x = Int(mainScreen.frame.width * mainScreen.backingScaleFactor)
        y = Int(mainScreen.frame.height * mainScreen.backingScaleFactor)
        let request = NSMutableURLRequest(URL: NSURL(string: "https://api.ifl.cc/v1/wallpapers/?limit=1&resolution=\(x)x\(y)&sort_by=random")!)
        request.addValue(delegate.globals.appKey, forHTTPHeaderField: "X-IFL-API-Key")
        NSURLConnection.sendAsynchronousRequest(request, queue: NSOperationQueue.mainQueue()) {(response, data, error) in
            if !(error? != nil) {
                let httpResponse = response as NSHTTPURLResponse
                let json = JSON(data: data)
                let title = json[0]["title"]
                let detailURL = json[0]["url_ifl"]
                self.latestTitle = "\(title)"
                self.latestDetailURL = "\(detailURL)"
                self.downloadLinkViaAPI(json[0])
            } else {
                self.delegate.notificationController.notify("Wallpiper:", message: "Getting wallpaper item failed", link: nil)
                self.delegate.statusItemDelegate.setDownloadState(false)
            }
        }
    }
    
    func downloadLinkViaAPI(item: JSON) {
        let id = item["id"]
        let request = NSMutableURLRequest(URL: NSURL(string: "https://api.ifl.cc/v1/wallpaper_download/\(id)/\(x)x\(y)/")!)
        request.addValue(delegate.globals.appKey, forHTTPHeaderField: "X-IFL-API-Key")
        NSURLConnection.sendAsynchronousRequest(request, queue: NSOperationQueue.mainQueue()) {(response, data, error) in
            if !(error? != nil) {
                let json = JSON(data: data)
                let downloadURL = json["download_url"]
                let screen = self.mainScreen
                var datastring = NSString(data: data, encoding: NSUTF8StringEncoding)
                self.fetchImage("\(downloadURL)")
            } else {
                self.delegate.notificationController.notify("Wallpiper:", message: "Getting download link failed", link: nil)
                self.delegate.statusItemDelegate.setDownloadState(false)
            }
        }
    }
    
    func fetchImage(url: String) {
        println("fetching \(url)")
        let link: NSURL = NSURL(string: url)!
        let fileName: String = link.lastPathComponent!.stringByReplacingOccurrencesOfString(".jpg", withString: "_wpy.jpg", options: NSStringCompareOptions.LiteralSearch, range: nil)
        self.outputPath = "\(delegate.globals.savePath!)/\(fileName)"
        let request = NSMutableURLRequest(URL: link)
        let connection: NSURLConnection = NSURLConnection(request: request, delegate: self, startImmediately: true)!
    }
    
    func connection(connection: NSURLConnection!, didReceiveData data: NSData!) {
        self.data!.appendData(data)
        self.downloadProgress = (Float(self.data!.length) / Float(self.downloadSize)) * 100
        let progress: Int = Int(self.downloadProgress)
        if (progress != 100) {
            delegate.statusItemDelegate.changeIcon("menubar-icon-dl-\(((progress / 10) * 10) + 10)", setToDefault: false)
        }
    }
    
    func connection(connection: NSURLConnection!, didReceiveResponse response: NSHTTPURLResponse!) {
        self.response = response
        let statusCode: Int = response.statusCode
        self.downloadSize = Float(response.expectedContentLength)
    }
    
    func connectionDidFinishLoading(connection: NSURLConnection!) {
        self.data!.writeToFile(self.outputPath, atomically: false)
        self.data = NSMutableData()
        self.downloadProgress = 0
        self.postDownload(outputPath)
    }
    
    func connection(connection: NSURLConnection!, didFailWithError error: NSError!) {
        delegate.notificationController.notify("Wallpiper:", message: "Error downloading wallpaper", link: nil)
        delegate.statusItemDelegate.setDownloadState(false)
    }
    
    func postDownload(image: String) {
        let imagePath = NSURL(fileURLWithPath: image, isDirectory: false)!
        if (fileManager.fileExistsAtPath(image)) {
            latestImagePath = image
            let workSpace: NSWorkspace = NSWorkspace.sharedWorkspace()
            let currentOptions: NSDictionary = workSpace.desktopImageOptionsForScreen(mainScreen)!
            workSpace.setDesktopImageURL(imagePath, forScreen: mainScreen, options: currentOptions, error: nil)
            delegate.statusItemDelegate.changeIcon(delegate.statusItemDelegate.defaultImage, setToDefault: false)
            delegate.statusItemDelegate.setDownloadState(false)
            delegate.notificationController.notify("Wallpiper: new wallpaper", message: self.latestTitle, link: self.latestDetailURL)
            delegate.statusItemDelegate.updateLatest()
        } else {
            delegate.statusItemDelegate.setDownloadState(false)
            delegate.notificationController.notify("Wallpiper:", message: "Setting wallpaper failed", link: nil)
        }
        
        if self.delegate.globals.deleteOldImages == 1 {
            if ((delegate.globals.lastImagePath != nil) && fileManager.fileExistsAtPath(delegate.globals.lastImagePath!)) {
                fileManager.removeItemAtPath(delegate.globals.lastImagePath!, error: nil)
            }
            delegate.globals.lastImagePath = image
            delegate.globals.saveSettings()
        }
        
        println("Download successful")
    }
    
}
