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
import com.example.currencystockprediction.models.TransactionItem
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
    private val recentTransactions = mutableListOf<TransactionItem>()

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

        setupButtonInteractions()
        lifecycleScope.launch {
            fetchAccountBalances()
            fetchRecentTransactions()
        }
        setupRecentTransactions()
    }

    private fun setupRecentTransactions() {
        recentTransactions.clear()

        transactionsAdapter = HomeTransactionsAdapter(recentTransactions)
        binding.recentTransactionsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        binding.recentTransactionsRecyclerView.adapter = transactionsAdapter
    }



    private suspend fun fetchRecentTransactions() {
        val page = 1
        val pageSize = 3
        val endpoint = "/myapp/accounts/transactions?page=$page&page_size=$pageSize"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            try {
                Log.d("HomeFragment", "Transactions Response: ${responsePair.second!!}")

                val jsonResponse = JSONObject(responsePair.second!!)
                val transactionsArray = jsonResponse.getJSONArray("transactions")

                recentTransactions.clear()



                for (i in 0 until transactionsArray.length()) {
                    val obj = transactionsArray.getJSONObject(i)
                    val type = obj.getString("transaction_type")
                    val title = obj.getString("title")
                    val amountStr = obj.getString("amount")
                    val amount = amountStr.toBigDecimalOrNull() ?: BigDecimal.ZERO
                    val date = obj.getString("date")
                    val iconRes = when (type) {
                        "deposit" -> R.drawable.delete
                        "withdraw" -> R.drawable.send
                        "transfer" -> R.drawable.finger_print
                        "exchange" -> R.drawable.edit_3
                        "send" -> R.drawable.send
                        else -> R.drawable.ic_launcher_background
                    }
                    val formattedDate = formatDate(date)
                    recentTransactions.add(
                        TransactionItem(
                            title = title,
                            amount = amount,
                            date = formattedDate,
                            iconRes = iconRes
                        )
                    )
                }
                transactionsAdapter.notifyDataSetChanged()
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


    private fun formatDate(dateStr: String): String {
        val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
        val formatter = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault())
        return try {
            val date = parser.parse(dateStr)
            formatter.format(date!!)
        } catch (e: Exception) {
            dateStr
        }
    }


    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }


}
