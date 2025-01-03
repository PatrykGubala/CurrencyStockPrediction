package com.example.currencystockprediction.home.history

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.DatePicker
import android.widget.SearchView
import android.widget.TimePicker
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentHomeHistoryBinding
import com.google.android.material.bottomnavigation.BottomNavigationView
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class HistoryFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private var _binding: FragmentHomeHistoryBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: HistoryViewModel
    private lateinit var adapter: HistoryTransactionsAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentHomeHistoryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val window = requireActivity().window
        insetsController = WindowInsetsControllerCompat(window, window.decorView)
        hideSystemUI()

        bottomNavView = requireActivity().findViewById(R.id.bottomNavView)
        originalBottomNavVisibility = bottomNavView.visibility
        bottomNavView.visibility = View.GONE

        setupToolbar()

        viewModel = ViewModelProvider(this).get(HistoryViewModel::class.java)
        setupToolbar()
        setupRecyclerView()
        setupSearchView()
        setupSwipeRefresh()
        observeViewModel()
        setupFilterButtons()
        setupDatePickers()
        setupIncomeOutcomeRadioGroup()
        viewModel.fetchUserAccountId()

    }

    private fun setupRecyclerView() {
        val tempUserId = viewModel.userAccountId ?: 0
        adapter = HistoryTransactionsAdapter(tempUserId)
        binding.historyRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        binding.historyRecyclerView.adapter = adapter
    }

    private fun setupSearchView() {
        binding.searchView.setOnQueryTextListener(
            object : SearchView.OnQueryTextListener {
                override fun onQueryTextSubmit(query: String?): Boolean {
                    return false
                }

                override fun onQueryTextChange(newText: String?): Boolean {
                    viewModel.setSearchQuery(newText ?: "")
                    return true
                }
            },
        )
    }

    private fun setupToolbar() {
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.homeFragment, false)
        }
    }

    private fun setupFilterButtons() {

        binding.filterImageButton.setOnClickListener {
            binding.filterDialogLayout.visibility =
                if (binding.filterDialogLayout.visibility == View.GONE) View.VISIBLE else View.GONE
        }
        binding.applyFilterButton.setOnClickListener {
            val fromAmountText = binding.fromAmountTextInputEditText.text.toString()
            val toAmountText = binding.toAmountTextInputEditText.text.toString()
            val fromDateText = binding.fromDateTextInputEditText.text.toString()
            val toDateText = binding.toDateTextInputEditText.text.toString()
            val isTransferChecked = binding.checkboxTransfer.isChecked

            val depositChecked = binding.checkboxDeposit.isChecked
            val withdrawChecked = binding.checkboxWithdraw.isChecked
            val exchangeChecked = binding.checkboxExchange.isChecked
            val sendChecked = binding.checkboxSend.isChecked
            val transferChecked = binding.checkboxTransfer.isChecked

            val filters = mutableListOf<String>()
            if (depositChecked) filters.add("deposit")
            if (withdrawChecked) filters.add("withdraw")
            if (exchangeChecked) filters.add("exchange")
            if (sendChecked) filters.add("send")
            if (transferChecked) filters.add("transfer")


            val fromAmount = fromAmountText.toBigDecimalOrNull()
            val toAmount = toAmountText.toBigDecimalOrNull()

            val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
            val fromDate = try {
                if (fromDateText.isNotEmpty()) sdf.parse(fromDateText)?.time else null
            } catch (e: Exception) {
                null
            }
            val toDate = try {
                if (toDateText.isNotEmpty()) sdf.parse(toDateText)?.time else null
            } catch (e: Exception) {
                null
            }

            viewModel.setFilters(filters)
            viewModel.setAmountRange(fromAmount, toAmount)
            viewModel.setDateRange(fromDate, toDate)

            binding.filterDialogLayout.visibility = View.GONE
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefreshLayoutHistory.setOnRefreshListener {
            viewModel.fetchTransactions()
        }
    }

    private fun setupIncomeOutcomeRadioGroup() {
        binding.incomeOutcomeRadioGroup.setOnCheckedChangeListener { _, checkedId ->
            when (checkedId) {
                R.id.radio_income -> viewModel.setTransactionKind("INCOME")
                R.id.radio_outcome -> viewModel.setTransactionKind("OUTCOME")
                R.id.radio_all -> viewModel.setTransactionKind("ALL")
            }
        }
    }

    private fun observeViewModel() {
        viewModel.transactions.observe(viewLifecycleOwner) { items ->
            adapter.submitList(items)
            Log.d("HistoryFragment", "Adapter submitted ${items.size} items")

        }

        viewModel.isRefreshing.observe(viewLifecycleOwner) { isRefreshing ->
            binding.swipeRefreshLayoutHistory.isRefreshing = isRefreshing
        }
    }

    private fun setupDatePickers() {
        binding.fromDateTextInputEditText.setOnClickListener {
            showDateTimePicker { dateTimeString ->
                binding.fromDateTextInputEditText.setText(dateTimeString)
            }
        }

        binding.toDateTextInputEditText.setOnClickListener {
            showDateTimePicker { dateTimeString ->
                binding.toDateTextInputEditText.setText(dateTimeString)
            }
        }
    }


    private fun showDateTimePicker(onDateSelected: (String) -> Unit) {
        val calendar = Calendar.getInstance()
        val datePicker = DatePickerDialog(
            requireContext(),
            { _: DatePicker, year: Int, month: Int, dayOfMonth: Int ->
                calendar.set(year, month, dayOfMonth)

                val timePicker = TimePickerDialog(
                    requireContext(),
                    { _: TimePicker, hourOfDay: Int, minute: Int ->
                        calendar.set(Calendar.HOUR_OF_DAY, hourOfDay)
                        calendar.set(Calendar.MINUTE, minute)

                        val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
                        onDateSelected(sdf.format(calendar.time))
                    },
                    calendar.get(Calendar.HOUR_OF_DAY),
                    calendar.get(Calendar.MINUTE),
                    true
                )
                timePicker.show()
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        )
        datePicker.show()
    }


    override fun onResume() {
        super.onResume()
        hideSystemUI()
        if (bottomNavView.visibility != View.GONE) {
            bottomNavView.visibility = View.GONE
        }
    }

    override fun onPause() {
        super.onPause()
        showSystemUI()
        bottomNavView.visibility = originalBottomNavVisibility

    }
    private fun hideSystemUI() {
        insetsController?.let { controller ->
            controller.hide(WindowInsetsCompat.Type.systemBars())
            controller.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }
    private fun showSystemUI() {
        insetsController?.show(WindowInsetsCompat.Type.systemBars())
    }

    override fun onDestroyView() {
        super.onDestroyView()
        bottomNavView.visibility = originalBottomNavVisibility
        insetsController = null
        _binding = null
    }
}
