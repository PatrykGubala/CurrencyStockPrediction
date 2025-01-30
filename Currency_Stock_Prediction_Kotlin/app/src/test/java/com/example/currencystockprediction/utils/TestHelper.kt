package com.example.currencystockprediction.utils

import com.google.firebase.auth.FirebaseAuth
import io.mockk.mockkStatic

object TestHelper {
    fun initializeFirebaseAuth(mockAuth: FirebaseAuth) {
        FirebaseAuthManager.firebaseAuth = mockAuth
    }


}