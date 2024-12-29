package com.example.currencystockprediction.currency

import android.graphics.Color
import android.graphics.Paint
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentCurrencyDataBinding
import com.example.currencystockprediction.models.CurrencyData
import com.example.currencystockprediction.utils.ApiClient
import com.github.mikephil.charting.components.AxisBase
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.components.MarkerView
import com.github.mikephil.charting.data.CandleData
import com.github.mikephil.charting.data.CandleDataSet
import com.github.mikephil.charting.data.CandleEntry
import com.github.mikephil.charting.formatter.IAxisValueFormatter
import com.github.mikephil.charting.highlight.Highlight
import com.github.mikephil.charting.utils.MPPointF
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.math.BigDecimal
import java.text.SimpleDateFormat
import java.util.*

class CurrencyDataFragment : Fragment() {

    private var _binding: FragmentCurrencyDataBinding? = null
    private val binding get() = _binding!!

    private lateinit var currencyCode: String
    private val dateFormat = SimpleDateFormat("dd MMM HH", Locale.getDefault())
    private val logDateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())

    private var currentMode: String = "last_month"
    private val TAG = "CurrencyDataFragment"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            currencyCode = it.getString("currencyCode") ?: "USD"
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentCurrencyDataBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.currencyFragment, false)
        }


        setupToolbar()
        setupChart()
        setupButtons()
        setupBuyButton()

        lifecycleScope.launch {
            fetchAndDisplayCurrencyData("last_month")
            fetchAndDisplayAccountUsdValue()
            fetchAndDisplayPercentageChanges()
            fetchAndDisplayThisCurrencyBalance()
        }
    }

    private fun setupToolbar() {
        binding.goBackToolbar.setNavigationOnClickListener {
            findNavController().popBackStack(R.id.currencyFragment, false)
        }
        binding.titleText.text = "USD$currencyCode=X"
    }

    private fun setupChart() {
        binding.candleStickChart.apply {
            description.text = "$currencyCode CandleStick Chart"
            axisRight.isEnabled = false
            xAxis.position = XAxis.XAxisPosition.BOTTOM
            xAxis.granularity = 1f
            xAxis.labelRotationAngle = -45f
            setBackgroundColor(Color.BLACK)
            setDrawGridBackground(false)
            xAxis.setDrawGridLines(false)
            axisLeft.setDrawGridLines(true)
            axisLeft.gridColor = Color.DKGRAY
            setDrawBorders(true)
            setBorderColor(Color.WHITE)
            setTouchEnabled(true)
            isDragEnabled = true
            setScaleEnabled(true)
            isAutoScaleMinMaxEnabled = true
            axisLeft.apply {
                textColor = Color.WHITE
                gridColor = Color.GRAY
            }
            xAxis.apply {
                textColor = Color.WHITE
                gridColor = Color.GRAY
            }
            legend.textColor = Color.WHITE
        }
    }

    private fun setupButtons() {
        binding.lastMonthButton.setOnClickListener {
            if (currentMode != "last_month") {
                currentMode = "last_month"
                lifecycleScope.launch {
                    fetchAndDisplayCurrencyData("last_month")
                }
                updateButtonStyles("last_month")
            }
        }
        binding.allDataButton.setOnClickListener {
            if (currentMode != "all_data") {
                currentMode = "all_data"
                lifecycleScope.launch {
                    fetchAndDisplayCurrencyData("all_data")
                }
                updateButtonStyles("all_data")
            }
        }
    }

    private fun setupBuyButton() {
        binding.buyCurrencyButton.setOnClickListener {
            val amountText = binding.buyCurrencyAmountEditText.text.toString()
            if (amountText.isEmpty()) {
                Toast.makeText(requireContext(), "Amount is empty", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val amount = amountText.toDoubleOrNull() ?: 0.0
            lifecycleScope.launch {
                buyCurrency(amount)
            }
        }
    }

    private suspend fun fetchAndDisplayCurrencyData(mode: String) {
        withContext(Dispatchers.IO) {
            val endpoint = "/myapp/currencies/data/$currencyCode/fetch"
            val frequency = if (mode == "last_month") "hourly" else "daily"
            val range = if (mode == "last_month") "last_month" else "all_data"
            ApiClient.getRequest("$endpoint?frequency=$frequency&range=$range") { success, responseBody ->
                if (success && responseBody != null) {
                    val jsonData = JSONObject(responseBody).getJSONArray("data")
                    val currencyDataList = mutableListOf<CurrencyData>()
                    val entries = mutableListOf<CandleEntry>()
                    val dates = mutableListOf<Long>()

                    for (i in 0 until jsonData.length()) {
                        val obj = jsonData.getJSONObject(i)
                        val currencyData = CurrencyData(
                            timestamp = obj.getLong("timestamp"),
                            open = BigDecimal(obj.getString("open")),
                            high = BigDecimal(obj.getString("high")),
                            low = BigDecimal(obj.getString("low")),
                            close = BigDecimal(obj.getString("close")),
                            volume = BigDecimal(obj.getString("volume"))
                        )
                        currencyDataList.add(currencyData)
                    }

                    currencyDataList.forEachIndexed { index, data ->
                        val dateReadable = Date(data.timestamp)
                        val dateStr = logDateFormat.format(dateReadable)
                        Log.d(
                            TAG,
                            "Fetched data #$index -> [$dateStr] open: ${data.open}, high: ${data.high}, low: ${data.low}, close: ${data.close}, volume: ${data.volume}"
                        )
                        entries.add(
                            CandleEntry(
                                index.toFloat(),
                                data.high.toFloat(),
                                data.low.toFloat(),
                                data.open.toFloat(),
                                data.close.toFloat()
                            )
                        )
                        dates.add(data.timestamp)
                    }

                    lifecycleScope.launch(Dispatchers.Main) {
                        updateChart(entries, dates, mode)
                    }
                } else {
                    activity?.runOnUiThread {
                        Toast.makeText(requireContext(), "Failed to load data", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }

    private fun updateChart(entries: List<CandleEntry>, dates: List<Long>, mode: String) {
        val dataSet = CandleDataSet(entries, "$currencyCode=X").apply {
            increasingColor = Color.GREEN
            decreasingColor = Color.RED
            increasingPaintStyle = Paint.Style.FILL
            decreasingPaintStyle = Paint.Style.FILL
            shadowColor = Color.WHITE
            shadowWidth = 0.2f
            setDrawValues(false)
        }
        binding.candleStickChart.data = CandleData(dataSet)
        val isHourly = mode == "last_month"
        val marker = CustomMarkerView(requireContext(), R.layout.marker_view, dateFormat, dates)
        binding.candleStickChart.marker = marker
        binding.candleStickChart.xAxis.valueFormatter = DateAxisFormatter(dates, isHourly)
        binding.candleStickChart.invalidate()
    }

    private fun updateButtonStyles(selectedMode: String) {
        binding.lastMonthButton.setBackgroundColor(Color.TRANSPARENT)
        binding.lastMonthButton.setTextColor(Color.WHITE)
        binding.allDataButton.setBackgroundColor(Color.TRANSPARENT)
        binding.allDataButton.setTextColor(Color.WHITE)
        when (selectedMode) {
            "last_month" -> {
                binding.lastMonthButton.setBackgroundResource(R.drawable.background_style_mildblue_rectangle)
                binding.lastMonthButton.setTextColor(Color.BLACK)
            }
            "all_data" -> {
                binding.allDataButton.setBackgroundResource(R.drawable.background_style_mildblue_rectangle)
                binding.allDataButton.setTextColor(Color.BLACK)
            }
        }
    }

    inner class DateAxisFormatter(private val dates: List<Long>, private val isHourly: Boolean) : IAxisValueFormatter {
        private val sdfHourly = SimpleDateFormat("dd MMM HH", Locale.getDefault()).apply {
            timeZone = TimeZone.getDefault()
        }
        private val sdfDaily = SimpleDateFormat("dd MMM", Locale.getDefault()).apply {
            timeZone = TimeZone.getDefault()
        }

        override fun getFormattedValue(value: Float, axis: AxisBase?): String {
            val index = value.toInt()
            return if (index in dates.indices) {
                val date = Date(dates[index])
                if (isHourly) {
                    sdfHourly.format(date)
                } else {
                    sdfDaily.format(date)
                }
            } else {
                ""
            }
        }
    }

    class CustomMarkerView(
        context: android.content.Context,
        layoutResource: Int,
        private val dateFormat: SimpleDateFormat,
        private val dates: List<Long>
    ) : MarkerView(context, layoutResource) {
        private val tvContent = findViewById<android.widget.TextView>(R.id.tvContent)

        override fun refreshContent(e: com.github.mikephil.charting.data.Entry?, highlight: Highlight?) {
            if (e is CandleEntry) {
                val index = e.x.toInt()
                if (index in dates.indices) {
                    val date = Date(dates[index])
                    val dateStr = dateFormat.format(date)
                    val content = "Date: $dateStr\nOpen: ${e.open}\nClose: ${e.close}\nHigh: ${e.high}\nLow: ${e.low}"
                    tvContent.text = content
                    Log.d("CustomMarkerView", "Marker content: $content")
                }
            }
            super.refreshContent(e, highlight)
        }

        override fun getOffset(): MPPointF {
            return MPPointF(-(width / 2).toFloat(), -height.toFloat())
        }
    }

    private suspend fun fetchAndDisplayAccountUsdValue() {
        withContext(Dispatchers.IO) {
            val endpoint = "/myapp/accounts/usd_value"
            ApiClient.getRequest(endpoint) { success, responseBody ->
                if (success && responseBody != null) {
                    val obj = JSONObject(responseBody)
                    val usdValue = obj.optDouble("usd_balance", 0.0)
                    lifecycleScope.launch(Dispatchers.Main) {
                        binding.accountUsdValueTextView.text = "Account USD Balance: $$usdValue"
                    }
                } else {
                    Log.e(TAG, "Failed to get USD account value")
                }
            }
        }
    }

    private suspend fun fetchAndDisplayPercentageChanges() {
        withContext(Dispatchers.IO) {
            val endpoint = "/myapp/currencies/changes/$currencyCode"
            ApiClient.getRequest(endpoint) { success, responseBody ->
                if (success && responseBody != null) {
                    val obj = JSONObject(responseBody)
                    val weeklyChange = obj.optString("weekly_change", "0%")
                    val monthlyChange = obj.optString("monthly_change", "0%")
                    val yearlyChange = obj.optString("yearly_change", "0%")
                    lifecycleScope.launch(Dispatchers.Main) {
                        binding.weeklyChangeTextView.text = "Weekly: $weeklyChange"
                        binding.monthlyChangeTextView.text = "Monthly: $monthlyChange"
                        binding.yearlyChangeTextView.text = "Yearly: $yearlyChange"
                    }
                }
            }
        }
    }

    private suspend fun fetchAndDisplayThisCurrencyBalance() {
        withContext(Dispatchers.IO) {
            val endpoint = "/myapp/accounts/currencies/$currencyCode/balance"
            ApiClient.getRequest(endpoint) { success, responseBody ->
                if (success && responseBody != null) {
                    val obj = JSONObject(responseBody)
                    val balance = obj.optString("balance", "0.0")
                    val code = obj.optString("currency_code", currencyCode)
                    lifecycleScope.launch(Dispatchers.Main) {
                        binding.accountOtherCurrencyValueTextView.text = "You have $balance $code"
                    }
                } else {
                    Log.e(TAG, "Failed to get balance for $currencyCode")
                }
            }
        }
    }

    private suspend fun buyCurrency(amount: Double) {
        withContext(Dispatchers.IO) {
            val endpoint = "/myapp/accounts/currencies/buy"
            val json = JSONObject().apply {
                put("currency_code", currencyCode)
                put("amount", amount)
            }
            ApiClient.postRequest(endpoint, json) { success, responseBody ->
                if (success) {
                    lifecycleScope.launch(Dispatchers.Main) {
                        Toast.makeText(requireContext(), "Currency bought successfully", Toast.LENGTH_SHORT).show()
                        fetchAndDisplayAccountUsdValue()
                        fetchAndDisplayThisCurrencyBalance()
                    }
                } else {
                    lifecycleScope.launch(Dispatchers.Main) {
                        Toast.makeText(requireContext(), "Buy failed: $responseBody", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
