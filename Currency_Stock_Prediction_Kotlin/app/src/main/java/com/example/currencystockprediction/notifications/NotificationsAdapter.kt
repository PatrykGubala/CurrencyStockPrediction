package com.example.currencystockprediction.notifications

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentNotificationsItemBinding
import com.example.currencystockprediction.models.NotificationItem

class NotificationsAdapter(private val notifications: MutableList<NotificationItem>) :
    RecyclerView.Adapter<NotificationsAdapter.NotificationViewHolder>() {

    inner class NotificationViewHolder(private val binding: FragmentNotificationsItemBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(item: NotificationItem) {
            binding.notificationIcon.setImageResource(item.iconRes)
            binding.notificationsTitle.text = item.title
            binding.notificationsMessage.text = item.message
            binding.notificationsDate.text = item.created_at
            val backgroundColor = if (item.is_read) {
                binding.notificationItemLayout.setBackgroundResource(R.drawable.background_style_black_rectangle_stroke)

            } else {
                binding.notificationItemLayout.setBackgroundResource(R.drawable.background_style_darkgrey_rectangle)

            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NotificationViewHolder {
        val binding = FragmentNotificationsItemBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return NotificationViewHolder(binding)
    }

    override fun onBindViewHolder(holder: NotificationViewHolder, position: Int) {
        holder.bind(notifications[position])
    }

    override fun getItemCount(): Int = notifications.size

    fun markAllAsRead() {
        for (notification in notifications) {
            notification.is_read = true
        }
        notifyDataSetChanged()
    }
}
