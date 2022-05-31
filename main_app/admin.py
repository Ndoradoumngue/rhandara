from django.contrib import admin
from .models import (Country, Town, SystemUser, CompanyDetails, OurPartners, Slider, Testimony, Event, News, Test,
	GalleryCategory, Gallery, Message, EventParticipant, OurService, OurProductCategory, OurProduct, Area, Route, 
	Vehicle, Trip, ErrorMesage, UserWhatsappMessage, ClientProductCategory, ClientProduct, ProductOwner)

admin.site.register(Country)

admin.site.register(Town)

admin.site.register(SystemUser)

admin.site.register(CompanyDetails)

admin.site.register(OurPartners)

admin.site.register(Slider)

admin.site.register(Testimony)

admin.site.register(Event)

admin.site.register(News)

admin.site.register(GalleryCategory)

admin.site.register(Gallery)

admin.site.register(Message)

admin.site.register(EventParticipant)

admin.site.register(OurService)

admin.site.register(OurProductCategory)

admin.site.register(OurProduct)

admin.site.register(Test)

admin.site.register(Area)

admin.site.register(Route)

admin.site.register(Vehicle)

admin.site.register(Trip)

admin.site.register(ErrorMesage)

admin.site.register(UserWhatsappMessage)

admin.site.register(ClientProductCategory)

admin.site.register(ClientProduct)

admin.site.register(ProductOwner)
