package com.example.currencystockprediction.home.contacts

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.recyclerview.widget.RecyclerView
import com.example.currencystockprediction.R
import com.example.currencystockprediction.models.Contact

class ContactsAdapter(
    private val context: Context,
    private var contacts: List<Contact>
) : RecyclerView.Adapter<ContactsAdapter.ContactViewHolder>() {

    inner class ContactViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val titleTextView: TextView = itemView.findViewById(R.id.contactsTitle)
        val publicAccountIdTextView: TextView = itemView.findViewById(R.id.contactsAccountPublicIdTextView)
        val copyButton: ImageButton = itemView.findViewById(R.id.copyPublicAccountIdImageButton)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ContactViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.fragment_home_contacts_item, parent, false)
        return ContactViewHolder(view)
    }

    override fun getItemCount(): Int = contacts.size

    override fun onBindViewHolder(holder: ContactViewHolder, position: Int) {
        val contact = contacts[position]
        holder.titleTextView.text = contact.title
        holder.publicAccountIdTextView.text = "${contact.public_account_id}${contact.currency_code}"

        holder.copyButton.setOnClickListener {
            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = ClipData.newPlainText("Public Account ID", contact.public_account_id)
            clipboard.setPrimaryClip(clip)
            Toast.makeText(context, "Public Account ID copied to clipboard", Toast.LENGTH_SHORT).show()
        }
    }

    fun updateContacts(newContacts: List<Contact>) {
        contacts = newContacts
        notifyDataSetChanged()
    }
}