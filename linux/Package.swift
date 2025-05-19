// swift-tools-version:5.10
import PackageDescription

let package = Package(
    name: "Freewrite",
    dependencies: [
        .package(url: "https://github.com/rhx/SwiftGTK.git", branch: "gtk3")
    ],
    targets: [
        .executableTarget(
            name: "Freewrite",
            dependencies: [
                .product(name: "Gtk", package: "SwiftGTK")
            ],
            path: "freewrite",
            resources: [
                .copy("Resources/default.md"),
                .copy("Resources/fonts/Lato-Black.ttf"),
                .copy("Resources/fonts/Lato-BlackItalic.ttf"),
                .copy("Resources/fonts/Lato-Bold.ttf"),
                .copy("Resources/fonts/Lato-BoldItalic.ttf"),
                .copy("Resources/fonts/Lato-Italic.ttf"),
                .copy("Resources/fonts/Lato-Light.ttf"),
                .copy("Resources/fonts/Lato-LightItalic.ttf"),
                .copy("Resources/fonts/Lato-Regular.ttf"),
                .copy("Resources/fonts/Lato-Thin.ttf"),
                .copy("Resources/fonts/Lato-ThinItalic.ttf"),
                .copy("Resources/fonts/OFL.txt")
            ]
        )
    ]
)
