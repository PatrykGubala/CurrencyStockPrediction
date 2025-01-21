package com.example.currencystockprediction.profile

import android.os.Bundle
import android.text.TextUtils
import android.util.Patterns
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentProfileChangePasswordBinding
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.firebase.auth.EmailAuthProvider
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await


class ProfileChangePasswordFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private var _binding: FragmentProfileChangePasswordBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileChangePasswordBinding.inflate(inflater, container, false)
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


        lifecycleScope.launch {
            val (reauthSuccess, reauthMessage) = reAuthenticateUser(email, oldPassword)
            if (reauthSuccess) {
                changePassword(newPassword)
            }else {
                Toast.makeText(requireContext(), "Ponowna autoryzacja się nie udała: ${reauthMessage ?: "Error"}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun reAuthenticateUser(email: String, password: String): Pair<Boolean, String?> {
        return try {
            val credential = EmailAuthProvider.getCredential(email, password)
            FirebaseAuthManager.firebaseAuth.currentUser?.reauthenticate(credential)?.await()
            Pair(true, null)
        } catch (e: Exception) {
            Pair(false, e.localizedMessage)
        }
    }

    private fun changePassword(newPassword: String) {
        lifecycleScope.launch {
            try {
                FirebaseAuthManager.firebaseAuth.currentUser?.updatePassword(newPassword)?.await()
                Toast.makeText(requireContext(), "Hasło zmienione", Toast.LENGTH_LONG).show()
                findNavController().popBackStack(R.id.profileFragment, false)
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "Nie udało się zmienić hasła: ${e.localizedMessage ?: "Error"}", Toast.LENGTH_SHORT).show()
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
        _binding = null
    }

}