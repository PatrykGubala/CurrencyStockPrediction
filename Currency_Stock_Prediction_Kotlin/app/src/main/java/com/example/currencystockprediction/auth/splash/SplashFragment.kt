package com.example.currencystockprediction.auth.splash

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import com.example.currencystockprediction.utils.SessionManager

class SplashFragment : Fragment(R.layout.fragment_splash) {

    override fun onViewCreated(view: android.view.View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        Handler(Looper.getMainLooper()).postDelayed({
            checkAuthenticationStatus()
        }, 1000)
    }

    private fun checkAuthenticationStatus() {
        if (FirebaseAuthManager.isUserLoggedIn()) {
            if (SessionManager.isAppInBackground()) {
                if (SecurityUtils.hasPin(requireContext()) || SecurityUtils.isBiometricEnabled(requireContext())) {
                    navigateToAuthentication()
                } else {
                    navigateToMainActivity()
                }
            } else {
                if (SecurityUtils.hasPin(requireContext()) || SecurityUtils.isBiometricEnabled(requireContext())) {
                    navigateToAuthentication()
                } else {
                    navigateToMainActivity()
                }
            }
        } else {
            navigateToStart()
        }
    }

    private fun navigateToAuthentication() {
        if (SecurityUtils.isBiometricEnabled(requireContext())) {
            navigateToBiometric()
        } else {
            navigateToPinInput()
        }
    }


    private fun navigateToBiometric() {

        findNavController().navigate(SplashFragmentDirections.actionSplashFragmentToPinInputFragment())
    }

    private fun navigateToPinInput() {
        findNavController().navigate(SplashFragmentDirections.actionSplashFragmentToPinInputFragment())
    }

    private fun navigateToSetPin() {
        findNavController().navigate(SplashFragmentDirections.actionSplashFragmentToSetPinFragment())
    }

    private fun navigateToStart() {
        findNavController().navigate(SplashFragmentDirections.actionSplashFragmentToStartFragment())
    }

    private fun navigateToMainActivity() {
        activity?.let {
            val intent = Intent(it, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            it.startActivity(intent)
            it.finish()
        }
    }
}
