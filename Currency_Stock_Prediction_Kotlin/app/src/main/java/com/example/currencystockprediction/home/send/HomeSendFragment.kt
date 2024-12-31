package com.example.currencystockprediction.home.send

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentHomeSendBinding
import com.example.currencystockprediction.home.HomeViewModel
import com.example.currencystockprediction.utils.ApiClient
import com.google.android.material.bottomnavigation.BottomNavigationView
import org.json.JSONObject
import java.util.regex.Pattern


class HomeSendFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private var _binding: FragmentHomeSendBinding? = null
    private val binding get() = _binding!!

    private val PUBLIC_ACCOUNT_ID_PATTERN = Pattern.compile("^[a-fA-F0-9]{13}[A-Z]{3}$")

    private lateinit var viewModel: HomeViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeSendBinding.inflate(inflater, container, false)
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

        viewModel = ViewModelProvider(requireActivity()).get(HomeViewModel::class.java)
        viewModel.usdBalance.observe(viewLifecycleOwner) { balance ->
            binding.accountAmountTextView.text = "Stan konta: $${String.format("%.2f", balance)}"
        }
        fetchAccountBalances()

        binding.sendSubmitButton.setOnClickListener {
            sendCurrency()
        }
    }

    private fun isValidPublicAccountId(publicAccountId: String): Boolean {
        val pattern = Pattern.compile("^[a-fA-F0-9]{13}[A-Z]{3,4}$")
        return pattern.matcher(publicAccountId).matches()
    }

    private fun sendCurrency() {
        val amountStr = binding.sendAmountTextInputEditText.text.toString().trim()
        val publicAccountId = binding.sendPublicAccountTextInputEditText.text.toString().trim()

        if (amountStr.isEmpty() || publicAccountId.isEmpty()) {
            Toast.makeText(
                requireContext(),
                "Please enter amount and Public Account ID",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        val amount = amountStr.toDoubleOrNull()
        if (amount == null || amount <= 0) {
            Toast.makeText(requireContext(), "Please enter a valid amount", Toast.LENGTH_SHORT)
                .show()
            return
        }

        if (!PUBLIC_ACCOUNT_ID_PATTERN.matcher(publicAccountId).matches()) {
            Toast.makeText(requireContext(), "Invalid Public Account ID format", Toast.LENGTH_SHORT)
                .show()
            return
        }

        val json = JSONObject().apply {
            put("public_account_id", publicAccountId)
            put("amount", amount)
        }
        binding.sendSubmitButton.isEnabled = false

        ApiClient.postRequest("/myapp/accounts/currencies/send", json) { success, response ->
            requireActivity().runOnUiThread {
                binding.sendSubmitButton.isEnabled = true
                if (success && response != null) {
                    try {
                        val jsonResponse = JSONObject(response)
                        val message = jsonResponse.optString("message", "Send successful.")
                        val senderNewBalance = jsonResponse.optDouble("sender_new_balance", -1.0)
                        val receiverNewBalance = jsonResponse.optDouble("receiver_new_balance", -1.0)

                        if (senderNewBalance >= 0 && receiverNewBalance >= 0) {
                            binding.sendAmountTextInputEditText.text?.clear()
                            binding.sendPublicAccountTextInputEditText.text?.clear()
                            viewModel.setUsdBalance(senderNewBalance)
                            Toast.makeText(requireContext(), "$message New Balance: $$senderNewBalance", Toast.LENGTH_SHORT).show()
                        } else {
                            Toast.makeText(requireContext(), message, Toast.LENGTH_SHORT).show()
                        }
                    } catch (e: Exception) {
                        Toast.makeText(requireContext(), "Error parsing response.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val errorMsg = response?.let { "Send failed: $it" } ?: "Send failed: Unknown error"
                    Toast.makeText(requireContext(), errorMsg, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }


    private fun fetchAccountBalances() {
        ApiClient.getRequest("/myapp/accounts/currencies") { success, response ->
            requireActivity().runOnUiThread {
                if (success && response != null) {
                    try {
                        val jsonResponse = JSONObject(response)
                        val currenciesArray = jsonResponse.getJSONArray("currencies")
                        for (i in 0 until currenciesArray.length()) {
                            val currencyObj = currenciesArray.getJSONObject(i)
                            val code = currencyObj.getString("currency_code")
                            val balance = currencyObj.getDouble("balance")
                            if (code.equals("USD", ignoreCase = true)) {
                                viewModel.setUsdBalance(balance)
                                break
                            }
                        }
                    } catch (e: Exception) {
                        Toast.makeText(
                            requireContext(),
                            "Error parsing account balances.",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                } else {
                    Toast.makeText(
                        requireContext(),
                        "Failed to fetch account balances.",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }


    private fun setupToolbar() {
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.homeFragment, false)
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
        _binding = null
    }
}

