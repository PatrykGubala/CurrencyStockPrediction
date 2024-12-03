// SetPinFragment.kt
package com.example.currencystockprediction.auth.pin

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.biometric.BiometricManager
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment

import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.databinding.FragmentSetPinBinding
import com.example.currencystockprediction.utils.BiometricUtils
import com.example.currencystockprediction.utils.SecurityUtils

class SetPinFragment : Fragment() {

    private var _binding: FragmentSetPinBinding? = null
    private val binding get() = _binding!!

    private val pinInput = StringBuilder()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentSetPinBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?,
    ) {
        super.onViewCreated(view, savedInstanceState)
        setUpNumericKeypad()
        binding.buttonBackwards.setOnClickListener { removeLastPinDigit() }

        if (BiometricUtils.isBiometricReady(requireContext())) {
            handleFingerprintAuthentication()
        }
    }

    private fun setUpNumericKeypad() {
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
                if (pinInput.length == 4) savePin()
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

    private fun savePin() {
        val pin = pinInput.toString()
        if (pin.length == 4) {
            val success = SecurityUtils.savePin(requireContext(), pin)
            if (success) {
                Toast.makeText(requireContext(), "PIN został ustawiony.", Toast.LENGTH_SHORT).show()
                navigateToMainActivity()
            } else {
                Toast.makeText(requireContext(), "Błąd podczas zapisywania PIN.", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(requireContext(), "PIN musi mieć 4 cyfry.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun handleFingerprintAuthentication() {
        if (BiometricUtils.isBiometricReady(requireContext())) {
            val biometricPrompt = androidx.biometric.BiometricPrompt(this,
                ContextCompat.getMainExecutor(requireContext()),
                object : androidx.biometric.BiometricPrompt.AuthenticationCallback() {
                    override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                        super.onAuthenticationError(errorCode, errString)
                        Toast.makeText(context, "Błąd uwierzytelniania: $errString", Toast.LENGTH_SHORT).show()
                    }

                    override fun onAuthenticationSucceeded(result: androidx.biometric.BiometricPrompt.AuthenticationResult) {
                        super.onAuthenticationSucceeded(result)
                        navigateToMainActivity()
                    }

                    override fun onAuthenticationFailed() {
                        super.onAuthenticationFailed()
                        Toast.makeText(context, "Uwierzytelnianie nie powiodło się", Toast.LENGTH_SHORT).show()
                    }
                })

            val promptInfo = androidx.biometric.BiometricPrompt.PromptInfo.Builder()
                .setTitle("Ustawienie Uwierzytelniania Biometrycznego")
                .setSubtitle("Ustaw biometryczne uwierzytelnianie jako alternatywę dla PIN")
                .setNegativeButtonText("Użyj PIN")
                .build()

            biometricPrompt.authenticate(promptInfo)
        } else {
            Toast.makeText(context, "Uwierzytelnianie biometryczne nie jest dostępne.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun navigateToMainActivity() {
        activity?.let {
            val intent = Intent(it, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            it.startActivity(intent)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
