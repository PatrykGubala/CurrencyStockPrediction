package com.example.currencystockprediction.home.contacts

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.currencystockprediction.R

import com.example.currencystockprediction.databinding.FragmentHomeContactsBinding
import com.example.currencystockprediction.home.contacts.ContactsAdapter
import com.example.currencystockprediction.home.contacts.ContactsViewModel
import com.example.currencystockprediction.models.Contact
import com.example.currencystockprediction.utils.ApiClient
import com.google.android.material.bottomnavigation.BottomNavigationView
import kotlinx.coroutines.launch
import org.json.JSONObject

class ContactsFragment : Fragment() {
    private var insetsController: WindowInsetsControllerCompat? = null
    private lateinit var bottomNavView: BottomNavigationView
    private var originalBottomNavVisibility: Int = View.VISIBLE


    private var _binding: FragmentHomeContactsBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: ContactsViewModel
    private lateinit var contactsAdapter: ContactsAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentHomeContactsBinding.inflate(inflater, container, false)
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

        viewModel = ViewModelProvider(this).get(ContactsViewModel::class.java)
        setupRecyclerView()
        observeViewModel()
        setupCreateContactButton()

        setupToolbar()

        fetchContacts()
    }



    private fun setupRecyclerView() {
        contactsAdapter = ContactsAdapter(requireContext(), emptyList())
        binding.contactsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        binding.contactsRecyclerView.adapter = contactsAdapter
    }

    private fun observeViewModel() {
        viewModel.contacts.observe(viewLifecycleOwner) { contacts ->
            contactsAdapter.updateContacts(contacts)
        }


        viewModel.error.observe(viewLifecycleOwner) { errorMsg ->
            errorMsg?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
                viewModel.setError(null)
            }
        }
    }

    private fun setupCreateContactButton() {
        binding.createContactVisibilityButton.setOnClickListener {
            val isVisible = binding.createContactConstraintLayout.visibility == View.VISIBLE
            binding.createContactConstraintLayout.visibility = if (isVisible) View.GONE else View.VISIBLE
        }

        binding.createContactButton.setOnClickListener {
            createContact()
        }
    }

    private fun createContact() {
        val title = binding.contactNameTextInputEditText.text.toString().trim()
        val publicAccountId = binding.contactPublicAccountIdTextInputEditText.text.toString().trim()
        val accountName = title
        val currencyCode = "USD"

        if (title.isEmpty() || publicAccountId.isEmpty() || accountName.isEmpty() || currencyCode.isEmpty()) {
            Toast.makeText(requireContext(), "Wypełnij wszystkie pola", Toast.LENGTH_SHORT).show()
            return
        }


        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val json = JSONObject()
                    .put("title", title)
                    .put("public_account_id", publicAccountId)
                    .put("account_name", accountName)
                    .put("currency_code", currencyCode)

                val (success, response) = ApiClient.postRequest("/myapp/users/contacts/create/", json)


                if (success && response != null) {
                    val jsonResponse = JSONObject(response)
                    val contactJson = jsonResponse.getJSONObject("contact")
                    val newContact = Contact(
                        id = contactJson.getInt("id"),
                        title = contactJson.getString("title"),
                        public_account_id = contactJson.getString("public_account_id"),
                        account_name = contactJson.getString("account_name"),
                        currency_code = contactJson.getString("currency_code")
                    )
                    val currentList = viewModel.contacts.value?.toMutableList() ?: mutableListOf()
                    currentList.add(newContact)
                    viewModel.setContacts(currentList)
                    clearCreateContactForm()
                    Toast.makeText(requireContext(), "Numer konta zapisany", Toast.LENGTH_SHORT).show()
                    binding.createContactConstraintLayout.visibility = View.GONE
                } else {
                    val errorMsg = response ?: "Nie udało się zapisać numeru konta"
                    Toast.makeText(requireContext(), errorMsg, Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "Error", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun clearCreateContactForm() {
        binding.contactNameTextInputEditText.text?.clear()
        binding.contactPublicAccountIdTextInputEditText.text?.clear()
    }

    private fun fetchContacts() {

        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val (success, response) = ApiClient.getRequest("/myapp/users/contacts/")

                if (success && response != null) {
                    val jsonResponse = JSONObject(response)
                    val contactsArray = jsonResponse.getJSONArray("contacts")
                    val contactsList = mutableListOf<Contact>()
                    for (i in 0 until contactsArray.length()) {
                        val contactObj = contactsArray.getJSONObject(i)
                        val contact = Contact(
                            id = contactObj.getInt("id"),
                            title = contactObj.getString("title"),
                            public_account_id = contactObj.getString("public_account_id"),
                            account_name = contactObj.getString("account_name"),
                            currency_code = contactObj.getString("currency_code")
                        )
                        contactsList.add(contact)
                    }
                    viewModel.setContacts(contactsList)
                } else {
                    val errorMsg = response ?: "ERROR"
                    Toast.makeText(requireContext(), errorMsg, Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "Error podczas pobierania danych", Toast.LENGTH_SHORT).show()
            }
        }
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
