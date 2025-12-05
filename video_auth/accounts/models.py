from django.db import models
from django.contrib.auth.models import User
import hashlib
from pathlib import Path

class Profile(models.Model):
    VIDEO_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified - Authentic'),
        ('duplicate', 'Duplicate Video'),
        ('ai_generated', 'AI-Generated Detected'),
        ('suspicious', 'Suspicious - Manual Review'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    video_hash = models.CharField(max_length=64, null=True, blank=True, unique=False)
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    video_status = models.CharField(max_length=20, choices=VIDEO_STATUS_CHOICES, default='pending')
    is_duplicate = models.BooleanField(default=False)
    is_ai_generated = models.BooleanField(default=False)
    ai_confidence = models.FloatField(default=0.0, help_text="AI detection confidence (0-100)")
    analysis_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @staticmethod
    def calculate_file_hash(file):
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        for chunk in file.chunks():
            hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    @staticmethod
    def analyze_video(file_path):
        """
        Comprehensive video analysis for:
        - Frame consistency (AI videos often have artifacts)
        - Color distribution patterns
        - Temporal inconsistencies
        - Metadata anomalies
        """
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                return {
                    'is_ai': False,
                    'confidence': 0.0,
                    'analysis': 'Could not open video file'
                }
            
            # Collect frame statistics
            frames_analyzed = 0
            frame_variance_list = []
            color_consistency_scores = []
            flicker_scores = []
            
            prev_frame = None
            frame_count = 0
            
            # Analyze up to 30 frames for performance
            while frames_analyzed < 30:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                if frame_count % 5 != 0:  # Analyze every 5th frame
                    continue
                
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate frame variance (smoother videos may indicate AI)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                frame_variance_list.append(laplacian_var)
                
                # Analyze color distribution
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])
                color_consistency = cv2.compareHist(hist, hist, cv2.HISTCMP_BHATTACHARYYA)
                color_consistency_scores.append(color_consistency)
                
                # Detect flicker (unnatural rapid changes)
                if prev_frame is not None:
                    diff = cv2.absdiff(gray, prev_frame)
                    flicker_score = np.mean(diff)
                    flicker_scores.append(flicker_score)
                
                prev_frame = gray
                frames_analyzed += 1
            
            cap.release()
            
            if not frame_variance_list:
                return {
                    'is_ai': False,
                    'confidence': 0.0,
                    'analysis': 'Insufficient frames for analysis'
                }
            
            # Calculate AI probability based on multiple factors
            ai_score = 0.0
            analysis_details = []
            
            # Factor 1: Frame variance (AI videos tend to have low variance)
            avg_variance = np.mean(frame_variance_list)
            if avg_variance < 100:
                ai_score += 20
                analysis_details.append(f"Low frame variance detected: {avg_variance:.2f}")
            
            # Factor 2: Color consistency (AI videos often have too-perfect colors)
            avg_color_consistency = np.mean(color_consistency_scores)
            if avg_color_consistency > 0.7:
                ai_score += 25
                analysis_details.append(f"High color consistency: {avg_color_consistency:.2f}")
            
            # Factor 3: Flicker analysis (AI videos have different flicker patterns)
            if flicker_scores:
                avg_flicker = np.mean(flicker_scores)
                if avg_flicker < 5 or avg_flicker > 40:
                    ai_score += 15
                    analysis_details.append(f"Unusual flicker pattern: {avg_flicker:.2f}")
            
            # Factor 4: Video metadata (AI tools often omit or generate metadata)
            try:
                cap = cv2.VideoCapture(str(file_path))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                
                # Unusual FPS or frame counts might indicate AI
                if fps not in [24, 25, 30, 60]:
                    ai_score += 10
                    analysis_details.append(f"Unusual FPS detected: {fps}")
                
                if frame_count < 30:
                    ai_score += 10
                    analysis_details.append("Very short video (potential AI generation)")
            except:
                pass
            
            # Final assessment
            is_ai = ai_score >= 50
            analysis_text = "; ".join(analysis_details) if analysis_details else "Video appears authentic"
            
            return {
                'is_ai': is_ai,
                'confidence': min(ai_score, 100),
                'analysis': analysis_text
            }
        
        except Exception as e:
            return {
                'is_ai': False,
                'confidence': 0.0,
                'analysis': f'Analysis error: {str(e)}'
            }

    @staticmethod
    def check_duplicate_video(file_hash):
        """Check if video hash already exists"""
        return Profile.objects.filter(video_hash=file_hash, is_verified=True).exists()


class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject}'
