package com.example.currencystockprediction

import android.content.Intent
import android.os.Bundle
import android.transition.TransitionInflater
import androidx.fragment.app.Fragment
import com.example.currencystockprediction.activities.AuthenticationActivity
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.utils.FirebaseAuthManager

abstract class BaseFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val transInflater = TransitionInflater.from(requireContext())
        enterTransition = transInflater.inflateTransition(R.transition.slide_right)
        exitTransition = transInflater.inflateTransition(R.transition.fade_out)
    }

    protected fun startMainActivity() {
        activity?.let {
            val intent = Intent(it, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            it.startActivity(intent)
            requireActivity().finish()

        }
    }

    protected fun finishMainActivity() {
        activity?.let {
            val intent = Intent(it, AuthenticationActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            it.startActivity(intent)
            requireActivity().finish()

        }
    }
}