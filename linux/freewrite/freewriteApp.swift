import SwiftGTK

class FreewriteApp {
    let window: Window
    let contentView: ContentView

    init() {
        Gtk.init()
        window = Window()
        window.title = "Freewrite"
        window.setDefaultSize(width: 1100, height: 600)
        window.onDestroy { Gtk.mainQuit() }

        contentView = ContentView()
        window.add(contentView.container)
        window.showAll()
    }

    func run() {
        Gtk.main()
    }
}

_ = FreewriteApp().run()
