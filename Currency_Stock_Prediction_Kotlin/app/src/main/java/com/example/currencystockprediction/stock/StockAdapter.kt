package com.example.currencystockprediction.stock

import android.graphics.Color
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
import com.example.currencystockprediction.models.Stock
import com.example.currencystockprediction.utils.FlagUtils
import com.example.currencystockprediction.utils.StockIconsUtils

class StockAdapter(
    private var stocks: List<Stock>,
    private val onItemClick: ((Stock) -> Unit)? = null
) : RecyclerView.Adapter<StockAdapter.StockViewHolder>() {

    inner class StockViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val iconImageView: ImageView = itemView.findViewById(R.id.stockFlagImageView)
        val nameTextView: TextView = itemView.findViewById(R.id.stockNameTextView)
        val percentageChangeTextView: TextView = itemView.findViewById(R.id.stockPercentageChangeTextView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): StockViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.fragment_stock_item, parent, false)
        return StockViewHolder(view)
    }

    override fun onBindViewHolder(holder: StockViewHolder, position: Int) {
        val stock = stocks[position]
        holder.nameTextView.text = stock.stock_symbol

        Glide.with(holder.iconImageView.context)
            .load(StockIconsUtils.getStockIconResource(stock.stock_symbol))
            .diskCacheStrategy(DiskCacheStrategy.ALL)
            .placeholder(R.drawable.ic_launcher_background)
            .error(R.drawable.ic_launcher_background)
            .into(holder.iconImageView)

        if (stock.dataAvailability && !stock.monthlyPercentageChange.isNullOrEmpty()) {
            holder.percentageChangeTextView.text = "${stock.monthlyPercentageChange}%"
            holder.percentageChangeTextView.setTextColor(
                if (stock.monthlyPercentageChange!!.startsWith("-")) Color.RED else Color.GREEN
            )
            holder.itemView.alpha = 1.0f
            holder.itemView.isEnabled = true
            holder.itemView.setOnClickListener {
                onItemClick?.invoke(stock)
            }
        } else {
            holder.percentageChangeTextView.text = "N/A"
            holder.percentageChangeTextView.setTextColor(Color.GRAY)
            holder.itemView.alpha = 0.5f
            holder.itemView.isEnabled = false
            holder.itemView.setOnClickListener(null)
        }
    }

    override fun getItemCount(): Int = stocks.size

    fun updateData(newStocks: List<Stock>) {
        stocks = newStocks
        notifyDataSetChanged()
    }
}