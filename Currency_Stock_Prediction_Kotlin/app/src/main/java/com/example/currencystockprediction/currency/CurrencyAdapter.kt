package com.example.currencystockprediction.currency

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.currencystockprediction.R
import com.example.currencystockprediction.models.Currency
import com.bumptech.glide.Glide

class CurrencyAdapter(
    private val currencies: List<Currency>,
    private val onItemClick: ((Currency) -> Unit)? = null
) : RecyclerView.Adapter<CurrencyAdapter.CurrencyViewHolder>() {

    inner class CurrencyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val flagImageView: ImageView = itemView.findViewById(R.id.currencyFlagImageView)
        val nameTextView: TextView = itemView.findViewById(R.id.currencyNameTextView)
        val percentageChangeTextView: TextView = itemView.findViewById(R.id.currencyPercentageChangeTextView)

        init {
            itemView.setOnClickListener {
                val position = adapterPosition
                if (position != RecyclerView.NO_POSITION && onItemClick != null) {
                    onItemClick.invoke(currencies[position])
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CurrencyViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.fragment_currency_item, parent, false)
        return CurrencyViewHolder(view)
    }

    override fun onBindViewHolder(holder: CurrencyViewHolder, position: Int) {
        val currency = currencies[position]
        holder.nameTextView.text = currency.code
        holder.percentageChangeTextView.text = "0.00%"

        val flagUrl = getFlagUrl(currency.code)
        Glide.with(holder.flagImageView.context)
            .load(flagUrl)
            .into(holder.flagImageView)
    }

    override fun getItemCount(): Int = currencies.size

    private fun getFlagUrl(currencyCode: String): String {

        val currencyToCountryCode = mapOf(
            "EUR" to "eu",
            "GBP" to "gb",
            "CHF" to "ch",
            "SEK" to "se",
            "NOK" to "no",
            "DKK" to "dk",
        )
        val countryCode = currencyToCountryCode[currencyCode] ?: "eu"
        return "https://flagcdn.com/w40/${countryCode}.png"
    }
}
