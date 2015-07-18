from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from phonenumber_field.modelfields import PhoneNumberField


class AbsModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InheritanceCastModel(AbsModel):
    """
    Credits goes to http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classes-of-an-object-in-django-without-knowing-the-nam
    An abstract base class that provides a ``real_type`` FK to ContentType.

    For use in trees of inherited models, to be able to downcast
    parent instances to their child types.

    """
    real_type = models.ForeignKey(ContentType, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(InheritanceCastModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    def instance_of(self, instance):
        return self.cast().__class__.__name__ == instance

    class Meta:
        abstract = True


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class UserProfile(AbsModel):
    user = models.OneToOneField(User)
    phone = PhoneNumberField(blank=True)
    skype = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


def user_post_delete(sender, instance, **kwargs):
    try:
        UserProfile.objects.get(user=instance).delete()
    except:
        pass


def user_post_save(sender, instance, **kwargs):
    try:
        UserProfile.objects.get_or_create(user=instance)
    except:
        pass


models.signals.post_delete.connect(user_post_delete, sender=User)
models.signals.post_save.connect(user_post_save, sender=User)
