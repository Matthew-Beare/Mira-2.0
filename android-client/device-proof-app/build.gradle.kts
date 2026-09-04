plugins {
    id("com.android.application")
}

android {
    namespace = "com.mira.deviceproof"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.mira.deviceproof"
        minSdk = 23
        targetSdk = 36
        versionCode = 1
        versionName = "0.1"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    testOptions {
        unitTests.all {
            it.useJUnit()
        }
    }
}

dependencies {
    implementation(project(":core"))
    implementation(project(":google-workspace"))

    testImplementation("junit:junit:4.13.2")
}
