package com.example.currencystockprediction.home

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.currencystockprediction.databinding.FragmentHomeTransactionItemBinding
import com.example.currencystockprediction.models.TransactionItem

class HomeTransactionsAdapter(private val transactions: List<TransactionItem>) :
    RecyclerView.Adapter<HomeTransactionsAdapter.TransactionViewHolder>() {

    inner class TransactionViewHolder(val binding: FragmentHomeTransactionItemBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(item: TransactionItem) {
            binding.transactionIcon.setImageResource(item.iconRes)
            binding.transactionTitle.text = item.title
            binding.transactionAmount.text = "$${String.format("%.2f", item.amount)}"
            binding.transactionDate.text = item.date
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TransactionViewHolder {
        val binding = FragmentHomeTransactionItemBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return TransactionViewHolder(binding)
    }

    override fun onBindViewHolder(holder: TransactionViewHolder, position: Int) {
        holder.bind(transactions[position])
    }

    override fun getItemCount(): Int = transactions.size
}