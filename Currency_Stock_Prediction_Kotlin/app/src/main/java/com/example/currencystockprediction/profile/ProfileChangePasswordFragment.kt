package com.example.currencystockprediction.profile

import android.content.ContentValues.TAG
import android.os.Bundle
import android.text.TextUtils
import android.util.Log
import android.util.Patterns
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageButton
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentProfileChangeEmailBinding
import com.example.currencystockprediction.databinding.FragmentProfileChangePasswordBinding
import com.example.currencystockprediction.databinding.FragmentProfileSettingsBinding
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.firebase.auth.EmailAuthProvider
import org.json.JSONObject


class ProfileChangePasswordFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private lateinit var binding: FragmentProfileChangePasswordBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentProfileChangePasswordBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val window = requireActivity().window
        insetsController = WindowInsetsControllerCompat(window, window.decorView)
        hideSystemUI()

        bottomNavView = requireActivity().findViewById(R.id.bottomNavView)
        originalBottomNavVisibility = bottomNavView.visibility
        bottomNavView.visibility = View.GONE

        setupToolbar()


        binding.changePasswordButton.setOnClickListener {
            initiateChangePassword()
        }


    }

    private fun initiateChangePassword() {
        val email = binding.emailTextInputEditText.text.toString().trim()
        val oldPassword = binding.currentPasswordEditText.text.toString().trim()
        val newPassword = binding.newPasswordEditText.text.toString().trim()

        if (!validateInputs(email, oldPassword, newPassword)) {
            return
        }


        reAuthenticateUser(email, oldPassword) { success, message ->
            if (success) {
                changePassword(newPassword)
            } else {
                requireActivity().runOnUiThread {
                    Toast.makeText(
                        requireContext(),
                        "Reauthentication failed: ${message ?: "Unknown error"}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }

    private fun changePassword(newPassword: String) {
        FirebaseAuthManager.firebaseAuth.currentUser?.updatePassword(newPassword)
            ?.addOnCompleteListener { task ->
                requireActivity().runOnUiThread {
                    if (task.isSuccessful) {
                        Toast.makeText(
                            requireContext(),
                            "Password changed successfully.",
                            Toast.LENGTH_LONG
                        ).show()
                        findNavController().popBackStack(R.id.profileFragment, false)
                    } else {
                        Toast.makeText(
                            requireContext(),
                            "Failed to change password: ${task.exception?.localizedMessage ?: "Unknown error"}",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            }
    }


    private fun reAuthenticateUser(email: String, password: String, callback: (Boolean, String?) -> Unit) {
        val credential = EmailAuthProvider.getCredential(email, password)
        FirebaseAuthManager.firebaseAuth.currentUser?.reauthenticate(credential)
            ?.addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    callback(true, null)
                } else {
                    val exception = task.exception
                    callback(false, exception?.localizedMessage)
                }
            }
    }


    private fun validateInputs(email: String, oldPassword: String, newPassword: String, ): Boolean {
        if (TextUtils.isEmpty(email)) {
            binding.emailTextInputLayout.error = "Aktualny adres e-mail jest wymagany"
            return false
        } else {
            binding.emailTextInputLayout.error = null
        }

        if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            binding.emailTextInputLayout.error = "Nieprawidłowy format e-mail"
            return false
        }

        if (TextUtils.isEmpty(oldPassword)) {
            binding.currentPasswordTextInputLayout.error = "Hasło jest wymagane"
            return false
        } else {
            binding.currentPasswordTextInputLayout.error = null
        }

        if (TextUtils.isEmpty(newPassword)) {
            binding.newPasswordTextInputLayout.error = "Nowe hasło jest wymagane"
            return false
        } else if (newPassword.length < 6) {
            binding.newPasswordTextInputLayout.error = "Hasło musi mieć co najmniej 6 znaków"
            return false
        } else {
            binding.newPasswordTextInputLayout.error = null
        }

        return true
    }


    private fun setupToolbar() {
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.profileFragment, false)
        }
    }

    override fun onResume() {
        super.onResume()
        hideSystemUI()
        if (bottomNavView.visibility != View.GONE) {
            bottomNavView.visibility = View.GONE
        }
    }

    override fun onPause() {
        super.onPause()
        showSystemUI()
        bottomNavView.visibility = originalBottomNavVisibility

    }
    private fun hideSystemUI() {
        insetsController?.let { controller ->
            controller.hide(WindowInsetsCompat.Type.systemBars())
            controller.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }
    private fun showSystemUI() {
        insetsController?.show(WindowInsetsCompat.Type.systemBars())
    }

    override fun onDestroyView() {
        super.onDestroyView()
        bottomNavView.visibility = originalBottomNavVisibility
        insetsController = null
    }

}