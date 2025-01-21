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
import com.example.currencystockprediction.databinding.FragmentProfileChangeUsernameBinding
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.firebase.auth.EmailAuthProvider
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import org.json.JSONObject

class ProfileChangeUsernameFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private var _binding: FragmentProfileChangeUsernameBinding? = null
    private val binding get() = _binding!!


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileChangeUsernameBinding.inflate(inflater, container, false)
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

        binding.changeUsernameButton.setOnClickListener {
            initiateChangeUsername()
        }
    }

    private fun initiateChangeUsername() {
        val email = binding.emailTextInputEditText.text.toString().trim()
        val password = binding.passwordEditText.text.toString().trim()
        val newUsername = binding.usernameEditText.text.toString().trim()

        if (!validateInputs(email, password, newUsername)) {
            return
        }

        lifecycleScope.launch {
            val (reauthSuccess, reauthMessage) = reAuthenticateUser(email, password)
            if (reauthSuccess) {
                changeUsername(newUsername)
            } else {
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

    private fun validateInputs(email: String, password: String, newUsername: String): Boolean {
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

        if (TextUtils.isEmpty(newUsername)) {
            binding.usernameTextInputLayout.error = "Nowa nazwa użytkownika jest wymagana"
            return false
        } else if (newUsername.length < 3) {
            binding.usernameTextInputLayout.error = "Nazwa użytkownika musi mieć co najmniej 3 znaki"
            return false
        } else {
            binding.usernameTextInputLayout.error = null
        }

        return true
    }

    private fun changeUsername(newUsername: String) {
        lifecycleScope.launch {
            val json = JSONObject().apply {
                put("new_username", newUsername)
            }
            val (success, response) = ApiClient.postRequest("/myapp/users/change_username", json)
            if (success) {
                Toast.makeText(
                    requireContext(),
                    "Nazwa użytkownika została zmienona",
                    Toast.LENGTH_LONG
                ).show()
                findNavController().popBackStack(R.id.profileFragment, false)
            } else {
                Toast.makeText(
                    requireContext(),
                    "Nie udało się zmienić nazwy użytkownika: ${response ?: "Error"}",
                    Toast.LENGTH_SHORT
                ).show()
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
