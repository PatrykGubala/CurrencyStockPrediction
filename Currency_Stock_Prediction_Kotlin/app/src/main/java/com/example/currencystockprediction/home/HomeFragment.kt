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
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.currencystockprediction.R
import com.example.currencystockprediction.currency.CurrencySpinnerAdapter
import com.example.currencystockprediction.databinding.FragmentHomeBinding
import com.example.currencystockprediction.models.Currency
import com.example.currencystockprediction.models.HistoryItem
import com.example.currencystockprediction.profile.ProfileFragmentDirections
import com.example.currencystockprediction.utils.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.math.BigDecimal
import java.text.SimpleDateFormat
import java.util.Locale

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: HomeViewModel
    private lateinit var currencyAdapter: CurrencySpinnerAdapter

    private lateinit var transactionsAdapter: HomeTransactionsAdapter
    private val recentTransactions = mutableListOf<HistoryItem.TransactionItem>()

    private lateinit var homeCurrenciesAdapter: HomeCurrencyAdapter
    private val homeCurrencies = mutableListOf<Currency>()


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
            binding.accountAmountTextView.text = "Stan konta: $${String.format("%.2f", balance)}"
        }
        setupRecentTransactionsRecycler()
        setupUserCurrenciesRecyclerView()

        setupButtonInteractions()
        lifecycleScope.launch {
            fetchAccountBalances()
            fetchRecentTransactions()
            fetchAvailableCurrencies()

        }
    }

    private fun setupUserCurrenciesRecyclerView() {
        homeCurrenciesAdapter = HomeCurrencyAdapter(homeCurrencies) { currency ->
        }
        binding.europeanCurrenciesRecyclerView.layoutManager =
            LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
        binding.europeanCurrenciesRecyclerView.adapter = homeCurrenciesAdapter
    }

    private fun setupRecentTransactionsRecycler() {
        transactionsAdapter = HomeTransactionsAdapter(userAccountId = 0)
        binding.recentTransactionsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        binding.recentTransactionsRecyclerView.adapter = transactionsAdapter
    }

    private suspend fun fetchAvailableCurrencies() {
        val endpoint = "/myapp/accounts/currencies"
        val responsePair = ApiClient.getRequest(endpoint)
        if (responsePair.first && responsePair.second != null) {
            val currencies = parseAccountCurrenciesResponse(responsePair.second!!)
            val filteredCurrencies = currencies.filter { !it.code.equals("USD", ignoreCase = true) }
            homeCurrencies.clear()
            homeCurrencies.addAll(filteredCurrencies)
            withContext(Dispatchers.Main) {
                binding.currenciesConstraintLayout.visibility =
                    if (homeCurrencies.isNotEmpty()) View.VISIBLE else View.GONE
                homeCurrenciesAdapter.updateData(homeCurrencies)
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Failed to load available currencies.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun parseAccountCurrenciesResponse(response: String): List<Currency> {
        val currencies = mutableListOf<Currency>()
        try {
            val jsonObject = JSONObject(response)
            val currenciesArray = jsonObject.getJSONArray("currencies")
            for (i in 0 until currenciesArray.length()) {
                val currencyObj = currenciesArray.getJSONObject(i)
                val code = currencyObj.getString("currency_code")
                // Tworzymy obiekt Currency z minimalnymi danymi
                currencies.add(
                    Currency(
                        id = 0,
                        code = code,
                        name = code,
                        symbol = "",
                        dataAvailability = true
                    )
                )
            }
        } catch (e: Exception) {
            Log.e("HomeFragment", "Error parsing account currencies: ${e.message}")
        }
        return currencies
    }


    private suspend fun fetchRecentTransactions() {
        val page = 1
        val pageSize = 3
        val endpoint = "/myapp/accounts/transactions?page=$page&page_size=$pageSize"
        val responsePair = ApiClient.getRequest(endpoint)
        if (responsePair.first && responsePair.second != null) {
            try {
                val jsonResponse = JSONObject(responsePair.second!!)
                val transactionsArray = jsonResponse.getJSONArray("transactions")
                recentTransactions.clear()
                for (i in 0 until transactionsArray.length()) {
                    val obj = transactionsArray.getJSONObject(i)
                    val type = obj.getString("transaction_type")
                    val amountValue = obj.getString("amount").toBigDecimalOrNull() ?: BigDecimal.ZERO
                    val costString = obj.optString("default_currency_cost", "")
                    val defaultCost = if (costString.isNotEmpty() && costString != "null") {
                        costString.toBigDecimal()
                    } else {
                        amountValue
                    }
                    val dateStr = obj.getString("date")
                    val exchangeRateStr = obj.optString("exchange_rate", "")
                    val feeStr = obj.optString("transaction_fee", "0")
                    val exchangeRate = if (exchangeRateStr.isNotEmpty() && exchangeRateStr != "null") {
                        exchangeRateStr.toBigDecimal()
                    } else {
                        null
                    }
                    val senderId = if (obj.isNull("sender_account_id")) null else obj.getInt("sender_account_id")
                    val receiverId = if (obj.isNull("receiver_account_id")) null else obj.getInt("receiver_account_id")
                    val iconRes = when (type) {
                        "deposit" -> R.drawable.plus
                        "withdraw" -> R.drawable.minus
                        "sell" -> R.drawable.arrow_up
                        "buy" -> R.drawable.arrow_left
                        "send" -> R.drawable.mail
                        else -> R.drawable.ic_launcher_background
                    }
                    recentTransactions.add(
                        HistoryItem.TransactionItem(
                            id = obj.getInt("id"),
                            transactionType = type,
                            title = obj.getString("title"),
                            amount = amountValue,
                            currencyCode = obj.getString("currency"),
                            exchangeRate = exchangeRate,
                            transactionFee = feeStr.toBigDecimal(),
                            senderAccountId = senderId,
                            receiverAccountId = receiverId,
                            date = dateStr,
                            iconRes = iconRes,
                            defaultCurrencyCost = defaultCost
                        )
                    )
                }
                transactionsAdapter.submitList(recentTransactions)
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(requireContext(), "Error parsing transactions.", Toast.LENGTH_SHORT).show()
                }
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Failed to fetch transactions.", Toast.LENGTH_SHORT).show()
            }
        }
    }



    private fun setupButtonInteractions() {
        binding.depositImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeDepositFragment())
        }
        binding.contactsImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeContactsFragment())
        }

        binding.sendImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeSendFragment())
        }

        binding.calculateImageButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHomeConvertFragment())
        }
        binding.viewAllTransactionsButton.setOnClickListener {
            findNavController().navigate(HomeFragmentDirections.actionHomeFragmentToHistoryFragment())
        }
    }




    private suspend fun fetchAccountBalances() {
        val endpoint = "/myapp/accounts/currencies"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            try {
                val jsonResponse = JSONObject(responsePair.second!!)
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
                withContext(Dispatchers.Main) {
                    Toast.makeText(requireContext(), "Error parsing account balances.", Toast.LENGTH_SHORT).show()
                }
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Failed to fetch account balances.", Toast.LENGTH_SHORT).show()
            }
        }
    }



    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }


}
