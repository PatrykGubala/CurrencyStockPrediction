package com.example.currencystockprediction.utils

import com.google.firebase.auth.FirebaseAuth

object FirebaseAuthManager {
    val firebaseAuth: FirebaseAuth = FirebaseAuth.getInstance()

    fun isUserLoggedIn(): Boolean {
        return firebaseAuth.currentUser != null
    }

    fun signOut() {
        firebaseAuth.signOut()
    }
}