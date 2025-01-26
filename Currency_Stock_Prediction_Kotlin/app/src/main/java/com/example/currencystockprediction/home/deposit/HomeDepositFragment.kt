package com.example.currencystockprediction.home.deposit

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.R
import com.example.currencystockprediction.databinding.FragmentHomeDepositBinding
import com.example.currencystockprediction.home.HomeViewModel
import com.google.android.material.bottomnavigation.BottomNavigationView
import kotlinx.coroutines.launch

class HomeDepositFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE

    private var _binding: FragmentHomeDepositBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: HomeDepositViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentHomeDepositBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupSystemUI()
        setupBottomNav()
        setupToolbar()

        viewModel = ViewModelProvider(this).get(HomeDepositViewModel::class.java)

        viewModel.usdBalance.observe(viewLifecycleOwner) { balance ->
            binding.accountAmountTextView.text = "Stan konta: $${String.format("%.2f", balance)}"
        }

        viewModel.depositResult.observe(viewLifecycleOwner) { result ->
            binding.depositSubmitButton.isEnabled = true
            result.onSuccess { newBalance ->
                binding.depositAmountTextInputEditText.text?.clear()
                Toast.makeText(
                    requireContext(),
                    "Nowy stan konta: $${String.format("%.2f", newBalance)}",
                    Toast.LENGTH_SHORT
                ).show()
            }.onFailure { exception ->
                Toast.makeText(
                    requireContext(),
                    "Nie udało się wpłacić środków: ${exception.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

        if (viewModel.usdBalance.value == null) {
            viewModel.fetchAccountBalances()
        }

        binding.depositSubmitButton.setOnClickListener {
            depositCurrency()
        }

        binding.depositAmountTextInputEditText.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                depositCurrency()
                true
            } else {
                false
            }
        }
    }

    private fun depositCurrency() {
        val amountStr = binding.depositAmountTextInputEditText.text.toString()
        if (amountStr.isNotEmpty()) {
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(requireContext(), "Wpisz poprawną wartość", Toast.LENGTH_SHORT).show()
                return
            }
            binding.depositSubmitButton.isEnabled = false
            viewModel.depositCurrency(amount)
        } else {
            Toast.makeText(requireContext(), "Proszę wpisać kwotę", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupSystemUI() {
        val window = requireActivity().window
        insetsController = WindowInsetsControllerCompat(window, window.decorView)
        hideSystemUI()
    }

    private fun setupBottomNav() {
        bottomNavView = requireActivity().findViewById(R.id.bottomNavView)
        originalBottomNavVisibility = bottomNavView.visibility
        bottomNavView.visibility = View.GONE
    }

    private fun setupToolbar() {
        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.homeFragment, false)
        }
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
