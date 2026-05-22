from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template.loader import render_to_string

# Create your views here.
def index(request):
    return render(request, 'core/index.html')


def contact_submit(request):
    if request.method != 'POST':
        return HttpResponseRedirect(f"{reverse('index')}#contact")

    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    subject = (request.POST.get('subject') or '').strip()
    message = (request.POST.get('message') or '').strip()

    if not all([name, email, subject, message]):
        messages.error(request, 'Please complete all form fields.')
        return HttpResponseRedirect(f"{reverse('index')}#contact")

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, 'Please enter a valid email address.')
        return HttpResponseRedirect(f"{reverse('index')}#contact")

    email_subject = f"[LearnCraft Contact] {subject}"

    # Basic SMTP sanity check before trying to send.
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        messages.error(request, 'Email service is not configured yet (missing EMAIL_HOST_USER or EMAIL_HOST_PASSWORD).')
        return HttpResponseRedirect(f"{reverse('index')}#contact")

    mail_context = {
        'sender_name': name,
        'sender_email': email,
        'subject': subject,
        'message': message,
    }

    text_body = render_to_string('core/emails/contact_message.txt', mail_context)
    html_body = render_to_string('core/emails/contact_message.html', mail_context)

    try:
        email_message = EmailMultiAlternatives(
            subject=email_subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECIPIENT_EMAIL],
            reply_to=[email],
        )
        email_message.attach_alternative(html_body, 'text/html')
        email_message.send(fail_silently=False)
    except Exception as exc:
        if settings.DEBUG:
            messages.error(request, f'Email error: {exc}')
        else:
            messages.error(request, 'We could not send your message. Please try again later.')
        return HttpResponseRedirect(f"{reverse('index')}#contact")

    messages.success(request, 'Your message has been sent successfully.')
    return HttpResponseRedirect(f"{reverse('index')}#contact")