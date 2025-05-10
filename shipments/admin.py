from django.contrib import admin
from .models import Shipment, BananaImage, DeliveryPerson

class BananaImageInline(admin.TabularInline):
    model = BananaImage
    extra = 0
    readonly_fields = ['uploaded_at']
    fields = ['uploaded_at']

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'id','created_by','receiver','delivery_person',
        'origin','destination','quantity','ripeness_status',
        'shelf_life','status','shipment_date'
    ]
    list_filter = ['status','ripeness_status','shipment_date','created_at']
    search_fields = [
        'created_by__username','receiver__username',
        'delivery_person__user__username','origin','destination'
    ]
    inlines = [BananaImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'created_by','receiver','delivery_person',
                'origin','destination','quantity','status',
                'shipment_date','estimated_arrival'
            )
        }),
        ('Ripeness Info', {
            'fields': (
                'ripeness_status','dominant_ripeness',
                'ripeness_summary','shelf_life','alert_sent'
            )
        }),
        ('Location Info', {
            'fields': ('current_lat','current_lon','optimized_route')
        }),
    )

@admin.register(BananaImage)
class BananaImageAdmin(admin.ModelAdmin):
    list_display = ['id','shipment','uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['shipment__id']

@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ['id','user','phone_number','vehicle_info']
    search_fields = ['user__username','phone_number','vehicle_info']
