package com.example.currencystockprediction.home.history

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentHomeHistoryTransactionHeaderBinding
import com.example.currencystockprediction.databinding.FragmentHomeHistoryTransactionItemBinding
import com.example.currencystockprediction.models.HistoryItem
import java.text.SimpleDateFormat
import java.util.Locale

class HistoryTransactionsAdapter(private val userAccountId: Int) :
    RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    private var items: List<HistoryItem> = listOf()

    fun submitList(list: List<HistoryItem>) {
        items = list
        notifyDataSetChanged()
    }

    inner class HeaderViewHolder(val binding: FragmentHomeHistoryTransactionHeaderBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(item: HistoryItem.HeaderItem) {
            binding.headerTextView.text = item.month
        }
    }

    inner class TransactionViewHolder(val binding: FragmentHomeHistoryTransactionItemBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(item: HistoryItem.TransactionItem) {
            val costToDisplay = item.defaultCurrencyCost ?: item.amount

            val isIncome = isIncome(item)
            val sign = if (isIncome) "+" else "-"

            binding.transactionIcon.setImageResource(item.iconRes)
            binding.transactionTitle.text = item.title
            binding.transactionAmount.text = "$sign${String.format("%.2f", costToDisplay)}"
            binding.transactionDate.text = formatDate(item.date)

            applyGroupBackground(itemView, layoutPosition)

        }

        private fun formatDate(dateStr: String): String {
            return try {
                val sdfInput = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                val sdfOutput = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault())
                val date = sdfInput.parse(dateStr)
                sdfOutput.format(date!!)
            } catch (e: Exception) {
                dateStr
            }
        }

        private fun isIncome(item: HistoryItem.TransactionItem): Boolean {
            return when (item.transactionType) {
                "deposit" -> true
                "sell" -> true
                "withdraw" -> false
                "buy" -> false
                "send" -> item.receiverAccountId == userAccountId
                else -> false
            }
        }
    }

    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is HistoryItem.HeaderItem -> VIEW_TYPE_HEADER
            is HistoryItem.TransactionItem -> VIEW_TYPE_TRANSACTION
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return if (viewType == VIEW_TYPE_HEADER) {
            val binding = FragmentHomeHistoryTransactionHeaderBinding.inflate(
                LayoutInflater.from(parent.context),
                parent,
                false
            )
            HeaderViewHolder(binding)
        } else {
            val binding = FragmentHomeHistoryTransactionItemBinding.inflate(
                LayoutInflater.from(parent.context),
                parent,
                false
            )
            TransactionViewHolder(binding)
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val item = items[position]
        if (holder is HeaderViewHolder && item is HistoryItem.HeaderItem) {
            holder.bind(item)
        } else if (holder is TransactionViewHolder && item is HistoryItem.TransactionItem) {
            holder.bind(item)
        }
    }

    private fun applyGroupBackground(itemView: View, position: Int) {
        val isFirstInGroup = isFirstInGroup(position)
        val isLastInGroup = isLastInGroup(position)

        when {
            isFirstInGroup && isLastInGroup -> {
                itemView.setBackgroundResource(R.drawable.background_style_darkgrey_rectangle_stroke_middle)
            }
            isFirstInGroup -> {
                itemView.setBackgroundResource(R.drawable.background_style_darkgrey_rectangle_stroke_top)
            }
            isLastInGroup -> {
                itemView.setBackgroundResource(R.drawable.background_style_darkgrey_rectangle_stroke_bottom)
            }
            else -> {
                itemView.setBackgroundResource(R.drawable.background_style_darkgrey_rectangle_stroke_middle)
            }
        }
    }

    private fun isFirstInGroup(position: Int): Boolean {
        if (position == 0) return true
        val currentItem = items[position]
        val prevItem = items[position - 1]
        return (currentItem is HistoryItem.HeaderItem && prevItem is HistoryItem.TransactionItem) ||
                (currentItem is HistoryItem.TransactionItem && prevItem is HistoryItem.HeaderItem)
    }

    private fun isLastInGroup(position: Int): Boolean {
        if (position == items.size - 1) return true
        val currentItem = items[position]
        val nextItem = items[position + 1]
        return (currentItem is HistoryItem.HeaderItem && nextItem is HistoryItem.HeaderItem) ||
                (currentItem is HistoryItem.TransactionItem && nextItem is HistoryItem.HeaderItem)
    }

    override fun getItemCount(): Int = items.size

    companion object {
        private const val VIEW_TYPE_HEADER = 0
        private const val VIEW_TYPE_TRANSACTION = 1
    }
}
