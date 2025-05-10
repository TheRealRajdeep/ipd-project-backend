# shipments/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import re

from .utils import get_map_url

class DeliveryPerson(models.Model):
    # add this line:
    id = models.AutoField(primary_key=True)

    user         = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="delivery_profile"
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    vehicle_info = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"DeliveryPerson {self.user.username}"


class Shipment(models.Model):

    id = models.AutoField(primary_key=True)
    
    RIPENESS_STATES   = [
        ("unripe",    "Unripe"),
        ("freshripe", "Fresh Ripe"),
        ("ripe",      "Ripe"),
        ("overripe",  "Overripe"),
        ("Unknown",   "Unknown"),
    ]
    STATUS_CHOICES    = [
        ("PENDING",    "Pending"),
        ("IN_TRANSIT", "In Transit"),
        ("DELIVERED",  "Delivered"),
        ("CANCELLED",  "Cancelled"),
    ]

    created_by        = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_shipments"
    )
    receiver          = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_shipments"
    )
    delivery_person   = models.ForeignKey(
        DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True
    )

    origin            = models.CharField(max_length=255)
    destination       = models.CharField(max_length=255)
    quantity          = models.IntegerField()
    status            = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    shipment_date     = models.DateField(default=timezone.now)
    estimated_arrival = models.DateField(null=True, blank=True)

    ripeness_status   = models.CharField(
        max_length=50, choices=RIPENESS_STATES, default="Unknown"
    )
    dominant_ripeness = models.CharField(
        max_length=50, choices=RIPENESS_STATES, default="Unknown"
    )
    ripeness_summary  = models.JSONField(default=dict, blank=True)
    predictions       = models.JSONField(default=list, blank=True)
    shelf_life        = models.CharField(max_length=20, blank=True)
    alert_sent        = models.BooleanField(default=False)
    result_image      = models.TextField(blank=True)

    current_lat       = models.FloatField(null=True, blank=True)
    current_lon       = models.FloatField(null=True, blank=True)
    optimized_route   = models.JSONField(default=dict, blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    last_updated      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment {self.id} from {self.origin} to {self.destination}"

    @property
    def map_url(self):
        if self.current_lat is None or self.current_lon is None:
            return ""
        return get_map_url(self.current_lat, self.current_lon, self.destination)


class BananaImage(models.Model):
    """
    Stores the raw binary of each uploaded batch image.
    """
    id = models.AutoField(primary_key=True)
    shipment    = models.ForeignKey(
        Shipment, related_name="images", on_delete=models.CASCADE
    )
    image_data  = models.BinaryField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Shipment {self.shipment.id}"


@receiver(post_save, sender=Shipment)
def check_shipment_shelf_life(sender, instance, created, **kwargs):
    """
    Send a one-time email alert if shelf_life ≤ 3 days.
    """
    if created or not instance.shelf_life or instance.alert_sent:
        return

    m = re.search(r"(\d+)", instance.shelf_life)
    if not m or int(m.group(1)) > 3:
        return

    subject = f"ALERT: Shipment #{instance.id} nearing expiry"
    message = (
        f"Dear {instance.receiver.get_full_name() or instance.receiver.username},\n\n"
        f"Your banana shipment #{instance.id} has approximately {instance.shelf_life} remaining.\n\n"
        "Please take action to prevent spoilage.\n\n"
        "Thank you,\n"
        "Banana Supply Chain System"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.receiver.email],
            fail_silently=False
        )
    except Exception:
        # swallow errors in prod; log if you need
        pass

    # mark it so we don’t re-alert
    Shipment.objects.filter(pk=instance.pk).update(alert_sent=True)
