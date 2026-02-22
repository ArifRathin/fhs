from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse
from fhs.email_sender import sendEmail
from address.models import Organization, Location

# Create your models here.
class UserManager(BaseUserManager):


    def create_user(self, first_name, last_name, email, phone, password):
        user = self.model(
            first_name=first_name,
            last_name = last_name,
            email = email,
            phone = phone
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self, email, phone, password, is_superadmin=False, is_active=False, first_name="Admin", last_name="Member"):
        user = self.create_user(
            first_name=first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            password = password
        )
        user.is_superadmin = is_superadmin
        user.is_active = is_active
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=7, default=None, null=True)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, default=None, null=True)
    user_location = models.ManyToManyField(Location, related_name='user_location')

    account_activation_code = models.CharField(max_length=255, default=None, null=True)
    change_password_code = models.CharField(max_length=255, default=None, null=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    is_enduser = models.BooleanField(default=False)
    is_technician = models.BooleanField(default=False)

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    
    # def has_perm(self, perm, object=None):
    #     return False
    
    def has_module_perms(self, app_label):
        return True
    

@receiver(post_save, sender=User)
def sendEmailToUser(sender, instance, created, **kwargs):
    if instance.is_enduser==True and instance.is_active == False and instance.account_activation_code != None:
        to = []
        to.append(instance.email)
        subject = "Account activation email from FHS"
        link = reverse('activate-account', args=[instance.account_activation_code])
        fullLink = f'{settings.BASIC_URL}{link}'
        body = 'front-end/emails/send-enduser-account-activation-link-email.html'
        context = {
            'receiver_name':f'{instance.first_name} {instance.last_name}',
            'full_link':fullLink
        }
        sendEmail.delay(subject=subject, body=body, context=context, to=to)