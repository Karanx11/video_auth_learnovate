from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Contact
from .forms import RegistrationForm, LoginForm, VideoUploadForm, ContactForm
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                # Update the profile created by the signal
                profile = Profile.objects.get(user=user)
                profile.full_name = form.cleaned_data['full_name']
                profile.save()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                try:
                    user_obj = User.objects.filter(email=username_or_email).first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    video_status = 'Not uploaded'
    status_info = {}
    
    if profile.video:
        video_status = profile.get_video_status_display()
        status_info = {
            'is_duplicate': profile.is_duplicate,
            'is_ai_generated': profile.is_ai_generated,
            'ai_confidence': profile.ai_confidence,
            'analysis_notes': profile.analysis_notes,
        }
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.uploaded_at = timezone.now()
            
            # Calculate and save video hash
            if profile.video:
                profile.video_hash = Profile.calculate_file_hash(profile.video)
                
                # Check for duplicates
                is_dup = Profile.check_duplicate_video(profile.video_hash)
                profile.is_duplicate = is_dup
                
                if is_dup:
                    profile.video_status = 'duplicate'
                    messages.warning(request, '⚠️ Duplicate video detected. This video already exists in the system.')
                else:
                    profile.video_status = 'pending'
                    messages.success(request, '✅ Video uploaded successfully. Pending verification.')
            
            profile.save()
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = VideoUploadForm(instance=profile)
    
    return render(request, 'dashboard.html', {
        'profile': profile,
        'video_status': video_status,
        'form': form,
        'status_info': status_info
    })


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        # Handle video upload
        if 'video' in request.FILES:
            video_file = request.FILES['video']
            # Validate using form
            form = VideoUploadForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.uploaded_at = timezone.now()
                # Calculate and save video hash
                profile.video_hash = Profile.calculate_file_hash(profile.video)
                
                # Check for duplicates
                is_dup = Profile.check_duplicate_video(profile.video_hash)
                profile.is_duplicate = is_dup
                
                if is_dup:
                    profile.video_status = 'duplicate'
                    messages.warning(request, '⚠️ Duplicate video detected!')
                else:
                    profile.video_status = 'pending'
                
                profile.is_verified = False  # Reset verification status
                profile.save()
                messages.success(request, '✅ Video uploaded and analyzed successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{error}')
        # Handle video delete
        elif 'delete_video' in request.POST:
            if profile.video:
                profile.video.delete(save=False)
                profile.video = None
                profile.video_hash = None
                profile.uploaded_at = None
                profile.is_verified = False
                profile.save()
                messages.success(request, 'Video deleted successfully!')
    return render(request, 'profile.html', {'profile': profile})

def users_list(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page. Only administrators can access the user list.')
        return redirect('home')
    users = User.objects.all().order_by('id')
    return render(request, 'users_list.html', {'users': users})

def user_detail(request, user_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page. Only administrators can access user details.')
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'user_detail.html', {'user': user, 'profile': profile})


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact = Contact(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message']
                )
                contact.save()
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('contact_us')
            except Exception as e:
                messages.error(request, f'Error submitting contact form: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ContactForm()
    return render(request, 'contact_us.html', {'form': form})
