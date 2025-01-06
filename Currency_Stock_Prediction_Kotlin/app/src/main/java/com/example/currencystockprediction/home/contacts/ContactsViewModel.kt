package com.example.currencystockprediction.home.contacts

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.example.currencystockprediction.models.Contact

class ContactsViewModel : ViewModel() {

    private val _contacts = MutableLiveData<List<Contact>>()
    val contacts: LiveData<List<Contact>> = _contacts


    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun setContacts(newContacts: List<Contact>) {
        _contacts.value = newContacts
    }


    fun setError(message: String?) {
        _error.value = message
    }
}