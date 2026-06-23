"""
PDF Generation for Family Trees
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_family_tree_pdf(family_data: dict, persons: list) -> BytesIO:
    """
    Generate a PDF report for a family tree
    
    Args:
        family_data: Dictionary containing family information
        persons: List of person dictionaries
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"<b>{family_data.get('name', 'Family Tree')}</b>", title_style)
    elements.append(title)
    
    # Family Information
    if family_data.get('description'):
        desc = Paragraph(family_data['description'], styles['Normal'])
        elements.append(desc)
        elements.append(Spacer(1, 0.2*inch))
    
    # Metadata
    metadata_data = [
        ['Created Date:', datetime.fromisoformat(family_data['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y')],
        ['Total Members:', str(family_data.get('person_count', len(persons)))],
        ['Subscription Plan:', family_data.get('subscription_plan', 'free').upper()],
        ['Person Limit:', str(family_data.get('person_limit', 50))],
        ['Join Code:', family_data.get('join_code', 'N/A')]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Family Members Section
    members_heading = Paragraph("<b>Family Members</b>", heading_style)
    elements.append(members_heading)
    
    if not persons:
        elements.append(Paragraph("No family members added yet.", styles['Normal']))
    else:
        # Group by generation or deceased status
        living = [p for p in persons if not p.get('is_deceased', False)]
        deceased = [p for p in persons if p.get('is_deceased', False)]
        
        if living:
            elements.append(Paragraph(f"<b>Living Members ({len(living)})</b>", styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))
            
            for person in living:
                person_data = format_person_data(person)
                person_table = create_person_table(person_data)
                elements.append(person_table)
                elements.append(Spacer(1, 0.15*inch))
        
        if deceased:
            elements.append(PageBreak())
            elements.append(Paragraph(f"<b>Deceased Members ({len(deceased)})</b>", styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))
            
            for person in deceased:
                person_data = format_person_data(person)
                person_table = create_person_table(person_data)
                elements.append(person_table)
                elements.append(Spacer(1, 0.15*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    footer = Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def format_person_data(person: dict) -> list:
    """Format person data for PDF table"""
    data = []
    
    # Full name
    full_name = f"{person.get('first_name', '')} "
    if person.get('middle_name'):
        full_name += f"{person['middle_name']} "
    full_name += person.get('last_name', '')
    if person.get('nickname'):
        full_name += f" ({person['nickname']})"
    
    data.append(['Name:', full_name])
    
    if person.get('gender'):
        data.append(['Gender:', person['gender'].title()])
    
    if person.get('birth_date'):
        data.append(['Birth Date:', person['birth_date']])
    
    if person.get('death_date'):
        data.append(['Death Date:', person['death_date']])
    
    if person.get('birth_place'):
        data.append(['Birth Place:', person['birth_place']])
    
    if person.get('bio'):
        data.append(['Biography:', person['bio']])
    
    if person.get('generation_level') is not None:
        data.append(['Generation:', str(person['generation_level'])])
    
    return data

def create_person_table(person_data: list) -> Table:
    """Create a styled table for a person's information"""
    table = Table(person_data, colWidths=[1.5*inch, 5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
    ]))
    return table
