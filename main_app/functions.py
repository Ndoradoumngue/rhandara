# -*- coding: utf-8 -*-

import hashlib
import random
import time
import re
import html
import requests
import base64
from django.db.models import Count, Sum, Q, F
from datetime import datetime, time, timedelta
from twilio.rest import Client, TwilioRestClient
# get server timezone
from requests.auth import HTTPBasicAuth
from .models import (CompanyDetails, ClientProduct, Area, ErrorMesage, Route, SystemUser, Trip, ContactedDrivers, 
    ProductOwner, OurPartners, Order, UserWhatsappMessage, ProductOwnerCall, OrderedProduct)


# sending whatsapp message

def send_whatsapp_message(message, send_to_whatsapp_number, media_url):
    account_sid = 'ACc6e7cfa1168814b5c816d0fb545fd226'
    auth_token = '693babe30d89ab052263c21c63ee7868' 

    message = html.unescape(message)

    client = Client(account_sid, auth_token) 

    if media_url == 'none':
        message_sent_response = client.messages.create(from_='whatsapp:+14155238886', body=message, to='whatsapp:'+send_to_whatsapp_number)
    else:
        message_sent_response = client.messages.create(from_='whatsapp:+14155238886', body=message, to='whatsapp:'+send_to_whatsapp_number, media_url=media_url) 

    UserWhatsappMessage.objects.create(user_number=send_to_whatsapp_number, message=message, response=message_sent_response)

    return '1'


# request for taxi

def route_request(user_message, user_number, list_of_registered_areas):

    if 'taxi' in user_message.lower():
        keyword = 'taxi'
    else:
        keyword = 'clando'

    lower_message = user_message.lower()

    splitted_from_starting_area = lower_message.split(str(keyword), 1)[1]
    starting_area = splitted_from_starting_area.split()[0]

    splitted_from_ending_area = splitted_from_starting_area.split(str(starting_area), 1)[1]
    ending_area = splitted_from_ending_area.split()[0]

    check_starting_area = Area.objects.filter(name__icontains=starting_area).count()
    if check_starting_area == 0:
        starting_error_message = "Désolé, "+starting_area+" n'est pas dans nos zones enregistrées.\nPour réserver un taxi, veuillez envoyer un message comme celui-ci : Taxi dembe amtoukoui.\nVoici la liste de nos zones enregistrées : "+list_of_registered_areas
      
        ErrorMesage.objects.create(user_message=user_message, error_message=starting_error_message)

        whatsapp_message_response = send_whatsapp_message(starting_error_message, user_number, 'none')

        return ('error', 'error', 'error', 'error', 'error', 'error')
    else:
        check_arriving_area = Area.objects.filter(name__icontains=ending_area).count()
        if check_arriving_area == 0:
            ending_error_message = "Désolé, "+ending_area+" n'est pas dans nos zones enregistrées.\nPour réserver un taxi, veuillez envoyer un message comme celui-ci : Taxi dembe amtoukoui.\nVoici la liste de nos zones enregistrées : "+list_of_registered_areas
          
            ErrorMesage.objects.create(user_message=user_message, error_message=ending_error_message)

            whatsapp_message_response = send_whatsapp_message(ending_error_message, user_number, 'none')

            return ('error', 'error', 'error', 'error', 'error', 'error')
        else:
            getting_starting_area_data = Area.objects.all().filter(name__icontains=starting_area)
            for starting_area_data in getting_starting_area_data:
                starting_area_slug = starting_area_data.slug
                starting_area_name = starting_area_data.name

            getting_ending_area_data = Area.objects.all().filter(name__icontains=ending_area)
            for ending_area_data in getting_ending_area_data:
                ending_area_slug = ending_area_data.slug
                ending_area_name = ending_area_data.slug

            starting_area_instance = Area.objects.get(slug=starting_area_slug)
            ending_area_instance = Area.objects.get(slug=ending_area_slug)

            checking_route = Route.objects.filter(point_a=starting_area_instance, point_b=ending_area_instance).count()
            
            if checking_route == 0:
                getting_route_data = Route.objects.all().filter(point_a=ending_area_instance, point_b=starting_area_instance)
            else:
                getting_route_data = Route.objects.all().filter(point_a=starting_area_instance, point_b=ending_area_instance)

            for route_data in getting_route_data:
                route_slug = route_data.slug

                if keyword == 'taxi':
                    price = route_data.taxi_price
                else:
                    price = route_data.motorbike_price

            return (keyword, route_slug, starting_area_slug, starting_area_name, ending_area_name, price)


# generate riding request code

def generate_riding_request_code():

    generate_riding_request_code_loop = True

    while generate_riding_request_code_loop:

        generate_riding_request_code_from = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        riding_request_code_length = 5
        riding_request_code = ""

        for i in range(riding_request_code_length):
            next_index = random.randrange(len(generate_riding_request_code_from))
            riding_request_code = riding_request_code + generate_riding_request_code_from[next_index]       

        check_riding_request_code = Trip.objects.filter(code=riding_request_code).count()
        if check_riding_request_code == 0:
            generate_riding_request_code_loop = False
            break
        else:
            generate_riding_request_code_loop = True

    return riding_request_code


# ride request 

def request_for_ride(ride_type, starting_area_slug, starting_area_name, ending_area_name, route_slug, user_slug, user_number, trip_price):

    if ride_type == 'taxi':
        is_taxi_trip = True
        is_motorbike_trip = False
    else:
        is_taxi_trip = False
        is_motorbike_trip = True

    starting_area_instance = Area.objects.get(slug=starting_area_slug)
    route_instance = Route.objects.get(slug=route_slug)
    user_instance = SystemUser.objects.get(slug=user_slug)

    generated_riding_request_code = generate_riding_request_code()

    Trip.objects.create(code=generated_riding_request_code, is_taxi_trip=is_taxi_trip, is_motorbike_trip=is_motorbike_trip, starting_point=starting_area_instance, route=route_instance, price=trip_price, client=user_instance)

    message = "Votre demande de "+ride_type+" a été enregistrée. Nous vous mettrons très bientôt en contact avec un(e) conducteur(trice)."
    whatsapp_message_response = send_whatsapp_message(message, user_number, 'none')

    get_requested_trip_data = Trip.objects.all().filter(code=generated_riding_request_code)
    for requested_trip_data in get_requested_trip_data:
        requested_trip_slug = requested_trip_data.slug

    requested_trip_instance = Trip.objects.get(slug=requested_trip_slug)

    if ride_type == 'taxi':
        checking_drivers_in_the_starting_area = SystemUser.objects.filter(current_area_location=starting_area_instance, is_car_driver=True, is_available_to_driver=True).count()
        getting_drivers_in_the_starting_area_data = SystemUser.objects.all().filter(current_area_location=starting_area_instance, is_car_driver=True, is_available_to_driver=True)
    else:
        checking_drivers_in_the_starting_area = SystemUser.objects.filter(current_area_location=starting_area_instance, is_motorbike_driver=True, is_available_to_driver=True).count()
        getting_drivers_in_the_starting_area_data = SystemUser.objects.all().filter(current_area_location=starting_area_instance, is_motorbike_driver=True, is_available_to_driver=True)
    
    if checking_drivers_in_the_starting_area == 0:
        message = "Désolé, nous n'avons pas pu trouver de "+ride_type+" à "+starting_area_name+" pour vous."
        whatsapp_message_response = send_whatsapp_message(message, user_number, 'none')
    else:
        for drivers_in_the_starting_area_data in getting_drivers_in_the_starting_area_data:
            driver_in_the_starting_area_tel = drivers_in_the_starting_area_data.tel1
            driver_in_the_starting_area_slug = drivers_in_the_starting_area_data.slug

            driver_instance = SystemUser.objects.get(slug=driver_in_the_starting_area_slug)

            ContactedDrivers.objects.create(contacted_driver=driver_instance, trip=requested_trip_instance)

            message = "Nous avons reçu une nouvelle demande de dépôt de "+starting_area_name+" à "+ending_area_name+". Pour accepter, répondez par "+generated_riding_request_code+" OK."
            whatsapp_message_response = send_whatsapp_message(message, driver_in_the_starting_area_tel, 'none')

    return '1'


# getting reference name in user message

def get_product_category_reference(user_message):
        
    food_keywords = ['repas', 'dejeuner', 'déjeuner', 'manger', 'nourriture']

    electronics_keywords = ['eletronique', 'électroniques']

    accessories_keywords = ['accessoires', 'accessoires']

    men_clothes_keywords = ['habit', 'homme']
    men_clothes_keywords2 = ['habits', 'hommes']

    women_clothes_keywords = ['habit', 'femme']
    women_clothes_keywords2 = ['habits', 'femmes']

    men_shoes_keywords = ['chaussure', 'homme']
    men_shoes_keywords2 = ['chaussures', 'hommes']

    women_shoes_keywords = ['chaussure', 'femme']
    women_shoes_keywords2 = ['chaussures', 'femmes']   

    if any(x in user_message.lower() for x in food_keywords):
        reference_name = 'food'
    elif any(x in user_message.lower() for x in accessories_keywords):
        reference_name = 'accessory'
    elif any(x in user_message.lower() for x in electronics_keywords):
        reference_name = 'electronic'
    elif all(x in user_message.lower() for x in men_clothes_keywords) or all(x in user_message.lower() for x in men_clothes_keywords2):
        reference_name = 'men-clothing'
    elif all(x in user_message.lower() for x in women_clothes_keywords) or all(x in user_message.lower() for x in women_clothes_keywords2):
        reference_name = 'women-clothing'
    elif all(x in user_message.lower() for x in men_shoes_keywords) or all(x in user_message.lower() for x in men_shoes_keywords2):
        reference_name = 'men-shoes'
    elif all(x in user_message.lower() for x in women_shoes_keywords) or all(x in user_message.lower() for x in women_shoes_keywords2):
        reference_name = 'women-shoes'
    else:
        reference_name = 'none'

    return reference_name


# listify sentence separated

def listify(message_to_listify):
    returned_list = re.split(' |,' ,message_to_listify)

    while("" in returned_list):
        returned_list.remove("")

    return returned_list


# generate order code

def generate_order_code():

    generate_order_code_loop = True

    while generate_order_code_loop:

        generate_order_code_from = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        generate_order_code_length = 8
        generate_order_code = ""

        for i in range(generate_order_code_length):
            next_index = random.randrange(len(generate_order_code_from))
            generate_order_code = generate_order_code + generate_order_code_from[next_index]       

        check_riding_request_code = Order.objects.filter(code=generate_order_code).count()
        if check_riding_request_code == 0:
            generate_order_code_loop = False
            break
        else:
            generate_order_code_loop = True

    return generate_order_code


# place order

def place_order(client_tel, client_slug, requested_products_codes_list):

    client_instance = SystemUser.objects.get(tel1=client_tel)

    order_code = generate_order_code()    

    Order.objects.create(code=order_code, client=client_instance)
    get_company_details = CompanyDetails.objects.all()
    for company_data in get_company_details:
        company_email = company_data.email
        company_tel = company_data.tel1

    order_instance = Order.objects.get(code=order_code)

    for product_code in requested_products_codes_list:

        uppercase_product_code = product_code.upper()

        check_client_products = ClientProduct.objects.filter(code=uppercase_product_code, active=True).count()
        if check_client_products == 0:
            error_message = "Désolé, nous n'avons pas réussi à trouver le produit avec le code "+uppercase_product_code+". Veuillez vérifier le code produit et réessayer."
            whatsapp_message_response = send_whatsapp_message(error_message, client_tel, 'none')
        else:
            getting_product_data = ClientProduct.objects.all().filter(code=uppercase_product_code, active=True)
            for product_data in getting_product_data:
                product_slug = product_data.slug
                product_name = product_data.title
                product_price = product_data.price

            product_instance = ClientProduct.objects.get(slug=product_slug)

            checking_product_owners = ProductOwner.objects.filter(product=product_instance, active=True).count()
            if checking_product_owners == 0:
                no_owner_error_message = "Désolé, nous n'avons pas réussi à trouver le vendeur du produit avec le code "+product_code+". Veuillez vérifier le code produit et réessayer."
                whatsapp_message_response = send_whatsapp_message(no_owner_error_message, client_tel, 'none')
            else:
                getting_product_owners_data = ProductOwner.objects.all().filter(product=product_instance, active=True)
                for product_owners_data in getting_product_owners_data:
                    product_owner_tel = product_owners_data.owner.tel1
                    product_owner_slug = product_owners_data.owner.slug

                    order_message = "Un client a commandé le produit "+product_name+" au prix de "+str(product_price)+" CFA. Le code de la commande est: "+order_code

                    whatsapp_message_response = send_whatsapp_message(order_message, product_owner_tel, 'none')

                    partner_instance = OurPartners.objects.get(slug=product_owner_slug)

                    checking_product_owner_call = ProductOwnerCall.objects.filter(order=order_instance, partner=partner_instance).count()
                    if checking_product_owner_call == 0:
                        ProductOwnerCall.objects.create(order=order_instance, partner=partner_instance, order_fulfilled=False)

                OrderedProduct.objects.create(order=order_instance, product=product_instance)

                completion_message = "Votre commande a été enregistrée avec le code "+order_code+". Pour plus de détails, n'hésitez pas à nous contacter au numéro de téléphone "+company_tel+" ou par mail à l'addresse "+company_email
                whatsapp_message_response = send_whatsapp_message(completion_message, client_tel, 'none')
    
    return '1'


# process request

def process_ride_request(request_code, client_slug, client_tel, user_first_name, user_last_name, remaining_text):

    today = datetime.now().date()

    current_datetime = datetime.now()

    user_instance = SystemUser.objects.get(slug=client_slug)

    get_company_details = CompanyDetails.objects.all()
    for company_data in get_company_details:
        company_email = company_data.email
        company_tel = company_data.tel1
        whatsapp_system_use_instructions = company_data.whatsapp_system_use_instructions

    clean = re.compile('<.*?>')
    whatsapp_system_use_instructions = re.sub(clean, '', whatsapp_system_use_instructions)

    check_request = Trip.objects.filter(code=request_code).count()
    if check_request == 0:
        error_message = whatsapp_system_use_instructions+" Vous pouvez nous contacter par téléphone au "+company_tel+" ou par email au "+company_email+" pour du support"
        whatsapp_message_response = send_whatsapp_message(error_message, client_tel, 'none')
    else:
        get_requested_trip_data = Trip.objects.all().filter(code=request_code)
        for requested_trip_data in get_requested_trip_data:
            requested_trip_slug = requested_trip_data.slug
            requested_trip_is_accepted = requested_trip_data.request_accepted
            requested_trip_has_started = requested_trip_data.trip_started
            requested_trip_is_completed = requested_trip_data.trip_finished
            requested_trip_is_cancelled = requested_trip_data.trip_cancelled
            requested_trip_client_tel = requested_trip_data.client.tel1
            requested_trip_client_first_name = requested_trip_data.client.first_name
            requested_trip_client_last_name = requested_trip_data.client.last_name

            requested_trip_client_instance = SystemUser.objects.get(slug=requested_trip_data.client.slug)

            if requested_trip_data.request_accepted_by == None or requested_trip_data.request_accepted_by == '':
                requested_trip_driver_tel = ''
                requested_trip_driver_slug = ''
                requested_trip_driver_first_name = ''
                requested_trip_driver_last_name = ''
            else:
                requested_trip_driver_tel = requested_trip_data.request_accepted_by.tel1
                requested_trip_driver_slug = requested_trip_data.request_accepted_by.slug
                requested_trip_driver_first_name = requested_trip_data.request_accepted_by.first_name
                requested_trip_driver_last_name = requested_trip_data.request_accepted_by.last_name

        requested_trip_instance = Trip.objects.get(slug=requested_trip_slug)

        if 'ok' in remaining_text.lower():
            check_contacted_driver = ContactedDrivers.objects.filter(contacted_driver=user_instance, trip=requested_trip_instance).count()
            if check_contacted_driver == 0:
                unauthorized_error_message = "Désolé, vous n'êtes pas autorisé à traiter cette demande de dépôt"
                whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
            else:
                if requested_trip_is_accepted == True and requested_trip_is_cancelled == False:
                    driver_trip_acceptation_message = "Désolé, cette commande de dépôt a déjà été prise en charge. Veuillez accepter la commande sans délai dès que vous recevez la notification pour gagner plus de commandes."
                    whatsapp_message_response1 = send_whatsapp_message(driver_trip_acceptation_message, client_tel, 'none')
                else:
                    Trip.objects.filter(slug=requested_trip_slug).update(is_new_request=False, request_accepted=True, request_accepted_by=user_instance, request_accepted_on_date_time=current_datetime)
                    SystemUser.objects.filter(slug=client_slug).update(is_available_to_driver=True)

                    # driver_trip_acceptation_message = "Merci d'accepter le depot de "+requested_trip_client_first_name+" "+requested_trip_client_last_name+". Veuillez le/la contacter au "+requested_trip_client_tel
                    driver_trip_acceptation_message = "Merci d'accepter le depot "+request_code+". Veuillez contacter le client au "+requested_trip_client_tel
                    whatsapp_message_response1 = send_whatsapp_message(driver_trip_acceptation_message, client_tel, 'none')
                    
                    client_trip_acceptation_message = user_first_name+" "+user_last_name+" a accepté votre demande de dépôt. Vous pouvez le contacter au "+client_tel
                    whatsapp_message_response2 = send_whatsapp_message(client_trip_acceptation_message, requested_trip_client_tel, 'none')

        elif 'annuler' in remaining_text.lower():
            check_trip_owner = Trip.objects.filter(code=request_code, client=requested_trip_client_instance).count()
            if check_trip_owner == 0:
                unauthorized_error_message = "Désolé, vous n'êtes pas autorisé à annuler cette demande de dépôt"
                whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
            else:
                if requested_trip_has_started == True and requested_trip_is_cancelled == False:
                    unauthorized_error_message = "Désolé, vous ne pouvez annuler cette demande de dépôt. Elle a déjà commencé, elle doit finir."
                    whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
                else:
                    Trip.objects.filter(slug=requested_trip_slug).update(trip_cancelled=True, trip_cancelled_on_date_time=current_datetime)
                    
                    client_trip_cancellation_message = "Vous avez annulé votre demande de dépôt avec succès."
                    whatsapp_message_response2 = send_whatsapp_message(client_trip_cancellation_message, requested_trip_client_tel, 'none')
                
        elif 'pris' in remaining_text.lower():

            requested_trip_driver_instance = SystemUser.objects.get(slug=requested_trip_driver_slug)

            check_trip_actors = Trip.objects.filter(code=request_code).filter(Q(client=requested_trip_client_instance) | Q(request_accepted_by=requested_trip_driver_instance)).count()
            if check_trip_actors == 0:
                unauthorized_error_message = "Désolé, vous n'êtes pas autorisé à traiter ce dépôt"
                whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
            else:
                Trip.objects.filter(slug=requested_trip_slug).update(trip_started=True, trip_started_on_date_time=current_datetime)
                
                client_trip_acceptation_message = "Le dépôt "+request_code+" a commencé."
                whatsapp_message_response1 = send_whatsapp_message(client_trip_acceptation_message, requested_trip_driver_tel, 'none')
                whatsapp_message_response2 = send_whatsapp_message(client_trip_acceptation_message, requested_trip_client_tel, 'none')
        
        elif 'fini' in remaining_text.lower():           

            requested_trip_driver_instance = SystemUser.objects.get(slug=requested_trip_driver_slug)

            check_trip_actors = Trip.objects.filter(code=request_code).filter(Q(client=requested_trip_client_instance) | Q(request_accepted_by=requested_trip_driver_instance)).count()
            if check_trip_actors == 0:
                unauthorized_error_message = "Désolé, vous n'êtes pas autorisé à traiter ce dépôt"
                whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
            else:
                # final_trip_code = request_code+"-"+requested_trip_client_tel+"-"+requested_trip_driver_tel
                # code=final_trip_code, 

                Trip.objects.filter(slug=requested_trip_slug).update(trip_finished=True, trip_finished_on_date_time=current_datetime)
                
                client_trip_acceptation_message = "Le dépôt "+request_code+" est fini. N'n'hésitez pas à évaluer ce service. Envoyez: Evaluer le code et votre evaluation sur 5. Ex: Evaluer "+request_code+" 5"
                whatsapp_message_response1 = send_whatsapp_message(client_trip_acceptation_message, requested_trip_driver_tel, 'none')
                whatsapp_message_response2 = send_whatsapp_message(client_trip_acceptation_message, requested_trip_client_tel, 'none')
        else:
            error_message = whatsapp_system_use_instructions+" Vous pouvez nous contacter par téléphone au "+company_tel+" ou par email au "+company_email+" pour du support"
            whatsapp_message_response = send_whatsapp_message(error_message, client_tel, 'none')

    return '1'


# evalaute trip

def evaluate_trip(extracted_trip_code, rank, user_slug, client_tel):

    check_trip = Trip.objects.filter(code=extracted_trip_code).count()
    if check_trip == 0:
        error_message = "Désolé, nous n'avons pas pu trouver d'historique de dépôt avec ce code."
        whatsapp_message_response = send_whatsapp_message(error_message, client_tel, 'none')
    else:
        getting_trip_data = Trip.objects.all().filter(code=extracted_trip_code)
        for trip_data in getting_trip_data:
            trip_client_slug = trip_data.client.slug
            trip_client_rating = trip_data.client.rating
            trip_client_number_of_raters = trip_data.client.number_of_raters
            trip_client_number_of_ratings = trip_data.client.number_of_ratings
            trip_driver_slug = trip_data.request_accepted_by.slug
            trip_driver_rating = trip_data.request_accepted_by.rating
            trip_driver_number_of_raters = trip_data.request_accepted_by.number_of_raters
            trip_driver_number_of_ratings = trip_data.request_accepted_by.number_of_ratings

        user_instance = SystemUser.objects.get(slug=user_slug)
        check_trip_client = Trip.objects.filter(client=user_instance, code=extracted_trip_code).count()
        check_trip_driver = Trip.objects.filter(request_accepted_by=user_instance, code=extracted_trip_code).count()

        if check_trip_client == 0 and check_trip_driver == 0:
            unauthorized_error_message = "Désolé, vous n'êtes pas autorisé à évaluer ce dépôt"
            whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
        elif check_trip_client != 0 and check_trip_driver == 0:

            new_trip_driver_number_of_raters = trip_driver_number_of_raters+1
            new_trip_driver_number_of_ratings = trip_driver_number_of_ratings+int(rank)

            new_trip_driver_rating = new_trip_driver_number_of_ratings/new_trip_driver_number_of_raters

            Trip.objects.filter(code=extracted_trip_code).update(client_trip_rating=int(rank))

            SystemUser.objects.filter(slug=trip_driver_slug).update(rating=new_trip_driver_rating, number_of_raters=new_trip_driver_number_of_raters, number_of_ratings=new_trip_driver_number_of_ratings)

            unauthorized_error_message = "Vous avez évalué le/la conducteur/trice à "+str(rank)+" étoiles."
            whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')
        elif check_trip_client == 0 and check_trip_driver != 0:

            new_trip_client_number_of_raters = trip_client_number_of_raters+1
            new_trip_client_number_of_ratings = trip_client_number_of_ratings+int(rank)

            new_trip_client_rating = new_trip_client_number_of_ratings/new_trip_client_number_of_raters

            Trip.objects.filter(code=extracted_trip_code).update(client_trip_rating=int(rank))

            SystemUser.objects.filter(slug=trip_client_slug).update(rating=new_trip_client_rating, number_of_raters=new_trip_client_number_of_raters, number_of_ratings=new_trip_client_number_of_ratings)

            unauthorized_error_message = "Vous avez évalué le/la client/e à "+str(rank)+" étoiles."
            whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')    
        else:
            unauthorized_error_message = "Désolé, vous n'êtes pas autorisé à évaluer ce dépôt"
            whatsapp_message_response = send_whatsapp_message(unauthorized_error_message, client_tel, 'none')


    return '1'


# trigger driver disponibility

def trigger_driver_disponibility(message, client_tel,  user_slug):

    get_company_details = CompanyDetails.objects.all()
    for company_data in get_company_details:
        company_tel = company_data.tel1
        company_email = company_data.email
        company_name = company_data.company_name
        list_of_registered_areas = company_data.list_of_registered_areas

    check_if_driver = SystemUser.objects.filter(slug=user_slug).filter(Q(is_car_driver=True) | Q(is_motorbike_driver=True)).count()
    if check_if_driver == 0:
        error_message = "Souhaitez-vous définir votre disponibilité à une position ? Si vous n'êtes pas chauffeur à "+company_name+" et que vous souhaitez devenir l'un de nos chauffeurs, veuillez nous contacter par téléphone au "+company_tel+" ou par mail à "+company_email
        whatsapp_message_response = send_whatsapp_message(error_message, client_tel, 'none')
    else:
        if 'position' in message.lower():
            splitted_from_position_keywords = message.lower().split('position', 1)[1]
            area_name = splitted_from_position_keywords.split()[0]

            check_area = Area.objects.filter(name__icontains=area_name).count()
            if check_area == 0:
                ending_error_message = "Désolé, "+area_name+" n'est pas dans nos zones enregistrées.\nPour définir votre disponibilité dans un quartier, veuillez envoyer Position le nom du quartier. Ex: Position Amtoukoui.\nVoici la liste de nos zones enregistrées : "+list_of_registered_areas
              
                ErrorMesage.objects.create(user_message=user_message, error_message=ending_error_message)

                whatsapp_message_response = send_whatsapp_message(ending_error_message, user_number, 'none')

                return ('error', 'error', 'error', 'error', 'error', 'error')
            else:
                getting_area_data = Area.objects.all().filter(name__icontains=area_name)
                for area_data in getting_area_data:
                    area_slug = area_data.slug
                    area_name = area_data.name

                area_instance = Area.objects.get(slug=area_slug)

                SystemUser.objects.filter(slug=user_slug).update(is_available_to_driver=True, current_area_location=area_instance)

                success_message = "Vous avez défini avec succès votre disponibilité au quartier "+area_name+"."
                whatsapp_message_response = send_whatsapp_message(success_message, client_tel, 'none')
        else:
            SystemUser.objects.filter(slug=user_slug).update(is_available_to_driver=False)

            success_message = "Vous avez défini avec succès que vous n'êtes pas disponible. Pour pouvoir recevoir des demandes de dépôt paramétrez votre disponibilité dans un quartier en envoyant : Position suivi du nom du quartier. Ex : Position Amtoukoui"
            whatsapp_message_response = send_whatsapp_message(success_message, client_tel, 'none')

    return '1'


# getting local timezone

def get_local_timezone():
    if time.daylight:
        offset_hour = time.altzone / 3600
    else:
        offset_hour = time.timezone / 3600

    return offset_hour


# get server timezone

def add_remove_days_to_date(start_date, days_to_add):
    needed_date = start_date + timedelta(days=int(days_to_add))

    return needed_date


# get server timezone

def test_int(integer):
    try:
        int(integer)
        result = '1'
    except Exception as e:
        result = '0'

    return result

   
# check safaricom number

def check_safaricom_phone_number(number):
    safaricom_prefixes = []

    safaricom_prefixes.append('0701')
    safaricom_prefixes.append('0702')
    safaricom_prefixes.append('0703')
    safaricom_prefixes.append('0704')
    safaricom_prefixes.append('0705')
    safaricom_prefixes.append('0706')
    safaricom_prefixes.append('0707')
    safaricom_prefixes.append('0708')
    safaricom_prefixes.append('0709')
    safaricom_prefixes.append('0710')
    safaricom_prefixes.append('0711')
    safaricom_prefixes.append('0712')
    safaricom_prefixes.append('0713')
    safaricom_prefixes.append('0714')
    safaricom_prefixes.append('0715')
    safaricom_prefixes.append('0716')
    safaricom_prefixes.append('0717')
    safaricom_prefixes.append('0718')
    safaricom_prefixes.append('0719')
    safaricom_prefixes.append('0720')
    safaricom_prefixes.append('0721')
    safaricom_prefixes.append('0722')
    safaricom_prefixes.append('0723')
    safaricom_prefixes.append('0724')
    safaricom_prefixes.append('0725')
    safaricom_prefixes.append('0726')
    safaricom_prefixes.append('0727')
    safaricom_prefixes.append('0728')
    safaricom_prefixes.append('0729')

    safaricom_prefixes.append('701')
    safaricom_prefixes.append('702')
    safaricom_prefixes.append('703')
    safaricom_prefixes.append('704')
    safaricom_prefixes.append('705')
    safaricom_prefixes.append('706')
    safaricom_prefixes.append('707')
    safaricom_prefixes.append('708')
    safaricom_prefixes.append('709')
    safaricom_prefixes.append('710')
    safaricom_prefixes.append('711')
    safaricom_prefixes.append('712')
    safaricom_prefixes.append('713')
    safaricom_prefixes.append('714')
    safaricom_prefixes.append('715')
    safaricom_prefixes.append('716')
    safaricom_prefixes.append('717')
    safaricom_prefixes.append('718')
    safaricom_prefixes.append('719')
    safaricom_prefixes.append('720')
    safaricom_prefixes.append('721')
    safaricom_prefixes.append('722')
    safaricom_prefixes.append('723')
    safaricom_prefixes.append('724')
    safaricom_prefixes.append('725')
    safaricom_prefixes.append('726')
    safaricom_prefixes.append('727')
    safaricom_prefixes.append('728')
    safaricom_prefixes.append('729')


    safaricom_prefixes.append('+254701')
    safaricom_prefixes.append('+254702')
    safaricom_prefixes.append('+254703')
    safaricom_prefixes.append('+254704')
    safaricom_prefixes.append('+254705')
    safaricom_prefixes.append('+254706')
    safaricom_prefixes.append('+254707')
    safaricom_prefixes.append('+254708')
    safaricom_prefixes.append('+254709')
    safaricom_prefixes.append('+254710')
    safaricom_prefixes.append('+254711')
    safaricom_prefixes.append('+254712')
    safaricom_prefixes.append('+254713')
    safaricom_prefixes.append('+254714')
    safaricom_prefixes.append('+254715')
    safaricom_prefixes.append('+254716')
    safaricom_prefixes.append('+254717')
    safaricom_prefixes.append('+254718')
    safaricom_prefixes.append('+254719')
    safaricom_prefixes.append('+254720')
    safaricom_prefixes.append('+254721')
    safaricom_prefixes.append('+254722')
    safaricom_prefixes.append('+254723')
    safaricom_prefixes.append('+254724')
    safaricom_prefixes.append('+254725')
    safaricom_prefixes.append('+254726')
    safaricom_prefixes.append('+254727')
    safaricom_prefixes.append('+254728')
    safaricom_prefixes.append('+254729')

    safaricom_prefixes.append('254701')
    safaricom_prefixes.append('254702')
    safaricom_prefixes.append('254703')
    safaricom_prefixes.append('254704')
    safaricom_prefixes.append('254705')
    safaricom_prefixes.append('254706')
    safaricom_prefixes.append('254707')
    safaricom_prefixes.append('254708')
    safaricom_prefixes.append('254709')
    safaricom_prefixes.append('254710')
    safaricom_prefixes.append('254711')
    safaricom_prefixes.append('254712')
    safaricom_prefixes.append('254713')
    safaricom_prefixes.append('254714')
    safaricom_prefixes.append('254715')
    safaricom_prefixes.append('254716')
    safaricom_prefixes.append('254717')
    safaricom_prefixes.append('254718')
    safaricom_prefixes.append('254719')
    safaricom_prefixes.append('254720')
    safaricom_prefixes.append('254721')
    safaricom_prefixes.append('254722')
    safaricom_prefixes.append('254723')
    safaricom_prefixes.append('254724')
    safaricom_prefixes.append('254725')
    safaricom_prefixes.append('254726')
    safaricom_prefixes.append('254727')
    safaricom_prefixes.append('254728')
    safaricom_prefixes.append('254729')

    supplied_number_prefix = str(number)[:4]

    if supplied_number_prefix in safaricom_prefixes:
        if len(number) == 10:
            is_safaricom_number = '1'
        else:
            is_safaricom_number = '0'
    else:
        is_safaricom_number = '0'

    return is_safaricom_number

# get twilio account details

def get_twilio_account_details():
    
    # Account SID from twilio.com/console
    account_sid = "AC6d64f4138d40052e23cd17f2a0bebeac"

    # Auth Token from twilio.com/console
    auth_token  = "609c69d53d3b536785c8e6f02115909b"

    # Twilio phone number
    twilio_number = '+14348851286'

    return account_sid, auth_token, twilio_number

# verify and format kenyan number

def verify_kenyan_phone_number(phone_number):

    if len(phone_number) == 10:
        if phone_number[:2] == '07':
            number_corrected = True
            number_to_use = '+254'+phone_number[1:]
        else:
            number_corrected = False
            number_to_use = 'Number is not a mobile number'
    elif len(phone_number) == 9:
        if phone_number[:1] == '7':
            number_corrected = True
            number_to_use = '+254'+phone_number
        else:
            number_corrected = False
            number_to_use = 'Number is not a mobile number'
    elif len(phone_number) == 12:
        if phone_number[:3] == '254':
            number_corrected = True
            number_to_use = '+'+phone_number
        else:
            number_corrected = False
            number_to_use = 'Number is not a mobile number'
    elif len(phone_number) == 13:
        if phone_number[:4] == '+254':
            number_corrected = True
            number_to_use = phone_number
        else:
            number_corrected = False
            number_to_use = 'Number is not a mobile number'
    elif len(phone_number) == 14:
        if phone_number[:5] == '00254':
            number_corrected = True
            number_to_use = '+'+phone_number[2:]
        else:
            number_corrected = False
            number_to_use = 'Number is not a mobile number'
    elif len(phone_number) == 15:
        if phone_number[:6] == '000254':
            number_corrected = True
            number_to_use = '+'+phone_number[3:]
        else:
            number_corrected = False
            number_to_use = 'Number is not a mobile number'
    else:
        number_corrected = False
        number_to_use = 'Number is not a mobile number'

    return number_corrected, number_to_use

# send sms twilio

def send_twilio_sms(tel_number, sms):

    # test phone number

    phone_number_correct, number_to_use = verify_kenyan_phone_number(tel_number)
    if phone_number_correct == True:
        account_sid, auth_token, twilio_number = get_twilio_account_details()

        client = Client(account_sid, auth_token)
        message = client.messages.create(to=number_to_use, from_=twilio_number, body=sms)

        sms_sent = True
        message_sid = message.sid
    else:
        sms_sent = False
        message_sid = 'None'

    return sms_sent, message_sid

# get duration

def get_duration_in_hours(starting_date, end_date):
    starting_date_formatted = datetime.strptime(str(starting_date)[:19], '%Y-%m-%d %H:%M:%S')
    end_date_formatted = datetime.strptime(str(end_date)[:19], '%Y-%m-%d %H:%M:%S')

    if end_date_formatted < starting_date_formatted:
        result_code = "0"
        duration_in_hours = 0
        message = "starting date must be greater than end date"
    else:
        dates_substraction = end_date_formatted - starting_date_formatted

        dates_substraction_string = str(dates_substraction)

        if "-" in dates_substraction_string:
            result_code = "0"
            duration_in_hours = 0
            message = "starting date must be greater than end date"
        else:
            if "days," in dates_substraction_string:
                the_number_of_days = float(dates_substraction_string.split("days")[0])
                the_hours_part = dates_substraction_string[-8:]
            else:
                if "day," in dates_substraction_string:
                    the_number_of_days = float(dates_substraction_string.split("day")[0])
                    the_hours_part = dates_substraction_string[-8:]
                else:
                    the_number_of_days = 0
                    if ':' in dates_substraction_string[:2]:
                        the_hours_part = '0' + dates_substraction_string
                    else:
                        the_hours_part = dates_substraction_string

            the_number_of_hours = float(the_hours_part[:2])
            the_number_of_minutes = float(the_hours_part[3:5])

            if the_number_of_minutes > 0:
                minute_converted_to_hour = 1
            else:
                minute_converted_to_hour = 0

            duration_in_hours = the_number_of_days * 24 + the_number_of_hours + minute_converted_to_hour
            result_code = "1"
            message = "Success"

    return result_code, str(duration_in_hours), message


def convert_hours_to_second(hour):
    return hour * 60


# hash password

def hash_password_function(raw_password):
    encoded_password = raw_password.encode('utf-8')
    h = hashlib.md5()
    h.update(encoded_password)
    hashed_password = h.hexdigest()

    return hashed_password
    

# function to return current datetime in safaricom mpesa timestamp

def get_safaricom_timestamp():
    current_datetime = datetime.now()
    datetime_without_dash = str(current_datetime).replace("-", "")
    datetime_without_space = datetime_without_dash.replace(" ", "")
    datetime_without_colon = datetime_without_space.replace(":", "")

    mpesa_date_stamp = datetime_without_colon[:14]

    return (mpesa_date_stamp)

# function to encode data in base64

def encode_in_base64(data_to_encode):
    bytes_encoded_data = base64.b64encode(data_to_encode.encode())

    from_b_data = str(bytes_encoded_data).split('b\'', 1)[1:]
    encoded_data = from_b_data[0].split('\'', 1)[:1]

    return (encoded_data[0])

# mpesa access token

def get_mpesa_access_token():

    today = datetime.now().date()

    current_datetime = datetime.now()

    get_current_mpesa_token = CompanyDetails.objects.all()
    for current_mpesa_token_data in get_current_mpesa_token:
        current_mpesa_access_token = current_mpesa_token_data.current_mpesa_access_token
        current_mpesa_access_token_generated_on_datetime = current_mpesa_token_data.current_mpesa_access_token_generated_on_datetime

    if current_mpesa_access_token == '' or current_mpesa_access_token == None:
        generate_another_mpesa_access_token = True
    else:
        period_of_last_generated_mpesa_access_token = current_datetime.replace(tzinfo=None)-current_mpesa_access_token_generated_on_datetime.replace(tzinfo=None)
        period_of_last_generated_mpesa_access_token_string = str(period_of_last_generated_mpesa_access_token)

        if 'days' in period_of_last_generated_mpesa_access_token_string or 'day' in period_of_last_generated_mpesa_access_token_string:
            generate_another_mpesa_access_token = True
        else:
            extracted_hour = period_of_last_generated_mpesa_access_token_string.split(':', 1)[:1]
            if int(extracted_hour[0]) > 0:
                generate_another_mpesa_access_token = True
            else:
                generate_another_mpesa_access_token = False


    if generate_another_mpesa_access_token == True:
        consumer_key = "duhDY8aQ1qFn0P3jrdkaSUGqMf5EK0zS"
        consumer_secret = "duiTT3Wp7k1OBKgS"
        api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        # Test.objects.create(test=r)

        from_token_data = r.text.split('"access_token": "', 1)[1:]

        access_token_data = from_token_data[0].split('",', 1)[:1]

        access_token_data = access_token_data[0]

        CompanyDetails.objects.update(current_mpesa_access_token=access_token_data, current_mpesa_access_token_generated_on_datetime=today)
    else:
        access_token_data = current_mpesa_access_token

    return (access_token_data)

# perform user mpesa transfer

def perform_client_mpesa_transfer(mpesa_access_token, amount, user_mpesa_tel):

    paybill_number = "834700"
    access_token = mpesa_access_token
    lipa_na_mpesa_online_pass_key = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"    

    timestamp = get_safaricom_timestamp()

    string_to_encode = paybill_number+""+lipa_na_mpesa_online_pass_key+""+timestamp

    mpesa_password = encode_in_base64(string_to_encode)

    api_url="https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers={"Authorization":"Bearer %s"%access_token}
    request={
        "BusinessShortCode": paybill_number,
        "Password": mpesa_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": user_mpesa_tel,
        "PartyB": paybill_number,
        "PhoneNumber": user_mpesa_tel,
        "CallBackURL": "https://technologiepenempesatest.herokuapp.com/rest_online_paybill_transaction_confirmation/",
        "AccountReference": 'NormalPayment',
        "TransactionDesc": 'Sacco payment'
    }

    response = requests.post(api_url,json=request,headers=headers)

    return (response.text)
    