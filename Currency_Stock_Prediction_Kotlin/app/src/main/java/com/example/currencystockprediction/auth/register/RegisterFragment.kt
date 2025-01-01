package com.example.currencystockprediction.auth.register

import android.content.ContentValues.TAG
import android.os.Bundle
import android.text.TextUtils
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentRegisterBinding
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import kotlinx.coroutines.launch
import org.json.JSONObject

class RegisterFragment : BaseFragment() {
    private lateinit var binding: FragmentRegisterBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        binding = FragmentRegisterBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?,
    ) {
        super.onViewCreated(view, savedInstanceState)



        binding.registerButton.setOnClickListener {
            registerUser()
        }
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }

        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }
    }

    private fun registerUser() {
        val email = binding.textInputEditTextEmail.text.toString().trim()
        val password = binding.textInputEditTextPassword.text.toString().trim()
        val repeatPassword = binding.textInputEditTextRepeatPassword.text.toString().trim()
        val username = binding.textInputEditTextUsername.text.toString().trim()

        if (TextUtils.isEmpty(email)) {
            binding.textInputEditTextPassword.error = "Email is required"
            return
        }

        if (TextUtils.isEmpty(password)) {
            binding.textInputEditTextPassword.error = "Password is required"
            return
        }

        if (password.length < 6) {
            binding.textInputEditTextPassword.error = "Password must be at least 6 characters"
            return
        }

        if (password != repeatPassword) {
            binding.textInputEditTextPassword.error = "Passwords do not match"
            return
        }

        if (TextUtils.isEmpty(username)) {
            binding.textInputEditTextUsername.error = "Username is required"
            return
        }

        binding.progressBar.visibility = View.VISIBLE

        FirebaseAuthManager.firebaseAuth.createUserWithEmailAndPassword(email, password)
            .addOnCompleteListener(requireActivity()) { task ->
                if (task.isSuccessful) {
                    val firebaseUser = FirebaseAuthManager.firebaseAuth.currentUser
                    firebaseUser?.let {
                        val firebaseUid = it.uid
                        registerUserOnBackend(firebaseUid, email, username)
                    } ?: run {
                        binding.progressBar.visibility = View.GONE
                        Toast.makeText(context, "Firebase registration failed: User is null", Toast.LENGTH_LONG).show()
                    }
                } else {
                    requireActivity().runOnUiThread {
                        binding.progressBar.visibility = View.GONE
                        Toast.makeText(context, "Firebase registration failed: ${task.exception?.message}", Toast.LENGTH_LONG).show()
                    }
                }
            }
    }

    private fun registerUserOnBackend(firebaseUid: String, email: String, username: String) {
        val json = JSONObject()
        json.put("firebase_uid", firebaseUid)
        json.put("email", email)
        json.put("username", username)

        lifecycleScope.launch {
            binding.progressBar.visibility = View.VISIBLE
            val (success, message) = ApiClient.postRequest("/myapp/users/register", json)
            binding.progressBar.visibility = View.GONE
            if (success) {
                SecurityUtils.saveReAuthNeeded(requireContext(), true)
                Toast.makeText(context, "User registered successfully", Toast.LENGTH_LONG).show()
                findNavController().navigate(RegisterFragmentDirections.actionRegisterFragmentToSetPinFragment())
            } else {
                deleteUserFromFirebase(firebaseUid)
                Toast.makeText(context, "Registration failed: $message", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun deleteUserFromFirebase(firebaseUid: String) {
        FirebaseAuthManager.firebaseAuth.currentUser?.delete()
            ?.addOnCompleteListener(requireActivity()) { task ->
                if (task.isSuccessful) {
                    Log.d("RegisterFragment", "User deleted from Firebase successfully.")
                } else {
                    Log.e("RegisterFragment", "Failed to delete user from Firebase: ${task.exception?.message}")
                }
            }
    }
}
