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



    fun postRequest2(endpoint: String, json: JSONObject, callback: (Boolean, String?) -> Unit) {
        FirebaseAuthManager.firebaseAuth.currentUser?.getIdToken(false)
            ?.addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val token = task.result?.token
                    val requestBody = json.toString().toRequestBody(mediaTypeJson)

                    val requestBuilder = Request.Builder()
                        .url("$BACKEND_URL$endpoint")
                        .post(requestBody)

                    if (!token.isNullOrEmpty()) {
                        requestBuilder.addHeader("Authorization", "Bearer $token")
                    }

                    val request = requestBuilder.build()

                    client.newCall(request).enqueue(object : Callback {
                        override fun onFailure(call: Call, e: IOException) {
                            Log.e(TAG, "POST request failed: ${e.message}")
                            callback(false, "Network error: ${e.message}")
                        }

                        override fun onResponse(call: Call, response: Response) {
                            response.use {
                                if (response.isSuccessful) {
                                    val responseBody = response.body?.string()
                                    callback(true, responseBody)
                                } else {
                                    val responseBody = response.body?.string()
                                    val errorMessage = try {
                                        JSONObject(responseBody ?: "").getString("error")
                                    } catch (e: Exception) {
                                        response.message
                                    }
                                    callback(false, errorMessage)
                                }
                            }
                        }
                    })
                } else {
                    Log.e(TAG, "Failed to get Firebase token: ${task.exception?.message}")
                    callback(false, "Authentication error: ${task.exception?.message}")
                }
            }
    }

    fun getRequest2(endpoint: String, callback: (Boolean, String?) -> Unit) {
        FirebaseAuthManager.firebaseAuth.currentUser?.getIdToken(false)
            ?.addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val token = task.result?.token

                    val requestBuilder = Request.Builder()
                        .url("$BACKEND_URL$endpoint")
                        .get()

                    if (!token.isNullOrEmpty()) {
                        requestBuilder.addHeader("Authorization", "Bearer $token")
                    }

                    val request = requestBuilder.build()

                    client.newCall(request).enqueue(object : Callback {
                        override fun onFailure(call: Call, e: IOException) {
                            Log.e(TAG, "GET request failed: ${e.message}")
                            callback(false, "Network error: ${e.message}")
                        }

                        override fun onResponse(call: Call, response: Response) {
                            response.use {
                                if (response.isSuccessful) {
                                    val responseBody = response.body?.string()
                                    callback(true, responseBody)
                                } else {
                                    val responseBody = response.body?.string()
                                    val errorMessage = try {
                                        JSONObject(responseBody ?: "").getString("error")
                                    } catch (e: Exception) {
                                        response.message
                                    }
                                    callback(false, errorMessage)
                                }
                            }
                        }
                    })
                } else {
                    Log.e(TAG, "Failed to get Firebase token: ${task.exception?.message}")
                    callback(false, "Authentication error: ${task.exception?.message}")
                }
            }
    }



}
