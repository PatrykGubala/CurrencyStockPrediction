package com.example.currencystockprediction.profile.settings

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
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
                SecurityUtils.savePin(requireContext(), "")
            }
        }

        binding.biometricsSwitch.isChecked = SecurityUtils.isBiometricEnabled(requireContext())
        binding.biometricsSwitch.setOnCheckedChangeListener { _, isChecked ->
            SecurityUtils.setBiometricEnabled(requireContext(), isChecked)
        }
    }
}
