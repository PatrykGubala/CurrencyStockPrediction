package com.example.currencystockprediction.models

import java.math.BigDecimal

data class TransactionItem(
    val title: String,
    val amount: BigDecimal,
    val date: String,
    val iconRes: Int
)