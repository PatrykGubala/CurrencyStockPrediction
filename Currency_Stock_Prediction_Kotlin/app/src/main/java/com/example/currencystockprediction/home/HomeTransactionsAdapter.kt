package com.example.currencystockprediction.home

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.currencystockprediction.databinding.FragmentHomeHistoryTransactionItemBinding
import com.example.currencystockprediction.databinding.FragmentHomeTransactionItemBinding
import com.example.currencystockprediction.models.HistoryItem
import com.example.currencystockprediction.models.TransactionItem
import java.text.SimpleDateFormat
import java.util.Locale

class HomeTransactionsAdapter(
    private val userAccountId: Int
) : RecyclerView.Adapter<HomeTransactionsAdapter.TransactionViewHolder>() {

    private val items = mutableListOf<HistoryItem.TransactionItem>()

    inner class TransactionViewHolder(
        private val binding: FragmentHomeTransactionItemBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        fun bind(item: HistoryItem.TransactionItem) {
            val costToDisplay = item.defaultCurrencyCost
            val isIncome = isIncome(item)
            val sign = if (isIncome) "+" else "-"
            binding.transactionIcon.setImageResource(item.iconRes)
            binding.transactionTitle.text = item.title
            binding.transactionAmount.text = "$sign${String.format("%.2f", costToDisplay)}"
            binding.transactionDate.text = formatDate(item.date)
        }

        private fun isIncome(item: HistoryItem.TransactionItem): Boolean {
            return when (item.transactionType) {
                "deposit" -> true
                "withdraw" -> false
                "send", "transfer", "exchange" -> item.receiverAccountId == userAccountId
                else -> false
            }
        }

        private fun formatDate(dateStr: String): String {
            return try {
                val sdfInput = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                val sdfOutput = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault())
                val date = sdfInput.parse(dateStr)
                sdfOutput.format(date!!)
            } catch (_: Exception) {
                dateStr
            }
        }
    }


    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TransactionViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        val binding = FragmentHomeTransactionItemBinding.inflate(inflater, parent, false)
        return TransactionViewHolder(binding)
    }
    override fun onBindViewHolder(holder: TransactionViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size

    fun submitList(newItems: List<HistoryItem.TransactionItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }
}