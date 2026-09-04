plugins {
    id("com.android.library")
}

android {
    namespace = "com.mira.client.core"
    compileSdk = 36

    defaultConfig {
        minSdk = 23
        consumerProguardFiles("consumer-rules.pro")
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
    testImplementation("junit:junit:4.13.2")
    // Android supplies org.json at runtime. JVM unit tests need the real implementation
    // instead of android.jar method stubs so the production row parser is actually exercised.
    testImplementation("org.json:json:20250517")
}
