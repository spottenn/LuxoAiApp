plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    id("com.chaquo.python")
}

android {
    namespace = "com.spottenn.luxoai"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.spottenn.luxoai"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk {
            abiFilters += listOf("arm64-v8a", "x86_64")
        }

        // Define BuildConfig fields for API keys
        // Priority: Environment variable > .env file > default empty string
        val openAIKey = System.getenv("OPENAI_API_KEY") ?: project.findProperty("OPENAI_API_KEY") as? String ?: ""
        val anthropicKey = System.getenv("ANTHROPIC_API_KEY") ?: project.findProperty("ANTHROPIC_API_KEY") as? String ?: ""
        val replicateToken = System.getenv("REPLICATE_API_TOKEN") ?: project.findProperty("REPLICATE_API_TOKEN") as? String ?: ""

        buildConfigField("String", "OPENAI_API_KEY", "\"$openAIKey\"")
        buildConfigField("String", "ANTHROPIC_API_KEY", "\"$anthropicKey\"")
        buildConfigField("String", "REPLICATE_API_TOKEN", "\"$replicateToken\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    flavorDimensions += "pyVersion"
    productFlavors {
        create("py310") { dimension = "pyVersion" }
    }
}
chaquopy {
    productFlavors {
        getByName("py310") { version = "3.10" }
    }
}
dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}