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
import com.example.currencystockprediction.utils.SecurityUtils
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.firebase.auth.EmailAuthProvider
import com.google.firebase.auth.FirebaseAuthException
import org.json.JSONObject


class ProfileChangeEmailFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private var _binding: FragmentProfileChangeEmailBinding? = null
    private val binding get() = _binding!!


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileChangeEmailBinding.inflate(inflater, container, false)
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

        binding.changeEmailButton.setOnClickListener {
            changeEmail()
        }
    }

    private fun changeEmail() {
        val email = binding.emailTextInputEditText.text.toString().trim()
        val password = binding.passwordInputEditText.text.toString().trim()
        val newEmail = binding.newEmailTextInputEditText.text.toString().trim()

        if (!validateInputs(email, password, newEmail)) {
            return
        }

        reAuthenticateUser(email, password) { success, message ->
            if (success) {
                initiateEmailChange(newEmail)
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




    private fun validateInputs(email: String, password: String, newEmail: String, ): Boolean {
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

        if (TextUtils.isEmpty(password)) {
            binding.passwordTextInputLayout.error = "Hasło jest wymagane"
            return false
        } else {
            binding.passwordTextInputLayout.error = null
        }

        if (TextUtils.isEmpty(newEmail)) {
            binding.newEmailTextInputLayout.error = "Nowy adres e-mail jest wymagany"
            return false
        } else {
            binding.newEmailTextInputLayout.error = null
        }

        if (!Patterns.EMAIL_ADDRESS.matcher(newEmail).matches()) {
            binding.newEmailTextInputLayout.error = "Nieprawidłowy format e-mail"
            return false
        }
        return true
    }

    private fun initiateEmailChange(newEmail: String) {
        val json = JSONObject()
        json.put("new_email", newEmail)

        ApiClient.postRequest("/myapp/users/initiate_change_email", json) { success, response ->
            requireActivity().runOnUiThread {
                if (success) {
                    Toast.makeText(
                        requireContext(),
                        "Verification email sent to your new email address. Please check your inbox to verify the change.",
                        Toast.LENGTH_LONG
                    ).show()
                    findNavController().popBackStack(R.id.profileFragment, false)
                } else {
                    Toast.makeText(
                        requireContext(),
                        "Failed to initiate email change: ${response ?: "Unknown error"}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
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
        _binding = null
    }

}