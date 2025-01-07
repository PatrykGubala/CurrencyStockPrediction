package com.example.currencystockprediction.home.convert

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.currency.CurrencySpinnerAdapter
import com.example.currencystockprediction.databinding.FragmentHomeConvertBinding
import com.example.currencystockprediction.databinding.FragmentHomeDepositBinding
import com.example.currencystockprediction.home.HomeViewModel
import com.example.currencystockprediction.utils.ApiClient
import com.google.android.material.bottomnavigation.BottomNavigationView
import kotlinx.coroutines.launch
import org.json.JSONObject


class HomeConvertFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE

    private var _binding: FragmentHomeConvertBinding? = null
    private val binding get() = _binding!!

    private lateinit var currencyAdapter: CurrencySpinnerAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeConvertBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val window = requireActivity().window
        insetsController = WindowInsetsControllerCompat(window, window.decorView)
        hideSystemUI()

        bottomNavView = requireActivity().findViewById(R.id.bottomNavView)
        if (bottomNavView != null) {
            originalBottomNavVisibility = bottomNavView.visibility
            bottomNavView.visibility = View.GONE
        }

        setupToolbar()

        initializeCurrencySpinners()
        lifecycleScope.launch {
            fetchAvailableCurrencies()
        }
        binding.calculateButton.setOnClickListener {
            convertCurrency()
        }
        binding.calculateSubmitButton.setOnClickListener {
            convertCurrency()
        }
    }

    private fun initializeCurrencySpinners() {
        val mutableCurrencies = mutableListOf<String>()
        currencyAdapter = CurrencySpinnerAdapter(requireContext(), mutableCurrencies)
        binding.fromCurrencySpinner.adapter = currencyAdapter
        binding.toCurrencySpinner.adapter = currencyAdapter
    }

    private suspend fun fetchAvailableCurrencies() {
        val endpoint = "/myapp/currencies"
        val (success, response) = ApiClient.getRequest(endpoint)
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
                currencyAdapter.clear()
                currencyAdapter.addAll(currenciesList)
                currencyAdapter.notifyDataSetChanged()
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "Error parsing currencies.", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(requireContext(), "Failed to fetch currencies.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun convertCurrency() {
        val amountStr = binding.calculateAmountTextInputEditText.text.toString()
        val fromCurrency = binding.fromCurrencySpinner.selectedItem as? String
        val toCurrency = binding.toCurrencySpinner.selectedItem as? String

        if (amountStr.isNotEmpty() && fromCurrency != null && toCurrency != null) {
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(requireContext(), "Please enter a valid amount", Toast.LENGTH_SHORT).show()
                return
            }

            lifecycleScope.launch {
                val json = JSONObject().apply {
                    put("amount", amount)
                    put("from_currency", fromCurrency)
                    put("to_currency", toCurrency)
                }

                binding.calculateSubmitButton.isEnabled = false
                val (success, response) = ApiClient.postRequest("/myapp/currencies/convert", json)
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
                        binding.calculateAmountTextInputEditText.text?.clear()
                        binding.resultAmountTextInputEditText.setText("$convertedAmount $toCurrency")
                        binding.resultExchangeRateTextInputEditText.setText("$conversionRate")
                    } catch (e: Exception) {
                        Toast.makeText(requireContext(), "Error parsing response.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(requireContext(), "Conversion failed: ${response ?: "Unknown error"}", Toast.LENGTH_SHORT).show()
                }
            }
        } else {
            Toast.makeText(requireContext(), "Please enter amount and select currencies", Toast.LENGTH_SHORT).show()
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
        bottomNavView?.let {
            if (it.visibility != View.GONE) {
                it.visibility = View.GONE
            }
        }
    }

    override fun onPause() {
        super.onPause()
        showSystemUI()
        bottomNavView?.visibility = originalBottomNavVisibility
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