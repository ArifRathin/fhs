from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from celery import shared_task

@shared_task
def sendEmail(**kwargs):
    subject = kwargs.get('subject')
    body = kwargs.get('body')
    emailFrom = settings.DEFAULT_FROM_EMAIL
    emailTo = kwargs.get('to')

    context = kwargs.get('context')

    htmlContent = render_to_string(body, context=context)

    textContent = strip_tags(htmlContent)

    email = EmailMultiAlternatives(subject=subject, body=textContent, from_email=emailFrom, to=emailTo)

    email.attach_alternative(htmlContent, 'text/html')
    try:
        email.send()
        return True
    except:
        return False