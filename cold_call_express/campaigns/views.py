from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Avg
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
import json
import csv
import io

from .models import Campaign, Contact
from .forms import CampaignForm, ContactForm, CSVUploadForm
from chatbot.utils import generate_text


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'campaigns/campaign_list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        return Campaign.objects.filter(user=self.request.user)


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    success_url = reverse_lazy('campaign:campaign_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    
class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    success_url = reverse_lazy('campaign:campaign_list')


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    template_name = 'campaigns/campaign_confirm_delete.html'
    success_url = reverse_lazy('campaign:campaign_list')


class CampaignDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'campaigns/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_campaigns = Campaign.objects.filter(user=self.request.user)
        context['total_campaigns'] = user_campaigns.count()
        context['total_interactions'] = user_campaigns.aggregate(Sum('chatbot_interactions'))['chatbot_interactions__sum'] or 0
        context['average_conversion_rate'] = user_campaigns.aggregate(Avg('conversion_rate'))['conversion_rate__avg'] or 0
        context['average_interaction_duration'] = user_campaigns.aggregate(Avg('average_interaction_duration'))['average_interaction_duration__avg']
        context['recent_campaigns'] = user_campaigns.order_by('-created_at')[:5]
        return context
    

class GeneratePitchView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        company_details = data.get('company_details', '')
        product_service = data.get('product_service', '')
        marketing_keywords = data.get('marketing_keywords', '')
        print(company_details, product_service, marketing_keywords)
        # Here you would make a call to your AI API
        # For now, we'll just return a placeholder response
        print('Generating pitch...')
        response = generate_text(company_details, product_service, marketing_keywords)
        print('Pitch generated:', response)
        return JsonResponse({'pitch': response.replace("\n", " ").strip()})
    

class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = 'campaigns/campaign_details.html'
    context_object_name = 'campaign'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = self.object.contacts.all()
        context['contact_form'] = ContactForm()
        context['csv_upload_form'] = CSVUploadForm()
        return context


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'campaigns/contact_form.html'

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        form.instance.campaign = campaign
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('campaign:campaign_details', kwargs={'pk': self.kwargs['campaign_pk']})


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'campaigns/contact_form.html'

    def get_success_url(self):
        return reverse_lazy('campaign:campaign_details', kwargs={'pk': self.object.campaign.pk})


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'campaigns/contact_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('campaign:campaign_details', kwargs={'pk': self.object.campaign.pk})


class CampaignStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Campaign.STATUS_CHOICES):
            campaign.status = new_status
            campaign.save()
            return JsonResponse({'status': 'success', 'new_status': new_status})
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)


class InitiateCampaignView(LoginRequiredMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.status == 'draft' and campaign.starting_pitch and campaign.contacts.exists():
            campaign.status = 'in_progress'
            campaign.save()
            # Here you would integrate with Twilio API to initiate calls
            return JsonResponse({'status': 'success', 'message': 'Campaign initiated'})
        return JsonResponse({'status': 'error', 'message': 'Unable to initiate campaign'}, status=400)
    

class CSVUploadView(LoginRequiredMixin, FormView):
    form_class = CSVUploadForm
    template_name = 'campaigns/csv_upload.html'

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        csv_file = form.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(self.request, 'File is not CSV type')
            return super().form_invalid(form)
        
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        required_columns = ['name', 'phone_number', 'email', 'age', 'gender', 'location']
        if not all(column in reader.fieldnames for column in required_columns):
            messages.error(self.request, 'CSV file does not have all required columns')
            return super().form_invalid(form)
        
        for row in reader:
            Contact.objects.create(
                campaign=campaign,
                name=row['name'],
                phone_number=row['phone_number'],
                email=row['email'],
                age=row['age'] if row['age'] else None,
                gender=row['gender'],
                location=row['location']
            )
        
        messages.success(self.request, 'Contacts uploaded successfully')
        return redirect('campaign:campaign_details', pk=campaign.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error uploading the CSV file')
        return super().form_invalid(form)