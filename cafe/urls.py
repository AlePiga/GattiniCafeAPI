from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', views.MeView.as_view(), name='me'),

    # Categorie
    path('categorie/', views.CategoriaListCreateView.as_view(), name='categorie-list'),
    path('categorie/<int:pk>/', views.CategoriaDetailView.as_view(), name='categorie-detail'),

    # Prodotti
    path('prodotti/', views.ProdottoListCreateView.as_view(), name='prodotti-list'),
    path('prodotti/<int:pk>/', views.ProdottoDetailView.as_view(), name='prodotti-detail'),

    # Ordini
    path('ordini/', views.OrdineListCreateView.as_view(), name='ordini-list'),
    path('ordini/<int:pk>/', views.OrdineDetailView.as_view(), name='ordini-detail'),
    path('ordini/<int:pk>/stato/', views.OrdineStatoView.as_view(), name='ordini-stato'),

    # Admin stats (bonus)
    path('admin/stats/', views.AdminStatsView.as_view(), name='admin-stats'),
]
