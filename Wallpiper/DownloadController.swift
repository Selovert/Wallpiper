//
//  DownloadController.swift
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

class DownloadController: NSObject {
    
    var globals: Globals
    var timerController: TimerController
    var notificationController: NotificationController
    var error: NSError?
    var fileManager: NSFileManager = NSFileManager.defaultManager()
    
    var data: NSMutableData? = nil
    var response : NSHTTPURLResponse? = nil
    var downloadSize: Float = 0
    var downloadProgress: Float = 0
    var output: String = ""
    var currentScreen: NSScreen = NSScreen()
    
    class imageFile  {
        var filePath: String = String()
        var lastModDate: NSDate = NSDate()
    }
    
    init(g: Globals, t: TimerController, n: NotificationController) {
        globals = g
        timerController = t
        notificationController = n
        self.data = NSMutableData()
        super.init()
    }
    
    func getItemViaAPI() {
        globals.appDelegate!.setDownloadState(true)
        for (i, screen) in enumerate(globals.screens) {
            let x: Int = globals.screenOverrides[i][0]
            let y: Int = globals.screenOverrides[i][1]
            let request = NSMutableURLRequest(URL: NSURL(string: "https://interfacelift-interfacelift-wallpapers.p.mashape.com/v1/wallpapers/?limit=1&resolution=\(x)x\(y)&sort_by=random")!)
            request.addValue("WOHjrTgcS7mshaocg3WN1kKhSGn1p1Hpk0UjsncivjfU3T6632", forHTTPHeaderField: "X-Mashape-Key")
            NSURLConnection.sendAsynchronousRequest(request, queue: NSOperationQueue.mainQueue()) {(response, data, error) in
                if !(error? != nil) {
                    let httpResponse = response as NSHTTPURLResponse
                    let json = JSON(data: data)
                    let title = json[0]["title"]
                    let detailURL = json[0]["url_ifl"]
                    self.globals.latestTitle = "\(title)"
                    self.globals.latestDetailURL = "\(detailURL)"
                    self.downloadItemViaAPI(json[0], i: i)
                } else {
                    self.notificationController.notify("Wallpiper:", message: "Getting APIlist failed", link: nil)
                    self.globals.appDelegate!.setDownloadState(false)
                }
            }
        }
    }
    
    func downloadItemViaAPI(item: JSON, i: Int) {
        let x: Int = globals.screenOverrides[i][0]
        let y: Int = globals.screenOverrides[i][1]
        let id = item["id"]
        let request = NSMutableURLRequest(URL: NSURL(string: "https://interfacelift-interfacelift-wallpapers.p.mashape.com/v1/wallpaper_download/\(id)/\(x)x\(y)/")!)
        request.addValue("WOHjrTgcS7mshaocg3WN1kKhSGn1p1Hpk0UjsncivjfU3T6632", forHTTPHeaderField: "X-Mashape-Key")
        NSURLConnection.sendAsynchronousRequest(request, queue: NSOperationQueue.mainQueue()) {(response, data, error) in
            if !(error? != nil) {
                let httpResponse = response as NSHTTPURLResponse
                let headers: NSDictionary = httpResponse.allHeaderFields
                let remainingString: String = headers["X-RateLimit-wallpaper-downloads-Remaining"]! as String
                let remaining: Int = remainingString.toInt()!
                println("\(remaining) downloads remaining month.")
                if (remaining > 10) {
                    let json = JSON(data: data)
                    let downloadURL = json["download_url"]
                    let screen = self.globals.screens[i]
                    var datastring = NSString(data: data, encoding: NSUTF8StringEncoding)
                    self.fetchImage("\(downloadURL)", screen: screen)
                } else {
                    self.notificationController.notify("Wallpiper:", message: "No downloads remaining this month", link: nil)
                    self.globals.appDelegate!.setDownloadState(false)
                }
            } else {
                self.notificationController.notify("Wallpiper:", message: "Getting download link failed", link: nil)
                self.globals.appDelegate!.setDownloadState(false)
            }
        }

    }
    
    func checkScreens() {
        let newScreens: [NSScreen] = NSScreen.screens() as [NSScreen]
        var screensChanged = false
        if (globals.screens.count == newScreens.count) {
            for (i, screen) in enumerate(globals.screens) {
                let screenDescription = globals.screens[i].deviceDescription["NSScreenNumber"]! as Int
                let newScreenDescription = newScreens[i].deviceDescription["NSScreenNumber"]! as Int
                if (screenDescription != newScreenDescription) {
                    screensChanged = true
                }
            }
        } else {
            screensChanged = true
        }
        if screensChanged {
            globals.screens = newScreens
        }
        
    }
    
    func fetchImage(url: String, screen: NSScreen) {
        println("fetching \(url)")
        let link: NSURL = NSURL(string: url)!
        let fileName: String = link.lastPathComponent.stringByReplacingOccurrencesOfString(".jpg", withString: "_wpy.jpg", options: NSStringCompareOptions.LiteralSearch, range: nil)
        self.output = "\(globals.savePath)/\(fileName)"
        self.currentScreen = screen
        let request = NSMutableURLRequest(URL: link)
        let connection: NSURLConnection = NSURLConnection(request: request, delegate: self, startImmediately: true)!
    }
    
    func connection(connection: NSURLConnection!, didReceiveData data: NSData!) {
        self.data!.appendData(data)
        self.downloadProgress = (Float(self.data!.length) / Float(self.downloadSize)) * 100
        let progress: Int = Int(self.downloadProgress)
        if (progress != 100) {
            self.globals.appDelegate!.changeIcon("menubar-icon-dl-\((progress / 10) * 10)", setToDefault: false)
        }
    }
    
    func connection(connection: NSURLConnection!, didReceiveResponse response: NSHTTPURLResponse!) {
        self.response = response
        let statusCode: Int = response.statusCode
        self.downloadSize = Float(response.expectedContentLength)
    }
    
    func connectionDidFinishLoading(connection: NSURLConnection!) {
        self.data!.writeToFile(self.output, atomically: false)
        self.data = NSMutableData()
        self.downloadProgress = 0
        self.cleanDirectory()
        self.postDownload(output, screen: self.currentScreen)
        self.notificationController.notify("Wallpiper: new wallpaper", message: self.globals.latestTitle, link: self.globals.latestDetailURL)
        self.globals.appDelegate!.updateLatest()
    }
    
    func connection(connection: NSURLConnection!, didFailWithError error: NSError!) {
        self.notificationController.notify("Wallpiper:", message: "Error downloading wallpaper", link: nil)
        self.globals.appDelegate!.setDownloadState(false)
        self.timerController.timerLoop()
    }
    
    func postDownload(image: String, screen: NSScreen) {
        println("Download successful")
        let imagePath: NSURL = NSURL(fileURLWithPath: image, isDirectory: false)!
        if (fileManager.fileExistsAtPath(image)) {
            let workSpace: NSWorkspace = NSWorkspace.sharedWorkspace()
            let currentOptions: NSDictionary = workSpace.desktopImageOptionsForScreen(screen)!
            workSpace.setDesktopImageURL(imagePath, forScreen: screen, options: currentOptions, error: nil)
            globals.appDelegate!.changeIcon(globals.defaultImage, setToDefault: false)
            globals.appDelegate!.setDownloadState(false)
        }
    }
    
    func cleanDirectory() {
        var fileArray: [String] = getSortedFilesFromFolder(globals.savePath.path!)
        while (fileArray.count > globals.archiveImages) {
            fileManager.removeItemAtPath(fileArray[0], error: nil)
            fileArray.removeAtIndex(0)
        }
    }
    
    func getSortedFilesFromFolder(folderPath: String) -> [String] {
        let error: NSErrorPointer = NSErrorPointer()
        var fileArray: NSArray = fileManager.contentsOfDirectoryAtPath(folderPath, error: error)!
        let predicate: NSPredicate = NSPredicate(format: "SELF EndsWith '_wpy.jpg'")!
        fileArray = fileArray.filteredArrayUsingPredicate(predicate)
        
        var filesAndProperties: [imageFile] = []
        for file in fileArray {
            let image: imageFile = imageFile()
            let filePath: String = "\(folderPath)/\(file)"
            let properties: NSDictionary = fileManager.attributesOfItemAtPath(filePath, error: error)!
            image.lastModDate = properties.objectForKey(NSFileModificationDate)! as NSDate
            image.filePath = filePath
            filesAndProperties.append(image)
        }
        filesAndProperties.sort {
            item1, item2 in
            let date1 = item1.lastModDate as NSDate
            let date2 = item2.lastModDate as NSDate
            return date1.compare(date2) == NSComparisonResult.OrderedAscending
        }
        var returnArray: [String] = []
        for image in filesAndProperties {
            returnArray.append(image.filePath)
        }
        return returnArray
    }
    
}
