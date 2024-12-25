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
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.currencystockprediction.utils.FlagUtils

class CurrencyAdapter(
    private var currencies: List<Currency>,
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
        holder.percentageChangeTextView.text = if (currency.dataAvailability) {
            "0.00%"
        } else {
            "N/A"
        }

        val flagUrl = FlagUtils.getFlagUrl(currency.code)
        Glide.with(holder.flagImageView.context)
            .load(flagUrl)
            .diskCacheStrategy(DiskCacheStrategy.ALL)
            .placeholder(R.drawable.ic_launcher_background)
            .error(R.drawable.ic_launcher_background)
            .into(holder.flagImageView)
    }

    override fun getItemCount(): Int = currencies.size

    fun updateData(newCurrencies: List<Currency>) {
        currencies = newCurrencies
        notifyDataSetChanged()
    }


}
