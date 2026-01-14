from django.urls import path
from . import views
urlpatterns = [
    path('stocks/', views.stock_list, name='stock_list'),
    path('truck/', views.truck_list, name='truck_list'),
    path('truck/in/', views.truck_in_add, name='truck_in'),
    # path('truck/in/list/', truck_in_list, name='truck_in_list'),
    path('truck/out/', views.truck_out_add, name='truck_out'),
    path('truck/out/list/', views.truck_out_list, name='truck_out_list'),
    path('truck/history/', views.truck_history, name='truck_history'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('', views.login_view, name='login'),
    path('quarry/', views.quarry_list, name='quarry_list'),
    path('quarry/add/', views.quarry_add, name='quarry_add'),
    path('stock/add/', views.stock_add, name='stock_add'),
    path('material/add/', views.material_add, name='material_add'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # EDITS
    
    path('quarry/edit/<int:id>/', views.edit_quarry, name='edit_quarry'),
    path('quarry/delete/<int:id>/', views.delete_quarry, name='delete_quarry'),
    path('stock/edit/<int:id>/', views.edit_stock, name='edit_stock'),
    path('stock/delete/<int:id>/', views.delete_stock, name='delete_stock'),
    path('truck-in/edit/<int:pk>/', views.truck_in_edit, name='truck_in_edit'),
    path('truck-in/delete/<int:pk>/', views.truck_in_delete, name='truck_in_delete'),
    path('truck-out/edit/<int:pk>/', views.truck_out_edit, name='truck_out_edit'),
    path('truck-out/delete/<int:pk>/', views.truck_out_delete, name='truck_out_delete'),


]
