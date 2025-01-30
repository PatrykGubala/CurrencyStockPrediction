package com.example.currencystockprediction.utils

import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import java.security.KeyStore
import java.security.Provider
import java.security.Security
import java.util.*

@Implements(KeyStore::class)
class ShadowKeyStore {
    private val store = HashMap<String, Any>()

    companion object {
        @JvmStatic
        @Implementation
        fun getInstance(type: String): KeyStore {
            val provider = MockProvider()
            Security.addProvider(provider)
            return KeyStore.getInstance(type, provider)
        }
    }
}

private class MockProvider : Provider("AndroidKeyStore", 1.0, "Mock Android KeyStore Provider") {
    init {
        put("KeyStore.AndroidKeyStore", "org.robolectric.shadows.ShadowKeyStoreSpi")
    }
}