package com.example.currencystockprediction.utils

import android.app.Activity
import android.content.ContentValues.TAG
import android.content.Context
import android.content.Intent
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
    private const val SAVED_ACCOUNT_KEY = "saved_account"
    private const val SAVED_EMAIL_KEY = "saved_email"
    private const val SAVED_PASSWORD_KEY = "saved_password"

    const val BIOMETRIC_REQUEST_CODE = 1001
    const val ENROLLMENT_REQUEST_CODE = 1002

    fun saveAccount(context: Context, account: String) {
        try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit().putString(SAVED_ACCOUNT_KEY, account).apply()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun getSavedAccount(context: Context): String? {
        return try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.getString(SAVED_ACCOUNT_KEY, null)
        } catch (e: Exception) {
            null
        }
    }

    fun clearSavedAccount(context: Context) {
        try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit().remove(SAVED_ACCOUNT_KEY).apply()
        } catch (e: Exception) {
            e.printStackTrace()
        }
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

    fun saveCredentials(context: Context, email: String, password: String): Boolean {
        return try {
            Log.d(TAG, "Saving user credentials.")
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit()
                .putString(SAVED_EMAIL_KEY, email)
                .putString(SAVED_PASSWORD_KEY, password)
                .apply()
            Log.d(TAG, "User credentials saved successfully.")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error saving user credentials: ${e.message}")
            e.printStackTrace()
            false
        }
    }

    fun getCredentials(context: Context): Pair<String, String>? {
        return try {
            val sharedPreferences = getEncryptedSharedPreferences(context)
            val email = sharedPreferences.getString(SAVED_EMAIL_KEY, null)
            val password = sharedPreferences.getString(SAVED_PASSWORD_KEY, null)
            if (email != null && password != null) {
                Log.d(TAG, "Retrieved user credentials.")
                Pair(email, password)
            } else {
                Log.e(TAG, "User credentials not found.")
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error retrieving user credentials: ${e.message}")
            e.printStackTrace()
            null
        }
    }

    fun clearCredentials(context: Context) {
        try {
            Log.d(TAG, "Clearing user credentials.")
            val sharedPreferences = getEncryptedSharedPreferences(context)
            sharedPreferences.edit()
                .remove(SAVED_EMAIL_KEY)
                .remove(SAVED_PASSWORD_KEY)
                .apply()
            Log.d(TAG, "User credentials cleared successfully.")
        } catch (e: Exception) {
            Log.e(TAG, "Error clearing user credentials: ${e.message}")
            e.printStackTrace()
        }
    }
}
