package com.example.currencystockprediction.utils

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import org.json.JSONObject
import java.io.IOException

object ApiClient {

    private const val TAG = "ApiClient"

    private const val BACKEND_URL = "https://f07d-37-31-33-59.ngrok-free.app"

    private val client: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()
    }

    private val mediaTypeJson = "application/json; charset=utf-8".toMediaType()




    suspend fun postRequest(endpoint: String, json: JSONObject): Pair<Boolean, String?> {
        return withContext(Dispatchers.IO) {
            try {
                val tokenResult = FirebaseAuthManager.firebaseAuth.currentUser?.getIdToken(false)?.await()
                val requestBody = json.toString().toRequestBody(mediaTypeJson)

                val token = tokenResult?.token

                val requestBuilder = Request.Builder()
                    .url("$BACKEND_URL$endpoint")
                    .post(requestBody)

                if (!token.isNullOrEmpty()) {
                    requestBuilder.addHeader("Authorization", "Bearer $token")
                }

                val request = requestBuilder.build()
                val response = client.newCall(request).execute()

                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    Pair(true, responseBody)
                } else {
                    val responseBody = response.body?.string()
                    val errorMessage = try {
                        JSONObject(responseBody ?: "").getString("error")
                    } catch (e: Exception) {
                        response.message
                    }
                    Pair(false, errorMessage)
                }
            } catch (e: Exception) {
                Log.e(TAG, "POST request failed: ${e.message}")
                Pair(false, "Network error: ${e.message}")
            }
        }
    }

    suspend fun getRequest(endpoint: String): Pair<Boolean, String?> {
        return withContext(Dispatchers.IO) {
            try {
                val tokenResult = FirebaseAuthManager.firebaseAuth.currentUser?.getIdToken(false)?.await()
                val token = tokenResult?.token

                val requestBuilder = Request.Builder()
                    .url("$BACKEND_URL$endpoint")
                    .get()

                if (!token.isNullOrEmpty()) {
                    requestBuilder.addHeader("Authorization", "Bearer $token")
                }

                val request = requestBuilder.build()
                val response = client.newCall(request).execute()

                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    Pair(true, responseBody)
                } else {
                    val responseBody = response.body?.string()
                    val errorMessage = try {
                        JSONObject(responseBody ?: "").getString("error")
                    } catch (e: Exception) {
                        response.message
                    }
                    Pair(false, errorMessage)
                }
            } catch (e: Exception) {
                Log.e(TAG, "GET request failed: ${e.message}")
                Pair(false, "Network error: ${e.message}")
            }
        }
    }





}
