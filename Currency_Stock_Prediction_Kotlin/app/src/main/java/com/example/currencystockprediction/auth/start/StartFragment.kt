package com.example.currencystockprediction.auth.start

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.databinding.FragmentStartBinding
import com.example.currencystockprediction.BaseFragment



class StartFragment : BaseFragment() {

    private lateinit var binding: FragmentStartBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = FragmentStartBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.apply {
            setupLoginClick()
            setupRegistrationClick()
        }
    }

    private fun setupRegistrationClick() {

        binding.registerButton.setOnClickListener {
            findNavController().navigate(StartFragmentDirections.actionStartFragmentToRegistrationFragment())
        }
    }

    private fun setupLoginClick() {
        binding.loginButton.setOnClickListener {
            findNavController().navigate(StartFragmentDirections.actionStartFragmentToLoginFragment())
        }
    }
}
