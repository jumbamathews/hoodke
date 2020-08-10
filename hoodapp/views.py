import folium
import random
import string
from django.shortcuts import render, redirect
from django.http  import HttpResponse,Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from .email import send_signup_email_admin, send_signup_email_resident
from .models import Admin_Profile, Neighbourhood, Resident_Profile, Facility, Business, Post
from .forms import AdminProfileForm, NeighbourhoodForm, AddResidentForm, FacilityForm, ChangePasswordForm, BusinessForm, MakePostForm

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
    current_user = request.user
    admin_profile = None
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        pass

    resident_profile = None
    try:
        resident_profile = Resident_Profile.objects.get(this_user = current_user)
    except Resident_Profile.DoesNotExist:
        pass

    if admin_profile:
        return redirect(my_admin_profile)
    elif resident_profile:
        return redirect(my_user_profile)
    else:
        raise Http404    

@login_required(login_url='/accounts/login/')
def send_email(request):
    current_user = request.user
    email = current_user.email
    name = current_user.username
    send_signup_email_admin(name, email)
    return redirect(create_profile_admin)


@login_required(login_url='/accounts/login/')
def create_profile_admin(request):
    current_user = request.user
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.this_user = current_user
            profile.save()
        return redirect(create_hood)

    else:
        form = AdminProfileForm()
      
    title = "Admin profile "
    return render(request, 'create-profile-admin.html', {"form": form, "title": title})


@login_required(login_url='/accounts/login/')
def create_hood(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()

    my_hood = None
    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        pass

    if my_hood:
        return redirect(my_admin_profile)

    if request.method == 'POST':
        form = NeighbourhoodForm(request.POST)
        if form.is_valid():
            hood = form.save(commit=False)
            hood.admin = admin_profile
            hood.save()
        return redirect(my_admin_profile)

    else:
        form = NeighbourhoodForm()
      
    title = "Create Hood"
    return render(request, 'create-hood.html', {"form": form, "title": title})


@login_required(login_url='/accounts/login/')
def my_admin_profile(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()

    my_hood =None
    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        raise Http404()

    if my_hood:
        longitude = my_hood.location[0]
        latitude = my_hood.location[1]
    

    m = folium.Map(location=[latitude, longitude], zoom_start=16)
    folium.Marker([latitude,longitude],
                    popup='<h5>My neighbourhood.</h5>',
                    tooltip=f'{my_hood.hood_name}',
                    icon=folium.Icon(icon='glyphicon-home', color='blue')).add_to(m),
    hospitals = Facility.objects.filter(category='hospital', hood=my_hood)
    police_posts = Facility.objects.filter(category='police', hood=my_hood)
    businesses = Business.objects.filter(hood=my_hood)
    for hospital in hospitals:
        hosp_longitude = hospital.location[0]
        hosp_latitude = hospital.location[1]
        folium.Marker([hosp_latitude,hosp_longitude],
                    popup=f'<p>{hospital.contact}</p>',
                    tooltip=f'{hospital.facility_name}',
                    icon=folium.Icon(icon='glyphicon-plus-sign', color='purple')).add_to(m), 
    for post in police_posts:
        post_longitude = post.location[0]
        post_latitude = post.location[1]
        folium.Marker([post_latitude,post_longitude],
                    popup=f'<p>{post.contact}</p>',
                    tooltip=f'{post.facility_name}',
                    icon=folium.Icon(icon='glyphicon-flag', color='darkgreen')).add_to(m), 
    for business in businesses:
        biz_longitude = business.location[0]
        biz_latitude = business.location[1]
        folium.Marker([biz_latitude,biz_longitude],
                    popup=f'<p>{business.business_name}</p>',
                    tooltip=f'{business.business_email}',
                    icon=folium.Icon(icon='glyphicon-shopping-cart', color='darkred')).add_to(m), 

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=200,
        popup=f'{my_hood.hood_name}',
        color='#428bca',
        fill=True,
        fill_color='#428bca'
    ).add_to(m),

    map_page = m._repr_html_() 

    posts = Post.objects.filter(hood=my_hood).order_by("-created") 
      
    title = admin_profile.this_user.username
    return render(request, 'my-admin-profile.html', {"profile": admin_profile, "title": title, "hood": my_hood, "map_page":map_page, "posts":posts})


@login_required(login_url='/accounts/login/')
def add_resident(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()

    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        raise Http404()

    if request.method == 'POST':
        form = AddResidentForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            this_resident =User.objects.create_user(username, email, password)
            resident_profile = Resident_Profile(full_name=name, this_user=this_resident, username=username, hood=my_hood)
            resident_profile.save()
            my_hood.occupants_count = len(Resident_Profile.objects.filter(hood = my_hood))+1
            my_hood.save()
            send_signup_email_resident(name, username, password,admin_profile.full_name, my_hood.hood_name, email)
            
        return redirect(my_admin_profile)

    else:
        form = AddResidentForm()
      
    title = "Add resident"
    return render(request, 'add-resident.html', {"form": form, "title": title})


@login_required(login_url='/accounts/login/')
def update_hood(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()
    
    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        pass

    if request.method == 'POST':
        form = NeighbourhoodForm(request.POST)
        if form.is_valid():
            my_hood.hood_name = form.cleaned_data['hood_name']
            my_hood.location = form.cleaned_data['location']
            my_hood.save()
        return redirect(my_admin_profile)

    else:
        form = NeighbourhoodForm()
      
    title = "Update Hood"
    return render(request, 'update-hood.html', {"form": form, "title": title})



@login_required(login_url='/accounts/login/')
def delete_hood(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()
    
    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        pass

    admin_profile.delete()
    current_user.delete()

    return redirect(index)



@login_required(login_url='/accounts/login/')
def add_facility(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()
    
    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        pass    

    if request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            facility = form.save(commit=False)
            facility.hood = my_hood
            facility.save()
        return redirect(my_admin_profile)

    else:
        form = FacilityForm()
      
    title = "Add Facility"
    return render(request, 'add-facility.html', {"form": form, "title": title})



@login_required(login_url='/accounts/login/')
def my_user_profile(request):
    current_user = request.user
    try:
        resident_profile = Resident_Profile.objects.get(this_user = current_user)
    except Resident_Profile.DoesNotExist:
        raise Http404()

    my_hood = resident_profile.hood
    longitude = my_hood.location[0]
    latitude = my_hood.location[1]       

    m = folium.Map(location=[latitude, longitude], zoom_start=16)
    folium.Marker([latitude,longitude],
                    popup='<h5>My neighbourhood.</h5>',
                    tooltip=f'{my_hood.hood_name}',
                    icon=folium.Icon(icon='glyphicon-home', color='blue')).add_to(m),
    hospitals = Facility.objects.filter(category='hospital', hood=my_hood)
    police_posts = Facility.objects.filter(category='police', hood=my_hood)
    businesses = Business.objects.filter(hood=my_hood)
    for hospital in hospitals:
        hosp_longitude = hospital.location[0]
        hosp_latitude = hospital.location[1]
        folium.Marker([hosp_latitude,hosp_longitude],
                    popup=f'<p>{hospital.contact}</p>',
                    tooltip=f'{hospital.facility_name}',
                    icon=folium.Icon(icon='glyphicon-plus-sign', color='purple')).add_to(m), 
    for post in police_posts:
        post_longitude = post.location[0]
        post_latitude = post.location[1]
        folium.Marker([post_latitude,post_longitude],
                    popup=f'<p>{post.contact}</p>',
                    tooltip=f'{post.facility_name}',
                    icon=folium.Icon(icon='glyphicon-flag', color='darkgreen')).add_to(m), 
    for business in businesses:
        biz_longitude = business.location[0]
        biz_latitude = business.location[1]
        folium.Marker([biz_latitude,biz_longitude],
                    popup=f'<p>{business.business_email}</p>',
                    tooltip=f'{business.business_name}',
                    icon=folium.Icon(icon='glyphicon-shopping-cart', color='darkred')).add_to(m), 

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=200,
        popup=f'{my_hood.hood_name}',
        color='#428bca',
        fill=True,
        fill_color='#428bca'
    ).add_to(m),

    map_page = m._repr_html_()  

    posts = Post.objects.filter(hood=my_hood).order_by("-created")
      
    title = resident_profile.username
    return render(request, 'my-user-profile.html', {"profile": resident_profile, "title": title, "hood": my_hood, "map_page":map_page, "posts":posts})


@login_required(login_url='/accounts/login/')
def delete_resident_profile(request):
    current_user = request.user
    try:
        resident_profile = Resident_Profile.objects.get(this_user = current_user)
    except Resident_Profile.DoesNotExist:
        raise Http404()
    resident_profile.delete()
    current_user.delete()
    
    return redirect(index)


@login_required(login_url='/accounts/login/')
def change_password(request):
    current_user = request.user    

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_pass = form.cleaned_data['old_password']
            new_pass = form.cleaned_data['new_password']
            confirm_pass = form.cleaned_data['confirm_password']
            user = authenticate(username=current_user.username, password=old_pass)
            if user is not None:
                if new_pass == confirm_pass:
                    current_user.set_password(new_pass)
                    current_user.save()
                    messages.success(request, 'Your password was updated successfully!')
                    return redirect(my_user_profile)
                else:
                    messages.warning(request, 'Your passwords did not match.')
                
            else:
                messages.warning(request, 'Your old password is incorrect.')    

    else:
        form = ChangePasswordForm()
      
    title = "Change password"
    return render(request, 'change-password.html', {"form": form, "title": title})


@login_required(login_url='/accounts/login/')
def change_profile_photo(request):
    current_user = request.user
    try:
        profile = Resident_Profile.objects.get(this_user = current_user)
    except Resident_Profile.DoesNotExist:
        raise Http404()
    
    if request.method == 'POST':
        profile.profile_photo = request.FILES['img']        
        profile.save()
        return redirect(my_user_profile)

    title = "Profile photo"    
    return render(request, 'update-prof-pic.html', {"title": title})



@login_required(login_url='/accounts/login/')
def add_business(request):
    current_user = request.user
    try:
        resident_profile = Resident_Profile.objects.get(this_user = current_user)
    except Resident_Profile.DoesNotExist:
        raise Http404()
    
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            business.hood = resident_profile.hood
            business.owner = current_user
            business.save()
        return redirect(my_user_profile)

    else:
        form = BusinessForm()
      
    title = "Add Business"
    return render(request, 'add-business.html', {"form": form, "title": title})


@login_required(login_url='/accounts/login/')
def make_post(request):
    current_user = request.user
    try:
        resident_profile = Resident_Profile.objects.get(this_user = current_user)                
    except Resident_Profile.DoesNotExist:
        raise Http404()   

    if request.method == 'POST':
        form = MakePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.posted_by = resident_profile  
            post.hood = resident_profile.hood         
            post.save()
        return redirect(my_user_profile)

    else:
        form = MakePostForm()
        
    title = "Add Post"
    return render(request, 'make-post.html', {"form": form, "title": title})


@login_required(login_url='/accounts/login/')
def residents_list(request):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404()
    
    try:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    except Neighbourhood.DoesNotExist:
        raise Http404()

    residents = Resident_Profile.objects.filter(hood=my_hood)

    title = "Residents"
    return render(request, 'residents-list.html', {"title": title, "residents":residents, "hood":my_hood})


@login_required(login_url='/accounts/login/')
def delete_resident(request, res_id):
    current_user = request.user
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        raise Http404() 

    try:
        resident = Resident_Profile.objects.get(pk = res_id)
    except Resident_Profile.DoesNotExist:
        raise Http404() 

    u_account=resident.this_user
    resident.delete()
    u_account.delete()   
    
    return redirect(residents_list)


@login_required(login_url='/accounts/login/')
def search_business(request):
    current_user = request.user
    admin_profile = None
    try:
        admin_profile = Admin_Profile.objects.get(this_user = current_user)
    except Admin_Profile.DoesNotExist:
        pass

    resident_profile = None
    try:
        resident_profile = Resident_Profile.objects.get(this_user = current_user)
    except Resident_Profile.DoesNotExist:
        pass

    if admin_profile:
        my_hood = Neighbourhood.objects.get(admin = admin_profile)
    elif resident_profile:
        my_hood = resident_profile.hood
    else:
        raise Http404 

    if 'searchbusiness' in request.GET and request.GET["searchbusiness"]:
        search_term = request.GET.get("searchbusiness") 
        search_businesses = Business.objects.filter(business_name__icontains = search_term, hood=my_hood)
        
        message = f"{search_term}"

        return render(request, 'search.html',{"message":message, "businesses":search_businesses})

    else:
        blank_message = "You haven't searched for any business."
        return render(request, 'search.html',{"blank_message":blank_message})