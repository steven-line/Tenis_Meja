from django.db import models
from django.contrib.auth.models import User 
from django.db.models import F
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import time


class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    image_title = models.CharField(max_length=255)
    image_file = models.ImageField(upload_to='uploads/')
    description = models.TextField(blank=True, null=True)  
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.image_title

    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile" 
    
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='forum_images/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class Announcement(models.Model):
    title = models.CharField(blank=False, max_length=50)
    message = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TournamentSchedule(models.Model):
    day = models.CharField(max_length=10)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.day}, {self.date} at {self.venue}"

class TournamentRegistration(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    tournament_type = models.CharField(max_length=50, choices=[('Individu', 'Individu'), ('Ganda', 'Ganda')])
    division = models.CharField(max_length=50, choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')])
    tournament_schedule = models.ForeignKey(TournamentSchedule, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.tournament_type} ({self.division})"


class Player(models.Model):
    name = models.CharField(max_length=100)
    points = models.IntegerField(default=0)  
    city = models.CharField(max_length=100)
    rank = models.IntegerField(null=True, blank=True)  
    previous_rank = models.IntegerField(null=True, blank=True)  

    def save(self, *args, **kwargs):
        if self.pk:
            previous_instance = Player.objects.filter(pk=self.pk).first()
            if previous_instance:
                self.previous_rank = previous_instance.rank

        super().save(*args, **kwargs)
        self.update_player_ranks()  

    @classmethod
    def update_player_ranks(cls):
        players = cls.objects.all().order_by('-points')  
        for index, player in enumerate(players, start=1):
            player.rank = index
        cls.objects.bulk_update(players, ['rank']) 

    def rank_change(self):
        if self.previous_rank is not None and self.rank is not None:
            change = self.previous_rank - self.rank
            if change > 0:
                return f"▲ {change}"
            elif change < 0:
                return f"▼ {abs(change)}"
        return "−"

    def __str__(self):
        return f"{self.name} - Rank: {self.rank}, Points: {self.points}" 

class PlayerRankingHistory(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    points_before = models.IntegerField()
    points_after = models.IntegerField()
    rank_before = models.IntegerField()
    rank_after = models.IntegerField()
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"History for {self.player.name} - {self.changed_at}"


class TrainingSchedule(models.Model):
    day = models.CharField(max_length=20)
    date = models.DateField(max_length=15)
    time = models.TimeField()
    venue = models.CharField(max_length=100)

    def clean(self):
        # Contoh validasi: waktu pelatihan harus antara 08:00 - 22:00
        if not (time(8, 0) <= self.time <= time(22, 0)):
            raise ValidationError("Training time must be between 08:00 and 22:00.")

    def __str__(self):
        return f"{self.day}, {self.date} - {self.venue}"
    # models.py
from django.db import models

class RegistrationRequest(models.Model):
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    # Tambahkan field untuk payment gateway
    order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='pending')  # pending/success/failed
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100000)  # Rp100.000
    payment_proof = models.URLField(blank=True, null=True)  # Untuk menyimpan URL bukti pembayaran dari gateway
    midtrans_response = models.JSONField(blank=True, null=True)  # Menyimpan raw response dari Midtrans

    def __str__(self):
        return f"{self.full_name} - {self.email}"

    def generate_order_id(self):
        if not self.order_id:
            self.order_id = f"REG-{self.id}-{uuid.uuid4().hex[:6]}"
            self.save()
        return self.order_id


