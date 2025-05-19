// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "Freewrite",
    dependencies: [
        .package(url: "https://github.com/rhx/SwiftGTK.git", from: "3.0.0")
    ],
    targets: [
        .executableTarget(
            name: "Freewrite",
            dependencies: ["SwiftGTK"],
            path: "freewrite"
        )
    ]
)
