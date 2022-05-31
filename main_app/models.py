# coding=utf-8

import random
from ckeditor.fields import RichTextField
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify

from .validators import validate_file_extension

# Country

class Country(models.Model):
    country_name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=50)
    is_our_country_of_operation = models.BooleanField(default=False)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.country_name

def create_country_slug(instance, new_slug=None):
    slug = slugify(instance.country_name)
    if new_slug is not None:
        slug = new_slug
    qs = Country.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_country_slug(instance, new_slug=new_slug)
    return slug

def presave_country(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_country_slug(instance)

pre_save.connect(presave_country, sender=Country)


# Town

class Town(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    town_name = models.CharField(max_length=50)
    town_code = models.CharField(max_length=50)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.town_name

def create_town_slug(instance, new_slug=None):
    slug = slugify(instance.town_name)
    if new_slug is not None:
        slug = new_slug
    qs = Town.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_town_slug(instance, new_slug=new_slug)
    return slug

def presave_town(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_town_slug(instance)

pre_save.connect(presave_town, sender=Town)


# Areas

# inputed in the database following this order:
# From the town center the the areas following each other are inputed going to the East then to the west then north and south

class Area(models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    latitude_coordinate = models.CharField(max_length=50, null=True, blank=True)
    longitude_coordinate = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.name

def create_area_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Area.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_area_slug(instance, new_slug=new_slug)
    return slug

def presave_area(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_area_slug(instance)

pre_save.connect(presave_area, sender=Area)


# Routes

class Route(models.Model):
    name = models.CharField(max_length=50)
    point_a = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='route_point_one')
    point_b = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='route_point_two')
    taxi_price = models.IntegerField()
    motorbike_price = models.IntegerField()
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.name

def create_route_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Route.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_route_slug(instance, new_slug=new_slug)
    return slug

def presave_route(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_route_slug(instance)

pre_save.connect(presave_route, sender=Route)


# users

class SystemUser(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)    
    town = models.ForeignKey(Town, on_delete=models.CASCADE, related_name='user_town', null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='user_country', null=True, blank=True)
    profile_image = models.FileField(null=True, blank=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=500, null=True, blank=True)
    tel1 = models.CharField(max_length=20, null=True, blank=True)
    tel2 = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_car_driver = models.BooleanField(default=False)
    is_motorbike_driver = models.BooleanField(default=False)
    is_available_to_driver = models.BooleanField(default=False)
    current_area_location = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    brief_bio = models.CharField(max_length=500, null=True, blank=True)
    role_in_company = models.CharField(max_length=50, null=True, blank=True)
    employee_ranking = models.IntegerField(default=0)
    profession = models.CharField(max_length=50, null=True, blank=True)
    rating = models.IntegerField(default=5)
    number_of_ratings = models.IntegerField(default=0)
    number_of_raters = models.IntegerField(default=0)
    facebook_profile_link = models.URLField(null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    twitter_profile_link = models.URLField(null=True, blank=True)
    active = models.BooleanField(default=True)
    registered_for_newsletter = models.BooleanField(default=False)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    deleted = models.BooleanField(default=False)
    deleted_on_date_time = models.DateTimeField(blank=True, null=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.first_name

def create_system_user_slug(instance, new_slug=None):
    slug = slugify(instance.first_name)
    if new_slug is not None:
        slug = new_slug
    qs = SystemUser.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_system_user_slug(instance, new_slug=new_slug)
    return slug

def presave_system_user(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_system_user_slug(instance)

pre_save.connect(presave_system_user, sender=SystemUser)


# Vehicle Brands

class VehicleBrand(models.Model):
    brand = models.CharField(max_length=50)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.brand

def create_vehicle_brand_slug(instance, new_slug=None):
    slug = slugify(instance.brand)
    if new_slug is not None:
        slug = new_slug
    qs = VehicleBrand.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_vehicle_brand_slug(instance, new_slug=new_slug)
    return slug

def presave_vehicle_brand(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_vehicle_brand_slug(instance)

pre_save.connect(presave_vehicle_brand, sender=VehicleBrand)


# Vehicles

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=50)
    brand = models.ForeignKey(VehicleBrand, on_delete=models.CASCADE)
    description = RichTextField()
    rating = models.IntegerField(default=5)
    number_of_ratings = models.IntegerField(default=0)
    number_of_raters = models.IntegerField(default=0)
    owner = models.ForeignKey(SystemUser, on_delete=models.CASCADE, related_name='vehicle_owner')
    added_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, related_name="vehicle_added_by")
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.plate_number

def create_vehicle_slug(instance, new_slug=None):
    slug = slugify(instance.plate_number)
    if new_slug is not None:
        slug = new_slug
    qs = Vehicle.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_vehicle_slug(instance, new_slug=new_slug)
    return slug

def presave_vehicle(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_vehicle_slug(instance)

pre_save.connect(presave_vehicle, sender=Vehicle)


# Trips

class Trip(models.Model):    
    code = models.CharField(max_length=50)
    starting_point = models.ForeignKey(Area, on_delete=models.CASCADE)
    starting_point_latitude = models.CharField(max_length=50, blank=True, null=True)
    starting_point_longitude = models.CharField(max_length=50, blank=True, null=True)
    arriving_point_latitude = models.CharField(max_length=50, blank=True, null=True)
    arriving_point_longitude = models.CharField(max_length=50, blank=True, null=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    price = models.IntegerField()
    client = models.ForeignKey(SystemUser, on_delete=models.CASCADE, related_name='request_by_client')
    is_taxi_trip = models.BooleanField(default=True)
    is_motorbike_trip = models.BooleanField(default=True)
    is_new_request = models.BooleanField(default=True)
    request_accepted = models.BooleanField(default=False)
    request_accepted_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, related_name='request_picked_by_driver', blank=True, null=True)
    request_accepted_on_date_time = models.DateTimeField(blank=True, null=True)
    trip_started = models.BooleanField(default=False)
    trip_started_on_date_time = models.DateTimeField(blank=True, null=True)
    trip_finished = models.BooleanField(default=False)
    trip_finished_on_date_time = models.DateTimeField(blank=True, null=True)
    trip_cancelled = models.BooleanField(default=False)
    trip_cancelled_on_date_time = models.DateTimeField(blank=True, null=True)
    client_trip_rating = models.IntegerField(default=0)
    driver_trip_rating = models.IntegerField(default=0)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    request_started_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.code

def create_trip_slug(instance, new_slug=None):
    slug = slugify(instance.code)
    if new_slug is not None:
        slug = new_slug
    qs = Trip.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_trip_slug(instance, new_slug=new_slug)
    return slug

def presave_trip(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_trip_slug(instance)

pre_save.connect(presave_trip, sender=Trip)


# Contacted Drivers

class ContactedDrivers(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    contacted_driver = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.slug

def create_contacted_drivers_slug(instance, new_slug=None):
    
    trip_code = instance.trip.code
    contacted_driver_first_name = instance.contacted_driver.first_name
    contacted_driver_last_name = instance.contacted_driver.last_name

    created_slug = trip_code+'-'+contacted_driver_first_name+'-'+contacted_driver_last_name

    slug = slugify(created_slug)
    if new_slug is not None:
        slug = new_slug
    qs = ContactedDrivers.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_contacted_drivers_slug(instance, new_slug=new_slug)
    return slug

def presave_contacted_drivers(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_contacted_drivers_slug(instance)

pre_save.connect(presave_contacted_drivers, sender=ContactedDrivers)


# company details

class CompanyDetails(models.Model):
    company_name = models.CharField(max_length=50)
    slogan = models.CharField(max_length=100)
    company_description = RichTextField()
    short_description = models.CharField(max_length=500)
    company_logo = models.FileField(validators=[validate_file_extension])
    about_image = models.FileField(validators=[validate_file_extension])
    email = models.EmailField(max_length=50)
    tel1 = models.CharField(max_length=20)
    tel2 = models.CharField(max_length=20, null=True, blank=True)
    mission = models.CharField(max_length=500)
    vision = models.CharField(max_length=250)
    values = RichTextField()
    whatsapp_system_use_instructions = RichTextField()
    list_of_registered_areas = models.CharField(max_length=1500)
    address = models.CharField(max_length=150, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    director = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    facebook_profile_link = models.URLField(null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    twitter_profile_link = models.URLField(null=True, blank=True)
    youtube_profile_link = models.URLField(null=True, blank=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.company_name

def create_company_details_slug(instance, new_slug=None):
    slug = slugify(instance.company_name)
    if new_slug is not None:
        slug = new_slug
    qs = CompanyDetails.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_company_details_slug(instance, new_slug=new_slug)
    return slug

def presave_company_details(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_company_details_slug(instance)

pre_save.connect(presave_company_details, sender=CompanyDetails)


# our partners

class OurPartners(models.Model):
    company_name = models.CharField(max_length=50)
    company_logo = models.FileField(validators=[validate_file_extension])
    email = models.EmailField(max_length=50, null=True, blank=True)
    tel1 = models.CharField(max_length=20, null=True, blank=True)
    tel2 = models.CharField(max_length=20, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    town = models.ForeignKey(Town, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    facebook_profile_link = models.URLField(null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    twitter_profile_link = models.URLField(null=True, blank=True)
    profile_website_link = models.URLField(null=True, blank=True)
    representative = models.ForeignKey(SystemUser, on_delete=models.CASCADE, related_name="company_representative", null=True, blank=True)
    added_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, related_name="company_added_by", null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.company_name

def create_our_partners_slug(instance, new_slug=None):
    slug = slugify(instance.company_name)
    if new_slug is not None:
        slug = new_slug
    qs = OurPartners.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_our_partners_slug(instance, new_slug=new_slug)
    return slug

def presave_our_partners(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_our_partners_slug(instance)

pre_save.connect(presave_our_partners, sender=OurPartners)


# Slider

class Slider(models.Model):
    title = models.CharField(max_length=57)
    sub_title = models.CharField(max_length=57)
    rank = models.IntegerField()
    image = models.FileField(validators=[validate_file_extension])
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

def create_slider_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Slider.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_slider_slug(instance, new_slug=new_slug)
    return slug

def presave_slider(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slider_slug(instance)

pre_save.connect(presave_slider, sender=Slider)


# Testimony

class Testimony(models.Model):
	testifier = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
	review = models.CharField(max_length=250)
	active = models.BooleanField(default=True)
	first_in_the_list = models.BooleanField(default=False)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	generated_code_from = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	code_length = 30
	generated_slug = ""

	for i in range(code_length):
		next_index = random.randrange(len(generated_code_from))
		generated_slug = generated_slug + generated_code_from[next_index]

def create_testimony_slug(instance, new_slug=None):
	slug = slugify(instance.generated_slug)
	if new_slug is not None:
		slug = new_slug
	qs = Testimony.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_testimony_slug(instance, new_slug=new_slug)
	return slug

def presave_testimony(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_testimony_slug(instance)

pre_save.connect(presave_testimony, sender=Testimony)


# News

class News(models.Model):
    title = models.CharField(max_length=50)
    short_description = models.CharField(max_length=350)
    news = RichTextField()
    image = models.FileField()
    is_breaking_news = models.BooleanField(default=True)
    posted_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    number_of_comments = models.IntegerField(default=0)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    posted_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

def create_news_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = News.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_news_slug(instance, new_slug=new_slug)
	return slug

def presave_news(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_news_slug(instance)

pre_save.connect(presave_news, sender=News)


# News Comments

class NewsComment(models.Model):
	news = models.ForeignKey(News, on_delete=models.CASCADE, null=True, blank=True)
	commented_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
	comment = models.CharField(max_length=250)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	generated_code_from = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	code_length = 30
	generated_slug = ""

	for i in range(code_length):
		next_index = random.randrange(len(generated_code_from))
		generated_slug = generated_slug + generated_code_from[next_index]

def create_news_comment_slug(instance, new_slug=None):
	slug = slugify(instance.generated_slug)
	if new_slug is not None:
		slug = new_slug
	qs = NewsComment.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_news_comment_slug(instance, new_slug=new_slug)
	return slug

def presave_news_comment(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_news_comment_slug(instance)

pre_save.connect(presave_news_comment, sender=NewsComment)


# Gallery Category

class GalleryCategory(models.Model):
	category = models.CharField(max_length=50)
	active = models.BooleanField(default=True)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.category

def create_gallery_category_slug(instance, new_slug=None):
	slug = slugify(instance.category)
	if new_slug is not None:
		slug = new_slug
	qs = GalleryCategory.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_gallery_category_slug(instance, new_slug=new_slug)
	return slug

def presave_gallery_category(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_gallery_category_slug(instance)

pre_save.connect(presave_gallery_category, sender=GalleryCategory)


# Gallery

class Gallery(models.Model):
	category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	image = models.FileField()
	active = models.BooleanField(default=True)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.title

def create_gallery_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = Gallery.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_gallery_slug(instance, new_slug=new_slug)
	return slug

def presave_gallery(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_gallery_slug(instance)

pre_save.connect(presave_gallery, sender=Gallery)


# Our Services

class OurService(models.Model):
    title = models.CharField(max_length=50)
    image = models.FileField()
    short_description = models.CharField(max_length=100)
    description = RichTextField()
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

def create_our_service_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = OurService.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_our_service_slug(instance, new_slug=new_slug)
	return slug

def presave_our_service(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_our_service_slug(instance)

pre_save.connect(presave_our_service, sender=OurService)


# Events

class Event(models.Model):
	formateur = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
	title = models.CharField(max_length=75)
	from_datetime = models.DateTimeField()
	to_datetime = models.DateTimeField()
	venue = models.CharField(max_length=150)
	brief_description = models.CharField(max_length=150)
	description = RichTextField()
	image = models.FileField()
	seats_limit = models.IntegerField()
	image_thumb = models.FileField()
	upcoming = models.BooleanField(default=True)
	reached_percecntage_goal = models.IntegerField(default=0)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.title

def create_event_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = Event.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_event_slug(instance, new_slug=new_slug)
	return slug

def presave_event(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_event_slug(instance)

pre_save.connect(presave_event, sender=Event)


# Event Participants

class EventParticipant(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
	participant = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
	message = models.CharField(max_length=250)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	registered_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	generated_code_from = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	code_length = 30
	generated_slug = ""

	for i in range(code_length):
		next_index = random.randrange(len(generated_code_from))
		generated_slug = generated_slug + generated_code_from[next_index]

def create_event_participant_slug(instance, new_slug=None):
	slug = slugify(instance.generated_slug)
	if new_slug is not None:
		slug = new_slug
	qs = EventParticipant.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_event_participant_slug(instance, new_slug=new_slug)
	return slug

def presave_event_participant(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_event_participant_slug(instance)

pre_save.connect(presave_event_participant, sender=EventParticipant)


# Event Participants waiting list

class EventParticipantWaitingList(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
	participant = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
	message = models.CharField(max_length=250)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	registered_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	generated_code_from = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	code_length = 30
	generated_slug = ""

	for i in range(code_length):
		next_index = random.randrange(len(generated_code_from))
		generated_slug = generated_slug + generated_code_from[next_index]

def create_event_participant_waiting_list_slug(instance, new_slug=None):
	slug = slugify(instance.generated_slug)
	if new_slug is not None:
		slug = new_slug
	qs = EventParticipantWaitingList.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_event_participant_waiting_list_slug(instance, new_slug=new_slug)
	return slug

def presave_event_participant_waiting_list(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_event_participant_waiting_list_slug(instance)

pre_save.connect(presave_event_participant_waiting_list, sender=EventParticipantWaitingList)


# Event Comments

class EventComment(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
	commented_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
	comment = models.CharField(max_length=250)
	slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
	added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	generated_code_from = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	code_length = 30
	generated_slug = ""

	for i in range(code_length):
		next_index = random.randrange(len(generated_code_from))
		generated_slug = generated_slug + generated_code_from[next_index]

def create_event_comment_slug(instance, new_slug=None):
	slug = slugify(instance.generated_slug)
	if new_slug is not None:
		slug = new_slug
	qs = EventComment.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_event_comment_slug(instance, new_slug=new_slug)
	return slug

def presave_event_comment(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_event_comment_slug(instance)

pre_save.connect(presave_event_comment, sender=EventComment)


# Our Products Categories

class OurProductCategory(models.Model):
    category = models.CharField(max_length=150)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    posted_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.category

def create_our_product_category_slug(instance, new_slug=None):
    slug = slugify(instance.category)
    if new_slug is not None:
        slug = new_slug
    qs = OurProductCategory.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_our_product_category_slug(instance, new_slug=new_slug)
    return slug

def presave_our_product_category(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_our_product_category_slug(instance)

pre_save.connect(presave_our_product_category, sender=OurProductCategory)


# Our Product

class OurProduct(models.Model):
    category = models.ForeignKey(OurProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(validators=[validate_file_extension])
    title = models.CharField(max_length=150)
    price = models.CharField(max_length=50)
    description = RichTextField()
    active = models.BooleanField(default=True)
    added_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

def create_our_product_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = OurProduct.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_our_product_slug(instance, new_slug=new_slug)
    return slug

def presave_our_product(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_our_product_slug(instance)

pre_save.connect(presave_our_product, sender=OurProduct)


# Client Product Category

class ClientProductCategory(models.Model):
    category = models.CharField(max_length=150)
    reference_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    posted_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.category

def create_client_product_category_slug(instance, new_slug=None):
    slug = slugify(instance.category)
    if new_slug is not None:
        slug = new_slug
    qs = ClientProductCategory.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_client_product_category_slug(instance, new_slug=new_slug)
    return slug

def presave_client_product_category(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_client_product_category_slug(instance)

pre_save.connect(presave_client_product_category, sender=ClientProductCategory)


# Client Product

class ClientProduct(models.Model):
    category = models.ForeignKey(ClientProductCategory, on_delete=models.CASCADE)
    image = models.FileField(validators=[validate_file_extension])
    title = models.CharField(max_length=150)
    code = models.CharField(max_length=25)
    price = models.IntegerField()
    description = RichTextField()
    active = models.BooleanField(default=True)
    added_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

def create_client_product_slug(instance, new_slug=None):
    slug = slugify(instance.code)
    if new_slug is not None:
        slug = new_slug
    qs = ClientProduct.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_client_product_slug(instance, new_slug=new_slug)
    return slug

def presave_client_product(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_client_product_slug(instance)

pre_save.connect(presave_client_product, sender=ClientProduct)


# Product Owner

class ProductOwner(models.Model):
    product = models.ForeignKey(ClientProduct, on_delete=models.CASCADE)
    owner = models.ForeignKey(OurPartners, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    added_by = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.slug

def create_product_owner_slug(instance, new_slug=None):

    product_name  = instance.product.title
    owner = instance.owner.company_name

    created_slug = product_name+"-"+owner

    slug = slugify(created_slug)
    if new_slug is not None:
        slug = new_slug
    qs = ProductOwner.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_product_owner_slug(instance, new_slug=new_slug)
    return slug

def presave_product_owner(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_product_owner_slug(instance)

pre_save.connect(presave_product_owner, sender=ProductOwner)


# Order

class Order(models.Model):
    code = models.CharField(max_length=50)
    client = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    placed_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.code

def create_order_slug(instance, new_slug=None):
    slug = slugify(instance.code)
    if new_slug is not None:
        slug = new_slug
    qs = Order.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_order_slug(instance, new_slug=new_slug)
    return slug

def presave_order(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_order_slug(instance)

pre_save.connect(presave_order, sender=Order)


# Ordered Product

class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ClientProduct, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    ordered_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.slug

def create_ordered_product_slug(instance, new_slug=None):

    order_code = instance.order.code
    product_name = instance.product.title

    formed_slug = order_code+'-'+product_name

    slug = slugify(formed_slug)
    if new_slug is not None:
        slug = new_slug
    qs = OrderedProduct.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_ordered_product_slug(instance, new_slug=new_slug)
    return slug

def presave_ordered_product(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_ordered_product_slug(instance)

pre_save.connect(presave_ordered_product, sender=OrderedProduct)


# Product Owner Call

class ProductOwnerCall(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    partner = models.ForeignKey(OurPartners, on_delete=models.CASCADE)
    order_fulfilled = models.BooleanField(default=False)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    ordered_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.slug

def create_product_owner_call_slug(instance, new_slug=None):
    order_code = instance.order.code
    partner_name = instance.partner.company_name

    formed_slug = order_code+'-'+partner_name

    slug = slugify(formed_slug)
    if new_slug is not None:
        slug = new_slug
    qs = ProductOwnerCall.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_product_owner_call_slug(instance, new_slug=new_slug)
    return slug

def presave_product_owner_call(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_product_owner_call_slug(instance)

pre_save.connect(presave_product_owner_call, sender=ProductOwnerCall)


# Messages

class Message(models.Model):
    full_name = models.CharField(max_length=100)
    # from_user_last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    subject = models.CharField(max_length=50, null=True, blank=True)
    message = RichTextField()
    attended = models.BooleanField(default=False)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    sent_on_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.full_name

def create_message_slug(instance, new_slug=None):
	slug = slugify(instance.full_name)
	if new_slug is not None:
		slug = new_slug
	qs = Message.objects.filter(slug=slug).order_by('id')
	exists = qs.exists()
	if exists:
		new_slug = '%s-%s' % (slug, qs.first().id)
		return create_message_slug(instance, new_slug=new_slug)
	return slug

def presave_message(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_message_slug(instance)

pre_save.connect(presave_message, sender=Message)


# Test

class Test(models.Model):
    test = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.test

def create_test_slug(instance, new_slug=None):
    slug = slugify(instance.test)
    if new_slug is not None:
        slug = new_slug
    qs = Test.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_test_slug(instance, new_slug=new_slug)
    return slug

def presave_test(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_test_slug(instance)

pre_save.connect(presave_test, sender=Test)


# ErrorMesage

class ErrorMesage(models.Model):
    user_message = models.CharField(max_length=500)
    error_message = models.CharField(max_length=500)
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.slug

    generated_code_from = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code_length = 20
    generated_slug = ""

    for i in range(code_length):
        next_index = random.randrange(len(generated_code_from))
        generated_slug = generated_slug + generated_code_from[next_index]

def create_error_mesage_slug(instance, new_slug=None):
    slug = slugify(instance.generated_slug)
    if new_slug is not None:
        slug = new_slug
    qs = ErrorMesage.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_error_mesage_slug(instance, new_slug=new_slug)
    return slug

def presave_error_mesage(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_error_mesage_slug(instance)

pre_save.connect(presave_error_mesage, sender=ErrorMesage)


# User Whatsapp Message

class UserWhatsappMessage(models.Model):
    user_number = models.CharField(max_length=50)
    message = RichTextField()
    response = RichTextField()
    slug = models.SlugField(max_length=5000, null=True, blank=True, unique=True)
    added_on_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.user_number

def create_user_whatsapp_message_slug(instance, new_slug=None):
    slug = slugify(instance.user_number)
    if new_slug is not None:
        slug = new_slug
    qs = UserWhatsappMessage.objects.filter(slug=slug).order_by('id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_user_whatsapp_message_slug(instance, new_slug=new_slug)
    return slug

def presave_user_whatsapp_message(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_user_whatsapp_message_slug(instance)

pre_save.connect(presave_user_whatsapp_message, sender=UserWhatsappMessage)
