from django.contrib import admin
from .models import MeterPoint, Meter, FlowFile, Reading

# Register your models here.

@admin.register(MeterPoint)
class MeterPointAdmin(admin.ModelAdmin):
    """Admin interface for MeterPoint model."""
    list_display = ['mpan', 'created_at', 'updated_at']
    search_fields = ['mpan']
    readonly_fields = ['created_at', 'updated_at']
    
    # Shows related meters inline
    class MeterInline(admin.TabularInline):
        model = Meter
        extra = 0
        readonly_fields = ['created_at', 'updated_at']
    
    inlines = [MeterInline]


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    """Admin interface for Meter model."""
    list_display = ['serial_number', 'meter_point', 'created_at']
    list_filter = ['created_at']
    search_fields = ['serial_number', 'meter_point__mpan']
    readonly_fields = ['created_at', 'updated_at']
    
    # Quick link to meter point
    def meter_point_link(self, obj):
        return obj.meter_point.mpan
    meter_point_link.short_description = 'MPAN'


@admin.register(FlowFile)
class FlowFileAdmin(admin.ModelAdmin):
    """Admin interface for FlowFile model."""
    list_display = ['filename', 'imported_at', 'reading_count']
    list_filter = ['imported_at']
    search_fields = ['filename']
    readonly_fields = ['imported_at']
    
    def reading_count(self, obj):
        """Show count of readings in this file."""
        return obj.readings.count()
    reading_count.short_description = 'Readings'


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    """Admin interface for Reading model."""
    list_display = [
        'meter_serial', 'mpan', 'reading_date', 
        'value', 'register_type', 'flow_file'
    ]
    list_filter = ['reading_date', 'register_type', 'flow_file']
    search_fields = [
        'meter__serial_number', 
        'meter__meter_point__mpan'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'reading_date'
    
    # Custom display methods for better readability
    def meter_serial(self, obj):
        return obj.meter.serial_number
    meter_serial.short_description = 'Meter Serial'
    meter_serial.admin_order_field = 'meter__serial_number'
    
    def mpan(self, obj):
        return obj.meter.meter_point.mpan
    mpan.short_description = 'MPAN'
    mpan.admin_order_field = 'meter__meter_point__mpan'
