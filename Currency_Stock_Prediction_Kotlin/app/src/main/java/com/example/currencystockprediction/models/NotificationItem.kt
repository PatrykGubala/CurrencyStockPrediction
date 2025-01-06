package com.example.currencystockprediction.models

data class NotificationItem(
    val iconRes: Int,
    val title: String,
    val message: String,
    val created_at: String,
    var is_read: Boolean
)