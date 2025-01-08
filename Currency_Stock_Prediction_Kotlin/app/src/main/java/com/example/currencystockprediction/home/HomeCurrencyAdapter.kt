package com.example.currencystockprediction.home

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.currencystockprediction.R
import com.example.currencystockprediction.models.Currency
import com.example.currencystockprediction.utils.FlagUtils

class HomeCurrencyAdapter(
    private var currencies: List<Currency>,
    private val onItemClick: ((Currency) -> Unit)? = null
) : RecyclerView.Adapter<HomeCurrencyAdapter.CurrencyViewHolder>() {

    inner class CurrencyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val currencyImageView: ImageView = itemView.findViewById(R.id.currencyImageView)
        val currencyNameTextView: TextView = itemView.findViewById(R.id.currencyNameTextView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CurrencyViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.fragment_home_currency_item, parent, false)
        return CurrencyViewHolder(view)
    }

    override fun onBindViewHolder(holder: CurrencyViewHolder, position: Int) {
        val currency = currencies[position]
        holder.currencyNameTextView.text = currency.code
        val flagUrl = FlagUtils.getFlagUrl(currency.code)
        Glide.with(holder.currencyImageView.context)
            .load(flagUrl)
            .diskCacheStrategy(DiskCacheStrategy.ALL)
            .placeholder(R.drawable.ic_launcher_background)
            .error(R.drawable.ic_launcher_background)
            .into(holder.currencyImageView)
        holder.itemView.setOnClickListener {
            onItemClick?.invoke(currency)
        }
    }

    override fun getItemCount(): Int = currencies.size

    fun updateData(newCurrencies: List<Currency>) {
        currencies = newCurrencies
        notifyDataSetChanged()
    }
}
