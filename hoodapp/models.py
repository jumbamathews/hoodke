from django.db import models
from django.contrib.auth.models import User
from mapbox_location_field.models import LocationField, AddressAutoHiddenField


# Create your models here.
class Admin_Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to = 'profilepics/', blank=True)
    full_name= models.CharField(max_length = 50)    
    bio = models.TextField()
    this_user = models.ForeignKey(User,on_delete=models.CASCADE)    

    def __str__(self):
        return self.full_name 


    
class Neighbourhood(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    hood_name = models.CharField(max_length = 50)   
    location = LocationField(map_attrs={"center": [36.82, -1.29], "marker_color": "blue"})
    address = AddressAutoHiddenField(blank=True)
    occupants_count = models.IntegerField(default=1)
    admin = models.ForeignKey(Admin_Profile,on_delete=models.CASCADE)

    def __str__(self):
        return self.hood_name 

    def create_hood(self):
        self.save()

    def delete_hood(self):
        self.delete()

    def update_hood(self):
        self.save()


    @classmethod
    def find_neigborhood(cls, neigborhood_id):
        pass

    @classmethod
    def update_occupants(cls):
        pass

    
class Resident_Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to = 'profilepics/', blank=True)
    username = models.CharField(max_length = 50) 
    full_name= models.CharField(max_length = 50)    
    bio = models.TextField(blank=True)
    this_user = models.ForeignKey(User,on_delete=models.CASCADE)
    hood = models.ForeignKey(Neighbourhood,on_delete=models.CASCADE)
    home_location = LocationField(map_attrs={"center": [36.82, -1.29], "marker_color": "blue"}, blank=True)

    def __str__(self):
        return self.full_name 


class Business(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    business_name = models.CharField(max_length = 50) 
    short_description = models.CharField(max_length = 150) 
    business_email = models.EmailField() 
    location = LocationField(map_attrs={"center": [36.82, -1.29], "marker_color": "blue"})
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    hood = models.ForeignKey(Neighbourhood,on_delete=models.CASCADE)


FACILITY_CHOICES = (
    ('police','Police Post'),
    ('hospital', 'Hospital/Healthcare center'),    
)

class Facility(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    facility_name = models.CharField(max_length = 100) 
    category = models.CharField(max_length=50, choices=FACILITY_CHOICES, default='police')
    contact = models.CharField(max_length = 100, blank=True)
    location = LocationField(map_attrs={"center": [36.82, -1.29], "marker_color": "blue"})
    hood = models.ForeignKey(Neighbourhood,on_delete=models.CASCADE)


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    posted_by = models.ForeignKey(Resident_Profile,on_delete=models.CASCADE)
    hood = models.ForeignKey(Neighbourhood,on_delete=models.CASCADE)
    