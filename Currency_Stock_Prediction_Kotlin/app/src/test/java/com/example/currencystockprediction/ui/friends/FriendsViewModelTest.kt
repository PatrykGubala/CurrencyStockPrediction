package com.example.currencystockprediction.ui.friends

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.Observer
import com.example.currencystockprediction.ui.data.User
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.firestore.FirebaseFirestore
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.Mock
import org.mockito.Mockito.mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever

class FriendsViewModelTest {
    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @Mock
    private lateinit var firestore: FirebaseFirestore

    @Mock
    private lateinit var auth: FirebaseAuth

    private lateinit var viewModel: FriendsViewModel

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        val mockUser = mock(FirebaseUser::class.java)
        whenever(auth.currentUser).thenReturn(mockUser)
        viewModel = FriendsViewModel(firestore, auth)
    }

    @Test
    fun testSetSearchQuery() {
        val user1 = User(null, "1", "jj@jj.com", "john", "0000", null, null, emptyList(), emptyList(), emptyList())
        val user2 = User(null, "2", "j@j.com", "johny", "0000", null, null, emptyList(), emptyList(), emptyList())

        viewModel._friends.value = listOf(user1, user2)

        val observer = Observer<List<User>> {}
        try {
            viewModel.filteredFriends.observeForever(observer)
            val query = "johny"
            viewModel.setSearchQuery(query)
            assertEquals(query, viewModel.filteredFriends.value?.get(0)?.username)
        } finally {
            viewModel.filteredFriends.removeObserver(observer)
        }
    }

    @Test
    fun testFilterFriends() {
        val user1 = User(null, "1", "jj@jj.com", "john", "0000", null, null, emptyList(), emptyList(), emptyList())
        val user2 = User(null, "2", "j@j.com", "johny", "0000", null, null, emptyList(), emptyList(), emptyList())

        viewModel._friends.value = listOf(user1, user2)

        val observer = Observer<List<User>> {}
        try {
            viewModel.filteredFriends.observeForever(observer)
            viewModel.setSearchQuery("johny")
            val filteredFriends = viewModel.filteredFriends.value
            assertEquals(1, filteredFriends?.size)
            assertEquals("johny", filteredFriends?.get(0)?.username)
        } finally {
            viewModel.filteredFriends.removeObserver(observer)
        }
    }
}
