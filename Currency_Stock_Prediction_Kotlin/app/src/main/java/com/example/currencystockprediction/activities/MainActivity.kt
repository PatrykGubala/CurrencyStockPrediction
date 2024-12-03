// MainActivity.kt
package com.example.currencystockprediction.activities

import android.os.Build
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.example.currencystockprediction.R
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navView: BottomNavigationView = findViewById(R.id.bottomNavView)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.mainNavHostFragment) as NavHostFragment
        val navController = navHostFragment.navController

        navView.setupWithNavController(navController)

        changeNavigationBarColor()

        navView.itemIconTintList = getColorStateList(R.color.bottom_nav_icon_color)
        navView.itemTextColor = getColorStateList(R.color.bottom_nav_icon_color)
    }

    private fun changeNavigationBarColor() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            window.navigationBarColor = getColor(R.color.dark_grey)
        }
    }
}
