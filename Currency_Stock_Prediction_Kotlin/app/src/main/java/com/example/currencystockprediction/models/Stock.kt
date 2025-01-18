package com.example.currencystockprediction.models

data class Stock(
    val id: Int,
    val stock_symbol: String,
    val stock_name: String,
    val company_id: Int,
    var exchange_id: Int,
    var share_class: String? = null,
    var dataAvailability: Boolean,
    var monthlyPercentageChange: String? = null
)

