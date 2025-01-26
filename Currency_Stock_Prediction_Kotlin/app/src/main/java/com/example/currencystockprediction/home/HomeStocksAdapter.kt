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
import com.example.currencystockprediction.models.Stock
import com.example.currencystockprediction.stock.StockAdapter
import com.example.currencystockprediction.utils.StockIconsUtils


class HomeStocksAdapter(
    private var stocks: List<Stock>,
    private val onItemClick: ((Stock) -> Unit)? = null
) : RecyclerView.Adapter<HomeStocksAdapter.StockViewHolder>() {

    inner class StockViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val stockImageView: ImageView = itemView.findViewById(R.id.stockImageView)
        val stockTextView: TextView = itemView.findViewById(R.id.stockTextView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): StockViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.fragment_home_stock_item, parent, false)
        return StockViewHolder(view)
    }

    override fun onBindViewHolder(holder: StockViewHolder, position: Int) {
        val stock = stocks[position]
        holder.stockTextView.text = stock.stock_symbol
        Glide.with(holder.stockImageView.context)
            .load(StockIconsUtils.getStockIconResource(stock.stock_symbol))
            .diskCacheStrategy(DiskCacheStrategy.ALL)
            .placeholder(R.drawable.ic_launcher_background)
            .error(R.drawable.ic_launcher_background)
            .into(holder.stockImageView)
        holder.itemView.setOnClickListener {
            onItemClick?.invoke(stock)
        }
    }

    override fun getItemCount(): Int = stocks.size

    fun updateData(newStocks: List<Stock>) {
        stocks = newStocks
        notifyDataSetChanged()
    }
}
