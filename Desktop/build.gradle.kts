import org.jetbrains.compose.desktop.application.dsl.TargetFormat
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    kotlin("jvm") version "2.4.20"
    id("org.jetbrains.compose") version "1.12.1"
    id("org.jetbrains.kotlin.plugin.compose") version "2.4.20"
}
group = "com.falloutlondon"
val appVersion: String = file("../VERSION").readText().trim()
version = appVersion

// Native installers (MSI / DEB / RPM) require numeric MAJOR.MINOR.PATCH package versions.
// The shared VERSION file uses "major.minor" with a two-digit minor ("1.01", "1.10"), so map it
// numerically: 1.01 -> 1.1.0, 1.10 -> 1.10.0. Fails fast with a clear message if VERSION is malformed.
val nativePackageVersion: String = appVersion.split('.').map { part ->
    part.toIntOrNull() ?: error("VERSION component '$part' in '$appVersion' is not a number")
}.let { parts ->
    require(parts.isNotEmpty() && parts[0] > 0) { "VERSION '$appVersion' must start with a major version >= 1" }
    listOf(parts[0], parts.getOrElse(1) { 0 }, parts.getOrElse(2) { 0 }).joinToString(".")
}
dependencies {
    implementation(compose.desktop.currentOs)
    implementation(compose.material3)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    implementation("org.json:json:20250517")
    testImplementation("junit:junit:4.13.2")
}
kotlin { compilerOptions.jvmTarget.set(JvmTarget.JVM_21) }
tasks.test { useJUnit() }
compose.desktop {
    application {
        mainClass = "com.falloutlondon.companion.desktop.MainKt"
        nativeDistributions {
            packageName = "Fallout London Companion"
            packageVersion = nativePackageVersion
            description = "Fallout London Companion desktop client"
            vendor = "Fallout London Companion"
            targetFormats(TargetFormat.Msi, TargetFormat.Exe, TargetFormat.Deb, TargetFormat.Rpm, TargetFormat.AppImage)
            windows {
                menuGroup = "Fallout London Companion"
                shortcut = true
                dirChooser = true
                iconFile.set(project.file("src/main/resources/app.ico"))
            }
            linux {
                packageName = "fallout-london-companion"
                appCategory = "Utility"
                iconFile.set(project.file("src/main/resources/app.png"))
            }
        }
    }
}
