package com.example.currencystockprediction.stock

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.databinding.FragmentStockBinding
import com.example.currencystockprediction.models.Stock
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.CacheManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

class StockFragment : BaseFragment() {

    private var _binding: FragmentStockBinding? = null
    private val binding get() = _binding!!

    private val nyseStocks = mutableListOf<Stock>()
    private val xnasStocks = mutableListOf<Stock>()

    private lateinit var nyseAdapter: StockAdapter
    private lateinit var xnasAdapter: StockAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentStockBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        setupRecyclerViews()
        fetchAllStocks()
    }

    private fun setupRecyclerViews() {
        nyseAdapter = StockAdapter(nyseStocks) { stock ->
            handleStockClick(stock)
        }
        binding.nyseExchangeRecyclerView.apply {
            layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
            adapter = nyseAdapter
        }

        xnasAdapter = StockAdapter(xnasStocks) { stock ->
            handleStockClick(stock)
        }
        binding.xnasExchangeRecyclerView.apply {
            layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
            adapter = xnasAdapter
        }
    }

    private fun fetchAllStocks() {
        lifecycleScope.launch {
            fetchStocks("XNYS", nyseStocks, nyseAdapter)
            fetchStocks("XNAS", xnasStocks, xnasAdapter)
            fetchAllMonthlyPercentageChanges()
        }
    }

    private suspend fun fetchStocks(exchangeName: String, list: MutableList<Stock>, adapter: StockAdapter) {
        val exchangeId = getExchangeIdByName(exchangeName)
        if (exchangeId == null) {
            withContext(Dispatchers.Main) { showError("Exchange $exchangeName not found") }
            return
        }

        val cachedData = CacheManager.getStocks(requireContext(), exchangeName)
        if (cachedData != null) {
            val stocks = parseStocksResponse(cachedData, exchangeId)
            list.clear()
            list.addAll(stocks)
            adapter.notifyDataSetChanged()
        }

        val endpoint = "/myapp/stocks/"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            CacheManager.saveStocks(requireContext(), exchangeName, responsePair.second!!)
            val stocks = parseStocksResponse(responsePair.second!!, exchangeId)
            list.clear()
            list.addAll(stocks)
            adapter.notifyDataSetChanged()
        } else {
            withContext(Dispatchers.Main) {
                showError("Failed to load stocks for $exchangeName")
            }
        }
    }

    private fun parseStocksResponse(response: String, targetExchangeId: Int): List<Stock> {
        val stocks = mutableListOf<Stock>()
        try {
            val jsonObject = JSONObject(response)
            val stocksArray = jsonObject.getJSONArray("stocks")
            for (i in 0 until stocksArray.length()) {
                val stockObj = stocksArray.getJSONObject(i)
                val exchangeId = stockObj.optInt("exchange_id", -1)

                if (exchangeId != targetExchangeId) continue

                val s = Stock(
                    id = stockObj.getInt("id"),
                    stock_symbol = stockObj.getString("symbol"),
                    stock_name = stockObj.optString("name"),
                    company_id = stockObj.getInt("company_id"),
                    exchange_id = exchangeId,
                    share_class = stockObj.optString("share_class"),
                    dataAvailability = stockObj.optBoolean("data_availability", true),
                    monthlyPercentageChange = null
                )
                stocks.add(s)
            }
        } catch (e: Exception) {
            Log.e("StockFragment", "Error parsing stocks: ${e.message}")
        }
        return stocks
    }

    private suspend fun fetchAllMonthlyPercentageChanges() {
        val allStocks = nyseStocks + xnasStocks
        coroutineScope {
            val deferreds = allStocks
                .filter { it.dataAvailability }
                .map { stock ->
                    async {
                        val position = when (stock) {
                            in nyseStocks -> nyseStocks.indexOf(stock)
                            in xnasStocks -> xnasStocks.indexOf(stock)
                            else -> -1
                        }
                        fetchMonthlyPercentageChange(stock)
                        notifyItemChanged(stock, position)
                    }
                }
            deferreds.awaitAll()
        }
    }

    private suspend fun notifyItemChanged(stock: Stock, position: Int) {
        withContext(Dispatchers.Main) {
            when (stock) {
                in nyseStocks -> nyseAdapter.notifyItemChanged(position)
                in xnasStocks -> xnasAdapter.notifyItemChanged(position)
            }
        }
    }

    private suspend fun fetchMonthlyPercentageChange(stock: Stock) {
        val endpoint = "/myapp/stocks/data/${stock.stock_symbol}/monthly_change"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            try {
                val jsonObject = JSONObject(responsePair.second!!)
                val monthlyChange = jsonObject.optDouble("monthly_change", 0.0)
                stock.monthlyPercentageChange = String.format("%.2f", monthlyChange)
            } catch (e: Exception) {
                Log.e("StockFragment", "Error parsing monthly change for ${stock.stock_symbol}: ${e.message}")
                stock.monthlyPercentageChange = null
                stock.dataAvailability = false
            }
        } else {
            Log.e("StockFragment", "Failed to fetch monthly change for ${stock.stock_symbol}")
            stock.monthlyPercentageChange = null
            stock.dataAvailability = false
        }
    }

    private suspend fun getExchangeIdByName(exchangeName: String): Int? {
        val responsePair = ApiClient.getRequest("/myapp/exchanges/")
        if (responsePair.first && responsePair.second != null) {
            try {
                val jsonObject = JSONObject(responsePair.second)
                val exchangesArray = jsonObject.getJSONArray("exchanges")
                for (i in 0 until exchangesArray.length()) {
                    val exch = exchangesArray.getJSONObject(i)
                    if (exch.getString("name").equals(exchangeName, ignoreCase = true)) {
                        return exch.getInt("id")
                    }
                }
            } catch (e: Exception) {
                Log.e("StockFragment", "Error parsing exchanges: ${e.message}")
            }
        }
        return null
    }


    private fun handleStockClick(stock: Stock) {
        lifecycleScope.launch {
            val action = StockFragmentDirections
                .actionStockFragmentToStockDataFragment(stockSymbol = stock.stock_symbol)
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
