from django.urls import path
from myapp.controllers.users_controller import register_user
from myapp.controllers.currency_pairs_controller import create_currency_pair, get_all_currency_pairs, get_currency_pair, delete_currency_pair
from myapp.controllers.accounts_controller import create_account
from myapp.controllers.account_currencies_controller import add_currency_to_account, get_account_currencies, update_account_currency_balance, remove_currency_from_account
from myapp.controllers.countries_controller import load_only_countries, load_countries_with_details, get_all_countries, get_country
from myapp.controllers.regions_controller import get_all_regions, get_region, load_regions, create_region, update_region, delete_region

urlpatterns = [
    path('users/register', register_user, name='register_user'),
    path('currency-pairs/create', create_currency_pair, name='create_currency_pair'),
    path('currency-pairs/', get_all_currency_pairs, name='get_all_currency_pairs'),
    path('currency-pairs/<int:pair_id>', get_currency_pair, name='get_currency_pair'),
    path('currency-pairs/<int:pair_id>/delete', delete_currency_pair, name='delete_currency_pair'),
    path('accounts/create', create_account, name='create_account'),
    path('accounts/currencies', get_account_currencies, name='get_account_currencies'),
    path('accounts/currencies/add', add_currency_to_account, name='add_currency_to_account'),
    path('accounts/currencies/<str:currency_code>/update', update_account_currency_balance, name='update_account_currency_balance'),
    path('accounts/currencies/<str:currency_code>/delete', remove_currency_from_account, name='remove_currency_from_account'),
    path('countries/load', load_only_countries, name='load_only_countries'),
    path('countries/load-all', load_countries_with_details, name='load_countries_with_details'),
    path('countries/', get_all_countries, name='get_all_countries'),
    path('countries/<str:country_code>', get_country, name='get_country'),
    path('regions/', get_all_regions, name='get_all_regions'),
    path('regions/<int:region_id>', get_region, name='get_region'),
    path('regions/load', load_regions, name='load_regions'),
    path('regions/create', create_region, name='create_region'),
    path('regions/<int:region_id>/update', update_region, name='update_region'),
    path('regions/<int:region_id>/delete', delete_region, name='delete_region'),
]