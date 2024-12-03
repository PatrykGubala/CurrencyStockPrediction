package com.example.currencystockprediction

import android.app.Application
import android.content.Context
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.OnLifecycleEvent
import androidx.lifecycle.ProcessLifecycleOwner
import com.example.currencystockprediction.utils.LocaleHelper
import com.example.currencystockprediction.utils.SessionManager

class App : Application(), DefaultLifecycleObserver {

    override fun onCreate() {
        super<Application>.onCreate()
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
        SessionManager.setAppInBackground(true)
    }

    override fun onStart(owner: LifecycleOwner) {
        super.onStart(owner)
        SessionManager.setAppInBackground(false)
    }
}
