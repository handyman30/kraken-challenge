from django.db import models
from datetime import datetime

# Create your models here.

class MeterPoint(models.Model):
    """
    Represents an abstract meter point (electricity consumption point).
    Identified by MPAN - not the same as physical meter.
    """
    mpan = models.CharField(
        max_length=13,  # MPANs are typically 13 digits
        unique=True,
        help_text="Meter Point Administration Number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['mpan']
    
    def __str__(self):
        return f"MeterPoint: {self.mpan}"


class Meter(models.Model):
    """
    Physical meter device installed at a property.
    Has a serial number and belongs to a meter point.
    """
    serial_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Physical meter serial number"
    )
    meter_point = models.ForeignKey(
        MeterPoint,
        on_delete=models.CASCADE,
        related_name='meters'
    )
    # Could add meter type, installation date etc later
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['serial_number']
    
    def __str__(self):
        return f"Meter: {self.serial_number} (MPAN: {self.meter_point.mpan})"


class FlowFile(models.Model):
    """
    Tracks imported D0010 flow files.
    """
    filename = models.CharField(max_length=255)
    imported_at = models.DateTimeField(auto_now_add=True)
    # Could add file hash, size, status etc for better tracking
    
    class Meta:
        ordering = ['-imported_at']
    
    def __str__(self):
        return f"{self.filename} (imported: {self.imported_at})"


class Reading(models.Model):
    """
    Meter reading value at a specific point in time.
    Links to both meter and the flow file it came from.
    """
    REGISTER_TYPES = [
        ('E', 'Economy 7 Day'),
        ('N', 'Economy 7 Night'),
        ('S', 'Standard'),
    ]
    
    meter = models.ForeignKey(
        Meter,
        on_delete=models.CASCADE,
        related_name='readings'
    )
    reading_date = models.DateField()
    register_type = models.CharField(
        max_length=1,
        choices=REGISTER_TYPES,
        default='S'
    )
    register_id = models.CharField(
        max_length=5,
        default='00000',
        help_text="Register identifier"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cumulative electricity consumption"
    )
    flow_file = models.ForeignKey(
        FlowFile,
        on_delete=models.CASCADE,
        related_name='readings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reading_date', 'meter']
        # Prevent duplicate readings for same meter/date/register
        unique_together = ['meter', 'reading_date', 'register_type', 'register_id']
    
    def __str__(self):
        return f"Reading: {self.value} kWh on {self.reading_date} for {self.meter.serial_number}"
