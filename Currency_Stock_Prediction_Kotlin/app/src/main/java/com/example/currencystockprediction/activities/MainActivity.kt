package com.example.currencystockprediction.activities

import android.content.ContentValues.TAG
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.firebase.auth.FirebaseAuth
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private lateinit var authListener: FirebaseAuth.AuthStateListener

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "MainActivity onCreate")
        setContentView(R.layout.activity_main)
        if (!FirebaseAuthManager.isUserLoggedIn()) {
            Log.e(TAG, "User not logged in. Navigating to AuthenticationActivity.")
            navigateToAuthentication()
        }

        authListener = FirebaseAuth.AuthStateListener { firebaseAuth ->
            val user = firebaseAuth.currentUser
            if (user == null) {
                Log.e(TAG, "User logged out. Navigating to AuthenticationActivity.")
                navigateToAuthentication()
            } else {
                Log.d(TAG, "User is logged in: ${user.uid}")
            }
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





    override fun onStart() {
        super.onStart()
        FirebaseAuthManager.addAuthStateListener(authListener)
    }

    override fun onStop() {
        super.onStop()
        FirebaseAuthManager.removeAuthStateListener(authListener)

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
}
