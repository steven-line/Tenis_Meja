from django import forms
from .models import UploadedImage
from django.contrib.auth.models import User
from .models import ChatMessage
from .spam_filter import is_spam_naive_bayes 
from .models import Profile
from .models import ChatMessage


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image_title', 'image_file', 'description']   


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'phone_number', 'height', 'weight']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'image']
    
    def clean_message(self):
        # Ambil pesan dari form
        message = self.cleaned_data.get('message')
        
        import re
        words = re.findall(r'\b\w+\b', message)  
        if len(words) > 200:
            raise forms.ValidationError("Pesan ini terlalu panjang dan dianggap sebagai spam.")
        
        # Memeriksa apakah pesan mengandung kata spam menggunakan algoritma Naive Bayes
        if is_spam_naive_bayes(message):
            raise forms.ValidationError("Pesan ini mengandung kata yang dianggap spam.")
        
        return message

class AddPointsForm(forms.Form):
    points_to_add = forms.IntegerField(label='Points to Add', min_value=1, required=True)