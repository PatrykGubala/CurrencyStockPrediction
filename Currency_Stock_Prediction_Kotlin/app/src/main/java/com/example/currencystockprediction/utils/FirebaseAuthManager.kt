package com.example.currencystockprediction.utils

import com.google.firebase.auth.FirebaseAuth

object FirebaseAuthManager {
    private var instance: FirebaseAuth? = null

    var firebaseAuth: FirebaseAuth
        get() = instance ?: FirebaseAuth.getInstance().also { instance = it }
        set(value) {
            instance = value
        }

    fun isUserLoggedIn(): Boolean {
        return firebaseAuth.currentUser != null
    }
}