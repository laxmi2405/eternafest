from django.urls import path
from . import views
from .views import user_login, user_signup, verify_otp, send_otp, admin_dashboard, delete_event, edit_event

app_name = "users"  # Important for namespace-based URL resolution

urlpatterns = [
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),  # Defines the logout URL
    path("verify_otp/", verify_otp, name="verify_otp"),
    path('send_otp/', send_otp, name='send_otp'),
    path('admin-signup/', views.admin_signup, name='admin_signup'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('edit-event/<int:id>/', edit_event, name='edit_event'),
    path('delete-event/<int:id>/', delete_event, name='delete_event'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('book_event/<int:event_id>/', views.book_event, name='book_event'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('save-event/<int:event_id>/',views.toggle_save_event,name='toggle_save_event')
]


