package com.example.currencystockprediction.utils

import com.example.currencystockprediction.R

object StockIconsUtils {
    fun getStockIconResource(stockCode: String): Int {
        return when (stockCode) {
            "AAPL" -> R.drawable.ic_comp_aapl
            "META" -> R.drawable.ic_comp_meta
            "JNJ" -> R.drawable.ic_comp_jnj
            "V" -> R.drawable.ic_comp_v
            "MSFT" -> R.drawable.ic_comp_msft
            else -> R.drawable.ic_launcher_background
        }
    }
}