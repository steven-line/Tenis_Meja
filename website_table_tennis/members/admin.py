from django.contrib import admin
from django import forms
from .models import TournamentRegistration
from .models import TournamentSchedule
from .models import Player
from .models import UploadedImage
from .models import Profile
from .models import TrainingSchedule
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render, redirect
from .models import Player, PlayerRankingHistory    
from django.db.models import F
from .models import RegistrationRequest, Announcement

class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('image_title', 'user', 'uploaded_at')  
    list_filter = ('user',)  
    search_fields = ('image_title', 'user__username')  

admin.site.register(UploadedImage, UploadedImageAdmin)
from django.contrib import messages
class AnnouncementModelForm(forms.ModelForm):
    def clean(self):
        if Announcement.objects.count() > 1:
           raise forms.ValidationError("Tidak boleh lebih dari 1")
     
        return self.cleaned_data

class AnnouncementAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change and Announcement.objects.count() >= 1:
            messages.error(request, "Hanya boleh ada 1 pengumuman.")
            return
        super().save_model(request, obj, form, change)
admin.site.register(Announcement, AnnouncementAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'phone_number', 'height', 'weight')

    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        (None, {
            'fields': ('user', 'address', 'phone_number', 'height', 'weight')
        }),
    )

admin.site.register(Profile, ProfileAdmin)

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('get_address', 'get_phone_number', 'get_height', 'get_weight')
    
    # Menambahkan method untuk menampilkan kolom profil di UserAdmin
    def get_address(self, obj):
        return obj.profile.address if hasattr(obj, 'profile') else 'No address'
    get_address.short_description = 'Address'

    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else 'No phone number'
    get_phone_number.short_description = 'Phone Number'

    def get_height(self, obj):
        return obj.profile.height if hasattr(obj, 'profile') else 'No height'
    get_height.short_description = 'Height'

    def get_weight(self, obj):
        return obj.profile.weight if hasattr(obj, 'profile') else 'No weight'
    get_weight.short_description = 'Weight'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(TournamentSchedule)
class TournamentScheduleAdmin(admin.ModelAdmin):
    list_display = ['day', 'date', 'start_time', 'end_time', 'venue']

@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'tournament_type', 'division', 'tournament_schedule', 'created_at']
    list_filter = ['tournament_type', 'division', 'tournament_schedule']

# forms.py (jika Anda ingin membuat form dinamis, tidak perlu diubah jika hanya menambah opsi tetap)
class AddPointsForm(forms.Form):
    points_to_add = forms.IntegerField(label='Points to Add', min_value=1, required=True)

# admin.py
def add_points_100(modeladmin, request, queryset):
    add_points_generic(modeladmin, request, queryset, 100)

def add_points_200(modeladmin, request, queryset):
    add_points_generic(modeladmin, request, queryset, 200)

def add_points_300(modeladmin, request, queryset):
    add_points_generic(modeladmin, request, queryset, 300)

def add_points_generic(modeladmin, request, queryset, points_to_add):
    for player in queryset:
        old_points = player.points
        old_rank = player.rank

        # Tambahkan poin pemain
        player.points += points_to_add
        player.save()

        # History
        history = PlayerRankingHistory(
            player=player,
            points_before=old_points,
            points_after=player.points,
            rank_before=old_rank,
            rank_after=player.rank,
            changed_by=request.user  
        )
        history.save()

    modeladmin.message_user(request, f'{queryset.count()} pemain berhasil ditambah {points_to_add} poin.')

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'points', 'city', 'rank']
    actions = [add_points_100, add_points_200, add_points_300] 

    # Untuk memberikan nama lebih user-friendly pada actions
    add_points_100.short_description = "Tambah 100 Poin"
    add_points_200.short_description = "Tambah 200 Poin"
    add_points_300.short_description = "Tambah 300 Poin"


admin.site.register(Player, PlayerAdmin)

@admin.register(TrainingSchedule)
class TrainingScheduleAdmin(admin.ModelAdmin):
    list_display = ('day', 'date', 'time', 'venue')
    list_filter = ('day', 'venue')  
    search_fields = ('day', 'venue')  
    ordering = ('date', 'time')  

    fieldsets = (
        (None, {
            'fields': ('day', 'date', 'time', 'venue'),
        }),
    )
    
admin.site.register(RegistrationRequest)
