package com.example.currencystockprediction.auth.pin

import android.content.ContentValues.TAG
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.databinding.FragmentPinInputBinding
import com.example.currencystockprediction.databinding.FragmentSetPinBinding
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import com.example.currencystockprediction.utils.SessionManager

class PinInputFragment : BaseFragment() {

    private var _binding: FragmentPinInputBinding? = null
    private val binding get() = _binding!!

    private val pinInput = StringBuilder()
    private lateinit var storedPin: String

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentPinInputBinding.inflate(inflater, container, false)
        return binding.root
    }


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        loadStoredPin()
        setupNumericKeypad()
        binding.buttonBackwards.setOnClickListener {
            removeLastPinDigit()
        }
        binding.buttonFingerprint.setOnClickListener {
            handleBiometricAuthentication()
        }
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }
    }

    private fun setupNumericKeypad() {
        val buttons = listOf(
            binding.button0, binding.button1, binding.button2,
            binding.button3, binding.button4, binding.button5,
            binding.button6, binding.button7, binding.button8,
            binding.button9
        )
        buttons.forEach { button ->
            button.setOnClickListener {
                if (pinInput.length < 4) {
                    pinInput.append(button.text.toString())
                    updatePinDots()
                }
                if (pinInput.length == 4)
                {
                    validatePin()
                    Log.e(TAG, "PIN validation.")

                }
            }
        }
    }

    private fun updatePinDots() {
        val pinDots = listOf(
            binding.dot1, binding.dot2, binding.dot3, binding.dot4
        )
        for (i in pinDots.indices) {
            if (i < pinInput.length) {
                pinDots[i].setBackgroundResource(R.drawable.pin_dot_filled)
            } else {
                pinDots[i].setBackgroundResource(R.drawable.pin_dot_empty)
            }
        }
    }

    private fun removeLastPinDigit() {
        if (pinInput.isNotEmpty()) {
            pinInput.deleteCharAt(pinInput.length - 1)
            updatePinDots()
        }
    }

    private fun validatePin() {
        val inputPin = pinInput.toString()
        if (inputPin == storedPin) {
            Log.d(TAG, "PIN validation successful.")

            authenticateWithStoredCredentials()
        } else {
            Log.e(TAG, "PIN validation failed.")

            Toast.makeText(requireContext(), "Niepoprawny PIN. Spróbuj ponownie.", Toast.LENGTH_SHORT).show()
            pinInput.clear()
            updatePinDots()
        }
    }


    private fun authenticateWithStoredCredentials() {
        val credentials = SecurityUtils.getCredentials(requireContext())
        if (credentials != null) {
            val (email, password) = credentials
            Log.d(TAG, "Authenticating with stored credentials for email: $email")
            FirebaseAuthManager.signIn(email, password) { success, exception ->
                if (success) {
                    Log.d(TAG, "Re-authentication successful.")
                    navigateToMainActivity()
                } else {
                    Log.e(TAG, "Re-authentication failed: ${exception?.message}")
                    Toast.makeText(requireContext(), "Re-authentication failed: ${exception?.message}", Toast.LENGTH_SHORT).show()
                }
            }
        } else {
            Log.e(TAG, "No stored credentials found.")
            Toast.makeText(requireContext(), "Nie znaleziono konta na urządzeniu. Proszę się zalogować ponownie.", Toast.LENGTH_SHORT).show()
            findNavController().navigate(R.id.action_pinInputFragment_to_startFragment)
        }
    }

    private fun loadStoredPin() {
        storedPin = SecurityUtils.getPin(requireContext()) ?: ""
        Log.d(TAG, "Loaded stored PIN: $storedPin")

        if (storedPin.isEmpty()) {
            Toast.makeText(requireContext(), "PIN nie został ustawiony. Proszę się zarejestrować ponownie.", Toast.LENGTH_SHORT).show()
            findNavController().navigate(R.id.action_pinInputFragment_to_startFragment)
        }
    }

    private fun handleBiometricAuthentication() {
        if (SecurityUtils.isBiometricReady(requireContext())) {
            val biometricPrompt = BiometricPrompt(this,
                ContextCompat.getMainExecutor(requireContext()),
                object : BiometricPrompt.AuthenticationCallback() {
                    override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                        super.onAuthenticationError(errorCode, errString)
                        if (errorCode != BiometricPrompt.ERROR_NEGATIVE_BUTTON) {
                            Toast.makeText(context, "Authentication error: $errString", Toast.LENGTH_SHORT).show()
                        }
                    }

                    override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                        super.onAuthenticationSucceeded(result)
                        navigateToMainActivity()
                    }

                    override fun onAuthenticationFailed() {
                        super.onAuthenticationFailed()
                        Toast.makeText(context, "Authentication failed", Toast.LENGTH_SHORT).show()
                    }
                })

            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle("Biometric Authentication")
                .setSubtitle("Authenticate using biometrics")
                .setNegativeButtonText("Use PIN")
                .build()

            biometricPrompt.authenticate(promptInfo)
        } else {
            Toast.makeText(context, "Biometric authentication not available.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun navigateToMainActivity() {
        SessionManager.setAppInBackground(false)

        activity?.let {
            val intent = Intent(it, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            it.startActivity(intent)
            it.finish()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
