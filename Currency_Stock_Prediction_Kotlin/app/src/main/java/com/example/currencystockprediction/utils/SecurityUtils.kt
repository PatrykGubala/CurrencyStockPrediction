package com.example.currencystockprediction.utils

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

object SecurityUtils {

    private const val PIN_KEY = "user_pin"
    private const val BIOMETRIC_ENABLED_KEY = "biometric_enabled"
    private const val PREFS_FILENAME = "secure_prefs"

    fun savePin(context: Context, pin: String): Boolean {
        return try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit().putString(PIN_KEY, pin).apply()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    fun getPin(context: Context): String? {
        return try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.getString(PIN_KEY, null)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    fun hasPin(context: Context): Boolean {
        return getPin(context) != null
    }

    fun setBiometricEnabled(context: Context, enabled: Boolean) {
        try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit().putBoolean(BIOMETRIC_ENABLED_KEY, enabled).apply()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun isBiometricEnabled(context: Context): Boolean {
        return try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.getBoolean(BIOMETRIC_ENABLED_KEY, false)
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    private fun getEncryptedSharedPreferences(context: Context) =
        EncryptedSharedPreferences.create(
            context,
            PREFS_FILENAME,
            MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
}
