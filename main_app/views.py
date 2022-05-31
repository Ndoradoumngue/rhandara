# -*- coding: utf-8 -*-

import os
import sys
import logging
import mimetypes
import requests
import re
import html
from django.core.mail import send_mail
from twilio.rest import Client, TwilioRestClient
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.conf import settings
from django.db.models import Count, Sum, Q, F
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
# from django.core.urlresolvers import resolve, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import resolve, reverse
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta, time
from .functions import *
from .models import *

# home

def home_view(request):

	today = datetime.now().date()

	on_home_page = 'active-link'
	title = 'Bienvenu chez Rhandara'

	page_keywords = "Rhandara, livraison, ecommerce"
	
	page_description = "Rhandara est une plate-forme qui permet aux utilisateurs d'obtenir des services rapides et fiables autour d'eux. En utilisant les systèmes de communication existants, comme WhatsApp, la plate-forme permet aux vendeurs de vendre sans tracas et aux clients d'obtenir des services de qualité à proximité grâce à la géolocalisation."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	our_team = SystemUser.objects.all().filter(is_employee=True).order_by('employee_ranking')
	our_partners_list = OurPartners.objects.all().filter(active=True)

	newsletter_email = request.POST.get('newsletterEmail', None)

	if newsletter_email == None or newsletter_email == '':
		pass
	else:
		check_new_newsletter_user = SystemUser.objects.filter(email=newsletter_email).count()
		if check_new_newsletter_user != 0:
			SystemUser.objects.filter(email=newsletter_email).update(registered_for_newsletter=True)
			messages.success(request, "Vous êtes inscrits a notre newsletter!")
		else:
			SystemUser.objects.create(first_name='newsletter user', email=newsletter_email, registered_for_newsletter=True)

			messages.success(request, "Vous êtes déjà inscrits a notre newsletter!")

		return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))

	home_context = {

		'title': title,
		'onHomePage': on_home_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'ourTeam': our_team,
		'ourPartnersList': our_partners_list,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name
	}
	return render(request, 'main_app/home.html', home_context)


# about us

def about_us_view(request):

	today = datetime.now().date()

	on_about_page = 'active-link'
	title = 'Amasot - Tchad | A PROPOS'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()
	testimonies_list = Testimony.objects.all().order_by('-id')

	about_us_context = {

		'title': title,
		'onAboutPage': on_about_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'companyDetails': company_details,
		'testimoniesList': testimonies_list,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/about_us.html', about_us_context)


# our services

def our_services_view(request):

	today = datetime.now()

	on_our_services_page = 'active-link'
	title = 'Amasot - Tchad | Nos Domaines'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Nos événéments"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Participez a nos événéments."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	get_our_services_list = OurService.objects.all().filter(active=True)
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	paginator = Paginator(get_our_services_list, 9)
	page = request.GET.get('page')
	try:
		our_services_list = paginator.page(page)
	except PageNotAnInteger:
		our_services_list = paginator.page(1)
	except EmptyPage:
		our_services_list = paginator.page(paginator.num_pages)
	
	our_services_context = {

		'title': title,
		'onOurServicesPage': on_our_services_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'ourServicesList': our_services_list,
		'ourServicesListFirstRow': our_services_list[:3],
		'ourServicesListSecondRow': our_services_list[3:6],
		'ourServicesListThirdRow': our_services_list[6:9],
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/our_services.html', our_services_context)


# service details view

def service_details_view(request, service_slug):

	today = datetime.now().date()

	on_our_services_page = 'active-link'
	title = 'Amasot - Tchad | Cause'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	company_details = CompanyDetails.objects.all()
	check_service = OurService.objects.filter(slug=service_slug).count()
	if check_service == 0:
		messages.error(request, "Désolé, nous n'avons pas trouvé le service que vous avez demandé!")

		return HttpResponseRedirect(reverse('mainAppNamespace:OurServicesName'))
	else:
		requested_service = OurService.objects.all().filter(slug=service_slug)
		# for requested_service_data in requested_service:
		# 	cause_category_slug = requested_service_data.linked_to_gallery_category.slug

		# 	cause_category_instance = GalleryCategory.objects.get(slug=cause_category_slug)

		# cause_images_gallery = Gallery.objects.all().filter(category=cause_category_instance)
		
		service_details_context = {

			'title': title,
			'requestedService': requested_service,
			'onOurServicesPage': on_our_services_page,
			'pageKeywords': page_keywords,
			'pageDescription': page_description,
			'companyDetails': company_details,
			'user_is_logged': user_is_logged,
			'user_is_employee': user_is_employee,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
			'user_is_admin': user_is_admin,
			'can_admnistrate': can_admnistrate,
			'logged_user_slug': logged_user_slug,
			'logged_user_last_name': logged_user_last_name		
		}
		return render(request, 'main_app/service_details.html', service_details_context)


# opportunities view

def opportunities_view(request):

	today = datetime.now()

	on_opportunities_page = 'active-link'
	title = 'Amasot - Tchad | Opportunites'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Nos événéments"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Participez a nos événéments."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	get_our_product_list = OurProduct.objects.all().filter(active=True)
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	paginator = Paginator(get_our_product_list, 9)
	page = request.GET.get('page')
	try:
		our_product_list = paginator.page(page)
	except PageNotAnInteger:
		our_product_list = paginator.page(1)
	except EmptyPage:
		our_product_list = paginator.page(paginator.num_pages)
	
	opportunities_context = {

		'title': title,
		'ourProductList': our_product_list,
		'onOpportunitiesPage': on_opportunities_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/opportunities.html', opportunities_context)


# opportunity details

def opportunity_view(request, opportunity_slug):

	today = datetime.now().date()

	on_opportunities_page = 'active-link'
	title = 'Amasot - Tchad | Cause'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	current_url = request.META.get('HTTP_HOST')+''+request.META.get('PATH_INFO') 
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	company_details = CompanyDetails.objects.all()
	check_product = OurProduct.objects.filter(slug=opportunity_slug).count()
	if check_product == 0:
		messages.error(request, "Désolé, nous n'avons pas trouvé l'opportunité!")

		return HttpResponseRedirect(reverse('mainAppNamespace:OpportunitiesName'))
	else:
		product_details = OurProduct.objects.all().filter(slug=opportunity_slug)
		
		opportunity_context = {

			'title': title,
			'currentURL': current_url,
			'onOpportunitiesPage': on_opportunities_page,
			'productDetails': product_details,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
			'pageKeywords': page_keywords,
			'pageDescription': page_description,
			'companyDetails': company_details,
			'user_is_logged': user_is_logged,
			'user_is_employee': user_is_employee,
			'user_is_admin': user_is_admin,
			'can_admnistrate': can_admnistrate,
			'logged_user_slug': logged_user_slug,
			'logged_user_last_name': logged_user_last_name		
		}
		return render(request, 'main_app/opportunity.html', opportunity_context)


# our team

def our_team_view(request):

	today = datetime.now().date()

	on_about_page = 'active-link'
	title = 'Amasot - Tchad | Notre Equipe'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	our_team = SystemUser.objects.all().filter(is_employee=True)
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	our_team_context = {

		'title': title,
		'ourTeam': our_team,
		'onAboutPage': on_about_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/our_team.html', our_team_context)


# our gallery

def our_gallerie_view(request):

	today = datetime.now().date()

	on_about_page = 'active-link'
	title = 'Amasot - Tchad | Gallerie'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	our_gallery_category = GalleryCategory.objects.all().filter(active=True)
	our_gallery = Gallery.objects.all().filter(active=True)
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()
	
	our_gallerie_context = {

		'title': title,
		'ourGallery': our_gallery,
		'ourGalleryCategory': our_gallery_category,
		'onAboutPage': on_about_page,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/our_gallerie.html', our_gallerie_context)


# cause details

def cause_details_view(request, cause_slug):

	today = datetime.now().date()

	on_cause_page = 'active-link'
	title = 'Amasot - Tchad | Cause'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()
	check_cause = OurCause.objects.filter(slug=cause_slug).count()
	if check_cause == 0:
		messages.error(request, "Désolé, nous n'avons pas trouvé la cause que vous avez demandée!")

		return HttpResponseRedirect(reverse('mainAppNamespace:OurCausesName'))
	else:
		our_cause = OurCause.objects.all().filter(slug=cause_slug)
		for cause_data in our_cause:
			cause_category_slug = cause_data.linked_to_gallery_category.slug

			cause_category_instance = GalleryCategory.objects.get(slug=cause_category_slug)

		cause_images_gallery = Gallery.objects.all().filter(category=cause_category_instance)
		
		cause_details_context = {

			'title': title,
			'ourCause': our_cause,
			'onCausePage': on_cause_page,
			'pageKeywords': page_keywords,
			'causeImagesGallery': cause_images_gallery,
			'pageDescription': page_description,
			'companyDetails': company_details,
			'user_is_logged': user_is_logged,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
			'user_is_employee': user_is_employee,
			'user_is_admin': user_is_admin,
			'can_admnistrate': can_admnistrate,
			'logged_user_slug': logged_user_slug,
			'logged_user_last_name': logged_user_last_name		
		}
		return render(request, 'main_app/cause_details.html', cause_details_context)


# donate view

def donate_view(request):

	today = datetime.now().date()

	on_about_page = 'active-link'
	title = 'Amasot - Tchad | Faire un don'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Faire un don a Amasot"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Faites un don pour soutenir nos activités."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	cause_to_fund = request.GET.get('cause', None)
	if cause_to_fund == None or cause_to_fund == '':
		our_cause = OurCause.objects.all().filter(active=True)
		cause_selected = 'false'
	else:
		check_cause = OurCause.objects.filter(slug=cause_to_fund).count()
		if check_cause == 0:
			our_cause = OurCause.objects.all().filter(active=True)
			cause_selected = 'false'
		else:
			cause_selected = 'true'
			our_cause = OurCause.objects.all().filter(slug=cause_to_fund)

	email = request.POST.get('email', None)
	if email == None or email == '':
		pass
	else:
		first_name = request.POST.get('first_name', None)
		last_name = request.POST.get('last_name', None)
		tel = request.POST.get('tel', None)
		cause = request.POST.get('cause', None)
		message = request.POST.get('message', None)

		if cause_selected == 'true':
			selected_cause_instance = OurCause.objects.get(slug=cause_to_fund)
		else:
			check_form_sent_cause = OurCause.objects.filter(slug=cause).count()
			if check_form_sent_cause == 0:
				selected_cause_instance = None
			else:
				selected_cause_instance = OurCause.objects.get(slug=cause)

		Message.objects.create(cause=selected_cause_instance, from_user_first_name=first_name, from_user_last_name=last_name, from_user_email=email, from_user_tel=tel, message=message)

		messages.success(request, "Demande envoyé! Merci de votre interêt!")

		return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))
	
	donate_context = {

		'title': title,
		'ourCause': our_cause,
		'causeSelected': cause_selected,
		'onAboutPage': on_about_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/donate.html', donate_context)


# our causes

def events_view(request):

	today = datetime.now()

	on_event_page = 'active-link'
	title = 'Amasot - Tchad | Evenement'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Nos événéments"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Participez a nos événéments."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	# deactivate passed events

	get_current_upcoming_events = Event.objects.all().filter(upcoming=True)
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	for current_upcoming_events_data in get_current_upcoming_events:
		upcoming_events_slug = current_upcoming_events_data.slug
		validity_date = current_upcoming_events_data.from_datetime

		formatted_today = datetime.strptime(str(today)[:19], '%Y-%m-%d %H:%M:%S')
		formatted_validity_date = datetime.strptime(str(validity_date)[:19], '%Y-%m-%d %H:%M:%S')

		if formatted_validity_date < formatted_today:
			Event.objects.filter(slug=upcoming_events_slug).update(upcoming=False)

	company_details = CompanyDetails.objects.all()
	upcoming_events = Event.objects.all().filter(upcoming=True).order_by('?')[:4]
	recent_events = Event.objects.all().filter(upcoming=False).order_by('-id')[:4]
	our_cause = OurCause.objects.all().filter(active=True)

	cause = request.GET.get('cause', None)
	if cause == None or cause == '':
		events_title = "Tous nos événements"
		get_events_list = Event.objects.all().order_by('-id')
	else:
		check_cause = OurCause.objects.filter(slug=cause).count()
		if check_cause == 0:
			events_title = "Tous nos événements"
			get_events_list = Event.objects.all().order_by('-id')
		else:
			get_cause_data = OurCause.objects.all().filter(slug=cause)
			for cause_data in get_cause_data:
				events_title = cause_data.title

			cause_instance = OurCause.objects.get(slug=cause)
			get_events_list = Event.objects.all().filter(cause=cause_instance).order_by('-id')

	paginator = Paginator(get_events_list, 5)
	page = request.GET.get('page')
	try:
		events_list = paginator.page(page)
	except PageNotAnInteger:
		events_list = paginator.page(1)
	except EmptyPage:
		events_list = paginator.page(paginator.num_pages)
	
	events_context = {

		'title': title,
		'eventsTitle': events_title,
		'ourcause': our_cause,
		'eventsList': events_list,
		'recentEvents': recent_events,
		'upcomingEvents': upcoming_events,
		'onEventPage': on_event_page,
		'pageKeywords': page_keywords,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/events.html', events_context)


# event details

def event_details_view(request, event_slug):

	today = datetime.now()

	on_event_page = 'active-link'
	title = 'Amasot - Tchad | Evenement'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	upcoming_events = Event.objects.all().filter(upcoming=True).order_by('?')[:4]
	recent_events = Event.objects.all().filter(upcoming=False).order_by('-id')[:4]
	our_cause = OurCause.objects.all().filter(active=True)
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	company_details = CompanyDetails.objects.all()
	check_event = Event.objects.filter(slug=event_slug).count()

	if check_event == 0:
		messages.error(request, "Désolé, nous n'avons pas trouvé l'événement que vous avez demandée!")

		return HttpResponseRedirect(reverse('mainAppNamespace:EventsName'))
	else:
		event_data = Event.objects.all().filter(slug=event_slug)
		event_instance = Event.objects.get(slug=event_slug)

		number_of_registered_participants = EventParticipant.objects.filter(event=event_instance).count()
		number_of_event_comments = EventComment.objects.filter(event=event_instance).count()

		event_comments = EventComment.objects.all().filter(event=event_instance)

		comment = request.POST.get('comment', None)
		if comment == None or comment == '':
			pass
		else:
			if user_is_logged == 'true':
				logged_user_instance = SystemUser.objects.get(slug=logged_user_slug)
				EventComment.objects.create(event=event_instance, commented_by=logged_user_instance, comment=comment)

				messages.success(request, "Commentaire posté!")
				return HttpResponseRedirect(reverse('mainAppNamespace:EventDetailsName', kwargs={'event_slug': event_slug}))
			else:
				messages.error(request, "Veuillez vous connecter pour commenter cet événement!")
				return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))

		for the_event_data in event_data:
			upcoming_events_slug = the_event_data.slug
			validity_date = the_event_data.from_datetime

		formatted_today = datetime.strptime(str(today)[:19], '%Y-%m-%d %H:%M:%S')
		formatted_validity_date = datetime.strptime(str(validity_date)[:19], '%Y-%m-%d %H:%M:%S')

		if formatted_validity_date < formatted_today:
			passed = 'true'
			days = ''
			hours = ''
			minutes = ''
		else:			
			result_code, duration_in_hours, message = get_duration_in_hours(today, validity_date)
			if result_code == '0':
				passed = 'true'

				days = ''
				hours = ''
				minutes = ''
			else:
				passed = 'false'

				number_of_days = float(duration_in_hours)/24

				days = int(str(number_of_days).split(".")[0])

				remaining_days_float = float(number_of_days)-days
				remaining_hours_float = remaining_days_float*24

				hours = int(str(remaining_hours_float).split(".")[0])

				minutes = int(remaining_hours_float-hours)
		
		event_details_context = {

			'title': title,
			'eventPassed': passed,
			'eventData': event_data,
			'onEventPage': on_event_page,
			'pageKeywords': page_keywords,
			'recentEvents': recent_events,
			'upcomingEvents': upcoming_events,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
			'ourCause': our_cause,
			'daysToEvent': days,
			'hoursToEvent': hours,
			'minutesToEvent': minutes,
			'eventComments': event_comments,
			'pageDescription': page_description,
			'companyDetails': company_details,
			'user_is_logged': user_is_logged,
			'user_is_employee': user_is_employee,
			'user_is_admin': user_is_admin,
			'can_admnistrate': can_admnistrate,
			'logged_user_slug': logged_user_slug,
			'logged_user_last_name': logged_user_last_name,
			'numberOfEventComments': number_of_event_comments,
			'numberOfRegisteredParticipants': number_of_registered_participants	
		}
		return render(request, 'main_app/event_details.html', event_details_context)



# register to an event

def registration_to_an_event_view(request, event_slug):

	today = datetime.now()

	on_event_page = 'active-link'
	title = 'Amasot - Tchad | Evenement'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	check_event = Event.objects.filter(slug=event_slug).count()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	if check_event == 0:
		messages.error(request, "Désolé, nous n'avons pas trouvé l'événement que vous avez demandée!")

		return HttpResponseRedirect(reverse('mainAppNamespace:EventsName'))
	else:
		event_data = Event.objects.all().filter(slug=event_slug)
		event_instance = Event.objects.get(slug=event_slug)

		for the_event_data in event_data:
			upcoming_events_slug = the_event_data.slug
			validity_date = the_event_data.from_datetime
			event_seats_limit = the_event_data.seats_limit

		number_of_registered_participants = EventParticipant.objects.filter(event=event_instance).count()
		new_number_of_registered_participants = number_of_registered_participants+1

		formatted_today = datetime.strptime(str(today)[:19], '%Y-%m-%d %H:%M:%S')
		formatted_validity_date = datetime.strptime(str(validity_date)[:19], '%Y-%m-%d %H:%M:%S')

		if formatted_validity_date < formatted_today:
			messages.error(request, "Désolé, cet événement est deja passé!")

			return HttpResponseRedirect(reverse('mainAppNamespace:EventsName'))
		else:
			message = request.POST.get('message', None)
			if message == None or message == '':
				pass
			else:
				if user_is_logged == 'true':
					logged_user_instance = SystemUser.objects.get(slug=logged_user_slug)

					if event_seats_limit < new_number_of_registered_participants or event_seats_limit == new_number_of_registered_participants:

						EventParticipantWaitingList.objects.create(event=event_instance, participant=logged_user_instance, message=message)

						messages.error(request, "Désolé, nous avons atteint la limite des inscrits pour cet événement. Nous vous avons inscrit sur la liste d'attente dans le cas ou une place se libere. Merci.!")
						return HttpResponseRedirect(reverse('mainAppNamespace:EventsName'))
					else:
						EventParticipant.objects.create(event=event_instance, participant=logged_user_instance, message=message)

						messages.success(request, "Inscription reussie!")
						return HttpResponseRedirect(reverse('mainAppNamespace:EventsName'))
				else:
					messages.error(request, "Veuillez vous connecter pour vous inscrire a cet événement!")
					return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))			
			
			registration_to_an_event_context = {

				'title': title,
				'eventData': event_data,
				'onEventPage': on_event_page,
				'pageKeywords': page_keywords,
				'pageDescription': page_description,
				'companyDetails': company_details,
				'user_is_logged': user_is_logged,
				'user_is_employee': user_is_employee,
				'user_is_admin': user_is_admin,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
				'can_admnistrate': can_admnistrate,
				'logged_user_slug': logged_user_slug,
				'logged_user_last_name': logged_user_last_name
			}
			return render(request, 'main_app/registration_to_an_event.html', registration_to_an_event_context)

# news

def news_view(request):

	today = datetime.now()

	on_news_page = 'active-link'
	title = 'Amasot - Tchad | News'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Nos événéments"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Participez a nos événéments."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	get_news_list = News.objects.all().order_by('-id')

	paginator = Paginator(get_news_list, 6)
	page = request.GET.get('page')
	try:
		news_list = paginator.page(page)
	except PageNotAnInteger:
		news_list = paginator.page(1)
	except EmptyPage:
		news_list = paginator.page(paginator.num_pages)
	
	news_context = {

		'title': title,
		'newsList': news_list,
		'onNewsPage': on_news_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/news.html', news_context)


# news details

def news_details_view(request, news_slug):

	today = datetime.now()

	on_news_page = 'active-link'
	title = 'Amasot - Tchad | Evenement'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()

	check_news = News.objects.filter(slug=news_slug).count()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	if check_news == 0:
		messages.error(request, "Désolé, nous n'avons pas trouvé le news que vous avez demandée!")

		return HttpResponseRedirect(reverse('mainAppNamespace:NewsName'))
	else:
		ten_recent_news_list = News.objects.all().order_by('-id')[:10]

		news_data = News.objects.all().filter(slug=news_slug)
		news_instance = News.objects.get(slug=news_slug)

		for the_news_data in news_data:
			number_of_news_comments = the_news_data.number_of_comments

		news_comments = NewsComment.objects.all().filter(news=news_instance)

		comment = request.POST.get('comment', None)
		if comment == None or comment == '':
			pass
		else:
			if user_is_logged == 'true':
				logged_user_instance = SystemUser.objects.get(slug=logged_user_slug)
				NewsComment.objects.create(news=news_instance, commented_by=logged_user_instance, comment=comment)

				new_number_of_news_comments = number_of_news_comments+1

				News.objects.filter(slug=news_slug).update(number_of_comments=new_number_of_news_comments)

				messages.success(request, "Commentaire posté!")
				return HttpResponseRedirect(reverse('mainAppNamespace:NewsDetailsName', kwargs={'news_slug': news_slug}))
			else:
				messages.error(request, "Veuillez vous connecter pour commenter ce news!")
				return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))

		news_details_context = {

			'title': title,
			'onNewsPage': on_news_page,
			'pageKeywords': page_keywords,
			'newsData': news_data,
			'newsComments': news_comments,
			'pageDescription': page_description,
			'companyDetails': company_details,
			'user_is_logged': user_is_logged,
			'user_is_employee': user_is_employee,
			'breakingNews': breaking_news,
			'breakingNewsCheck': breaking_news_check,
			'user_is_admin': user_is_admin,
			'can_admnistrate': can_admnistrate,
			'logged_user_slug': logged_user_slug,
			'logged_user_last_name': logged_user_last_name
		}
		return render(request, 'main_app/news_details.html', news_details_context)



# report

def report_view(request):

	today = datetime.now()

	on_report_page = 'active-link'
	title = 'Amasot - Tchad | Rapports'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Nos événéments"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Participez a nos événéments."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	get_reports_list = Rapport.objects.all().order_by('-id')

	paginator = Paginator(get_reports_list, 6)
	page = request.GET.get('page')
	try:
		reports_list = paginator.page(page)
	except PageNotAnInteger:
		reports_list = paginator.page(1)
	except EmptyPage:
		reports_list = paginator.page(paginator.num_pages)
	
	report_context = {

		'title': title,
		'reportsList': reports_list,
		'onReportPage': on_report_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/report.html', report_context)



# volonteer view

def volonteer_view(request):

	today = datetime.now().date()
	
	title = 'Amasot - Tchad | Devenir Volontaire'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Faire un don a Amasot"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Faites un don pour soutenir nos activités."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	expertise = request.POST.get('expertise', None)
	if expertise == None or expertise == '':
		pass
	else:
		if user_is_logged == 'true':

			message = request.POST.get('message', None)

			logged_user_instance = SystemUser.objects.get(slug=logged_user_slug)

			VolonteerRequest.objects.create(volonteer=logged_user_instance, expertise=expertise, message=message)
			messages.success(request, "Demade evoyée!")

			return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))
		else:
			messages.error(request, "Veuillez vous connecter pour envoyer votre demande!")
			return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))
	
	volonteer_context = {

		'title': title,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/volonteer.html', volonteer_context)


# our country of operation view

def our_countries_of_operation_view(request):

	today = datetime.now().date()
	
	title = 'Amasot - Tchad | Notre Presence'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Faire un don a Amasot"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Faites un don pour soutenir nos activités."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	our_country_of_operations = Country.objects.all().filter(is_our_country_of_operation=True)
	number_of_our_countries_of_operation = Country.objects.filter(is_our_country_of_operation=True).count()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	our_countries_of_operation_context = {

		'title': title,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
		'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'logged_user_last_name': logged_user_last_name,
		'ourCountryOfOperations': our_country_of_operations,
		'numberOfOurCountriesOfOperation': number_of_our_countries_of_operation
	}
	return render(request, 'main_app/our_countries_of_operation.html', our_countries_of_operation_context)



# our partners view

def our_partners_view(request):

	today = datetime.now().date()
	
	title = 'Amasot - Tchad | Nos Partenaires'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Faire un don a Amasot"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Faites un don pour soutenir nos activités."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	list_of_our_partners = OurPartners.objects.all().filter(active=True)
	number_of_our_partners = OurPartners.objects.filter(active=True).count()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	our_partners_context = {

		'title': title,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'logged_user_slug': logged_user_slug,
		'logged_user_last_name': logged_user_last_name,
		'listOfOurPartners': list_of_our_partners,
		'numberOfOurPartners': number_of_our_partners
	}
	return render(request, 'main_app/our_partners.html', our_partners_context)


# contact view

def contact_view(request):

	today = datetime.now().date()

	on_contact_page = 'active-link'	
	title = 'Amasot - Tchad | Contact'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme, Faire un don a Amasot"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux. Faites un don pour soutenir nos activités."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	company_details = CompanyDetails.objects.all()
	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	full_name = request.POST.get('full_name', None)
	if full_name == None or full_name == '':
		pass
	else:
		subject = request.POST.get('subject', None)
		email = request.POST.get('email', None)
		tel = request.POST.get('phone', None)
		message = request.POST.get('message', None)

		Message.objects.create(full_name=full_name, email=email, tel=tel, subject=subject, message=message)

		messages.success(request, "Message evoyée!")
		return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))

	contact_context = {

		'title': title,
		'onContactPage': on_contact_page,
		'pageKeywords': page_keywords,
		'pageDescription': page_description,
		'companyDetails': company_details,
		'user_is_logged': user_is_logged,
		'user_is_employee': user_is_employee,
		'user_is_admin': user_is_admin,
		'can_admnistrate': can_admnistrate,
		'logged_user_slug': logged_user_slug,
			'breakingNews': breaking_news,
		'breakingNewsCheck': breaking_news_check,
		'logged_user_last_name': logged_user_last_name		
	}
	return render(request, 'main_app/contact.html', contact_context)


# authentification

def authentification_view(request):

	today = datetime.now().date()

	title = 'Amasot - Tchad | Connection'

	page_keywords = "Amasot, Amasot, tresses en France, Améliorer les conditions de vie des femmes, \
					Améliorer les conditions de vie d'une femme"
	
	page_description = "L'Amasot est une association à vocation de développement intégral de la société. Elle est née des analyses de la \
						situation de la femme, de l’homme et du rapport qui existe entre les deux."	

	user_is_logged = request.session.get('user_is_logged')
	user_is_admin = request.session.get('user_is_admin')
	can_admnistrate = request.session.get('can_admnistrate')
	user_is_employee = request.session.get('user_is_employee')
	logged_user_slug = request.session.get('logged_user_slug')
	logged_user_last_name = request.session.get('logged_user_last_name')

	breaking_news = News.objects.filter(is_breaking_news=True)	
	breaking_news_check = News.objects.filter(is_breaking_news=True).count()

	if user_is_logged == 'true':
		messages.warning(request, "Vous êtes connecté!")
		return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))
	else:
		company_details = CompanyDetails.objects.all()

		login_email = request.POST.get('loginEmail', None)
		if login_email == None or login_email == '':
			pass
		else:
			login_password = request.POST.get('loginPassword', None)

			hashed_login_password = hash_password_function(login_password)

			check_user_to_login = SystemUser.objects.filter(email=login_email, password=hashed_login_password).count()
			if check_user_to_login == 0:
				messages.error(request, "Erreur de connection. Veuillez vérifier vos identifier pour continuer!")
				return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))
			else:
				get_logged_user_data = SystemUser.objects.all().filter(email=login_email, password=hashed_login_password)
				for logged_user_data in get_logged_user_data:

					request.session['user_is_logged'] = 'true'
					request.session['logged_user_slug'] = logged_user_data.slug
					request.session['logged_user_email'] = logged_user_data.email
					request.session['logged_user_last_name'] = logged_user_data.last_name
					request.session['logged_user_first_name'] = logged_user_data.first_name

					if logged_user_data.is_admin == True:
						request.session['user_is_admin'] = 'true'
					else:
						request.session['user_is_admin'] = 'false'

					if logged_user_data.is_employee == True:
						request.session['user_is_employee'] = 'true'
					else:
						request.session['user_is_employee'] = 'false'

				messages.success(request, "Connection reussie. Bienvenu check Amasot!")
				return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))


		email_to_register = request.POST.get('registerEmail', None)
		if email_to_register == None or email_to_register == '':
			pass
		else:
			tel_to_register = request.POST.get('tel', None)

			check_user = SystemUser.objects.filter(Q(email=email_to_register) | Q(tel1=tel_to_register)).count()
			if check_user != 0:
				messages.warning(request, "Vous êtes inscrits. Veuillez vous connecter!")
				return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))
			else:
				first_name_to_register = request.POST.get('firstName', None)
				last_name_to_register = request.POST.get('lastName', None)			
				password_to_register = request.POST.get('password', None)
				password_to_register_confirmation = request.POST.get('passwordConfirmation', None)

				if password_to_register != password_to_register_confirmation:
					messages.warning(request, "Les deux mot de passes ne se correspondent pas. Veuillez vérifier votre mot de passe et continuer!")
					return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))
				else:
					hashed_registration_password = hash_password_function(password_to_register)
					SystemUser.objects.create(first_name=first_name_to_register, last_name=last_name_to_register, email=email_to_register, tel1=tel_to_register, password=hashed_registration_password)
					
					messages.success(request, "Inscription reussie! Veuillez vous connecter!")
					return HttpResponseRedirect(reverse('mainAppNamespace:AuthentificationName'))

		authentification_context = {

			'title': title,
			'pageKeywords': page_keywords,
			'pageDescription': page_description,
			'companyDetails': company_details,
			'user_is_logged': user_is_logged,
			'user_is_employee': user_is_employee,
			'user_is_admin': user_is_admin,
			'can_admnistrate': can_admnistrate,
			'logged_user_slug': logged_user_slug,
			'breakingNews': breaking_news,
			'breakingNewsCheck': breaking_news_check,
			'logged_user_last_name': logged_user_last_name		
		}
		return render(request, 'main_app/authentification.html', authentification_context)


# logout view

def logout_view(request):
	user_is_logged = request.session.get('user_is_logged')
	if user_is_logged != 'true':
		messages.success(request, "Vous vous êtes déconnecté avec succès!")
		return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))
	else:
		del request.session['user_is_logged']
		del request.session['logged_user_slug']
		del request.session['logged_user_email']
		del request.session['logged_user_last_name']
		del request.session['logged_user_first_name']
		del request.session['user_is_admin']
		del request.session['user_is_employee']

	messages.success(request, "Vous vous êtes déconnecté avec succès!")
	return HttpResponseRedirect(reverse('mainAppNamespace:HomeName'))


# receive twilio whatsapp message view

@csrf_exempt
def receive_whatsapp_message_view(request):

	today = datetime.now()

	current_url = request.META.get('HTTP_HOST')

	get_company_details = CompanyDetails.objects.all()
	for company_data in get_company_details:
		company_tel = company_data.tel1
		company_email = company_data.email
		company_name = company_data.company_name
		list_of_registered_areas = company_data.list_of_registered_areas
		whatsapp_system_use_instructions = company_data.whatsapp_system_use_instructions

	clean = re.compile('<.*?>')
	whatsapp_system_use_instructions = re.sub(clean, '', whatsapp_system_use_instructions)


	# Start our TwiML response
	# resp = MessagingResponse()

	user_number = request.POST.get('From', None)
	user_message = request.POST.get('Body', None)	

	splitted_from_whatsapp_keywords = user_number.split('whatsapp:', 1)[1]
	user_number = splitted_from_whatsapp_keywords.split()[0]

	check_user = SystemUser.objects.filter(tel1=user_number).count()
	if check_user == 0:
		SystemUser.objects.create(tel1=user_number, first_name='Whatsapp-user')
		welcome_message = "Bienvenue chez "+company_name+"\n"+whatsapp_system_use_instructions

		whatsapp_message_response = send_whatsapp_message(welcome_message, user_number, 'none')
	else:
		getting_user_data = SystemUser.objects.all().filter(tel1=user_number)
		for user_data in getting_user_data:
			user_slug = user_data.slug
			user_first_name = user_data.first_name
			user_last_name = user_data.last_name

		predefined_keywords = ['taxi', 'clando']

		if any(x in user_message.lower() for x in predefined_keywords):
			ride_type, route_slug, starting_area_slug, starting_area_name, ending_area_name, trip_price = route_request(user_message, user_number, list_of_registered_areas)

			ride_request_response = request_for_ride(ride_type, starting_area_slug, starting_area_name, ending_area_name, route_slug, user_slug, user_number, trip_price)
		else:
			reference_name = get_product_category_reference(user_message)

			if reference_name == 'none':
				if 'acheter' in user_message.lower():
					splitted_from_buy_keywords = user_message.lower().split('acheter', 1)[1]

					ordered_products_codes_list = listify(splitted_from_buy_keywords)

					products_order = place_order(user_number, user_slug, ordered_products_codes_list)
				else:
					predefined_keywords = ['evaluer', 'évaluer']

					if any(x in user_message.lower() for x in predefined_keywords):
						splitted_from_rank_keywords = user_message.lower().split('evaluer', 1)[1]
						extracted_trip_code = splitted_from_rank_keywords.split()[0]

						splitted_from_code = splitted_from_rank_keywords.lower().split(extracted_trip_code, 1)[1]
						rank = splitted_from_code.split()[0]

						if type(rank) != int:
							rank = 5

						if int(rank) > 5:
							rank = 5

						extracted_trip_code = extracted_trip_code.upper()

						trip_evaluation = evaluate_trip(extracted_trip_code, rank, user_slug, user_number)
					else:
						driver_keywords = ['position', 'dispo', 'disponible']
						if any(x in user_message.lower() for x in driver_keywords):
							driver_disponibility_trigger_response = trigger_driver_disponibility(user_message, user_number, user_slug)
						else:
							extracted_code = user_message.split()[0]
							splitted_from_extracted_code_keywords = user_message.split(extracted_code, 1)[1]

							ride_request_process_response = process_ride_request(extracted_code.upper(), user_slug, user_number, user_first_name, user_last_name, splitted_from_extracted_code_keywords)
			else:
				client_products_category_instance = ClientProductCategory.objects.get(reference_name=reference_name)

				get_client_products_data = ClientProduct.objects.all().filter(category=client_products_category_instance)
				for client_products_data in get_client_products_data:
					client_products_slug = client_products_data.slug
					client_products_code = client_products_data.code
					client_products_title = client_products_data.title
					client_products_price = client_products_data.price

					client_products_image_media_url = client_products_data.image.url

					client_products_image = 'https://rhandara.herokuapp.com/'+client_products_image_media_url[1:]

					product_message = client_products_title+'. Prix: '+str(client_products_price)+' CFA.\nPour commander, envoyez: Acheter '+client_products_code

					whatsapp_message_response = send_whatsapp_message(product_message, user_number, client_products_image)

	return HttpResponse('1')


# whatsapp message reception status view

@csrf_exempt
def whatsapp_message_reception_status_view(request):

	today = datetime.now()

	return ('well received')

