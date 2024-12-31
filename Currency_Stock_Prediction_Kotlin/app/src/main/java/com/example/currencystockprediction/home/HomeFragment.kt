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
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.currency.CurrencySpinnerAdapter
import com.example.currencystockprediction.databinding.FragmentHomeBinding
import com.example.currencystockprediction.profile.ProfileFragmentDirections
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

        binding.depositImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeDepositFragment())
        }

        binding.sendImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeSendFragment())
        }

        binding.calculateImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeConvertFragment())
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



    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }


}
