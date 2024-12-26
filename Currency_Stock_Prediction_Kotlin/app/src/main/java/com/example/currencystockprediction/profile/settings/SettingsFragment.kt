package com.example.currencystockprediction.profile.settings

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentProfileSettingsBinding
import com.example.currencystockprediction.utils.SecurityUtils

class SettingsFragment : BaseFragment() {

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

        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.profileFragment, false)
        }

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
}
