package com.example.currencystockprediction.models

import java.math.BigDecimal

sealed class HistoryItem {
    data class HeaderItem(val month: String) : HistoryItem()
    data class TransactionItem(
        val id: Int,
        val transactionType: String,
        val title: String,
        val amount: BigDecimal,
        val currencyCode: String,
        val exchangeCurrencyCode: String?,
        val exchangeRate: BigDecimal?,
        val transactionFee: BigDecimal,
        val senderAccountId: Int?,
        val receiverAccountId: Int?,
        val date: String,
        val iconRes: Int,
        val defaultCurrencyCost: BigDecimal
    ) : HistoryItem()
}