package com.example.currencystockprediction.utils

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

object SessionManager {

    private const val PREFS_NAME = "session_prefs"
    private const val KEY_APP_IN_BACKGROUND = "app_in_background"

    private lateinit var prefs: SharedPreferences

    fun initialize(context: Context) {
        prefs = EncryptedSharedPreferences.create(
            context,
            PREFS_NAME,
            MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun setAppInBackground(isInBackground: Boolean) {
        prefs.edit().putBoolean(KEY_APP_IN_BACKGROUND, isInBackground).apply()
    }

    fun isAppInBackground(): Boolean {
        return prefs.getBoolean(KEY_APP_IN_BACKGROUND, false)
    }
}
