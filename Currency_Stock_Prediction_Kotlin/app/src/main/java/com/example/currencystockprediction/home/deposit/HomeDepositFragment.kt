package com.example.currencystockprediction.home.deposit

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
import com.example.currencystockprediction.databinding.FragmentHomeDepositBinding
import com.example.currencystockprediction.databinding.FragmentHomeSendBinding
import com.example.currencystockprediction.home.HomeFragmentDirections
import com.example.currencystockprediction.home.HomeViewModel
import com.example.currencystockprediction.utils.ApiClient
import com.google.android.material.bottomnavigation.BottomNavigationView
import org.json.JSONObject


class HomeDepositFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE

    private var _binding: FragmentHomeDepositBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: HomeViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeDepositBinding.inflate(inflater, container, false)
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


        binding.depositSubmitButton.setOnClickListener {
            depositCurrency()
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
                        Toast.makeText(requireContext(), "Error parsing account balances.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(requireContext(), "Failed to fetch account balances.", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun depositCurrency() {
        val amountStr = binding.depositAmountTextInputEditText.text.toString()
        if (amountStr.isNotEmpty()) {
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(requireContext(), "Please enter a valid amount", Toast.LENGTH_SHORT).show()
                return
            }
            val json = JSONObject().apply {
                put("amount", amount)
            }
            binding.depositSubmitButton.isEnabled = false
            ApiClient.postRequest("/myapp/accounts/deposit", json) { success, response ->
                requireActivity().runOnUiThread {
                    binding.depositSubmitButton.isEnabled = true
                    if (success && response != null) {
                        try {
                            val jsonResponse = JSONObject(response)
                            val newBalance = jsonResponse.getDouble("new_balance")
                            binding.depositAmountTextInputEditText.text?.clear()
                            viewModel.setUsdBalance(newBalance)
                            Toast.makeText(requireContext(), "Deposit successful. New Balance: $${String.format("%.2f", newBalance)}", Toast.LENGTH_SHORT).show()
                        } catch (e: Exception) {
                            Toast.makeText(requireContext(), "Error parsing response.", Toast.LENGTH_SHORT).show()
                        }
                    } else {
                        Toast.makeText(requireContext(), "Deposit failed: ${response ?: "Unknown error"}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        } else {
            Toast.makeText(requireContext(), "Please enter an amount", Toast.LENGTH_SHORT).show()
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