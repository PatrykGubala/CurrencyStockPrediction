package com.example.currencystockprediction.activities

import android.content.ContentValues.TAG
import android.content.Intent
import android.content.SharedPreferences
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.example.currencystockprediction.R

import com.example.currencystockprediction.utils.SecurityUtils
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.firebase.auth.FirebaseAuth
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private val reAuthNeededKey = "re_auth_needed"

    private val preferenceChangeListener = SharedPreferences.OnSharedPreferenceChangeListener { sharedPrefs, key ->
        if (key == reAuthNeededKey) {
            val isReAuthNeeded = sharedPrefs.getBoolean(key, false)
            if (isReAuthNeeded) {
                Log.d(TAG, "Re-authentication needed. Navigating to AuthenticationActivity.")
                navigateToAuthentication()
            }
        }
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "MainActivity onCreate")
        setContentView(R.layout.activity_main)

        sharedPreferences = SecurityUtils.getSharedPreferences(this)
        sharedPreferences.registerOnSharedPreferenceChangeListener(preferenceChangeListener)

        if (SecurityUtils.isReAuthNeeded(this)) {
            navigateToAuthentication()
        }





        val navView: BottomNavigationView = findViewById(R.id.bottomNavView)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.mainNavHostFragment) as NavHostFragment
        val navController = navHostFragment.navController

        navView.setupWithNavController(navController)

        changeNavigationBarColor()

        navView.itemIconTintList = getColorStateList(R.color.bottom_nav_icon_color)
        navView.itemTextColor = getColorStateList(R.color.bottom_nav_icon_color)


    }






    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
    }


    override fun onStart() {
        super.onStart()
    }

    override fun onStop() {
        super.onStop()

    }

    private fun changeNavigationBarColor() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            window.navigationBarColor = getColor(R.color.dark_grey)
        }
    }

    private fun navigateToAuthentication() {
        val intent = Intent(this, AuthenticationActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        startActivity(intent)
        finish()
    }

    override fun onDestroy() {
        super.onDestroy()
        sharedPreferences.unregisterOnSharedPreferenceChangeListener(preferenceChangeListener)
    }
}
