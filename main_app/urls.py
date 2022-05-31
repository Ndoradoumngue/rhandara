from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from main_app.views import *

app_name='main_app'

urlpatterns = [
    url(r'^$', home_view, name='HomeName'),
    url(r'^a-propos/', about_us_view, name='AboutUsName'),
    url(r'^notre-equipe/', our_team_view, name='OurTeamName'),
    url(r'^gallerie/', our_gallerie_view, name='OurGalleryName'),
    url(r'^nos-domaines/', our_services_view, name='OurServicesName'),
    url(r'^domaine/(?P<service_slug>.+)/$', service_details_view, name='ServiceDetailsName'), 
    url(r'^nos-produits/', opportunities_view, name='OpportunitiesName'), 
    url(r'^produit/(?P<opportunity_slug>.+)/$', opportunity_view, name='OpportunityName'),
    url(r'^cause/(?P<cause_slug>.+)/$', cause_details_view, name='CauseDetailsName'),
    url(r'^faire-un-don/$', donate_view, name='DonateName'),
    url(r'^nos-evenements/$', events_view, name='EventsName'),
    url(r'^evenement/(?P<event_slug>.+)/$', event_details_view, name='EventDetailsName'),
    url(r'^inscription-a-un-evenement/(?P<event_slug>.+)/$', registration_to_an_event_view, name='RegistrationToAnEventName'),
    url(r'^news/$', news_view, name='NewsName'),
    url(r'^lire_news/(?P<news_slug>.+)/$', news_details_view, name='NewsDetailsName'),
    url(r'^rapport/$', report_view, name='ReportName'),
    url(r'^devenir-volontaire/$', volonteer_view, name='VolonteerName'),
    url(r'^notre-presence/$', our_countries_of_operation_view, name='OurCountriesOfOperationName'),
    url(r'^nos-partenaires/$', our_partners_view, name='OurPartnersName'),
    url(r'^contact/$', contact_view, name='ContactName'),
    url(r'^connection/$', authentification_view, name='AuthentificationName'),
    url(r'^deconnection/$', logout_view, name='LogoutName'),
    url(r'^receive_whatsapp_message/$', receive_whatsapp_message_view, name='ReceiveWhatsappMessageName'),
    url(r'^whatsapp_message_reception_status/$', whatsapp_message_reception_status_view, name='WhatsappMessageReceptionStatusName'),

    # rest urls

    # url(r'^rest_process_payment/', RestProcessPaymentClass.as_view(), name='RestProcessPaymentName'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
