from django.urls import path
from transactions import views

app_name="transactions"
urlpatterns = [
	path('', views.TransactionListView.as_view(), name="index"),
	path('upload/', views.UploadTransactionsFormView.as_view(), name="upload"),
	path('upload-anonymous', views.UploadAnonymousTransactionsFormView.as_view(), name="upload-anonymous")
]