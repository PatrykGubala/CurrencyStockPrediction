package com.example.currencystockprediction.home.deposit

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.currencystockprediction.utils.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

class HomeDepositViewModel : ViewModel() {

    private val _usdBalance = MutableLiveData<Double>()
    val usdBalance: LiveData<Double> get() = _usdBalance

    private val _depositResult = MutableLiveData<Result<Double>>()
    val depositResult: LiveData<Result<Double>> get() = _depositResult

    init {
        fetchAccountBalances()
    }

    fun fetchAccountBalances() {
        viewModelScope.launch {
            val endpoint = "/myapp/accounts/currencies"
            val responsePair = ApiClient.getRequest(endpoint)

            if (responsePair.first && responsePair.second != null) {
                try {
                    val jsonResponse = JSONObject(responsePair.second!!)
                    val currenciesArray = jsonResponse.getJSONArray("currencies")
                    var usdBalanceValue = 0.0
                    for (i in 0 until currenciesArray.length()) {
                        val currencyObj = currenciesArray.getJSONObject(i)
                        val code = currencyObj.getString("currency_code")
                        val balance = currencyObj.getDouble("balance")
                        if (code.equals("USD", ignoreCase = true)) {
                            usdBalanceValue = balance
                            break
                        }
                    }
                    _usdBalance.postValue(usdBalanceValue)
                } catch (e: Exception) {
                    _depositResult.postValue(Result.failure(Exception("Error parsing account balances.")))
                }
            } else {
                _depositResult.postValue(Result.failure(Exception("Failed to fetch account balances.")))
            }
        }
    }

    fun depositCurrency(amount: Double) {
        viewModelScope.launch {
            val json = JSONObject().apply {
                put("amount", amount)
            }

            val responsePair = ApiClient.postRequest("/myapp/accounts/deposit", json)

            if (responsePair.first && responsePair.second != null) {
                try {
                    val jsonResponse = JSONObject(responsePair.second!!)
                    val newBalance = jsonResponse.getDouble("new_balance")
                    _usdBalance.postValue(newBalance)
                    _depositResult.postValue(Result.success(newBalance))
                } catch (e: Exception) {
                    _depositResult.postValue(Result.failure(Exception("Error processing deposit response.")))
                }
            } else {
                _depositResult.postValue(
                    Result.failure(
                        Exception(
                            "Failed to deposit funds: ${responsePair.second ?: "Unknown error."}"
                        )
                    )
                )
            }
        }
    }
}
