package com.example.currencystockprediction.auth.splash

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import com.example.currencystockprediction.utils.SessionManager
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class SplashFragment : Fragment(R.layout.fragment_splash) {

    override fun onViewCreated(view: android.view.View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            delay(1000)
            checkAuthenticationStatus()
        }
    }

    private fun checkAuthenticationStatus() {
        if (isUserOnDevice()) {
            if (FirebaseAuthManager.isUserLoggedIn()) {
                navigateToMain()
            }else {
                checkTwoFactorAuth()
            }

        } else {
            navigateToStart()
        }
    }

    private fun isUserOnDevice(): Boolean {
        return SecurityUtils.getSavedAccount(requireContext()) != null
    }

    private fun checkTwoFactorAuth() {
        if (SecurityUtils.hasPin(requireContext()) || SecurityUtils.isBiometricEnabled(requireContext())) {
            navigateToPinInput()
        } else {
            navigateToMain()
        }
    }

    private fun navigateToMain() {
        activity?.let {
            val intent = Intent(it, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            it.startActivity(intent)
            it.finish()
        }
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


}
