package com.example.currencystockprediction

import android.app.Application
import android.content.Context
import android.content.Intent
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.OnLifecycleEvent
import androidx.lifecycle.ProcessLifecycleOwner
import com.example.currencystockprediction.activities.AuthenticationActivity
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.LocaleHelper
import com.example.currencystockprediction.utils.SecurityUtils
import com.example.currencystockprediction.utils.SessionManager
import com.google.firebase.FirebaseApp

class App : Application(), DefaultLifecycleObserver {

    private var lastBackgroundTime: Long = 0
    private val SESSION_TIMEOUT = 2 * 60 * 1000L

    override fun onCreate() {
        super<Application>.onCreate()
        FirebaseApp.initializeApp(this)
        SessionManager.initialize(this)
        ProcessLifecycleOwner.get().lifecycle.addObserver(this)
    }
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(LocaleHelper.setLocale(base, LocaleHelper.getLanguage(base)))
    }

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
        LocaleHelper.setLocale(this, LocaleHelper.getLanguage(this))
    }


    override fun onStop(owner: LifecycleOwner) {
        super.onStop(owner)
        lastBackgroundTime = System.currentTimeMillis()
        SessionManager.setAppInBackground(true)
    }

    override fun onStart(owner: LifecycleOwner) {
        super.onStart(owner)
        SessionManager.setAppInBackground(false)
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastBackgroundTime > SESSION_TIMEOUT) {
            promptReauthentication()
        }
    }

    private fun promptReauthentication() {

        val intent = Intent(this, AuthenticationActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        startActivity(intent)
    }
}
