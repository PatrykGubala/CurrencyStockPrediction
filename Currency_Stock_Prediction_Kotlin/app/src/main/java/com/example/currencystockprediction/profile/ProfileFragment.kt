package com.example.currencystockprediction.profile

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.auth.start.StartFragmentDirections
import com.example.currencystockprediction.databinding.FragmentProfileBinding
import com.example.currencystockprediction.databinding.FragmentStartBinding
import com.example.currencystockprediction.utils.FirebaseAuthManager

class ProfileFragment : BaseFragment() {

    private lateinit var binding: FragmentProfileBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View{
        binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.logoutImageButton.setOnClickListener {
            logoutUser()
        }


        binding.settingsImageButton.setOnClickListener {
            findNavController().navigate(ProfileFragmentDirections.actionProfileFragmentToProfileSettingsFragment())
        }
    }

    private fun logoutUser() {
        FirebaseAuthManager.firebaseAuth.signOut()
        finishMainActivity()

        Toast.makeText(requireContext(), "Logged out successfully", Toast.LENGTH_SHORT).show()
    }
}