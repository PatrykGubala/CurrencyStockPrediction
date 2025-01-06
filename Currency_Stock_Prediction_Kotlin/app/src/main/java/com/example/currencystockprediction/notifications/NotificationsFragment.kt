package com.example.currencystockprediction.notifications

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentNotificationsBinding
import com.example.currencystockprediction.models.NotificationItem

class NotificationsFragment : Fragment() {

    private var _binding: FragmentNotificationsBinding? = null
    private val binding get() = _binding!!

    private lateinit var notificationsAdapter: NotificationsAdapter
    private val notificationsList = mutableListOf<NotificationItem>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentNotificationsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        notificationsAdapter = NotificationsAdapter(notificationsList)
        binding.notificationsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        binding.notificationsRecyclerView.adapter = notificationsAdapter

        loadMockNotifications()

        binding.rightButton.setOnClickListener {
            markAllNotificationsAsRead()
        }
    }

    private fun loadMockNotifications() {
        notificationsList.add(
            NotificationItem(
                iconRes = R.drawable.help_circle,
                title = "USD Price Alert",
                message = "Waluta PLN osiągneła poziom 4.1415231",
                created_at = "3d",
                is_read = false
            )
        )
        notificationsList.add(
            NotificationItem(
                iconRes = R.drawable.check,
                title = "Nowy transfer",
                created_at = "28d",
                message = "Otrzymałeś transfer $500 USD.",
                is_read = false
            )
        )
        notificationsAdapter.notifyDataSetChanged()
    }

    private fun markAllNotificationsAsRead() {
        notificationsAdapter.markAllAsRead()
        Toast.makeText(requireContext(), "All notifications marked as read.", Toast.LENGTH_SHORT).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
