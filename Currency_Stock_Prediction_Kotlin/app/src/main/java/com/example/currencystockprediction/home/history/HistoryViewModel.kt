package com.example.currencystockprediction.home.history

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.currencystockprediction.R
import com.example.currencystockprediction.models.HistoryItem
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.FirebaseAuthManager
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.math.BigDecimal
import java.text.SimpleDateFormat
import java.util.Locale

class HistoryViewModel : ViewModel() {

    private val _transactions = MutableLiveData<List<HistoryItem>>()
    val transactions: LiveData<List<HistoryItem>> = _transactions

    private val _isRefreshing = MutableLiveData<Boolean>()
    val isRefreshing: LiveData<Boolean> = _isRefreshing

    private var allTransactions: List<HistoryItem.TransactionItem> = listOf()
    private var currentSearchQuery: String = ""
    private var currentFilters: List<String> = listOf()
    private var fromAmount: BigDecimal? = null
    private var toAmount: BigDecimal? = null
    private var fromDate: Long? = null
    private var toDate: Long? = null
    private var transactionKind: String = "ALL"

    var userAccountId: Int? = null


    init {
        fetchUserAccountId()
    }

    fun fetchUserAccountId() {
       viewModelScope.launch {
            val endpoint = "/myapp/accounts/get_account_id"
            val (success, response) = ApiClient.getRequest(endpoint)
            if (success && response != null) {
                try {
                    val jsonResponse = JSONObject(response)
                    userAccountId = jsonResponse.getInt("account_id")
                    Log.d("HistoryViewModel", "User Account ID: $userAccountId")
                    fetchTransactions()
                } catch (e: Exception) {
                    Log.e("HistoryViewModel", "Error parsing account ID: ${e.message}")
                    _transactions.value = listOf()
                }
            } else {
                Log.e("HistoryViewModel", "Failed to fetch account ID")
            }
        }
    }

    fun fetchTransactions() {
        _isRefreshing.value = true
        viewModelScope.launch {
            val endpoint = "/myapp/accounts/transactions?page=1&page_size=100"
            val responsePair = ApiClient.getRequest(endpoint + buildFilterQuery())
            if (responsePair.first && responsePair.second != null) {
                val transactionsList = mutableListOf<HistoryItem.TransactionItem>()
                try {
                    val jsonResponse = JSONObject(responsePair.second!!)
                    val transactionsArray = jsonResponse.getJSONArray("transactions")
                    for (i in 0 until transactionsArray.length()) {
                        val obj = transactionsArray.getJSONObject(i)

                        val exchangeRateString = obj.optString("exchange_rate", "")
                        val exchangeRate = if (exchangeRateString.isNotEmpty() && exchangeRateString != "null") {
                            exchangeRateString.toBigDecimal()
                        } else {
                            null
                        }
                        val amountValue = obj.getString("amount").toBigDecimal()

                        val defaultCostString = obj.optString("default_currency_cost", "")
                        val defaultCost = if (defaultCostString.isNotEmpty() && defaultCostString != "null") {
                            defaultCostString.toBigDecimal()
                        } else {
                            amountValue
                        }
                        val transactionItem = HistoryItem.TransactionItem(
                            id = obj.getInt("id"),
                            transactionType = obj.getString("transaction_type"),
                            title = obj.getString("title"),
                            amount = amountValue,
                            currencyCode = obj.getString("currency"),
                            exchangeCurrencyCode = if (obj.isNull("exchange_currency")) null else obj.getString("exchange_currency"),
                            exchangeRate = exchangeRate,
                            transactionFee = obj.getString("transaction_fee").toBigDecimal(),
                            senderAccountId = if (obj.isNull("sender_account_id")) null else obj.getInt("sender_account_id"),
                            receiverAccountId = if (obj.isNull("receiver_account_id")) null else obj.getInt("receiver_account_id"),
                            date = obj.getString("date"),
                            iconRes = getIconResource(obj.getString("transaction_type")),
                            defaultCurrencyCost = defaultCost

                        )
                        transactionsList.add(transactionItem)
                    }
                    allTransactions = transactionsList
                    Log.d("HistoryViewModel", "Fetched ${allTransactions.size} transactions")
                    applyFilters()
                } catch (e: Exception) {
                    Log.e("HistoryViewModel", "Error parsing transactions: ${e.message}")
                    _transactions.value = listOf()
                }
            } else {
                Log.e("HistoryViewModel", "Failed to fetch transactions or response is null")
            }
            _isRefreshing.value = false
        }
    }

    private fun buildFilterQuery(): String {
        val queryParams = mutableListOf<String>()
        if (currentFilters.isNotEmpty()) {
            val types = currentFilters.joinToString(",")
            queryParams.add("transaction_type=$types")
        }
        if (currentSearchQuery.isNotEmpty()) {
            queryParams.add("search=$currentSearchQuery")
        }
        if (fromAmount != null) {
            queryParams.add("amount_from=$fromAmount")
        }
        if (toAmount != null) {
            queryParams.add("amount_to=$toAmount")
        }
        if (fromDate != null) {
            val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val dateStr = sdf.format(fromDate!!)
            queryParams.add("date_from=$dateStr")
        }
        if (toDate != null) {
            val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val dateStr = sdf.format(toDate!!)
            queryParams.add("date_to=$dateStr")
        }
        return if (queryParams.isNotEmpty()) "?" + queryParams.joinToString("&") else ""

    }

    private fun getIconResource(transactionType: String): Int {
        return when (transactionType) {
            "deposit" -> R.drawable.plus
            "withdraw" -> R.drawable.minus
            "transfer" -> R.drawable.arrow_up
            "exchange" -> R.drawable.arrow_left
            "send" -> R.drawable.mail
            else -> R.drawable.ic_launcher_background
        }
    }

    fun setSearchQuery(query: String) {
        currentSearchQuery = query
        applyFilters()
    }

    fun setFilters(filters: List<String>) {
        currentFilters = filters
        applyFilters()
    }

    fun setAmountRange(from: BigDecimal?, to: BigDecimal?) {
        fromAmount = from
        toAmount = to
        applyFilters()
    }

    fun setDateRange(from: Long?, to: Long?) {
        fromDate = from
        toDate = to
        applyFilters()
    }

    fun setTransactionKind(kind: String) {
        transactionKind = kind
        applyFilters()
    }

    private fun applyFilters() {
        var filtered = allTransactions
        if (currentSearchQuery.isNotEmpty()) {
            filtered = filtered.filter {
                it.title.contains(currentSearchQuery, ignoreCase = true) ||
                        it.transactionType.contains(currentSearchQuery, ignoreCase = true)
            }
        }
        if (currentFilters.isNotEmpty()) {
            filtered = filtered.filter { it.transactionType in currentFilters }
        }
        if (transactionKind == "INCOME") {
            filtered = filtered.filter { isIncome(it) }
        } else if (transactionKind == "OUTCOME") {
            filtered = filtered.filter { isOutcome(it) }
        }
        if (fromAmount != null) {
            filtered = filtered.filter { it.defaultCurrencyCost >= fromAmount!! }
        }
        if (toAmount != null) {
            filtered = filtered.filter { it.amount <= toAmount!! }
        }
        if (fromDate != null) {
            filtered = filtered.filter {
                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                val transactionTime = try {
                    sdf.parse(it.date)?.time
                } catch (e: Exception) {
                    Log.e("HistoryViewModel", "Error parsing transaction date: ${e.message}")
                    null
                }
                transactionTime != null && transactionTime >= fromDate!!
            }
        }
        if (toDate != null) {
            filtered = filtered.filter {
                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                val transactionTime = try {
                    sdf.parse(it.date)?.time
                } catch (e: Exception) {
                    Log.e("HistoryViewModel", "Error parsing transaction date: ${e.message}")
                    null
                }
                transactionTime != null && transactionTime <= toDate!!
            }
        }
        val groupedList = groupTransactionsByDay(filtered)
        Log.d("HistoryViewModel", "Filtered transactions count: ${filtered.size}, Grouped list count: ${groupedList.size}")
        _transactions.value = groupedList
    }

    private fun isIncome(item: HistoryItem.TransactionItem): Boolean {
        return when (item.transactionType) {
            "deposit" -> true
            "withdraw" -> false
            "exchange" -> item.currencyCode == "USD"

            "send", "transfer"-> {
                item.receiverAccountId == userAccountId
            }
            else -> false
        }
    }

    private fun isOutcome(item: HistoryItem.TransactionItem): Boolean {
        return when (item.transactionType) {
            "withdraw" -> true
            "deposit" -> false
            "exchange" -> item.exchangeCurrencyCode == "USD"
            "send", "transfer"-> {
                item.senderAccountId == userAccountId
            }
            else -> false
        }
    }

    private fun groupTransactionsByDay(transactions: List<HistoryItem.TransactionItem>): List<HistoryItem> {
        val sdfInput = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
        val sdfOutput = SimpleDateFormat("dd MMM yyyy", Locale.getDefault())

        val grouped = transactions.groupBy {
            val dateParsed = try {
                sdfInput.parse(it.date)
            } catch (e: Exception) {
                null
            }
            if (dateParsed != null) sdfOutput.format(dateParsed) else ""
        }

        val result = mutableListOf<HistoryItem>()

        val sortedKeys = grouped.keys.sortedByDescending { key ->
            try {
                sdfOutput.parse(key)?.time
            } catch (e: Exception) {
                0L
            }
        }

        for (key in sortedKeys) {
            if (key.isNotEmpty()) {
                result.add(HistoryItem.HeaderItem(key))
            }
            result.addAll(grouped[key] ?: emptyList())
        }
        return result
    }
}
