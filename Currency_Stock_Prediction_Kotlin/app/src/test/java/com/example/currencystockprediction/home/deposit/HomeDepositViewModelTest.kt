package com.example.currencystockprediction.home.deposit

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.Observer
import com.example.currencystockprediction.utils.ApiClient
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SessionManager
import com.example.currencystockprediction.utils.ShadowKeyStore
import com.example.currencystockprediction.utils.TestHelper
import com.google.firebase.auth.FirebaseAuth
import io.mockk.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.json.JSONArray
import org.json.JSONObject
import org.junit.*
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

@Config(shadows = [ShadowKeyStore::class])
@ExperimentalCoroutinesApi
@RunWith(RobolectricTestRunner::class)
class HomeDepositViewModelTest {
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var usdBalanceObserver: Observer<Double>
    private lateinit var depositResultObserver: Observer<Result<Double>>
    private lateinit var viewModel: HomeDepositViewModel

    @Before
    fun setUp() {
        Dispatchers.setMain(testDispatcher)
        val mockAuth = mockk<FirebaseAuth>(relaxed = true)
        TestHelper.initializeFirebaseAuth(mockAuth)

        usdBalanceObserver = mockk(relaxed = true)
        depositResultObserver = mockk(relaxed = true)
        mockkObject(ApiClient)
        every { FirebaseAuthManager.isUserLoggedIn() } returns true
        coEvery { ApiClient.getRequest(any()) } returns Pair(false, null)
        coEvery { ApiClient.postRequest(any(), any()) } returns Pair(false, null)
    }
    @After
    fun tearDown() {
        Dispatchers.resetMain()
        unmockkAll()
    }

    @Test
    fun `fetchAccountBalances init triggers`() = runTest {
        val mockResponse = JSONObject().apply {
            put("currencies", JSONArray().apply {
                put(JSONObject().apply {
                    put("currency_code", "USD")
                    put("balance", 1000.0)
                })
            })
        }.toString()
        coEvery { ApiClient.getRequest("/myapp/accounts/currencies") } returns Pair(true, mockResponse)

        viewModel = HomeDepositViewModel()
        viewModel.usdBalance.observeForever(usdBalanceObserver)
        advanceUntilIdle()

        verify { usdBalanceObserver.onChanged(1000.0) }
    }

    @Test
    fun `depositCurrency successful deposit`() = runTest {
        val depositAmount = 500.0
        val mockResponse = JSONObject().apply {
            put("new_balance", 1500.0)
        }.toString()
        coEvery { ApiClient.postRequest("/myapp/accounts/deposit", any()) } returns Pair(true, mockResponse)

        viewModel = HomeDepositViewModel()
        viewModel.usdBalance.observeForever(usdBalanceObserver)
        viewModel.depositResult.observeForever(depositResultObserver)
        viewModel.depositCurrency(depositAmount)
        advanceUntilIdle()

        verify { usdBalanceObserver.onChanged(1500.0) }
        verify { depositResultObserver.onChanged(Result.success(1500.0)) }
    }

    @Test
    fun `depositCurrency API error`() = runTest {
        coEvery { ApiClient.postRequest("/myapp/accounts/deposit", any()) } returns Pair(false, "Server error")

        viewModel = HomeDepositViewModel()
        viewModel.depositResult.observeForever(depositResultObserver)
        viewModel.depositCurrency(500.0)
        advanceUntilIdle()

        verify { depositResultObserver.onChanged(match { it.isFailure && it.exceptionOrNull()?.message == "Error deposit currencies" }) }
    }

    @Test
    fun `fetchAccountBalances API failure`() = runTest {
        coEvery { ApiClient.getRequest("/myapp/accounts/currencies") } returns Pair(false, "Fetch error")

        viewModel = HomeDepositViewModel()
        viewModel.depositResult.observeForever(depositResultObserver)
        viewModel.fetchAccountBalances()
        advanceUntilIdle()

        verify { depositResultObserver.onChanged(match { it.isFailure && it.exceptionOrNull()?.message == "Error failed fetch balance" }) }
    }

    @Test
    fun `fetchAccountBalances parsing error`() = runTest {
        coEvery { ApiClient.getRequest("/myapp/accounts/currencies") } returns Pair(true, "Invalid JSON")

        viewModel = HomeDepositViewModel()
        viewModel.depositResult.observeForever(depositResultObserver)
        viewModel.fetchAccountBalances()
        advanceUntilIdle()

        verify { depositResultObserver.onChanged(match { it.isFailure && it.exceptionOrNull()?.message == "Error account balance" }) }
    }
}
