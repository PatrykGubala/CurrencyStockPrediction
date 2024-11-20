package com.example.currencystockprediction.auth

import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore

object FirebaseAuthManager {
    private val firebaseAuth = FirebaseAuth.getInstance()
    private val db = FirebaseFirestore.getInstance()
    private val TAG = "FirebaseAuthManager"

    fun registerUser(
        email: String,
        password: String,
        username: String,
        usernameCode: String,
        onComplete: (Boolean, String?) -> Unit
    ) {
        firebaseAuth.createUserWithEmailAndPassword(email, password)
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val user = task.result?.user
                    user?.let { firebaseUser ->
                        val userDocRef = db.collection("users").document(firebaseUser.uid)

                        val userData = hashMapOf(
                            "email" to email,
                            "username" to username,
                        )

                        userDocRef.set(userData)
                            .addOnSuccessListener {
                                onComplete(true, null)
                            }
                            .addOnFailureListener { exception ->
                                onComplete(false, exception.message)
                                Log.e(TAG, "Error adding user data", exception)
                            }
                    }
                } else {
                    onComplete(false, task.exception?.message)
                    Log.e(TAG, "Error registering user", task.exception)
                }
            }
    }
    fun logoutUser() {
        firebaseAuth.signOut()
    }
}