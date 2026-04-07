from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, ProfileEditForm


def landing(request):
    if request.user.is_authenticated:
        return redirect('browse_projects')
    return render(request, 'landing.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                gender=form.cleaned_data['gender'],
                bio=form.cleaned_data.get('bio', ''),
                resume=form.cleaned_data.get('resume'),
                terms_accepted=form.cleaned_data['terms_accepted'],
            )
            login(request, user)
            return redirect('browse_projects')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard(request):
    user_projects = request.user.projects.all().order_by('-created_at')
    user_applications = request.user.applications.select_related(
        'role', 'project'
    ).order_by('-applied_at')
    return render(request, 'users/dashboard.html', {
        'user_projects': user_projects,
        'user_applications': user_applications,
    })


@login_required
def profile(request):
    profile_obj = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile_obj, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'users/profile.html', {'form': form})