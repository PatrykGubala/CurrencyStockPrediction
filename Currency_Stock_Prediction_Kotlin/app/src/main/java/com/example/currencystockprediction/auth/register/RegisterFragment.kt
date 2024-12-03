// RegisterFragment.kt
package com.example.currencystockprediction.auth.register

import android.os.Bundle
import android.text.TextUtils
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.google.android.material.textfield.TextInputEditText
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

class RegisterFragment : BaseFragment() {

    private lateinit var emailEditText: TextInputEditText
    private lateinit var passwordEditText: TextInputEditText
    private lateinit var repeatPasswordEditText: TextInputEditText
    private lateinit var usernameEditText: TextInputEditText
    private lateinit var registerButton: Button
    private lateinit var backButton: ImageButton
    private lateinit var progressBar: ProgressBar

    private val backendUrl = "https://166e-37-31-56-55.ngrok-free.app"

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?

    ): View? {
        val view = inflater.inflate(R.layout.fragment_register, container, false)

        emailEditText = view.findViewById(R.id.textInputEditTextEmail)
        passwordEditText = view.findViewById(R.id.textInputEditTextPassword)
        repeatPasswordEditText = view.findViewById(R.id.textInputEditTextRepeatPassword)
        usernameEditText = view.findViewById(R.id.textInputEditTextUsername)
        registerButton = view.findViewById(R.id.registerButton)
        backButton = view.findViewById(R.id.back_button)
        progressBar = view.findViewById(R.id.progressBar)

        registerButton.setOnClickListener {
            registerUser()
        }

        backButton.setOnClickListener {
            requireActivity().onBackPressed()
        }

        return view
    }

    private fun registerUser() {
        val email = emailEditText.text.toString().trim()
        val password = passwordEditText.text.toString().trim()
        val repeatPassword = repeatPasswordEditText.text.toString().trim()
        val username = usernameEditText.text.toString().trim()

        if (TextUtils.isEmpty(email)) {
            emailEditText.error = "Email is required"
            return
        }

        if (TextUtils.isEmpty(password)) {
            passwordEditText.error = "Password is required"
            return
        }

        if (password.length < 6) {
            passwordEditText.error = "Password must be at least 6 characters"
            return
        }

        if (password != repeatPassword) {
            repeatPasswordEditText.error = "Passwords do not match"
            return
        }

        if (TextUtils.isEmpty(username)) {
            usernameEditText.error = "Username is required"
            return
        }

        progressBar.visibility = View.VISIBLE

        FirebaseAuthManager.firebaseAuth.createUserWithEmailAndPassword(email, password)
            .addOnCompleteListener(requireActivity()) { task ->
                if (task.isSuccessful) {
                    val firebaseUser = FirebaseAuthManager.firebaseAuth.currentUser
                    firebaseUser?.let {
                        val firebaseUid = it.uid
                        registerUserOnBackend(firebaseUid, email, username) { backendSuccess, backendMessage ->
                            if (backendSuccess) {
                                progressBar.visibility = View.GONE
                                Toast.makeText(context, "User registered successfully", Toast.LENGTH_LONG).show()
                                findNavController().navigate(RegisterFragmentDirections.actionRegisterFragmentToSetPinFragment())
                            } else {
                                deleteUserFromFirebase(firebaseUid)
                                progressBar.visibility = View.GONE
                                Toast.makeText(context, "Registration failed: $backendMessage", Toast.LENGTH_LONG).show()
                            }
                        }
                    } ?: run {
                        progressBar.visibility = View.GONE
                        Toast.makeText(context, "Firebase registration failed: User is null", Toast.LENGTH_LONG).show()
                    }
                } else {
                    progressBar.visibility = View.GONE
                    Toast.makeText(context, "Firebase registration failed: ${task.exception?.message}", Toast.LENGTH_LONG).show()
                }
            }
    }

    private fun registerUserOnBackend(firebaseUid: String, email: String, username: String, callback: (Boolean, String?) -> Unit) {
        val client = OkHttpClient()

        val json = JSONObject()
        json.put("firebase_uid", firebaseUid)
        json.put("email", email)
        json.put("username", username)

        val mediaType = "application/json; charset=utf-8".toMediaType()
        val body = json.toString().toRequestBody(mediaType)

        val request = Request.Builder()
            .url("$backendUrl/register")
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                requireActivity().runOnUiThread {
                    callback(false, "Backend request failed: ${e.message}")
                }
            }

            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                requireActivity().runOnUiThread {
                    if (response.isSuccessful) {
                        callback(true, null)
                    } else {
                        val errorMessage = try {
                            JSONObject(responseBody).getString("error")
                        } catch (e: Exception) {
                            response.message
                        }
                        callback(false, errorMessage)
                    }
                }
            }
        })
    }

    private fun deleteUserFromFirebase(firebaseUid: String) {
        FirebaseAuthManager.firebaseAuth.currentUser?.delete()
            ?.addOnCompleteListener(requireActivity()) { task ->
                if (task.isSuccessful) {
                    println("User deleted from Firebase successfully.")
                } else {
                    println("Failed to delete user from Firebase: ${task.exception?.message}")
                }
            }
    }
}
