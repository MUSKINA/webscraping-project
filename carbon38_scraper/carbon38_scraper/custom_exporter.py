import scrapy
from scrapy.exporters import CsvItemExporter


class CustomCsvItemExporter(CsvItemExporter):
    def start_exporting(self):
        """
        Start exporting by writing custom headers including Sl. No, Field Name, Field Type, and Example.
        """
        self._serial_number = 1  # Start counting serial numbers from 1
        self.csv_writer.writerow(['Sl. No', 'Field Name', 'Field Type', 'Example'])
        super().start_exporting()

    def export_item(self, item):
        """
        Customize the item export by adding serial number and organizing fields into Sl. No, Field Name, Field Type, Example.
        """
        # Add serial number
        sl_no = self._serial_number
        self._serial_number += 1

        # Create a list of field names, types, and examples
        field_names = list(item.keys())
        field_types = ['String' for _ in field_names]  # Assume all fields are strings
        examples = [str(item.get(field, '')) for field in field_names]  # Get the field values

        # Write the row for each field
        for field_name, field_type, example in zip(field_names, field_types, examples):
            self.csv_writer.writerow([sl_no, field_name, field_type, example])

        super().export_item(item)
