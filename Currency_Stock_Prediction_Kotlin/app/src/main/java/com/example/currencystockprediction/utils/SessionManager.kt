package com.example.currencystockprediction.utils

import android.content.Context
import android.content.SharedPreferences
import android.os.Build
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

object SessionManager {

    private const val PREFS_NAME = "session_prefs"
    private const val KEY_APP_IN_BACKGROUND = "app_in_background"

    private lateinit var prefs: SharedPreferences

    private fun isTestRunner(): Boolean {
        return Build.FINGERPRINT.equals("robolectric")
    }

    fun initialize(context: Context) {
        prefs = if (isTestRunner()) {
            context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        } else {
            EncryptedSharedPreferences.create(
                context,
                PREFS_NAME,
                MasterKey.Builder(context)
                    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                    .build(),
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        }
    }

    fun setAppInBackground(isInBackground: Boolean) {
        prefs.edit().putBoolean(KEY_APP_IN_BACKGROUND, isInBackground).apply()
    }

    fun isAppInBackground(): Boolean {
        return prefs.getBoolean(KEY_APP_IN_BACKGROUND, false)
    }
}
