package com.example.currencystockprediction.utils

import android.content.Context
import android.content.SharedPreferences

object CacheManager {
    private const val PREFS_NAME = "user_cache"
    private const val KEY_USERNAME = "username"
    private const val KEY_PROFILE_IMAGE_URL = "profile_image_url"

    private fun getPreferences(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    fun saveUsername(context: Context, username: String) {
        getPreferences(context).edit().putString(KEY_USERNAME, username).apply()
    }

    fun getUsername(context: Context): String? {
        return getPreferences(context).getString(KEY_USERNAME, null)
    }

    fun saveProfileImageUrl(context: Context, url: String) {
        getPreferences(context).edit().putString(KEY_PROFILE_IMAGE_URL, url).apply()
    }

    fun getProfileImageUrl(context: Context): String? {
        return getPreferences(context).getString(KEY_PROFILE_IMAGE_URL, null)
    }

    fun saveCurrencies(context: Context, region: String, data: String) {
        getPreferences(context).edit().putString("${region}_currencies", data).apply()
    }

    fun getCurrencies(context: Context, region: String): String? {
        return getPreferences(context).getString("${region}_currencies", null)
    }


    fun clearCache(context: Context) {
        getPreferences(context).edit().clear().apply()
    }
}
