from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from authentication import views 
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register_user, name='register_user'),
    path('users/', views.users, name='users'),
    path('add-payment/<str:username>/', views.add_payment, name='add_payment'),
    path('home/', views.home, name='home'),
    path('add_payment/', views.add_payment, name='add_payment'),
    path('payment_table/', views.payment_table, name='payment_table'),
    path('delete_user/<str:username>/', views.delete_user, name='delete_user'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('payment_list/', views.payment_list, name='payment_list'),
    path('no_data/', views.no_data, name='no_data'),
    path('logout/', views.logout_view, name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
