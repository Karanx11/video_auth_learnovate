from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError
import hashlib
import tempfile
import os

VIDEO_EXTENSIONS = ['mp4', 'webm', 'mov']

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        email = email.lower().strip()
        # Check if email already exists (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('This email is already registered. Please use a different email or login with this email.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('Username is required.')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken. Please choose a different one.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match.')
        if password and len(password) < 8:
            self.add_error('password', 'Password must be at least 8 characters long.')

class LoginForm(forms.Form):
    username_or_email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['video']

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            ext = video.name.split('.')[-1].lower()
            if ext not in VIDEO_EXTENSIONS:
                raise ValidationError('Invalid file type. Allowed: mp4, webm, mov.')
            if video.size > 50 * 1024 * 1024:
                raise ValidationError('File too large (max 50MB).')
            
            # Calculate hash to detect duplicates
            video_hash = Profile.calculate_file_hash(video)
            
            # Check if this exact video already exists in the system
            if Profile.objects.filter(video_hash=video_hash).exists():
                raise ValidationError('❌ DUPLICATE DETECTED: This exact video has already been uploaded. Each upload must be unique.')
            
            # Save to temporary file for AI analysis
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    for chunk in video.chunks():
                        tmp_file.write(chunk)
                    tmp_path = tmp_file.name
                
                # Perform AI detection analysis
                analysis_result = Profile.analyze_video(tmp_path)
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                # Check if AI-generated
                if analysis_result['is_ai']:
                    confidence = analysis_result['confidence']
                    raise ValidationError(
                        f"⚠️ AI-GENERATED VIDEO DETECTED (Confidence: {confidence:.1f}%)\n"
                        f"Analysis: {analysis_result['analysis']}\n"
                        f"This system requires authentic, human-recorded videos for verification."
                    )
            
            except ValidationError:
                raise
            except Exception as e:
                # If analysis fails, continue with upload but log the error
                pass
        
        return video


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'class': 'contact-input'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'class': 'contact-input'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Subject',
            'class': 'contact-input'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Your Message',
            'class': 'contact-textarea',
            'rows': 6
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return name.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        return email.lower().strip()

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject or len(subject.strip()) < 3:
            raise ValidationError('Subject must be at least 3 characters long.')
        return subject.strip()

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or len(message.strip()) < 10:
            raise ValidationError('Message must be at least 10 characters long.')
        return message.strip()
