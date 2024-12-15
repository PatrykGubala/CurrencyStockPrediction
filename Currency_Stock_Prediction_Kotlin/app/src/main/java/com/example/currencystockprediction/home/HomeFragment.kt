package com.example.currencystockprediction.home

import android.graphics.Color
import android.graphics.Paint
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentHomeBinding
import com.github.mikephil.charting.components.AxisBase
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.CandleData
import com.github.mikephil.charting.data.CandleDataSet
import com.github.mikephil.charting.data.CandleEntry
import com.github.mikephil.charting.formatter.IAxisValueFormatter
import com.github.mikephil.charting.highlight.Highlight
import com.github.mikephil.charting.components.MarkerView
import com.github.mikephil.charting.utils.MPPointF
import java.text.SimpleDateFormat
import java.util.*
import kotlin.random.Random

class HomeFragment : Fragment() {

    private lateinit var binding: FragmentHomeBinding
    private val dateFormat = SimpleDateFormat("dd MMM HH", Locale.getDefault())
    private val entriesDates = mutableListOf<Long>()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupChart()

        val dataSet = CandleDataSet(generateDailyEntries(), "USD/PLN").apply {
            increasingColor = Color.GREEN
            decreasingColor = Color.RED
            increasingPaintStyle = Paint.Style.FILL
            decreasingPaintStyle = Paint.Style.FILL
            shadowColor = Color.WHITE
            shadowWidth = 0.7f
            setDrawValues(false)
        }

        val candleData = CandleData(dataSet)
        binding.candleStickChart.data = candleData

        val marker = CustomMarkerView(requireContext(), R.layout.marker_view, dateFormat, entriesDates)
        binding.candleStickChart.marker = marker

        binding.candleStickChart.post {
            val totalEntries = entriesDates.size
            val lastDayStartIndex = if (totalEntries > 24) totalEntries - 24 else 0
            binding.candleStickChart.moveViewToX(lastDayStartIndex.toFloat())
            binding.candleStickChart.setVisibleXRangeMaximum(24f)
            binding.candleStickChart.invalidate()
        }

        binding.candleStickChart.invalidate()
    }

    private fun setupChart() {
        binding.candleStickChart.apply {
            description.text = "USD/PLN (Hourly)"
            axisRight.isEnabled = false
            xAxis.position = XAxis.XAxisPosition.BOTTOM
            xAxis.valueFormatter = DateAxisFormatter(entriesDates)
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

    private fun generateDailyEntries(): List<CandleEntry> {
        val entries = mutableListOf<CandleEntry>()
        var lastClose = 4.45f
        val calendar = Calendar.getInstance().apply {
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
            add(Calendar.DAY_OF_YEAR, -7)
        }
        for (i in 0 until 7 * 24) {
            val timestamp = calendar.timeInMillis
            entriesDates.add(timestamp)
            val open = lastClose
            val close = (open + Random.nextFloat() * 0.2f - 0.1f).coerceIn(4.20f, 4.70f)
            val high = maxOf(open, close) + Random.nextFloat() * 0.05f
            val low = minOf(open, close) - Random.nextFloat() * 0.05f
            entries.add(CandleEntry(i.toFloat(), high, low, open, close))
            lastClose = close
            calendar.add(Calendar.HOUR_OF_DAY, 1)
        }
        return entries
    }

    inner class DateAxisFormatter(private val dates: List<Long>) : IAxisValueFormatter {
        private val sdf = SimpleDateFormat("dd MMM\nHH", Locale.getDefault())
        override fun getFormattedValue(value: Float, axis: AxisBase?): String {
            val index = value.toInt()
            return if (index in dates.indices) {
                sdf.format(Date(dates[index]))
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
                    val content = "Date: $dateStr\n" +
                            "Open: ${e.open}\n" +
                            "Close: ${e.close}\n" +
                            "High: ${e.high}\n" +
                            "Low: ${e.low}"
                    tvContent.text = content
                }
            }
            super.refreshContent(e, highlight)
        }
        override fun getOffset(): MPPointF {
            return MPPointF(-(width / 2).toFloat(), -height.toFloat())
        }
    }
}
