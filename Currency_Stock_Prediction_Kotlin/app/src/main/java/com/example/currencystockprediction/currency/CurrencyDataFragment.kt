package com.example.currencystockprediction.currency

import android.graphics.Color
import android.graphics.Paint
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
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
import com.google.android.material.bottomnavigation.BottomNavigationView
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

    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE

    private lateinit var currencyCode: String
    private val hourlyDateFormat = SimpleDateFormat("dd.MM HH:00", Locale.getDefault())
    private val dailyDateFormat = SimpleDateFormat("yyyy MM dd", Locale.getDefault())
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

        val window = requireActivity().window
        insetsController = WindowInsetsControllerCompat(window, window.decorView)
        hideSystemUI()

        bottomNavView = requireActivity().findViewById(R.id.bottomNavView)
        originalBottomNavVisibility = bottomNavView.visibility
        bottomNavView.visibility = View.GONE




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
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.currencyFragment, false)
        }
        binding.titleText.text = "USD$currencyCode=X"
    }

    private fun setupChart() {
        binding.candleStickChart.apply {
            description.text = "$currencyCode CandleStick Chart"
            axisRight.isEnabled = false
            xAxis.position = XAxis.XAxisPosition.BOTTOM
            xAxis.granularity = 4f
            xAxis.labelRotationAngle = 0f
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
        updateButtonStyles("last_month")

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
            val endpoint = "/myapp/currencies/data/$currencyCode/get"
            val frequency = if (mode == "last_month") "hourly" else "daily"
            val range = if (mode == "last_month") "last_month" else "all_data"

            val responsePair = ApiClient.getRequest("$endpoint?frequency=$frequency&range=$range")


            if (responsePair.first && responsePair.second != null) {
                val jsonData = JSONObject(responsePair.second!!).getJSONArray("data")
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

                updateChart(entries, dates, mode)
            } else {
                withContext(Dispatchers.Main) {
                    Toast.makeText(requireContext(), "Failed to load data", Toast.LENGTH_SHORT)
                        .show()
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
            shadowWidth = 0.3f
            setDrawValues(false)
        }
        binding.candleStickChart.data = CandleData(dataSet)
        val isHourly = mode == "last_month"
        val marker = CustomMarkerView(requireContext(), R.layout.marker_view, hourlyDateFormat, dates)
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
        private val sdfHourly = hourlyDateFormat.apply {
            timeZone = TimeZone.getDefault()

        }

        private val sdfDaily = dailyDateFormat.apply {
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
        val endpoint = "/myapp/accounts/usd_value"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            val obj = JSONObject(responsePair.second!!)
            val usdValue = obj.optDouble("usd_balance", 0.0)
            withContext(Dispatchers.Main) {
                binding.accountUsdValueTextView.text = "Account USD Balance: $$usdValue"
            }
        } else {
            Log.e(TAG, "Failed to get USD account value")
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Failed to load USD balance", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun fetchAndDisplayPercentageChanges() {
        val endpoint = "/myapp/currencies/changes/$currencyCode"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            val obj = JSONObject(responsePair.second!!)
            val weeklyChange = obj.optString("weekly_change", "0%")
            val monthlyChange = obj.optString("monthly_change", "0%")
            val yearlyChange = obj.optString("yearly_change", "0%")
            withContext(Dispatchers.Main) {
                binding.weeklyChangeTextView.text = "Weekly: $weeklyChange"
                binding.monthlyChangeTextView.text = "Monthly: $monthlyChange"
                binding.yearlyChangeTextView.text = "Yearly: $yearlyChange"
            }
        } else {
            Log.e(TAG, "Failed to get percentage changes")
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Failed to load percentage changes", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun fetchAndDisplayThisCurrencyBalance() {
        val endpoint = "/myapp/accounts/currencies/$currencyCode/balance"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            val obj = JSONObject(responsePair.second!!)
            val balance = obj.optString("balance", "0.0")
            val code = obj.optString("currency_code", currencyCode)
            withContext(Dispatchers.Main) {
                binding.accountOtherCurrencyValueTextView.text = "You have $balance $code"
            }
        } else {
            Log.e(TAG, "Failed to get balance for $currencyCode")
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Failed to load currency balance", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun buyCurrency(amount: Double) {
        val endpoint = "/myapp/accounts/currencies/buy"
        val json = JSONObject().apply {
            put("currency_code", currencyCode)
            put("amount", amount)
        }
        val responsePair = ApiClient.postRequest(endpoint, json)

        if (responsePair.first) {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Currency bought successfully", Toast.LENGTH_SHORT).show()
                fetchAndDisplayAccountUsdValue()
                fetchAndDisplayThisCurrencyBalance()
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Buy failed: ${responsePair.second}", Toast.LENGTH_LONG).show()
            }
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
