"""
Google Document AI OCR Processor
Replaces mock OCR with actual Google Document AI processing
"""

import time
from datetime import datetime
from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
import os

class MockOCRProcessor:
    def process_document(self, document_path, category):
        return [
            {
                "field_name": "mock_field",
                "field_value": "mock_value",
                "confidence_score": 100,
                "field_position": "mock_position"
            }
        ]

class GoogleDocAIProcessor:
    """
    Google Document AI processor for extracting structured data from documents
    """
    
    def __init__(self, project_id, location, processor_id, credentials_path=None):
        """
        Initialize Google Document AI client
        
        Args:
            project_id: Your Google Cloud project ID
            location: Processor location (e.g., 'us', 'eu')
            processor_id: Your Document AI processor ID
            credentials_path: Path to service account JSON key (optional if using env var)
        """
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        
        # Initialize client with credentials
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = documentai.DocumentProcessorServiceClient(credentials=credentials)
        else:
            # Use GOOGLE_APPLICATION_CREDENTIALS environment variable
            self.client = documentai.DocumentProcessorServiceClient()
        
        # Build processor name
        self.processor_name = self.client.processor_path(
            project_id, location, processor_id
        )
    
    def process_document(self, document_path, category):
        """
        Process document using Google Document AI
        
        Args:
            document_path: Path to document file
            category: Category object with category_name
            
        Returns:
            list of dict with extracted fields
        """
        print(f"Processing {document_path} with Google Document AI...")
        
        # Read the file
        with open(document_path, 'rb') as doc_file:
            document_content = doc_file.read()
        
        # Determine mime type
        mime_type = self._get_mime_type(document_path)
        
        # Create Document AI request
        raw_document = documentai.RawDocument(
            content=document_content,
            mime_type=mime_type
        )
        
        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=raw_document
        )
        
        # Process document
        result = self.client.process_document(request=request)
        document = result.document
        
        print(f"✓ Document processed. Found {len(document.pages)} page(s)")
        
        # Extract data based on category
        if category.category_name == 'attendance_sheet':
            return self._extract_attendance(document)
        elif category.category_name == 'student_marksheet':
            return self._extract_grades(document)
        elif category.category_name == 'class_diary':
            return self._extract_class_diary(document)
        elif category.category_name == 'store_requisition':
            return self._extract_store_requisition(document)
        elif category.category_name == 'store_invoice':
            return self._extract_store_invoice(document)
        elif category.category_name == 'survey_form':
            return self._extract_survey(document)
        elif category.category_name == 'visitors_book':
            return self._extract_visitors(document)
        else:
            # Generic extraction
            return self._extract_generic(document)
    
    def _get_mime_type(self, file_path):
        """Determine MIME type from file extension"""
        ext = file_path.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'gif': 'image/gif',
            'bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'application/pdf')
    
    def _extract_table_data(self, document):
        """
        Extract table data from document
        Returns list of tables with rows and cells
        """
        tables = []
        
        for page in document.pages:
            for table in page.tables:
                table_data = {
                    'headers': [],
                    'rows': []
                }
                
                # Extract table structure
                for row_idx, row in enumerate(table.header_rows):
                    header_row = []
                    for cell in row.cells:
                        cell_text = self._get_text(cell.layout, document.text)
                        header_row.append(cell_text.strip())
                    table_data['headers'].append(header_row)
                
                # Extract data rows
                for row in table.body_rows:
                    data_row = []
                    for cell in row.cells:
                        cell_text = self._get_text(cell.layout, document.text)
                        data_row.append(cell_text.strip())
                    table_data['rows'].append(data_row)
                
                tables.append(table_data)
        
        return tables
    
    def _get_text(self, layout, document_text):
        """Extract text from a layout element"""
        text = ""
        for segment in layout.text_anchor.text_segments:
            start = int(segment.start_index) if segment.start_index else 0
            end = int(segment.end_index)
            text += document_text[start:end]
        return text
    
    def _extract_attendance(self, document):
        """
        Extract attendance sheet data
        Expected format: Student names in first column, attendance marks (P/A/O) in subsequent columns
        """
        fields = []
        tables = self._extract_table_data(document)
        
        if not tables:
            print("⚠ No tables found in document")
            return fields
        
        # Use first table (usually the main attendance table)
        table = tables[0]
        
        print(f"Found table with {len(table['rows'])} student rows")
        
        # Process each student row
        for student_idx, row in enumerate(table['rows'], start=1):
            if len(row) < 2:
                continue
            
            # First column: Student name or S.No + Name
            # Could be just S.No in first cell, name in second
            student_name = row[1] if len(row) > 1 and row[0].isdigit() else row[0]
            s_no = row[0] if row[0].isdigit() else str(student_idx)
            
            # Add student name
            fields.append({
                'field_name': f'student_{student_idx}_name',
                'field_value': student_name,
                'confidence_score': 95,  # Document AI doesn't provide per-field confidence
                'field_position': f'row_{student_idx}_col_1'
            })
            
            # Add S.No
            fields.append({
                'field_name': f'student_{student_idx}_sno',
                'field_value': s_no,
                'confidence_score': 95,
                'field_position': f'row_{student_idx}_col_0'
            })
            
            # Extract attendance marks from remaining columns (days 1-31)
            attendance_start_col = 2 if row[0].isdigit() else 1
            for day in range(1, 32):
                col_idx = attendance_start_col + day - 1
                if col_idx < len(row):
                    attendance_value = row[col_idx].strip().upper()
                    # Validate attendance mark
                    if attendance_value and attendance_value[0] in ['P', 'A', 'O', 'E']:
                        attendance_value = attendance_value[0]
                    else:
                        attendance_value = ''
                    
                    fields.append({
                        'field_name': f'student_{student_idx}_day_{day}',
                        'field_value': attendance_value,
                        'confidence_score': 90,
                        'field_position': f'row_{student_idx}_col_{col_idx}'
                    })
        
        print(f"✓ Extracted attendance for {len(table['rows'])} students")
        return fields
    
    def _extract_grades(self, document):
        """Extract grade/marksheet data"""
        fields = []
        tables = self._extract_table_data(document)
        
        if not tables:
            return fields
        
        table = tables[0]
        
        for student_idx, row in enumerate(table['rows'], start=1):
            if len(row) < 2:
                continue
            
            # Student name (usually first or second column)
            student_name = row[1] if len(row) > 1 and row[0].isdigit() else row[0]
            
            fields.append({
                'field_name': f'student_{student_idx}_name',
                'field_value': student_name,
                'confidence_score': 95,
                'field_position': f'row_{student_idx}_col_1'
            })
            
            # Extract subject marks (remaining columns)
            subjects = ['math', 'science', 'english', 'history', 'geography']
            for subj_idx, subject in enumerate(subjects):
                col_idx = (2 if row[0].isdigit() else 1) + subj_idx
                if col_idx < len(row):
                    mark = row[col_idx].strip()
                    fields.append({
                        'field_name': f'student_{student_idx}_{subject}',
                        'field_value': mark,
                        'confidence_score': 92,
                        'field_position': f'row_{student_idx}_col_{col_idx}'
                    })
        
        return fields
    
    def _extract_class_diary(self, document):
        """Extract class diary entries"""
        fields = []
        
        # Look for key-value pairs
        for entity in document.entities:
            if entity.type_ == 'date':
                fields.append({
                    'field_name': 'date',
                    'field_value': entity.mention_text,
                    'confidence_score': int(entity.confidence * 100),
                    'field_position': 'extracted'
                })
        
        # Extract full text for activities
        if document.text:
            fields.append({
                'field_name': 'activities',
                'field_value': document.text,
                'confidence_score': 85,
                'field_position': 'full_text'
            })
        
        return fields
    
    def _extract_store_requisition(self, document):
        """Extract store requisition/invoice data"""
        fields = []
        tables = self._extract_table_data(document)
        
        # Extract date and center info from entities
        for entity in document.entities:
            if entity.type_ == 'date':
                fields.append({
                    'field_name': 'date',
                    'field_value': entity.mention_text,
                    'confidence_score': int(entity.confidence * 100),
                    'field_position': 'extracted'
                })
        
        # Extract items from table
        if tables:
            table = tables[0]
            for item_idx, row in enumerate(table['rows'], start=1):
                if len(row) >= 2:
                    fields.append({
                        'field_name': f'item_{item_idx}_name',
                        'field_value': row[0],
                        'confidence_score': 92,
                        'field_position': f'row_{item_idx}_col_1'
                    })
                    fields.append({
                        'field_name': f'item_{item_idx}_quantity',
                        'field_value': row[1],
                        'confidence_score': 90,
                        'field_position': f'row_{item_idx}_col_2'
                    })
        
        return fields
    
    def _extract_store_invoice(self, document):
        """Extract store invoice data"""
        return self._extract_store_requisition(document)
    
    def _extract_survey(self, document):
        """Extract survey form data"""
        fields = []
        
        # Extract form fields
        for page in document.pages:
            for form_field in page.form_fields:
                field_name = self._get_text(form_field.field_name, document.text)
                field_value = self._get_text(form_field.field_value, document.text)
                
                fields.append({
                    'field_name': field_name.strip().replace(' ', '_').lower(),
                    'field_value': field_value.strip(),
                    'confidence_score': int(form_field.field_name.confidence * 100),
                    'field_position': 'form_field'
                })
        
        return fields
    
    def _extract_visitors(self, document):
        """Extract visitors book entries"""
        fields = []
        tables = self._extract_table_data(document)
        
        if not tables:
            return fields
        
        table = tables[0]
        
        for visitor_idx, row in enumerate(table['rows'], start=1):
            if len(row) >= 3:
                fields.extend([
                    {
                        'field_name': f'visitor_{visitor_idx}_name',
                        'field_value': row[0],
                        'confidence_score': 93,
                        'field_position': f'row_{visitor_idx}_col_1'
                    },
                    {
                        'field_name': f'visitor_{visitor_idx}_contact',
                        'field_value': row[1] if len(row) > 1 else '',
                        'confidence_score': 90,
                        'field_position': f'row_{visitor_idx}_col_2'
                    },
                    {
                        'field_name': f'visitor_{visitor_idx}_purpose',
                        'field_value': row[2] if len(row) > 2 else '',
                        'confidence_score': 88,
                        'field_position': f'row_{visitor_idx}_col_3'
                    }
                ])
        
        return fields
    
    def _extract_generic(self, document):
        """Generic extraction for unknown document types"""
        fields = []
        
        # Extract all text
        if document.text:
            fields.append({
                'field_name': 'full_text',
                'field_value': document.text,
                'confidence_score': 85,
                'field_position': 'document'
            })
        
        # Extract tables if present
        tables = self._extract_table_data(document)
        for table_idx, table in enumerate(tables):
            fields.append({
                'field_name': f'table_{table_idx}_data',
                'field_value': str(table),
                'confidence_score': 90,
                'field_position': f'table_{table_idx}'
            })
        
        return fields

