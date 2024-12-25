package com.example.currencystockprediction.currency

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import com.example.currencystockprediction.R
import com.example.currencystockprediction.utils.FlagUtils
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy

class CurrencySpinnerAdapter(
    context: Context,
    currencies: List<String>
) : ArrayAdapter<String>(context, R.layout.spinner_currency_item, currencies) {

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        return createItemView(position, convertView, parent)
    }

    override fun getDropDownView(position: Int, convertView: View?, parent: ViewGroup): View {
        return createItemView(position, convertView, parent)
    }

    private fun createItemView(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.spinner_currency_item, parent, false)

        val flagImageView: ImageView = view.findViewById(R.id.spinnerCurrencyFlagImageView)
        val currencyCodeTextView: TextView = view.findViewById(R.id.spinnerCurrencyCodeTextView)

        val currencyCode = getItem(position)
        currencyCodeTextView.text = currencyCode

        val flagUrl = FlagUtils.getFlagUrl(currencyCode ?: "")
        Glide.with(context)
            .load(flagUrl)
            .diskCacheStrategy(DiskCacheStrategy.ALL)
            .placeholder(R.drawable.ic_launcher_background)
            .error(R.drawable.ic_launcher_background)
            .into(flagImageView)

        return view
    }
}
