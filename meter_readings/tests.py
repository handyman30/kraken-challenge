from django.test import TestCase, Client
from django.core.management import call_command
from django.urls import reverse
from datetime import date
from decimal import Decimal
import tempfile
import os

from .models import MeterPoint, Meter, FlowFile, Reading


class ModelTests(TestCase):
    """Test our Django models."""
    
    def setUp(self):
        """Set up test data."""
        self.meter_point = MeterPoint.objects.create(
            mpan='1234567890123'
        )
        self.meter = Meter.objects.create(
            serial_number='TEST001',
            meter_point=self.meter_point
        )
    
    def test_meter_point_creation(self):
        """Test MeterPoint model."""
        self.assertEqual(str(self.meter_point), 'MeterPoint: 1234567890123')
        self.assertEqual(self.meter_point.mpan, '1234567890123')
    
    def test_meter_creation(self):
        """Test Meter model."""
        self.assertEqual(self.meter.serial_number, 'TEST001')
        self.assertEqual(self.meter.meter_point, self.meter_point)
        self.assertIn('TEST001', str(self.meter))
    
    def test_reading_creation(self):
        """Test Reading model."""
        flow_file = FlowFile.objects.create(filename='test.txt')
        reading = Reading.objects.create(
            meter=self.meter,
            reading_date=date(2024, 1, 1),
            value=Decimal('1234.56'),
            flow_file=flow_file
        )
        
        self.assertEqual(reading.value, Decimal('1234.56'))
        self.assertEqual(reading.meter, self.meter)
        self.assertEqual(reading.register_type, 'S')  # Default


class ImportCommandTests(TestCase):
    """Test the import_d0010 management command."""
    
    def test_import_valid_file(self):
        """Test importing a valid D0010 file."""
        # Create a temporary D0010 file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('ZHV|P|NDLO001|UDMS|Z|20240101|202401011430|\n')
            f.write('030|1|1234567890123|S|METER001|20240101|S|kWh|00000|1234.56|\n')
            f.write('030|1|1234567890123|S|METER001|20240102|S|kWh|00000|1235.67|\n')
            f.write('ZPT|000003|\n')
            temp_file = f.name
        
        try:
            # Run the import command
            call_command('import_d0010', temp_file)
            
            # Check data was imported
            self.assertEqual(MeterPoint.objects.count(), 1)
            self.assertEqual(Meter.objects.count(), 1)
            self.assertEqual(Reading.objects.count(), 2)
            self.assertEqual(FlowFile.objects.count(), 1)
            
            # Check specific values
            meter = Meter.objects.first()
            self.assertEqual(meter.serial_number, 'METER001')
            self.assertEqual(meter.meter_point.mpan, '1234567890123')
            
            reading = Reading.objects.filter(reading_date=date(2024, 1, 1)).first()
            self.assertEqual(reading.value, Decimal('1234.56'))
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_import_missing_file(self):
        """Test handling of missing file."""
        # This should not raise an exception
        call_command('import_d0010', 'nonexistent.txt')
        
        # No data should be imported
        self.assertEqual(Reading.objects.count(), 0)


class ViewTests(TestCase):
    """Test our web views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        
        # Create test data
        meter_point = MeterPoint.objects.create(mpan='9999888877776')
        meter = Meter.objects.create(
            serial_number='VIEWTEST001',
            meter_point=meter_point
        )
        flow_file = FlowFile.objects.create(filename='test_view.txt')
        Reading.objects.create(
            meter=meter,
            reading_date=date(2024, 1, 15),
            value=Decimal('5678.90'),
            flow_file=flow_file
        )
    
    def test_search_view_no_query(self):
        """Test search view without query."""
        response = self.client.get(reverse('search_readings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Meter Readings')
        self.assertContains(response, 'Welcome!')
    
    def test_search_by_mpan(self):
        """Test searching by MPAN."""
        response = self.client.get(reverse('search_readings'), {'q': '9999888877776'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'VIEWTEST001')
        self.assertContains(response, '5678.90')
        self.assertContains(response, 'Found 1 reading')
    
    def test_search_by_serial(self):
        """Test searching by meter serial number."""
        response = self.client.get(reverse('search_readings'), {'q': 'VIEWTEST'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '9999888877776')
        self.assertContains(response, '5678.90')
    
    def test_search_no_results(self):
        """Test search with no results."""
        response = self.client.get(reverse('search_readings'), {'q': 'NOTFOUND'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No results found')
