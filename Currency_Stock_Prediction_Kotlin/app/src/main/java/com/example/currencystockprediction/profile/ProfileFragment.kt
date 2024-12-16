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
import androidx.navigation.fragment.findNavController
import com.bumptech.glide.Glide
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.databinding.FragmentProfileBinding
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.CacheManager
import com.example.currencystockprediction.utils.FirebaseAuthManager
import org.json.JSONObject
import java.io.ByteArrayOutputStream

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
        loadCachedUserData()
        fetchUserData()
        binding.logoutImageButton.setOnClickListener {
            logoutUser()
        }
        binding.settingsImageButton.setOnClickListener {
            findNavController().navigate(ProfileFragmentDirections.actionProfileFragmentToProfileSettingsFragment())
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


    private fun fetchUserData() {
        ApiClient.getRequest("/myapp/users/get_user_info") { success, response ->
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
        val baos = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, baos) // Compress to 80% quality for optimization
        val imageBase64 = Base64.encodeToString(baos.toByteArray(), Base64.DEFAULT)
        val json = JSONObject()
        json.put("image_base64", imageBase64)
        ApiClient.postRequest("/myapp/users/upload_profile_image", json) { success, response ->
            requireActivity().runOnUiThread {
                if (success && response != null) {
                    try {
                        val responseJson = JSONObject(response)
                        val newImageUrl = responseJson.optString("profile_image_url", "")
                        if (!newImageUrl.isNullOrEmpty()) {
                            CacheManager.saveProfileImageUrl(requireContext(), newImageUrl)
                            Glide.with(requireContext())
                                .load(newImageUrl)
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
    }
    private fun logoutUser() {
        FirebaseAuthManager.firebaseAuth.signOut()
        CacheManager.clearCache(requireContext())
        finishMainActivity()

        Toast.makeText(requireContext(), "Logged out successfully", Toast.LENGTH_SHORT).show()
    }
}