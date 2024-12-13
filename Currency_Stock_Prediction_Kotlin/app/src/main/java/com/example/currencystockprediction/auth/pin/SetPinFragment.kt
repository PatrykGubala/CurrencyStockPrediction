package com.example.currencystockprediction.auth.pin

import android.content.ContentValues.TAG
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.biometric.BiometricManager
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import com.example.currencystockprediction.BaseFragment

import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.databinding.FragmentSetPinBinding
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils

class SetPinFragment : BaseFragment() {

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
            Log.d(TAG, "PIN saved successfully: $success")

            if (success) {
                val firebaseUser = FirebaseAuthManager.firebaseAuth.currentUser
                val firebaseUid = firebaseUser?.uid
                val email = firebaseUser?.email
                Log.d(TAG, "Firebase UID: $firebaseUid, Email: $email")

                if (firebaseUid != null && email != null) {
                    SecurityUtils.saveAccount(requireContext(), firebaseUid)
                } else {
                    Toast.makeText(
                        requireContext(),
                        "Błąd: Nie udało się uzyskać informacji o użytkowniku.",
                        Toast.LENGTH_SHORT
                    ).show()
                    return
                }

                Toast.makeText(requireContext(), "PIN został ustawiony.", Toast.LENGTH_SHORT).show()
                navigateToMainActivity()
            } else {
                Log.e(TAG, "Failed to save PIN.")
                Toast.makeText(requireContext(), "Błąd podczas zapisywania PIN.", Toast.LENGTH_SHORT).show()
            }
        } else {
            Log.e(TAG, "Invalid PIN length: ${pin.length}")
            Toast.makeText(requireContext(), "PIN musi mieć 4 cyfry.", Toast.LENGTH_SHORT).show()
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
