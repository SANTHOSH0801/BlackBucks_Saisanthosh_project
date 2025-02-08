from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Resume
from .serializers import UserSerializer
from reportlab.pdfgen import canvas
from io import BytesIO
from rest_framework.response import Response


User = get_user_model()

@csrf_exempt
def user_register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return render(request, 'login.html', {'success': 'Registration successful! Please log in.'})
        return render(request, 'register.html', {'errors': serializer.errors})
    return render(request, 'register.html')

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('create_resume')  # Redirect after successful login
        
        return render(request, 'login.html', {'error': 'Invalid Credentials'})  

    return render(request, 'login.html')

def resume_create(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        summary = request.POST.get('summary')
        education = request.POST.get('education')
        experience = request.POST.get('experience')
        skills = request.POST.get('skills')

        print(f"Received data: Name: {name}, Email: {email}, Phone: {phone}")  # Debugging

        if not (name and email and phone and summary and education and experience and skills):
            return render(request, 'resume_create.html', {'error': 'All fields are required'})

        if Resume.objects.filter(user=request.user).exists():
            return render(request, 'resume_create.html', {'error': 'Resume already exists'})

        resume = Resume(
            user=request.user,
            name=name,
            email=email,
            phone=phone,
            summary=summary,
            education=education,
            experience=experience,
            skills=skills
        )
        resume.save()  
        print(f"Resume saved for {request.user}") 
        
        return redirect('resume_preview')  # Redirect to preview page after saving

    return render(request, 'resume_create.html')

def resume_preview(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        resume = Resume.objects.get(user=request.user)
        print(f"Showing resume for {request.user}")  # Debugging
        return render(request, 'resume_preview.html', {'resume': resume})
    except Resume.DoesNotExist:
        return render(request, 'resume_preview.html', {'error': 'No resume found.'})


def resume_download(request):  
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        resume = Resume.objects.get(user=request.user)
        
        # Create PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"Resume of {resume.name}")
        p.drawString(100, 780, f"Email: {resume.email}")
        p.drawString(100, 760, f"Phone: {resume.phone}")
        p.drawString(100, 730, "Summary:")
        p.drawString(120, 710, resume.summary)
        p.drawString(100, 680, "Education:")
        p.drawString(120, 660, resume.education)
        p.drawString(100, 630, "Experience:")
        p.drawString(120, 610, resume.experience)
        p.drawString(100, 580, "Skills:")
        p.drawString(120, 560, resume.skills)
        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.name}_resume.pdf"'
        return response

    except Resume.DoesNotExist:
        return render(request, 'resume_preview.html', {'error': 'No resume found.'})

def token_refresh(request):  
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)
    
    refresh = RefreshToken.for_user(request.user)
    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})

def home(request):
    return render(request, 'home.html')
