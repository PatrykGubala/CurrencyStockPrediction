package com.example.currencystockprediction.activities

import android.os.Build
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.setupWithNavController
import com.example.currencystockprediction.R
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navView: BottomNavigationView = findViewById(R.id.bottomNavView)

        val navController = findNavController(R.id.mainNavHost)
        val appBarConfiguration = AppBarConfiguration(
            setOf(R.id.homeFragment, R.id.notificationsFragment, R.id.currencyFragment, R.id.stockFragment, R.id.profileFragment))

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
