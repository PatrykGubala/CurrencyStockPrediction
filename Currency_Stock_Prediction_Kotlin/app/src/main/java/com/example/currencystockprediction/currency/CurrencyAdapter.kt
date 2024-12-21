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

        val flagUrl = getFlagUrl(currency.code)
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

    private fun getFlagUrl(currencyCode: String): String {
        val currencyToCountryCode = mapOf(
            "USD" to "us",
            "AFN" to "af",
            "EUR" to "eu",
            "ALL" to "al",
            "DZD" to "dz",
            "AOA" to "ao",
            "XCD" to "ag",
            "ARS" to "ar",
            "AMD" to "am",
            "AWG" to "aw",
            "AUD" to "au",
            "AZN" to "az",
            "BSD" to "bs",
            "BHD" to "bh",
            "BDT" to "bd",
            "BBD" to "bb",
            "BYN" to "by",
            "BYR" to "by",
            "BZD" to "bz",
            "XOF" to "bf",
            "BMD" to "bm",
            "BTN" to "bt",
            "INR" to "in",
            "BOB" to "bo",
            "BAM" to "ba",
            "BWP" to "bw",
            "NOK" to "no",
            "BRL" to "br",
            "GBP" to "gb",
            "BND" to "bn",
            "SGD" to "sg",
            "BGN" to "bg",
            "BIF" to "bi",
            "KHR" to "kh",
            "XAF" to "cm",
            "CAD" to "ca",
            "CVE" to "cv",
            "KYD" to "ky",
            "CLP" to "cl",
            "CNY" to "cn",
            "COP" to "co",
            "KMF" to "km",
            "CDF" to "cd",
            "NZD" to "nz",
            "CKD" to "ck",
            "CRC" to "cr",
            "CUC" to "cu",
            "CUP" to "cu",
            "ANG" to "cw",
            "CZK" to "cz",
            "DKK" to "dk",
            "DJF" to "dj",
            "DOP" to "do",
            "EGP" to "eg",
            "ERN" to "er",
            "ETB" to "et",
            "FKP" to "fk",
            "FOK" to "fo",
            "FJD" to "fj",
            "XPF" to "pf",
            "GMD" to "gm",
            "GEL" to "ge",
            "GHS" to "gh",
            "GIP" to "gi",
            "GTQ" to "gt",
            "GGP" to "gg",
            "GNF" to "gn",
            "GYD" to "gy",
            "HTG" to "ht",
            "HNL" to "hn",
            "HUF" to "hu",
            "HKD" to "hk",
            "ISK" to "is",
            "IDR" to "id",
            "IRR" to "ir",
            "IQD" to "iq",
            "IMP" to "im",
            "ILS" to "il",
            "JMD" to "jm",
            "JPY" to "jp",
            "JEP" to "je",
            "JOD" to "jo",
            "KZT" to "kz",
            "KES" to "ke",
            "KID" to "ki",
            "KWD" to "kw",
            "KGS" to "kg",
            "LAK" to "la",
            "LBP" to "lb",
            "LSL" to "ls",
            "ZAR" to "za",
            "LRD" to "lr",
            "LYD" to "ly",
            "CHF" to "ch",
            "MOP" to "mo",
            "MKD" to "mk",
            "MGA" to "mg",
            "MWK" to "mw",
            "MYR" to "my",
            "MVR" to "mv",
            "MRO" to "mr",
            "MUR" to "mu",
            "MXN" to "mx",
            "MDL" to "md",
            "MNT" to "mn",
            "MAD" to "ma",
            "MZN" to "mz",
            "MMK" to "mm",
            "NAD" to "na",
            "NPR" to "np",
            "NIO" to "ni",
            "NGN" to "ng",
            "KPW" to "kp",
            "OMR" to "om",
            "PKR" to "pk",
            "PAB" to "pa",
            "PGK" to "pg",
            "PYG" to "py",
            "PEN" to "pe",
            "PHP" to "ph",
            "PND" to "pn",
            "PLN" to "pl",
            "QAR" to "qa",
            "RON" to "ro",
            "RUB" to "ru",
            "RWF" to "rw",
            "SHP" to "sh",
            "WST" to "ws",
            "STD" to "st",
            "SAR" to "sa",
            "RSD" to "rs",
            "SCR" to "sc",
            "SLL" to "sl",
            "SBD" to "sb",
            "SOS" to "so",
            "KRW" to "kr",
            "LKR" to "lk",
            "SDG" to "sd",
            "SSP" to "ss",
            "SRD" to "sr",
            "SZL" to "sz",
            "SEK" to "se",
            "SYP" to "sy",
            "TWD" to "tw",
            "TJS" to "tj",
            "TZS" to "tz",
            "THB" to "th",
            "TOP" to "to",
            "TTD" to "tt",
            "TND" to "tn",
            "TRY" to "tr",
            "TMT" to "tm",
            "TVD" to "tv",
            "UGX" to "ug",
            "UAH" to "ua",
            "AED" to "ae",
            "UYU" to "uy",
            "UZS" to "uz",
            "VUV" to "vu",
            "VEF" to "ve",
            "VND" to "vn",
            "YER" to "ye",
            "ZMW" to "zm"
        )
        val countryCode = currencyToCountryCode[currencyCode] ?: "eu"
        return "https://flagcdn.com/w160/${countryCode}.png"
    }
}
