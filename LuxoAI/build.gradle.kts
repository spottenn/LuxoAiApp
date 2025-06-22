// Top-level build file where you can add configuration options common to all sub-projects/modules.
import java.util.Properties
import java.io.FileInputStream

// Load .env file if it exists
val envFile = rootProject.file(".env")
if (envFile.exists()) {
    val properties = Properties()
    properties.load(FileInputStream(envFile))
    properties.forEach { (key, value) ->
        project.extra.set(key.toString(), value.toString())
    }
}

plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    id("com.chaquo.python") version "16.1.0" apply false

}