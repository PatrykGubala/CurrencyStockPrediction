package com.example.currencystockprediction.auth.login

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.currencystockprediction.BaseFragment
import com.example.currencystockprediction.R
import com.example.currencystockprediction.activities.MainActivity
import com.example.currencystockprediction.databinding.FragmentLoginBinding
import com.example.currencystockprediction.utils.FirebaseAuthManager
import com.example.currencystockprediction.utils.SecurityUtils
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.tasks.Task
import com.google.firebase.auth.FirebaseAuthInvalidCredentialsException
import com.google.firebase.auth.FirebaseAuthInvalidUserException
import com.google.firebase.auth.GoogleAuthProvider

class LoginFragment : BaseFragment() {
    private lateinit var binding: FragmentLoginBinding
    private val fbAuth = FirebaseAuthManager.firebaseAuth
    private val LOG_DEBUG = "LOG_DEBUG"

    private lateinit var googleSignInClient: GoogleSignInClient
    private val RC_SIGN_IN = 9001

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?,
    ) {
        super.onViewCreated(view, savedInstanceState)
        setupLoginClick()
        setupGoogleSignIn()
        setupForgotPasswordClick()

        binding.backButton.setOnClickListener {
            findNavController().popBackStack(R.id.startFragment, false)
        }
    }

    private fun setupLoginClick() {
        binding.loginButton.setOnClickListener {
            val email = binding.textInputLayoutEmail.editText?.text.toString().trim()
            val pass = binding.textInputLayoutPassword.editText?.text.toString().trim()

            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                Toast.makeText(requireContext(), "Niepoprawny format email", Toast.LENGTH_SHORT)
                    .show()
                return@setOnClickListener
            }

            if (pass.isEmpty()) {
                Toast.makeText(requireContext(), "Wpisz hasło", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (pass.length < 6) {
                Toast.makeText(
                    requireContext(),
                    "Hasło musi mieć co najmniej 6 znaków",
                    Toast.LENGTH_SHORT
                ).show()
                return@setOnClickListener
            }

            binding.progressBar.visibility = View.VISIBLE
            fbAuth.signInWithEmailAndPassword(email, pass)
                .addOnSuccessListener { authRes ->
                    binding.progressBar.visibility = View.GONE
                    val credentialsSaved = SecurityUtils.saveCredentials(requireContext(), email, pass)
                    if (credentialsSaved) {
                        Log.d(LOG_DEBUG, "Credentials saved successfully.")
                    } else {
                        Log.e(LOG_DEBUG, "Failed to save credentials.")
                    }
                    startMainActivity()
                }
                .addOnFailureListener { exc ->
                    binding.progressBar.visibility = View.GONE
                    val errorMessage = when (exc) {
                        is FirebaseAuthInvalidCredentialsException -> "Niepoprawne hasło"
                        is FirebaseAuthInvalidUserException -> "Nie znaleziono użytkownika z tym adresem email"
                        else -> "Logowanie się nie powiodło"
                    }
                    Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show()
                    Log.d(LOG_DEBUG, exc.message.toString())
                }
        }
    }

    private fun setupGoogleSignIn() {
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(getString(R.string.default_web_client_id))
            .requestEmail()
            .build()

        googleSignInClient = GoogleSignIn.getClient(requireActivity(), gso)

        binding.customGoogleSignInButton.setOnClickListener {
            signInWithGoogle()
        }
    }

    private fun signInWithGoogle() {
        val signInIntent = googleSignInClient.signInIntent
        startActivityForResult(signInIntent, RC_SIGN_IN)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == RC_SIGN_IN) {
            val task: Task<GoogleSignInAccount> = GoogleSignIn.getSignedInAccountFromIntent(data)
            try {
                val account: GoogleSignInAccount = task.getResult(ApiException::class.java)!!
                Log.d(LOG_DEBUG, "firebaseAuthWithGoogle:" + account.id)
                firebaseAuthWithGoogle(account.idToken!!)
            } catch (e: ApiException) {
                Log.w(LOG_DEBUG, "Google sign in failed", e)
                Toast.makeText(requireContext(), "Google sign in failed: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun firebaseAuthWithGoogle(idToken: String) {
        val credential = GoogleAuthProvider.getCredential(idToken, null)
        binding.progressBar.visibility = View.VISIBLE
        fbAuth.signInWithCredential(credential)
            .addOnCompleteListener(requireActivity()) { task ->
                binding.progressBar.visibility = View.GONE
                if (task.isSuccessful) {
                    Log.d(LOG_DEBUG, "signInWithCredential:success")
                    val email = fbAuth.currentUser?.email
                    if (email != null) {
                        val credentialsSaved = SecurityUtils.saveCredentials(requireContext(), email, "")
                        if (credentialsSaved) {
                            Log.d(LOG_DEBUG, "Credentials saved successfully (Google).")
                        } else {
                            Log.e(LOG_DEBUG, "Failed to save credentials (Google).")
                        }
                    }
                    startMainActivity()
                } else {
                    Log.w(LOG_DEBUG, "signInWithCredential:failure", task.exception)
                    Toast.makeText(requireContext(), "Authentication Failed.", Toast.LENGTH_SHORT).show()
                }
            }
    }

    private fun setupForgotPasswordClick() {
        binding.forgotPasswordButton.setOnClickListener {
            val email = binding.textInputLayoutEmail.editText?.text.toString().trim()
            if (email.isEmpty()) {
                Toast.makeText(requireContext(), "Wpisz swój adres email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                Toast.makeText(requireContext(), "Niepoprawny format email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            binding.progressBar.visibility = View.VISIBLE
            fbAuth.sendPasswordResetEmail(email)
                .addOnCompleteListener { task ->
                    binding.progressBar.visibility = View.GONE
                    if (task.isSuccessful) {
                        Toast.makeText(requireContext(), "Email do resetu hasła został wysłany", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(requireContext(), "Nie udało się wysłać emaila do resetu hasła", Toast.LENGTH_SHORT).show()
                    }
                }
        }
    }
}
