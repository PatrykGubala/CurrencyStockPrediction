package com.example.currencystockprediction.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class HomeViewModel : ViewModel() {
    private val _usdBalance = MutableLiveData<Double>()
    val usdBalance: LiveData<Double> get() = _usdBalance

    fun setUsdBalance(balance: Double) {
        _usdBalance.value = balance
    }
}