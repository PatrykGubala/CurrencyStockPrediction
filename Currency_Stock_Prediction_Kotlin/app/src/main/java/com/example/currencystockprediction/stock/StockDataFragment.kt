package com.example.currencystockprediction.stock

import android.graphics.Color
import android.graphics.Paint
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentStockDataBinding
import com.example.currencystockprediction.utils.ApiClient
import com.github.mikephil.charting.components.AxisBase
import com.github.mikephil.charting.components.Legend
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.components.MarkerView
import com.github.mikephil.charting.data.CandleData
import com.github.mikephil.charting.data.CandleDataSet
import com.github.mikephil.charting.data.CandleEntry
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.github.mikephil.charting.formatter.IAxisValueFormatter
import com.github.mikephil.charting.highlight.Highlight
import com.github.mikephil.charting.utils.MPPointF
import com.google.android.material.bottomnavigation.BottomNavigationView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class StockDataFragment : Fragment() {

    private var _binding: FragmentStockDataBinding? = null
    private val binding get() = _binding!!

    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE

    private lateinit var stockSymbol: String
    private val hourlyDateFormat = SimpleDateFormat("dd.MM HH:00", Locale.getDefault())
    private val dailyDateFormat = SimpleDateFormat("yyyy MM dd", Locale.getDefault())
    private var currentClosePrice = 0.0
    private var currentMode: String = "last_month"
    private val TAG = "StockDataFragment"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            stockSymbol = it.getString("stockSymbol") ?: "AAPL"
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentStockDataBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val window = requireActivity().window
        insetsController = WindowInsetsControllerCompat(window, window.decorView)

        bottomNavView = requireActivity().findViewById(R.id.bottomNavView)
        originalBottomNavVisibility = bottomNavView.visibility
        bottomNavView.visibility = View.GONE

        setupToolbar()
        setupCandleStickChart()
        setupLineChart()
        setupButtons()
        setupBuySellButtons()
        setupTextWatcher()

        lifecycleScope.launch {
            fetchAndDisplayStockData("last_month")
            fetchAndDisplayAccountUsdValue()
            fetchAndDisplayPercentageChanges()
            fetchAndDisplayThisStockBalance()
        }
    }

    private fun setupToolbar() {
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.stockFragment, false)
        }
        binding.titleText.text = stockSymbol
    }

    private fun setupCandleStickChart() {
        binding.candleStickChart.apply {
            description.text = "$stockSymbol CandleStick Chart"
            axisLeft.isEnabled = false
            axisLeft.setDrawGridLines(true)
            axisLeft.gridColor = Color.DKGRAY

            axisRight.isEnabled = true
            axisRight.setDrawGridLines(true)
            axisRight.gridColor = Color.DKGRAY
            axisRight.textColor = Color.WHITE

            xAxis.position = XAxis.XAxisPosition.BOTTOM
            xAxis.granularity = 4f
            xAxis.labelRotationAngle = 0f
            setBackgroundColor(Color.BLACK)
            setDrawGridBackground(false)
            xAxis.setDrawGridLines(false)

            setBorderColor(Color.WHITE)
            setTouchEnabled(true)
            isDragEnabled = true
            setScaleEnabled(true)
            setScaleXEnabled(true)
            setScaleYEnabled(false)
            isAutoScaleMinMaxEnabled = true

            xAxis.apply {
                textColor = Color.WHITE
                gridColor = Color.GRAY
            }
            legend.textColor = Color.WHITE
        }
    }

    private fun setupLineChart() {
        binding.lineChart.apply {
            description.text = "$stockSymbol Line Chart"
            setBackgroundColor(Color.BLACK)
            setTouchEnabled(true)
            isDragEnabled = true
            setScaleEnabled(true)
            setScaleXEnabled(true)
            setScaleYEnabled(false)
            axisLeft.isEnabled = false
            axisLeft.setDrawGridLines(true)
            axisLeft.gridColor = Color.DKGRAY
            axisRight.isEnabled = true
            axisRight.setDrawGridLines(true)
            axisRight.gridColor = Color.DKGRAY
            axisRight.textColor = Color.WHITE
            xAxis.position = XAxis.XAxisPosition.BOTTOM
            xAxis.granularity = 4f
            xAxis.labelRotationAngle = 0f
            xAxis.setDrawGridLines(false)
            xAxis.textColor = Color.WHITE
            legend.textColor = Color.WHITE
            legend.form = Legend.LegendForm.LINE
        }
    }

    private fun setupButtons() {
        updateButtonStyles("last_month")
        binding.lastMonthButton.setOnClickListener {
            if (currentMode != "last_month") {
                currentMode = "last_month"
                lifecycleScope.launch {
                    fetchAndDisplayStockData("last_month")
                }
                updateButtonStyles("last_month")
            }
        }
        binding.allDataButton.setOnClickListener {
            if (currentMode != "all_data") {
                currentMode = "all_data"
                lifecycleScope.launch {
                    fetchAndDisplayStockData("all_data")
                }
                updateButtonStyles("all_data")
            }
        }
        binding.allDataWithPredictionsButton.setOnClickListener {
            if (currentMode != "all_data_and_predict") {
                currentMode = "all_data_and_predict"
                lifecycleScope.launch {
                    fetchAndDisplayStockData("all_data_and_predict")
                }
                updateButtonStyles("all_data_and_predict")
            }
        }
    }

    private fun setupBuySellButtons() {
        binding.buyStockButton.setOnClickListener {
            val amountText = binding.amountTextInputEditText.text.toString()
            if (amountText.isEmpty()) {
                Toast.makeText(requireContext(), "Amount is empty", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val amount = amountText.toDoubleOrNull() ?: 0.0
            lifecycleScope.launch {
                buyStock(amount)
            }
        }

        binding.sellStockButton.setOnClickListener {
            val amountText = binding.amountTextInputEditText.text.toString()
            if (amountText.isEmpty()) {
                Toast.makeText(requireContext(), "Amount is empty", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val amount = amountText.toDoubleOrNull() ?: 0.0
            lifecycleScope.launch {
                sellStock(amount)
            }
        }
    }

    private suspend fun sellStock(amount: Double) {
        val endpoint = "/myapp/accounts/stocks/sell"
        val json = JSONObject().apply {
            put("stock_symbol", stockSymbol)
            put("amount", amount)
        }
        val responsePair = ApiClient.postRequest(endpoint, json)
        if (responsePair.first) {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Sprzedałeś akcje", Toast.LENGTH_SHORT).show()
                fetchAndDisplayAccountUsdValue()
                fetchAndDisplayThisStockBalance()
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Sprzedaż nie powiodła się: ${responsePair.second}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun setupTextWatcher() {
        binding.amountTextInputEditText.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                val inputAmount = s.toString().toDoubleOrNull() ?: 0.0
                val feeRate = 0.005
                val buyCostWithoutFee = inputAmount * (1.0 / currentClosePrice)
                val fee = buyCostWithoutFee * feeRate
                val buyTotal = buyCostWithoutFee + fee
                val revenueWithoutFee = inputAmount * (1.0 / currentClosePrice)
                val sellTotalAfterFee = revenueWithoutFee - fee

                binding.amountCalculatedTextInputEditText.setText(
                    String.format("Kup: %.2f USD / Sprzedaj: %.2f USD", buyTotal, sellTotalAfterFee)
                )
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) { }
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) { }
        })
    }

    private suspend fun fetchAndDisplayStockData(mode: String) {
        val endpoint = "/myapp/stocks/data/$stockSymbol/get"
        val frequency = if (mode == "last_month") "hourly" else "daily"
        val range = if (mode == "last_month") "last_month" else "all_data"
        val responsePair = withContext(Dispatchers.IO) {
            ApiClient.getRequest("$endpoint?frequency=$frequency&range=$range")
        }
        withContext(Dispatchers.Main) {
            if (responsePair.first && responsePair.second != null) {
                val jsonData = JSONObject(responsePair.second!!).getJSONArray("data")
                if (frequency == "hourly") {
                    val entries = mutableListOf<CandleEntry>()
                    val dates = mutableListOf<Long>()
                    for (i in jsonData.length() - 1 downTo 0) {
                        val obj = jsonData.getJSONObject(i)
                        val timestampString = obj.getString("timestamp")
                        val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                        val parsedDate = dateFormat.parse(timestampString)
                        val timestampLong = parsedDate?.time ?: 0L
                        val open = obj.getString("open_price").toFloat()
                        val high = obj.getString("high_price").toFloat()
                        val low = obj.getString("low_price").toFloat()
                        val close = obj.getString("close_price").toFloat()

                        val newIndex = jsonData.length() - 1 - i
                        entries.add(CandleEntry(newIndex.toFloat(), high, low, open, close))
                        dates.add(timestampLong)
                        if (i == 0) {
                            currentClosePrice = close.toDouble()
                        }
                    }
                    updateCandleChart(entries, dates)
                } else {
                    val lineEntries = mutableListOf<Entry>()
                    val dates = mutableListOf<Long>()
                    for (i in 0 until jsonData.length()) {
                        val obj = jsonData.getJSONObject(i)
                        val timestampString = obj.getString("timestamp")
                        val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                        val parsedDate = dateFormat.parse(timestampString)
                        val timestamp = parsedDate?.time ?: 0L
                        val close = obj.getString("close_price").toFloat()
                        lineEntries.add(Entry(i.toFloat(), close))
                        dates.add(timestamp)
                        if (i == jsonData.length() - 1) {
                            currentClosePrice = close.toDouble()
                        }
                    }
                    if (mode == "all_data_and_predict") {
                        lifecycleScope.launch {
                            val predEndpoint = "/myapp/stocks/prediction/$stockSymbol/data"
                            val predResponsePair = withContext(Dispatchers.IO) {
                                ApiClient.getRequest(predEndpoint)
                            }
                            if (predResponsePair.first && predResponsePair.second != null) {
                                val predJsonArray = JSONObject(predResponsePair.second!!)
                                    .getJSONArray("predictions")
                                val predEntries = mutableListOf<Entry>()

                                for (i in 0 until predJsonArray.length()) {
                                    val obj = predJsonArray.getJSONObject(i)
                                    val timestampString = obj.getString("timestamp")
                                    val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.getDefault())
                                    val parsedDate = dateFormat.parse(timestampString)
                                    val timestamp = parsedDate?.time ?: 0L
                                    val predicted = obj.getString("predicted_value").toFloat()
                                    val newIndex = lineEntries.size + i
                                    predEntries.add(Entry(newIndex.toFloat(), predicted))
                                    dates.add(timestamp)
                                }
                                val actualDataSet = LineDataSet(lineEntries, "Daily Close").apply {
                                    color = Color.YELLOW
                                    setDrawCircles(false)
                                    setDrawValues(false)
                                    lineWidth = 0.8f
                                }
                                val predictedDataSet = LineDataSet(predEntries, "Predicted").apply {
                                    color = Color.BLUE
                                    setDrawCircles(false)
                                    setDrawValues(false)
                                    lineWidth = 0.8f
                                }
                                val lineData = LineData(actualDataSet, predictedDataSet)
                                binding.lineChart.data = lineData
                                val marker = CustomMarkerView(requireContext(), R.layout.marker_view, dailyDateFormat, dates)
                                binding.lineChart.marker = marker
                                binding.lineChart.xAxis.valueFormatter = DateAxisFormatter(dates, false)
                                binding.lineChart.invalidate()
                            } else {
                                Toast.makeText(requireContext(), "Failed to load predictions", Toast.LENGTH_SHORT).show()
                            }
                        }
                    } else {
                        updateLineChart(lineEntries, dates)
                    }
                }
            } else {
                Toast.makeText(requireContext(), "Failed to load data", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun updateCandleChart(entries: List<CandleEntry>, dates: List<Long>) {
        binding.candleStickChart.visibility = View.VISIBLE
        binding.lineChart.visibility = View.GONE
        val dataSet = CandleDataSet(entries, "$stockSymbol=X").apply {
            increasingColor = Color.GREEN
            decreasingColor = Color.RED
            increasingPaintStyle = Paint.Style.FILL
            decreasingPaintStyle = Paint.Style.FILL
            shadowColor = Color.WHITE
            shadowWidth = 0.3f
            setDrawValues(false)
        }
        binding.candleStickChart.data = CandleData(dataSet)
        val marker = CustomMarkerView(requireContext(), R.layout.marker_view, hourlyDateFormat, dates)
        binding.candleStickChart.marker = marker
        binding.candleStickChart.xAxis.valueFormatter = DateAxisFormatter(dates, true)
        binding.candleStickChart.invalidate()
    }

    private fun updateLineChart(entries: List<Entry>, dates: List<Long>) {
        binding.candleStickChart.visibility = View.GONE
        binding.lineChart.visibility = View.VISIBLE
        val dataSet = LineDataSet(entries, "Daily Close").apply {
            color = Color.YELLOW
            setDrawCircles(false)
            setDrawValues(false)
            lineWidth = 0.8f
        }
        val lineData = LineData(dataSet)
        binding.lineChart.data = lineData
        val marker = CustomMarkerView(requireContext(), R.layout.marker_view, dailyDateFormat, dates)
        binding.lineChart.marker = marker
        binding.lineChart.xAxis.valueFormatter = DateAxisFormatter(dates, false)
        binding.lineChart.invalidate()
    }

    private fun updateButtonStyles(selectedMode: String) {
        binding.lastMonthButton.setBackgroundColor(Color.TRANSPARENT)
        binding.lastMonthButton.setTextColor(Color.WHITE)
        binding.allDataButton.setBackgroundColor(Color.TRANSPARENT)
        binding.allDataButton.setTextColor(Color.WHITE)
        binding.allDataWithPredictionsButton.setBackgroundColor(Color.TRANSPARENT)
        binding.allDataWithPredictionsButton.setTextColor(Color.WHITE)

        when (selectedMode) {
            "last_month" -> {
                binding.lastMonthButton.setBackgroundResource(R.drawable.background_style_mildblue_rectangle)
                binding.lastMonthButton.setTextColor(Color.BLACK)
            }
            "all_data" -> {
                binding.allDataButton.setBackgroundResource(R.drawable.background_style_mildblue_rectangle)
                binding.allDataButton.setTextColor(Color.BLACK)
            }
            "all_data_and_predict" -> {
                binding.allDataWithPredictionsButton.setBackgroundResource(R.drawable.background_style_mildblue_rectangle)
                binding.allDataWithPredictionsButton.setTextColor(Color.BLACK)
            }
        }
    }

    inner class DateAxisFormatter(
        private val dates: List<Long>,
        private val isHourly: Boolean
    ) : IAxisValueFormatter {
        override fun getFormattedValue(value: Float, axis: AxisBase?): String {
            val index = value.toInt()
            return if (index in dates.indices) {
                val date = Date(dates[index])
                if (isHourly) {
                    hourlyDateFormat.format(date)
                } else {
                    dailyDateFormat.format(date)
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

        override fun refreshContent(e: Entry?, highlight: Highlight?) {
            if (e is CandleEntry) {
                val index = e.x.toInt()
                if (index in dates.indices) {
                    val date = Date(dates[index])
                    val dateStr = dateFormat.format(date)
                    val content = "Date: $dateStr\nOpen: ${e.open}\nClose: ${e.close}\nHigh: ${e.high}\nLow: ${e.low}"
                    tvContent.text = content
                    Log.d("CustomMarkerView", "Stock: $content")
                }
            } else if (e != null) {
                val index = e.x.toInt()
                if (index in dates.indices) {
                    val date = Date(dates[index])
                    val dateStr = dateFormat.format(date)
                    val content = "Date: $dateStr\nValue: ${e.y}"
                    tvContent.text = content
                    Log.d("CustomMarkerView", "Stock: $content")
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
                binding.accountUsdValueTextView.text = "Stan konta USD: $%.2f".format(usdValue)
            }
        } else {
            Log.e(TAG, "Failed to get USD account value")
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Nie załadowano USD", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun fetchAndDisplayPercentageChanges() {
        val endpoint = "/myapp/stocks/data/$stockSymbol/change"
        val responsePair = ApiClient.getRequest(endpoint)
        if (responsePair.first && responsePair.second != null) {
            val obj = JSONObject(responsePair.second!!)
            val weeklyChange = obj.optString("weekly_change", "0%")
            val monthlyChange = obj.optString("monthly_change", "0%")
            val yearlyChange = obj.optString("yearly_change", "0%")

            withContext(Dispatchers.Main) {
                binding.weeklyChangePercantageTextView.text = weeklyChange
                binding.monthlyChangePercantageTextView.text = monthlyChange
                binding.yearlyChangePercantageTextView.text = yearlyChange
            }
        } else {
            Log.e(TAG, "Failed to get percentage changes")
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Nie udało się załadować zmian procentowych", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun fetchAndDisplayThisStockBalance() {
        val endpoint = "/myapp/accounts/stocks/$stockSymbol/balance"
        val responsePair = ApiClient.getRequest(endpoint)

        if (responsePair.first && responsePair.second != null) {
            val obj = JSONObject(responsePair.second!!)
            val balance = obj.optString("balance", "0.0")
            val symbol = obj.optString("stock_symbol", stockSymbol)
            withContext(Dispatchers.Main) {
                binding.accountOtherCurrencyValueTextView.text =
                    "Stan wybranej akcji: %.2f %s".format(balance.toDouble(), symbol)
            }
        } else {
            Log.e(TAG, "Failed to get balance for $stockSymbol")
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Nie załadowano stanu konta", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private suspend fun buyStock(amount: Double) {
        val endpoint = "/myapp/accounts/stocks/buy"
        val json = JSONObject().apply {
            put("stock_symbol", stockSymbol)
            put("amount", amount)
        }
        val responsePair = ApiClient.postRequest(endpoint, json)

        if (responsePair.first) {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Kupiłeś akcje", Toast.LENGTH_SHORT).show()
                fetchAndDisplayAccountUsdValue()
                fetchAndDisplayThisStockBalance()
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Kupno nie powiodło się: ${responsePair.second}", Toast.LENGTH_LONG).show()
            }
        }
    }

    override fun onPause() {
        super.onPause()
        bottomNavView.visibility = originalBottomNavVisibility
    }

    override fun onDestroyView() {
        super.onDestroyView()
        bottomNavView.visibility = originalBottomNavVisibility
        insetsController = null
        _binding = null
    }
}
