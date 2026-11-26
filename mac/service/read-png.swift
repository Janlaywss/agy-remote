import AppKit
import Foundation
let pb = CommandLine.arguments.count == 2 ? NSPasteboard(name: NSPasteboard.Name(CommandLine.arguments[1])) : .general
guard let image = NSImage(pasteboard: pb), let tiff = image.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff), let data = rep.representation(using: .png, properties: [:]) else { exit(1) }
FileHandle.standardOutput.write(data)
