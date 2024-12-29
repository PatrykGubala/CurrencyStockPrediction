package com.example.currencystockprediction.profile.settings

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentProfileSettingsBinding
import com.example.currencystockprediction.utils.SecurityUtils
import com.google.android.material.bottomnavigation.BottomNavigationView

class SettingsFragment : BaseFragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE

    private lateinit var binding: FragmentProfileSettingsBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentProfileSettingsBinding.inflate(inflater, container, false)
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


        binding.pinSwitch.isChecked = SecurityUtils.hasPin(requireContext())
        binding.pinSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                findNavController().navigate(
                    SettingsFragmentDirections.actionSettingsFragmentToSetPinFragment()
                )
            } else {
                SecurityUtils.clearPin(requireContext())
                binding.biometricsSwitch.isChecked = false
                SecurityUtils.setBiometricEnabled(requireContext(), false)
                Toast.makeText(context, "PIN został wyłączony.", Toast.LENGTH_SHORT).show()
            }
        }

        binding.biometricsSwitch.isChecked = SecurityUtils.isBiometricEnabled(requireContext())
        binding.biometricsSwitch.isEnabled = SecurityUtils.hasPin(requireContext())

        binding.biometricsSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                if (SecurityUtils.hasPin(requireContext())) {
                    if (SecurityUtils.isBiometricReady(requireContext())) {
                        SecurityUtils.setBiometricEnabled(requireContext(), true)
                        Toast.makeText(context, "Biometric authentication enabled.", Toast.LENGTH_SHORT).show()
                    } else {
                        binding.biometricsSwitch.isChecked = false
                        SecurityUtils.setBiometricEnabled(requireContext(), false)
                        SecurityUtils.promptBiometricEnrollment(requireActivity())
                        Toast.makeText(context, "Biometric features not available. Enrollment prompted.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    binding.biometricsSwitch.isChecked = false
                    findNavController().navigate(
                        SettingsFragmentDirections.actionSettingsFragmentToSetPinFragment()
                    )
                    Toast.makeText(context, "Please set up a PIN before enabling biometrics.", Toast.LENGTH_SHORT).show()
                }
            } else {
                SecurityUtils.setBiometricEnabled(requireContext(), false)
                Toast.makeText(context, "Biometric authentication disabled.", Toast.LENGTH_SHORT).show()
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
    }

}
