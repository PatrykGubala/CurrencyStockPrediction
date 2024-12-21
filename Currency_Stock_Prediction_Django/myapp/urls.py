
from django.urls import path
from myapp.controllers.users_controller import register_user, get_user_by_id, get_user_info, upload_profile_image
from myapp.controllers.accounts_controller import create_account
from myapp.controllers.account_currencies_controller import add_currency_to_account, get_account_currencies, update_account_currency_balance, remove_currency_from_account
from myapp.controllers.countries_controller import load_only_countries, load_countries_with_details, get_all_countries, get_country
from myapp.controllers.regions_controller import get_all_regions, get_region, load_regions, create_region, update_region, delete_region
from myapp.controllers.currencies_controller import get_european_currencies, get_asian_currencies, get_american_currencies, get_oceanian_currencies
from myapp.controllers.currencies_data_controller import get_all_currencies_data, load_currency_data, get_latest_currency_data, get_percentage_change_for_currency

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('users/register', register_user, name='register_user'),
    path('users/get_user_by_id', get_user_by_id, name='get_user_by_id'),
    path('users/get_user_info', get_user_info, name='get_user_info'),
    path('users/upload_profile_image', upload_profile_image, name='upload_profile_image'),


    path('currencies/european/', get_european_currencies, name='get_european_currencies'),
    path('currencies/asian/', get_asian_currencies, name='get_asian_currencies'),
    path('currencies/american/', get_american_currencies, name='get_american_currencies'),
    path('currencies/oceanian/', get_oceanian_currencies, name='get_oceanian_currencies'),

    path('currencies/data', get_all_currencies_data, name='get_all_currencies_data'),
    path('currencies/data/load_currency_data', load_currency_data, name='load_currency_data'),
    path('currencies/data/<int:currency_id>/latest', get_latest_currency_data, name='get_latest_currency_data'),
    path('currencies/data/<int:currency_id>/change', get_percentage_change_for_currency, name='get_percentage_change_for_currency'),



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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)