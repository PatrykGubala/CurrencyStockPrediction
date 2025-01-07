package com.example.currencystockprediction.utils

import android.content.ContentValues.TAG
import android.util.Log
import com.google.firebase.auth.FirebaseAuth

object FirebaseAuthManager {
    var firebaseAuth: FirebaseAuth = FirebaseAuth.getInstance()

    fun isUserLoggedIn(): Boolean {
        return firebaseAuth.currentUser != null
    }

    fun signOut() {
        firebaseAuth.signOut()
    }

    fun addAuthStateListener(listener: FirebaseAuth.AuthStateListener) {
        firebaseAuth.addAuthStateListener(listener)
    }

    fun removeAuthStateListener(listener: FirebaseAuth.AuthStateListener) {
        firebaseAuth.removeAuthStateListener(listener)
    }

    fun signIn(email: String, password: String, onComplete: (Boolean, Exception?) -> Unit) {
        Log.d(TAG, "Attempting to sign in user: $email")
        firebaseAuth.signInWithEmailAndPassword(email, password)
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    Log.d(TAG, "Sign-in successful for user: ${firebaseAuth.currentUser?.uid}")
                    onComplete(true, null)
                } else {
                    Log.e(TAG, "Sign-in failed: ${task.exception?.message}")
                    onComplete(false, task.exception)
                }
            }
    }

}