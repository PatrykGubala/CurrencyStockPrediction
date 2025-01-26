package com.example.currencystockprediction.utils

import android.os.Process
import io.mockk.every
import io.mockk.mockkStatic

object MockProcess {
    fun setup() {
        mockkStatic(Process::class)
        every { Process.myPid() } returns 1
    }
}