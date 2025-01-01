package com.example.currencystockprediction.currency

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.databinding.FragmentCurrencyBinding
import com.example.currencystockprediction.models.Currency
import com.example.currencystockprediction.utils.ApiClient
import org.json.JSONObject
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.utils.CacheManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class CurrencyFragment : BaseFragment() {

    private var _binding: FragmentCurrencyBinding? = null
    private val binding get() = _binding!!

    private val europeanCurrencies = mutableListOf<Currency>()
    private val asianCurrencies = mutableListOf<Currency>()
    private val americanCurrencies = mutableListOf<Currency>()
    private val oceanianCurrencies = mutableListOf<Currency>()

    private lateinit var europeanAdapter: CurrencyAdapter
    private lateinit var asianAdapter: CurrencyAdapter
    private lateinit var americanAdapter: CurrencyAdapter
    private lateinit var oceanianAdapter: CurrencyAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View{
        _binding = FragmentCurrencyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        setupRecyclerViews()
        fetchAllCurrencies()
    }

    private fun setupRecyclerViews() {
        europeanAdapter = CurrencyAdapter(europeanCurrencies) { currency ->
            handleCurrencyClick(currency)
        }
        binding.europeanCurrenciesRecyclerView.apply {
            layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
            adapter = europeanAdapter
        }

        asianAdapter = CurrencyAdapter(asianCurrencies) { currency ->
            handleCurrencyClick(currency)
        }
        binding.asianCurrenciesRecyclerView.apply {
            layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
            adapter = asianAdapter
        }

        americanAdapter = CurrencyAdapter(americanCurrencies) { currency ->
            handleCurrencyClick(currency)
        }
        binding.americanCurrenciesRecyclerView.apply {
            layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
            adapter = americanAdapter
        }
        oceanianAdapter = CurrencyAdapter(oceanianCurrencies) { currency ->
            handleCurrencyClick(currency)
        }
        binding.oceanianCurrenciesRecyclerView.apply {
            layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
            adapter = oceanianAdapter
        }
    }

    private fun fetchAllCurrencies() {
        lifecycleScope.launch {
            fetchCurrencies("european", europeanCurrencies, europeanAdapter)
            fetchCurrencies("american", americanCurrencies, americanAdapter)
            fetchCurrencies("asian", asianCurrencies, asianAdapter)
            fetchCurrencies("oceanian", oceanianCurrencies, oceanianAdapter)
        }
    }

    private suspend fun fetchCurrencies(region: String, list: MutableList<Currency>, adapter: CurrencyAdapter) {
        val cachedData = CacheManager.getCurrencies(requireContext(), region)
        if (cachedData != null) {
            val currencies = parseCurrenciesResponse(cachedData)
            list.clear()
            list.addAll(currencies)
            adapter.notifyDataSetChanged()
        }


        val endpoint = "/myapp/currencies/${region}/"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            CacheManager.saveCurrencies(requireContext(), region, responsePair.second!!)
            val currencies = parseCurrenciesResponse(responsePair.second!!)
            list.clear()
            list.addAll(currencies)
            adapter.notifyDataSetChanged()
        } else {
            withContext(Dispatchers.Main) {
                showError("Failed to load $region currencies")
            }
        }
    }






    private fun parseCurrenciesResponse(response: String): List<Currency> {
        val currencies = mutableListOf<Currency>()
        try {
            val jsonObject = JSONObject(response)
            val currenciesArray = jsonObject.getJSONArray("currencies")
            for (i in 0 until currenciesArray.length()) {
                val currencyObj = currenciesArray.getJSONObject(i)
                val currency = Currency(
                    id = currencyObj.getInt("id"),
                    code = currencyObj.getString("code"),
                    name = currencyObj.getString("name"),
                    symbol = currencyObj.optString("symbol"),
                    dataAvailability = currencyObj.getBoolean("dataAvailability")
                )
                currencies.add(currency)
            }
        } catch (e: Exception) {
            Log.e("CurrencyFragment", "Error parsing currencies: ${e.message}")
        }
        return currencies
    }

    private fun handleCurrencyClick(currency: Currency) {
        lifecycleScope.launch {
            val action = CurrencyFragmentDirections.actionCurrencyFragmentToCurrencyDataFragment(currencyCode = currency.code)
            findNavController().navigate(action)
        }
    }

    private fun showError(message: String) {
        lifecycleScope.launch {
            Toast.makeText(context, message, Toast.LENGTH_LONG).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
