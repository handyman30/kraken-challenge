from django.shortcuts import render
from django.db.models import Q
from .models import Reading, Meter, MeterPoint

# Create your views here.

def search_readings(request):
    """
    Main search view - allows searching by MPAN or meter serial number.
    """
    query = request.GET.get('q', '').strip()
    readings = []
    search_performed = False
    
    if query:
        search_performed = True
        
        # Search for readings by MPAN or meter serial number
        # Using Q objects for OR condition
        readings = Reading.objects.filter(
            Q(meter__serial_number__icontains=query) |
            Q(meter__meter_point__mpan__icontains=query)
        ).select_related(
            'meter',
            'meter__meter_point',
            'flow_file'
        ).order_by('-reading_date', 'meter__serial_number')
    
    context = {
        'query': query,
        'readings': readings,
        'search_performed': search_performed,
        'result_count': len(readings)
    }
    
    return render(request, 'meter_readings/search.html', context)


def reading_detail(request, reading_id):
    """
    Show details for a specific reading.
    Not strictly required but nice to have.
    """
    try:
        reading = Reading.objects.select_related(
            'meter',
            'meter__meter_point',
            'flow_file'
        ).get(id=reading_id)
    except Reading.DoesNotExist:
        reading = None
    
    # Get other readings for same meter
    related_readings = []
    if reading:
        related_readings = Reading.objects.filter(
            meter=reading.meter
        ).exclude(
            id=reading.id
        ).order_by('-reading_date')[:10]
    
    context = {
        'reading': reading,
        'related_readings': related_readings
    }
    
    return render(request, 'meter_readings/reading_detail.html', context)
