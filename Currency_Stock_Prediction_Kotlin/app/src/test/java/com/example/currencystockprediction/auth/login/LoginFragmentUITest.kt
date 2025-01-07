package com.example.currencystockprediction.auth.login

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.rules.activityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.AuthenticationActivity
import com.example.currencystockprediction.utils.ToastMatcher
import com.google.android.material.textfield.TextInputEditText
import com.google.firebase.FirebaseApp
import org.hamcrest.CoreMatchers.containsString
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LoginFragmentUITest {
    @get:Rule
    val activityRule = activityScenarioRule<AuthenticationActivity>()

    @Before
    fun setUpFirebase() {
        val context: Context = ApplicationProvider.getApplicationContext()
        FirebaseApp.initializeApp(context)

        activityRule.scenario.onActivity { activity ->
            activity.supportFragmentManager.beginTransaction()
                .replace(R.id.authNavHostFragment, LoginFragment())
                .commitNow()
        }
    }
    @Test
    fun testInvalidEmailFormat_showsToast() {
        onView(withId(R.id.textInputLayoutEmail))
            .check(matches(isDisplayed()))

        onView(withHint(R.string.login_fragment_input_email))
            .perform(typeText("invalid-email"), closeSoftKeyboard())
        onView(withId(R.id.loginButton))
            .perform(click())

        onView(withText(containsString("Niepoprawny format email")))
            .inRoot(ToastMatcher())
            .check(matches(isDisplayed()))
    }
}
