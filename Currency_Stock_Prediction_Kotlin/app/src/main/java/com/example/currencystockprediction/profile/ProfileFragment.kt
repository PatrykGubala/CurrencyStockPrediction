package com.example.currencystockprediction.profile

import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.os.Bundle
import android.provider.MediaStore
import android.util.Base64
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentHomeSendBinding
import com.example.currencystockprediction.databinding.FragmentProfileBinding
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.CacheManager
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.io.ByteArrayOutputStream

class ProfileFragment : BaseFragment() {
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View{
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        loadCachedUserData()

        lifecycleScope.launch {
            fetchUserData()
        }

        binding.logoutImageButton.setOnClickListener {
            logoutUser()
        }
        binding.settingsImageButton.setOnClickListener {
            findNavController().navigate(ProfileFragmentDirections.actionProfileFragmentToProfileSettingsFragment())
        }
        binding.emailImageButton.setOnClickListener {
            findNavController().navigate(ProfileFragmentDirections.actionProfileFragmentToProfileChangeEmailFragment())
        }
        binding.passwordImageButton.setOnClickListener {
            findNavController().navigate(ProfileFragmentDirections.actionProfileFragmentToProfileChangePasswordFragment())
        }
        binding.usernameChangeImageButton.setOnClickListener {
            findNavController().navigate(ProfileFragmentDirections.actionProfileFragmentToProfileChangeUsernameFragment())
        }
        binding.profileAvatarCardView.setOnClickListener {
            selectImageFromGallery()
        }
    }
    private fun loadCachedUserData() {
        val cachedUsername = CacheManager.getUsername(requireContext())
        val cachedProfileImageUrl = CacheManager.getProfileImageUrl(requireContext())

        if (!cachedUsername.isNullOrEmpty()) {
            binding.usernameTextView.text = cachedUsername
        }

        if (!cachedProfileImageUrl.isNullOrEmpty()) {
            Glide.with(requireContext())
                .load(cachedProfileImageUrl)
                .into(binding.profileAvatarImageView)
        }
    }


    private suspend fun fetchUserData() {
        val endpoint = "/myapp/users/get_user_info"
        val (success, response) = ApiClient.getRequest(endpoint)
        if (success && response != null) {
            try {
                val json = JSONObject(response)
                val username = json.optString("username", "")
                val profileImageUrl = json.optString("profile_image_url", "")

                if (!username.isNullOrEmpty()) {
                    CacheManager.saveUsername(requireContext(), username)
                }
                if (!profileImageUrl.isNullOrEmpty()) {
                    CacheManager.saveProfileImageUrl(requireContext(), profileImageUrl)
                }

                requireActivity().runOnUiThread {
                    binding.usernameTextView.text = username
                    if (!profileImageUrl.isNullOrEmpty()) {
                        Glide.with(requireContext())
                            .load(profileImageUrl)
                            .diskCacheStrategy(DiskCacheStrategy.ALL)
                            .placeholder(R.drawable.ic_launcher_background)
                            .error(R.drawable.ic_launcher_background)
                            .into(binding.profileAvatarImageView)
                    }
                }
            } catch (e: Exception) {
                Log.e("ProfileFragment", "Error parsing user data: ${e.message}")
                requireActivity().runOnUiThread {
                    Toast.makeText(context, "Failed to parse user data", Toast.LENGTH_SHORT).show()
                }
            }
        } else {
            requireActivity().runOnUiThread {
                Toast.makeText(context, "Failed to fetch user data: ${response ?: "Unknown error"}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    private val pickImage =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK && result.data != null) {
                val source = result.data!!.data?.let {
                    ImageDecoder.createSource(requireContext().contentResolver, it)
                }
                val bitmap = source?.let { ImageDecoder.decodeBitmap(it) }
                bitmap?.let { uploadProfileImage(it) }
            }
        }
    private fun selectImageFromGallery() {
        val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
        pickImage.launch(intent)
    }

    private fun uploadProfileImage(bitmap: Bitmap) {
        lifecycleScope.launch {
            val baos = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, 80, baos)
            val imageBase64 = Base64.encodeToString(baos.toByteArray(), Base64.DEFAULT)
            val json = JSONObject().apply {
                put("image_base64", imageBase64)
            }
            val (success, response) = ApiClient.postRequest("/myapp/users/upload_profile_image", json)
            if (success && response != null) {
                try {
                    val responseJson = JSONObject(response)
                    val newImageUrl = responseJson.optString("profile_image_url", "")
                    if (!newImageUrl.isNullOrEmpty()) {
                        CacheManager.saveProfileImageUrl(requireContext(), newImageUrl)
                        Glide.with(requireContext())
                            .load(newImageUrl)
                            .diskCacheStrategy(DiskCacheStrategy.ALL)
                            .placeholder(R.drawable.ic_launcher_background)
                            .error(R.drawable.ic_launcher_background)
                            .into(binding.profileAvatarImageView)
                        Toast.makeText(context, "Profile image updated successfully", Toast.LENGTH_SHORT).show()
                    } else {
                        Log.e("ProfileFragment", "profile_image_url not found in response")
                        Toast.makeText(context, "Failed to retrieve image URL", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Log.e("ProfileFragment", "Error parsing response: ${e.message}")
                    Toast.makeText(context, "Failed to parse server response", Toast.LENGTH_SHORT).show()
                }
            } else {
                Log.e("ProfileFragment", "Upload failed. Response: $response")
                Toast.makeText(context, "Failed to upload image: ${response ?: "Unknown error"}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun logoutUser() {
        lifecycleScope.launch {
            SecurityUtils.saveReAuthNeeded(requireContext(), true)
            CacheManager.clearCache(requireContext())
            finishMainActivity()
            Toast.makeText(requireContext(), "Logged out successfully", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}