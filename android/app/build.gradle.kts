plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.starquarry.game"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.starquarry.game"
        minSdk = 26
        targetSdk = 34
        versionCode = 191
        versionName = "Beta 0.40.9.191"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Uses the debug key so "Build APK" produces an installable file out of the box.
            // Replace with your own signing config before publishing to the Play Store.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.webkit:webkit:1.11.0")
}
