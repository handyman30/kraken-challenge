"""
Management command to import D0010 flow files.
Handles pipe-delimited meter reading data.
"""

import os
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from meter_readings.models import MeterPoint, Meter, FlowFile, Reading


class Command(BaseCommand):
    help = 'Import D0010 flow file(s) containing meter readings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file_paths',
            nargs='+',
            type=str,
            help='Path(s) to D0010 file(s) to import'
        )
    
    def handle(self, *args, **options):
        """
        Main entry point for the command.
        Process each file provided as argument.
        """
        file_paths = options['file_paths']
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.ERROR(f'File not found: {file_path}')
                )
                continue
                
            self.stdout.write(f'Processing file: {file_path}')
            
            try:
                with transaction.atomic():
                    # Using transaction to ensure data integrity
                    self._import_file(file_path)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully imported: {file_path}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing {file_path}: {str(e)}')
                )
    
    def _import_file(self, file_path):
        """
        Import a single D0010 file.
        Creates FlowFile record and processes all readings.
        """
        # Create flow file record
        flow_file = FlowFile.objects.create(
            filename=os.path.basename(file_path)
        )
        
        readings_count = 0
        
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line:
                    continue
                
                # Split by pipe delimiter
                fields = line.split('|')
                
                # D0010 reading lines start with '030'
                if fields[0] == '030' and len(fields) >= 10:
                    try:
                        self._process_reading_line(fields, flow_file)
                        readings_count += 1
                    except Exception as e:
                        # Log error but continue processing
                        self.stdout.write(
                            self.style.WARNING(
                                f'Line {line_num}: Failed to process - {str(e)}'
                            )
                        )
        
        self.stdout.write(f'  Imported {readings_count} readings')
    
    def _process_reading_line(self, fields, flow_file):
        """
        Process a single reading line from D0010 file.
        
        Expected format (simplified):
        030|1|MPAN|S|SerialNumber|ReadingDate|RegisterType|Unit|RegisterID|Value|
        """
        # Extract fields - being defensive about field positions
        mpan = fields[2] if len(fields) > 2 else ''
        serial_number = fields[4] if len(fields) > 4 else ''
        reading_date_str = fields[5] if len(fields) > 5 else ''
        register_type = fields[6] if len(fields) > 6 else 'S'
        register_id = fields[8] if len(fields) > 8 else '00000'
        value_str = fields[9] if len(fields) > 9 else '0'
        
        # Validate required fields
        if not all([mpan, serial_number, reading_date_str, value_str]):
            raise ValueError('Missing required fields')
        
        # Parse date (assuming YYYYMMDD format)
        try:
            reading_date = datetime.strptime(reading_date_str, '%Y%m%d').date()
        except ValueError:
            raise ValueError(f'Invalid date format: {reading_date_str}')
        
        # Parse value
        try:
            value = Decimal(value_str)
        except:
            raise ValueError(f'Invalid reading value: {value_str}')
        
        # Get or create meter point
        meter_point, _ = MeterPoint.objects.get_or_create(
            mpan=mpan
        )
        
        # Get or create meter
        meter, _ = Meter.objects.get_or_create(
            serial_number=serial_number,
            defaults={'meter_point': meter_point}
        )
        
        # Create reading (update if exists for same date/register)
        reading, created = Reading.objects.update_or_create(
            meter=meter,
            reading_date=reading_date,
            register_type=register_type,
            register_id=register_id,
            defaults={
                'value': value,
                'flow_file': flow_file
            }
        )
        
        if not created:
            # Log when we update existing reading
            self.stdout.write(
                self.style.WARNING(
                    f'  Updated existing reading for {serial_number} on {reading_date}'
                )
            ) 