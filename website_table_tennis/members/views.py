from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import ImageUploadForm
from .models import UploadedImage
from .models import ChatMessage
from .models import Player, PlayerRankingHistory
from .forms import ChatMessageForm, AddPointsForm
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import RegistrationRequest
from .spam_filter import is_spam_naive_bayes  
from .forms import ProfileForm, UserForm
from .models import Profile
from .models import TournamentRegistration, TournamentSchedule, TrainingSchedule, Announcement
from PIL import Image, ImageFilter, ImageEnhance
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import midtransclient
import uuid
from django.conf import settings


# Halaman Home
def home(request):
    announcement = Announcement.objects.last()
    context = {
        'announcement': announcement
    }
  
    return render(request, 'home.html', context)

def tournament_schedule_view(request):
    tournaments = TournamentSchedule.objects.all()
    return render(request, 'tournament_schedule.html', {'tournaments': tournaments})

def training_schedule(request):
    training_schedules = TrainingSchedule.objects.all()
    return render(request, 'training-schedule.html', {
        'training_schedules': training_schedules,
    })

# Halaman Ranking
def ranking(request):
    players = Player.objects.all().order_by('-points')
    ranking_history = PlayerRankingHistory.objects.all().order_by('-changed_at')[:10]  # 10 history terakhir

    for idx, player in enumerate(players, start=1):
        if player.rank != idx:  
            player.previous_rank = player.rank 
            player.rank = idx  
            player.save()

    return render(request, 'ranking.html', {'players': players, 'ranking_history': ranking_history})

# Halaman Documentation
def documentation(request):
    return render(request, 'documentation.html')

# Halaman Forum
def forum(request):
    if request.method == "POST":
        try:
            form = ChatMessageForm(request.POST, request.FILES)
            if form.is_valid():
                chat_message = form.save(commit=False)
                chat_message.user = request.user
                chat_message.save()
                messages.success(request, "Pesan berhasil dikirim!")
            else:
                messages.error(request, "Terjadi kesalahan dalam formulir: " + str(form.errors))
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect('forum')

    messages_data = ChatMessage.objects.all().order_by('-timestamp')
    form = ChatMessageForm()
    return render(request, 'forum.html', {'messages': messages_data, 'form': form})

# Halaman Login
def user_login(request):  
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)

            messages.success(request, 'Anda berhasil login.')

            return redirect('home')  
        else:
            messages.error(request, 'Username atau Password salah. Coba lagi.')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login') 

def upload_page(request):
    return render(request, 'upload.html')
def apply_image_filter(image_file, filter_type):
    img = Image.open(image_file)
    
    if filter_type == 'blur':
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_type == 'grayscale':
        img = img.convert('L')  # Hitam-putih
    elif filter_type == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)  # 1.5x lebih terang
    elif filter_type == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)  # 1.5x lebih kontras
    elif filter_type == 'sharpness':
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)  # 2.0x lebih tajam
    
    # Simpan gambar ke buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG' if image_file.name.lower().endswith(('.jpg', '.jpeg')) else 'PNG')
    buffer.seek(0)
    
    # Konversi ke InMemoryUploadedFile
    return InMemoryUploadedFile(
        buffer,
        None,
        image_file.name,
        image_file.content_type,
        buffer.tell(),
        None
    )
@login_required
def upload_image(request):
    if request.method == 'POST':
        files = request.FILES.getlist('image_file')  
        titles = request.POST.getlist('image_title') 
        descriptions = request.POST.getlist('description')  
        filter_type = request.POST.get('filter_type', None)  # Ambil jenis filter dari form

        if files and titles and descriptions and len(files) == len(titles) == len(descriptions): 
            for file, title, description in zip(files, titles, descriptions):
                try:
                    # Terapkan filter jika dipilih
                    if filter_type and filter_type in ['blur', 'grayscale', 'brightness', 'contrast', 'sharpness']:
                        file = apply_image_filter(file, filter_type)
                    
                    uploaded_image = UploadedImage(
                        user=request.user,
                        image_title=title,
                        image_file=file,
                        description=description 
                    )
                    uploaded_image.save()

                except Exception as e:
                    error_message = f"Gagal memproses gambar: {str(e)}"
                    return render(request, 'upload.html', {
                        'form': ImageUploadForm(),
                        'error': error_message
                    })

            return redirect('user_uploaded_images')  
        else:
            error_message = "Pastikan semua gambar memiliki judul dan deskripsi."
            return render(request, 'upload.html', {'form': ImageUploadForm(), 'error': error_message})
    else:
        form = ImageUploadForm()

    return render(request, 'upload.html', {'form': form})

@login_required
def user_uploaded_images(request):
    if request.user.is_superuser:  
        images = UploadedImage.objects.all()
    else:
        images = UploadedImage.objects.filter(user=request.user)
    
    return render(request, 'user_uploaded_images.html', {'images': images})

@login_required
def uploaded_images(request):
    if request.user.is_staff:  
        images = UploadedImage.objects.all().order_by('-uploaded_at')  
    else:  
        images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at') 

    return render(request, 'uploaded_images.html', {'images': images})

def forum(request):
    messages = ChatMessage.objects.all().order_by('timestamp')

    if len(messages) >= 15:
        messages.first().delete()

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        
        if form.is_valid():
            message = form.cleaned_data.get('message')

            if is_spam_naive_bayes(message):
                form.add_error('message', 'Pesan ini mengandung kata yang dianggap spam atau terlalu panjang.')
            else:
                chat_message = form.save(commit=False)
                chat_message.user = request.user
                chat_message.save()
                return redirect('forum')  
    else:
        form = ChatMessageForm()

    return render(request, 'forum.html', {'messages': messages, 'form': form})


@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile  
    except Profile.DoesNotExist:
        profile = None  

    edit = request.GET.get('edit', False)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'edit': edit,
    })

def ranking_details(request):
    rankings = [
        {"rank": 1, "name": "Rioz", "points": 1200, "country": "Indonesia"},
        {"rank": 2, "name": "Michael", "points": 1150, "country": "UK"},
        {"rank": 3, "name": "Michael Lee", "points": 1100, "country": "Canada"},
        {"rank": 4, "name": "Anna Brown", "points": 1050, "country": "Germany"},
        {"rank": 5, "name": "David Johnson", "points": 1000, "country": "Australia"},
    ]

    return render(request, 'ranking_details.html', {'rankings': rankings})

def join_tournament(request):
    if request.method == "POST":
        # Ambil data dari formulir
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']
        tournament_type = request.POST['tournament_type']
        division = request.POST['division']
        tournament_schedule_id = request.POST['tournament_schedule']

        tournament_schedule = TournamentSchedule.objects.get(id=tournament_schedule_id)

        registration = TournamentRegistration(
            name=name,
            address=address,
            phone=phone,
            tournament_type=tournament_type,
            division=division,
            tournament_schedule=tournament_schedule  
        )
        registration.save()

        messages.success(request, 'Anda berhasil terdaftar dalam turnamen!')
        
        return redirect('tournament_schedule')  

    tournament_schedules = TournamentSchedule.objects.all()
    return render(request, 'join_tournament.html', {'tournament_schedules': tournament_schedules})

def update_player_points(request, player_id, points_to_add):
    player = Player.objects.get(id=player_id)
    old_points = player.points
    old_rank = player.rank

    player.points += points_to_add
    player.save()

    player.update_player_ranks()

    history = PlayerRankingHistory(
        player=player,
        points_before=old_points,
        points_after=player.points,
        rank_before=old_rank,
        rank_after=player.rank,
    )
    history.save()

    return redirect('ranking') 

def registration_view(request):
    if request.method == 'POST':
        # 1. Simpan data registrasi
        registration = RegistrationRequest.objects.create(
            full_name=request.POST.get('full_name'),
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            height=request.POST.get('height'),
            weight=request.POST.get('weight'),
        )
        
        # 2. Inisialisasi Midtrans Snap
        snap = midtransclient.Snap(
            is_production=settings.MIDTRANS['SANDBOX'],
            server_key=settings.MIDTRANS['SERVER_KEY'],
            client_key=settings.MIDTRANS['CLIENT_KEY']
        )
        
        # 3. Siapkan parameter transaksi
        param = {
            "transaction_details": {
                "order_id": registration.generate_order_id(),
                "gross_amount": registration.payment_amount
            },
            "customer_details": {
                "first_name": registration.full_name,
                "last_name": "",
                "email": registration.email,
                "phone": registration.phone,
                "billing_address": {
                    "address": registration.address
                }
            },
            "item_details": [{
                "id": "reg-fee",
                "name": "Pendaftaran Member",
                "price": registration.payment_amount,
                "quantity": 1
            }]
        }
        
        # 4. Buat transaksi Midtrans
        transaction = snap.create_transaction(param)
        registration.midtrans_response = transaction
        registration.save()
        
        # 5. Redirect ke halaman pembayaran Midtrans
        return redirect(transaction['redirect_url'])
    
    return render(request, 'register.html')




@csrf_exempt
def payment_notification(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            order_id = payload['order_id']
            
            # Verifikasi notifikasi
            snap = midtransclient.Snap(
                is_production=settings.MIDTRANS['SANDBOX'],
                server_key=settings.MIDTRANS['SERVER_KEY']
            )
            status = snap.transactions.notification(payload)
            
            # Update status pembayaran
            registration = RegistrationRequest.objects.get(order_id=order_id)
            registration.payment_status = status['transaction_status']
            registration.payment_method = status['payment_type']
            
            if status['transaction_status'] == 'settlement':
                registration.payment_proof = status.get('pdf_url', '')
                registration.is_approved = True  # Otomatis approve jika pembayaran sukses
            
            registration.save()
            
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status=400)