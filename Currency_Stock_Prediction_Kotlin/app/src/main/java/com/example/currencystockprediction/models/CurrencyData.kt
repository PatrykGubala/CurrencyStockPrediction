package com.example.currencystockprediction.models

import java.math.BigDecimal

data class CurrencyData(
    val timestamp: Long,
    val open: BigDecimal,
    val high: BigDecimal,
    val low: BigDecimal,
    val close: BigDecimal,
    val volume: BigDecimal
)