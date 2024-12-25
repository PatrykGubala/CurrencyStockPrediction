package com.example.currencystockprediction.home

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.example.currencystockprediction.currency.CurrencySpinnerAdapter
import com.example.currencystockprediction.databinding.FragmentHomeBinding
import com.example.currencystockprediction.utils.ApiClient
import org.json.JSONObject

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: HomeViewModel
    private lateinit var currencyAdapter: CurrencySpinnerAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel = ViewModelProvider(this).get(HomeViewModel::class.java)

        viewModel.usdBalance.observe(viewLifecycleOwner) { balance ->
            binding.accountAmountTextView.text = "Account Amount: $${String.format("%.2f", balance)}"
        }

        initializeCurrencySpinners()
        fetchAccountBalances()
        fetchAvailableCurrencies()
        setupButtonInteractions()
    }

    private fun initializeCurrencySpinners() {
        val mutableCurrencies = mutableListOf<String>()
        currencyAdapter = CurrencySpinnerAdapter(requireContext(), mutableCurrencies)
        binding.fromCurrencySpinner.adapter = currencyAdapter
        binding.toCurrencySpinner.adapter = currencyAdapter
    }


    private fun setupButtonInteractions() {
        binding.depositLayout.visibility = View.GONE
        binding.sendLayout.visibility = View.GONE
        binding.calculateLayout.visibility = View.GONE

        binding.emailImageButton.setOnClickListener {
            showLayout("deposit")
        }

        binding.sellImageButton.setOnClickListener {
            showLayout("send")
        }

        binding.sendImageButton.setOnClickListener {
            showLayout("send")
        }

        binding.calculateImageButton.setOnClickListener {
            showLayout("calculate")
        }

        binding.depositSubmitButton.setOnClickListener {
            val amountStr = binding.depositAmountTextInputEditText.text.toString()
            if (amountStr.isNotEmpty()) {
                val amount = amountStr.toDoubleOrNull()
                if (amount == null || amount <= 0) {
                    Toast.makeText(requireContext(), "Please enter a valid amount", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
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
                                binding.depositLayout.visibility = View.GONE
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

        binding.sendSubmitButton.setOnClickListener {
            val amountStr = binding.sendAmountTextInputEditText.text.toString()
            val publicAccountId = binding.sendPublicAccountTextInputEditText.text.toString()
            if (amountStr.isNotEmpty() && publicAccountId.isNotEmpty()) {
                val amount = amountStr.toDoubleOrNull()
                if (amount == null || amount <= 0) {
                    Toast.makeText(
                        requireContext(),
                        "Please enter a valid amount",
                        Toast.LENGTH_SHORT
                    ).show()
                    return@setOnClickListener
                }
               //TODO
            } else {
                Toast.makeText(
                    requireContext(),
                    "Please enter amount and Public Account ID",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

        binding.calculateSubmitButton.setOnClickListener {
            val amountStr = binding.calculateAmountEditText.text.toString()
            val fromCurrency = binding.fromCurrencySpinner.selectedItem as? String
            val toCurrency = binding.toCurrencySpinner.selectedItem as? String

            if (amountStr.isNotEmpty() && fromCurrency != null && toCurrency != null) {
                val amount = amountStr.toDoubleOrNull()
                if (amount == null || amount <= 0) {
                    Toast.makeText(requireContext(), "Please enter a valid amount", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }

                val json = JSONObject().apply {
                    put("amount", amount)
                    put("from_currency", fromCurrency)
                    put("to_currency", toCurrency)
                }

                binding.calculateSubmitButton.isEnabled = false

                ApiClient.postRequest("/myapp/currencies/convert", json) { success, response ->
                    requireActivity().runOnUiThread {
                        binding.calculateSubmitButton.isEnabled = true

                        if (success && response != null) {
                            try {
                                val jsonResponse = JSONObject(response)
                                val convertedAmount = jsonResponse.getDouble("converted_amount")
                                val conversionRate = jsonResponse.getDouble("conversion_rate")
                                Toast.makeText(
                                    requireContext(),
                                    "Converted Amount: $convertedAmount $toCurrency\nRate: $conversionRate",
                                    Toast.LENGTH_LONG
                                ).show()
                                binding.calculateAmountEditText.text?.clear()
                                binding.resultAmountEditText.setText("Converted Amount: $convertedAmount $toCurrency\nRate: $conversionRate")
                            } catch (e: Exception) {
                                Toast.makeText(requireContext(), "Error parsing response.", Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            Toast.makeText(requireContext(), "Conversion failed: ${response ?: "Unknown error"}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } else {
                Toast.makeText(requireContext(), "Please enter amount and select currencies", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showLayout(layoutType: String) {
        when (layoutType) {
            "deposit" -> {
                binding.depositLayout.visibility = View.VISIBLE
                binding.sendLayout.visibility = View.GONE
                binding.calculateLayout.visibility = View.GONE
            }
            "send" -> {
                binding.depositLayout.visibility = View.GONE
                binding.sendLayout.visibility = View.VISIBLE
                binding.calculateLayout.visibility = View.GONE
            }
            "calculate" -> {
                binding.depositLayout.visibility = View.GONE
                binding.sendLayout.visibility = View.GONE
                binding.calculateLayout.visibility = View.VISIBLE
            }
            else -> {
                binding.depositLayout.visibility = View.GONE
                binding.sendLayout.visibility = View.GONE
                binding.calculateLayout.visibility = View.GONE
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
                        Toast.makeText(requireContext(), "Error parsing account balances.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(requireContext(), "Failed to fetch account balances.", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun fetchAvailableCurrencies() {
        ApiClient.getRequest("/myapp/currencies") { success, response ->
            requireActivity().runOnUiThread {
                if (success && response != null) {
                    try {
                        val jsonResponse = JSONObject(response)
                        val currenciesArray = jsonResponse.getJSONArray("currencies")
                        val currenciesList = mutableListOf<String>()
                        for (i in 0 until currenciesArray.length()) {
                            val currencyObj = currenciesArray.getJSONObject(i)
                            val code = currencyObj.getString("code")
                            currenciesList.add(code)
                        }
                        Log.d("HomeFragment", "Fetched currencies: $currenciesList")
                        currencyAdapter.clear()
                        currencyAdapter.addAll(currenciesList)
                        currencyAdapter.notifyDataSetChanged()
                    } catch (e: Exception) {
                        Log.e("HomeFragment", "Error parsing currencies: ${e.message}")
                        Toast.makeText(requireContext(), "Error parsing currencies.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Log.e("HomeFragment", "Failed to fetch currencies. Response: $response")
                    Toast.makeText(requireContext(), "Failed to fetch currencies.", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
