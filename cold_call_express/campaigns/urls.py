from django.urls import path
from .views import (
    CampaignListView, CampaignCreateView, CampaignUpdateView, 
    CampaignDeleteView,CampaignDashboardView, GeneratePitchView,
    CampaignStatusUpdateView, InitiateCampaignView, ContactCreateView,
    ContactUpdateView, ContactDeleteView, CampaignDetailView, CSVUploadView
)

app_name = 'campaign'

urlpatterns = [
    path('', CampaignListView.as_view(), name='campaign_list'),
    path('create/', CampaignCreateView.as_view(), name='campaign_create'),
    path('<int:pk>/', CampaignDetailView.as_view(), name='campaign_details'),
    path('<int:pk>/update/', CampaignUpdateView.as_view(), name='campaign_update'),
    path('<int:pk>/delete/', CampaignDeleteView.as_view(), name='campaign_delete'),
    path('dashboard/', CampaignDashboardView.as_view(), name='campaign_dashboard'),
    path('generate-pitch/', GeneratePitchView.as_view(), name='generate_pitch'),
    path('<int:pk>/status/', CampaignStatusUpdateView.as_view(), name='campaign_status_update'),
    path('<int:pk>/initiate/', InitiateCampaignView.as_view(), name='campaign_initiate'),
    path('<int:campaign_pk>/contact/add/', ContactCreateView.as_view(), name='contact_create'),
    path('contact/<int:pk>/update/', ContactUpdateView.as_view(), name='contact_update'),
    path('contact/<int:pk>/delete/', ContactDeleteView.as_view(), name='contact_delete'),
    path('<int:campaign_pk>/upload-csv/', CSVUploadView.as_view(), name='csv_upload'),
]