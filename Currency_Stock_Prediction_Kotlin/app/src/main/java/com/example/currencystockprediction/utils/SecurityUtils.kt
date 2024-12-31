package com.example.currencystockprediction.utils

import android.app.Activity
import android.content.ContentValues.TAG
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import androidx.biometric.BiometricManager
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import android.provider.Settings
import android.util.Log
import androidx.core.app.ActivityCompat

object SecurityUtils {

    private const val PIN_KEY = "user_pin"
    private const val BIOMETRIC_ENABLED_KEY = "biometric_enabled"
    private const val PREFS_FILENAME = "secure_prefs"





    private const val RE_AUTH_NEEDED_KEY = "re_auth_needed"


    const val BIOMETRIC_REQUEST_CODE = 1001
    const val ENROLLMENT_REQUEST_CODE = 1002


    fun saveReAuthNeeded(context: Context, isNeeded: Boolean) {
        val prefs = getEncryptedSharedPreferences(context)
        prefs.edit().putBoolean(RE_AUTH_NEEDED_KEY, isNeeded).apply()
    }

    fun isReAuthNeeded(context: Context): Boolean {
        val prefs = getEncryptedSharedPreferences(context)
        return prefs.getBoolean(RE_AUTH_NEEDED_KEY, false)
    }





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
        val pin = getPin(context)
        return !pin.isNullOrEmpty()
    }

    fun clearPin(context: Context) {
        try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit().remove(PIN_KEY).apply()
        } catch (e: Exception) {
            e.printStackTrace()
        }
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
    fun checkBiometricSupport(context: Context): Int {
        val biometricManager = BiometricManager.from(context)
        return biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.DEVICE_CREDENTIAL
        )
    }
    fun isBiometricReady(context: Context): Boolean {
        return when (checkBiometricSupport(context)) {
            BiometricManager.BIOMETRIC_SUCCESS -> true
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED,
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE,
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> false
            else -> false
        }
    }

    fun promptBiometricEnrollment(activity: Activity) {
        val enrollIntent = Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
            putExtra(
                Settings.EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED,
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                        BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
        }
        ActivityCompat.startActivityForResult(activity, enrollIntent, ENROLLMENT_REQUEST_CODE, null)
    }

    fun handleBiometricSetup(activity: Activity) {
        when (checkBiometricSupport(activity)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
            }
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                promptBiometricEnrollment(activity)
            }
        }
    }
    fun getSharedPreferences(context: Context): SharedPreferences {
        return getEncryptedSharedPreferences(context)
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
