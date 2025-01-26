package com.example.currencystockprediction.models

import java.math.BigDecimal


enum class TransactionType(val type: String) {
    DEPOSIT("deposit"),
    WITHDRAW("withdraw"),
    BUY("buy"),
    SELL("sell"),
    SEND("send"),
    TRANSFER("transfer");

    companion object {
        fun fromString(type: String): TransactionType? {
            return values().find { it.type.equals(type, ignoreCase = true) }
        }
    }
}


sealed class HistoryItem {
    data class HeaderItem(val month: String) : HistoryItem()
    data class TransactionItem(
        val id: Int,
        val transactionType: TransactionType,
        val title: String,
        val amount: BigDecimal,
        val currencyCode: String,
        val exchangeRate: BigDecimal?,
        val transactionFee: BigDecimal,
        val senderAccountId: Int?,
        val receiverAccountId: Int?,
        val date: String,
        val iconRes: Int,
        val defaultCurrencyCost: BigDecimal
    ) : HistoryItem()
}