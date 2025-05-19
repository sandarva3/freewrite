import SwiftGTK
import Foundation

struct HumanEntry: Identifiable {
    let id: UUID
    let date: String
    let filename: String
    var previewText: String

    static func createNew() -> HumanEntry {
        let id = UUID()
        let now = Date()
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd-HH-mm-ss"
        let dateString = dateFormatter.string(from: now)
        dateFormatter.dateFormat = "MMM d"
        let displayDate = dateFormatter.string(from: now)
        return HumanEntry(id: id, date: displayDate, filename: "[\(id)]-[\(dateString)].md", previewText: "")
    }
}

class ContentView {
    let container: Box
    private let textView: TextView
    private let timerLabel: Label
    private let fontButton: Button
    private let timerButton: Button
    private let newEntryButton: Button
    private let fileManager = FileManager.default
    private let documentsDirectory: URL
    private var timeRemaining = 900 // 15 minutes
    private var timerIsRunning = false
    private var entries: [HumanEntry] = []
    private var selectedEntryId: UUID?
    private var currentFont = "Lato-Regular"
    private let fontSizes: [Int] = [16, 18, 20, 22, 24, 26]
    private var fontSize = 18

    init() {
        // Setup documents directory
        documentsDirectory = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("Freewrite")
        try? fileManager.createDirectory(at: documentsDirectory, withIntermediateDirectories: true)

        // Main container
        container = Box(orientation: .vertical, spacing: 10)
        container.margin = 10

        // Text view
        textView = TextView()
        textView.buffer.text = "\n\n"
        textView.wrapMode = .word
        textView.overrideFont(fontDescription: PangoFontDescription(name: currentFont, size: fontSize * Pango.SCALE))
        let scrolledWindow = ScrolledWindow()
        scrolledWindow.add(textView)
        scrolledWindow.setSizeRequest(width: 650, height: 500)
        container.packStart(child: scrolledWindow, expand: true, fill: true, padding: 0)

        // Bottom bar
        let bottomBar = Box(orientation: .horizontal, spacing: 10)
        container.packStart(child: bottomBar, expand: false, fill: false, padding: 0)

        // Font button
        fontButton = Button(label: "Lato")
        fontButton.onClicked { [weak self] in
            self?.changeFont()
        }
        bottomBar.packStart(child: fontButton, expand: false, fill: false, padding: 0)

        // Font size button
        let fontSizeButton = Button(label: "\(fontSize)px")
        fontSizeButton.onClicked { [weak self] in
            guard let self = self else { return }
            let currentIndex = fontSizes.firstIndex(of: fontSize) ?? 0
            fontSize = fontSizes[(currentIndex + 1) % fontSizes.count]
            fontSizeButton.label = "\(fontSize)px"
            textView.overrideFont(fontDescription: PangoFontDescription(name: currentFont, size: fontSize * Pango.SCALE))
        }
        bottomBar.packStart(child: fontSizeButton, expand: false, fill: false, padding: 0)

        // Timer button
        timerLabel = Label(str: "15:00")
        timerButton = Button(label: "15:00")
        timerButton.onClicked { [weak self] in
            self?.toggleTimer()
        }
        bottomBar.packEnd(child: timerButton, expand: false, fill: false, padding: 0)

        // New entry button
        newEntryButton = Button(label: "New Entry")
        newEntryButton.onClicked { [weak self] in
            self?.createNewEntry()
        }
        bottomBar.packEnd(child: newEntryButton, expand: false, fill: false, padding: 0)

        // Load entries
        loadExistingEntries()
        if entries.isEmpty {
            createNewEntry()
        } else if let firstEntry = entries.first {
            selectedEntryId = firstEntry.id
            loadEntry(entry: firstEntry)
        }

        // Timer
        GLib.timeoutAdd(milliseconds: 1000) { [weak self] in
            self?.updateTimer()
            return true
        }

        // Autosave
        GLib.timeoutAdd(milliseconds: 1000) { [weak self] in
            self?.saveCurrentEntry()
            return true
        }
    }

    private func changeFont() {
        let fonts = ["Lato-Regular", "Arial", "Times New Roman"]
        let current = fontButton.label ?? "Lato"
        let next = fonts[(fonts.firstIndex(of: current) ?? 0 + 1) % fonts.count]
        currentFont = next
        fontButton.label = next
        textView.overrideFont(fontDescription: PangoFontDescription(name: next, size: fontSize * Pango.SCALE))
    }

    private func toggleTimer() {
        timerIsRunning.toggle()
        if !timerIsRunning {
            timeRemaining = 900
            timerButton.label = "15:00"
        }
    }

    private func updateTimer() {
        if timerIsRunning && timeRemaining > 0 {
            timeRemaining -= 1
            let minutes = timeRemaining / 60
            let seconds = timeRemaining % 60
            timerButton.label = String(format: "%d:%02d", minutes, seconds)
        } else if timeRemaining == 0 {
            timerIsRunning = false
        }
    }

    private func saveCurrentEntry() {
        guard let id = selectedEntryId, let entry = entries.first(where: { $0.id == id }) else { return }
        let fileURL = documentsDirectory.appendingPathComponent(entry.filename)
        try? textView.buffer.text.write(to: fileURL, atomically: true, encoding: .utf8)
        updatePreviewText(for: entry)
    }

    private func loadEntry(entry: HumanEntry) {
        let fileURL = documentsDirectory.appendingPathComponent(entry.filename)
        if fileManager.fileExists(atPath: fileURL.path) {
            textView.buffer.text = (try? String(contentsOf: fileURL, encoding: .utf8)) ?? "\n\n"
        }
    }

    private func createNewEntry() {
        let newEntry = HumanEntry.createNew()
        entries.insert(newEntry, at: 0)
        selectedEntryId = newEntry.id
        textView.buffer.text = "\n\n"
        if entries.count == 1, let defaultMessage = try? String(contentsOfFile: "freewrite/Resources/default.md") {
            textView.buffer.text = "\n\n" + defaultMessage
            saveCurrentEntry()
            updatePreviewText(for: newEntry)
        }
        saveCurrentEntry()
    }

    private func updatePreviewText(for entry: HumanEntry) {
        let fileURL = documentsDirectory.appendingPathComponent(entry.filename)
        guard let content = try? String(contentsOf: fileURL, encoding: .utf8) else { return }
        let preview = content.replacingOccurrences(of: "\n", with: " ").trimmingCharacters(in: .whitespacesAndNewlines)
        let truncated = preview.isEmpty ? "" : (preview.count > 30 ? String(preview.prefix(30)) + "..." : preview)
        if let index = entries.firstIndex(where: { $0.id == entry.id }) {
            entries[index].previewText = truncated
        }
    }

    private func loadExistingEntries() {
        let fileURLs = (try? fileManager.contentsOfDirectory(at: documentsDirectory, includingPropertiesForKeys: nil)) ?? []
        let mdFiles = fileURLs.filter { $0.pathExtension == "md" }

        entries = mdFiles.compactMap { fileURL in
            let filename = fileURL.lastPathComponent
            guard let uuidMatch = filename.range(of: "\\[(.*?)\\]", options: .regularExpression),
                  let dateMatch = filename.range(of: "\\[(\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}-\\d{2})\\]", options: .regularExpression),
                  let uuid = UUID(uuidString: String(filename[uuidMatch].dropFirst().dropLast())) else { return nil }

            let dateString = String(filename[dateMatch].dropFirst().dropLast())
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd-HH-mm-ss"
            guard let fileDate = dateFormatter.date(from: dateString) else { return nil }

            dateFormatter.dateFormat = "MMM d"
            let displayDate = dateFormatter.string(from: fileDate)
            let content = (try? String(contentsOf: fileURL, encoding: .utf8)) ?? ""
            let preview = content.replacingOccurrences(of: "\n", with: " ").trimmingCharacters(in: .whitespacesAndNewlines)
            let truncated = preview.isEmpty ? "" : (preview.count > 30 ? String(preview.prefix(30)) + "..." : preview)

            return HumanEntry(id: uuid, date: displayDate, filename: filename, previewText: truncated)
        }.sorted { dateFormatter.date(from: $0.date)! > dateFormatter.date(from: $1.date)! }
    }
}
