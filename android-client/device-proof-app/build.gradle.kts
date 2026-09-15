plugins {
    id("com.android.application")
}

val proofKeystorePath = providers.environmentVariable("MIRA_DEVICE_PROOF_KEYSTORE_PATH").orNull
val proofKeystorePassword = providers.environmentVariable("MIRA_DEVICE_PROOF_KEYSTORE_PASSWORD").orNull
val proofKeyAlias = providers.environmentVariable("MIRA_DEVICE_PROOF_KEY_ALIAS").orNull

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

    if (proofKeystorePath != null) {
        signingConfigs {
            create("proof") {
                storeFile = file(proofKeystorePath)
                storePassword = requireNotNull(proofKeystorePassword) {
                    "MIRA_DEVICE_PROOF_KEYSTORE_PASSWORD is required when proof signing is enabled"
                }
                keyAlias = requireNotNull(proofKeyAlias) {
                    "MIRA_DEVICE_PROOF_KEY_ALIAS is required when proof signing is enabled"
                }
                keyPassword = proofKeystorePassword
            }
        }

        buildTypes {
            getByName("debug") {
                signingConfig = signingConfigs.getByName("proof")
            }
        }
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
    // The proof Activity directly consumes AuthorizationResult/Task types exposed by
    // GooglePlayWorkspaceAuthorization, so keep this dependency explicit at the app edge.
    implementation("com.google.android.gms:play-services-auth:21.6.0")
    // Provider-owned scanner UI. MIRA receives decoded values only and does not request camera
    // permission or implement a second camera stack.
    implementation("com.google.android.gms:play-services-code-scanner:16.1.0")

    testImplementation("junit:junit:4.13.2")
}
