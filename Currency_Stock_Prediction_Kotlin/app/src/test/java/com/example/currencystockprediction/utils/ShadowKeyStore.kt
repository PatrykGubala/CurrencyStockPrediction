package com.example.currencystockprediction.utils

import android.security.keystore.KeyGenParameterSpec
import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import java.security.KeyStore
import java.security.KeyStoreSpi
import java.security.Provider
import java.io.InputStream
import java.io.OutputStream
import java.security.Key
import java.security.cert.Certificate
import java.util.*

@Implements(KeyStore::class)
class ShadowKeyStore {
    private val store = HashMap<String, Any>()

    @Implementation
    fun load(stream: InputStream?, password: CharArray?) {
    }

    @Implementation
    fun getKey(alias: String, password: CharArray?): Key? {
        return store[alias] as? Key
    }

    @Implementation
    fun getCertificate(alias: String): Certificate? {
        return store[alias] as? Certificate
    }

    @Implementation
    fun aliases(): Enumeration<String> {
        return Collections.enumeration(store.keys)
    }

    companion object {
        @JvmStatic
        @Implementation
        fun getInstance(type: String): KeyStore {
            return when (type) {
                "AndroidKeyStore" -> MockAndroidKeyStore()
                else -> KeyStore.getInstance(type)
            }
        }
    }
}

private class MockAndroidKeyStore : KeyStore(MockKeyStoreSpi(), MockProvider(), "AndroidKeyStore") {
    init {
        load(null)
    }
}

private class MockKeyStoreSpi : KeyStoreSpi() {
    private val store = HashMap<String, Any>()

    override fun engineLoad(stream: InputStream?, password: CharArray?) {}
    override fun engineGetKey(alias: String?, password: CharArray?): Key? = null
    override fun engineGetCertificate(alias: String?): Certificate? = null
    override fun engineGetCertificateChain(alias: String?): Array<Certificate>? = null
    override fun engineGetCreationDate(alias: String?): Date = Date()
    override fun engineSetKeyEntry(alias: String?, key: Key?, password: CharArray?, chain: Array<out Certificate>?) {}
    override fun engineSetKeyEntry(alias: String?, key: ByteArray?, chain: Array<out Certificate>?) {}
    override fun engineSetCertificateEntry(alias: String?, cert: Certificate?) {}
    override fun engineDeleteEntry(alias: String?) {}
    override fun engineAliases(): Enumeration<String> = Collections.enumeration(store.keys)
    override fun engineContainsAlias(alias: String?): Boolean = false
    override fun engineSize(): Int = 0
    override fun engineIsKeyEntry(alias: String?): Boolean = false
    override fun engineIsCertificateEntry(alias: String?): Boolean = false
    override fun engineGetCertificateAlias(cert: Certificate?): String? = null
    override fun engineStore(stream: OutputStream?, password: CharArray?) {}
}

private class MockProvider : Provider("MockAndroidKeyStore", 1.0, "Mock Android KeyStore provider") {
    init {
        put("KeyStore.AndroidKeyStore", MockKeyStoreSpi::class.java.name)
    }
}