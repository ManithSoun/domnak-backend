from fastapi import APIRouter, Depends, Response
from core.auth import get_current_user
from utils.response import success, error
from db.supabase import supabase
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import io
import os

router = APIRouter()

@router.get("/quotes/{quote_id}/report")
def generate_report(
    quote_id: str,
    current_user = Depends(get_current_user)
):
    """Generate PDF report for a quote"""
    try:
        # Get quote data
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", current_user.id).execute()
        if not quote.data:
            return error(message="Quote not found", status_code=404)
        
        line_items = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()
        
        # Create PDF
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(100, height - 80, "Quote Analysis Report")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, height - 95, f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Quote Details
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, height - 130, "Quote Details")
        pdf.setFont("Helvetica", 12)
        y = height - 150
        pdf.drawString(100, y, f"Quote ID: {quote_id[:8]}")
        y -= 20
        pdf.drawString(100, y, f"Contractor: {quote.data[0]['contractor_name']}")
        y -= 20
        pdf.drawString(100, y, f"Total Amount: ${quote.data[0]['total_amount']:,.2f}")
        y -= 20
        pdf.drawString(100, y, f"Status: {quote.data[0]['status']}")
        y -= 40
        
        # Line Items Table
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, y, "Line Items")
        y -= 25
        
        # Table headers
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(100, y, "Item")
        pdf.drawString(250, y, "Qty")
        pdf.drawString(310, y, "Unit")
        pdf.drawString(370, y, "Unit Price")
        pdf.drawString(450, y, "Total")
        y -= 15
        pdf.line(100, y, 550, y)
        y -= 15
        
        # Table rows
        pdf.setFont("Helvetica", 10)
        total_items = 0
        for item in line_items.data:
            if y < 100:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(100, y, "Item")
                pdf.drawString(250, y, "Qty")
                pdf.drawString(310, y, "Unit")
                pdf.drawString(370, y, "Unit Price")
                pdf.drawString(450, y, "Total")
                y -= 15
                pdf.line(100, y, 550, y)
                y -= 15
                pdf.setFont("Helvetica", 10)
            
            pdf.drawString(100, y, item['material_name'][:20])
            pdf.drawString(250, y, str(item['quantity']))
            pdf.drawString(310, y, item['unit'])
            pdf.drawString(370, y, f"${item['unit_price']:.2f}")
            pdf.drawString(450, y, f"${item['total_price']:.2f}")
            y -= 20
            total_items += 1
        
        # Summary
        y -= 20
        pdf.line(100, y, 550, y)
        y -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(350, y, f"Total Items: {total_items}")
        y -= 20
        pdf.drawString(350, y, f"Total Amount: ${quote.data[0]['total_amount']:,.2f}")
        
        pdf.save()
        
        # Return PDF
        buffer.seek(0)
        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=quote_report_{quote_id[:8]}.pdf"}
        )
        
    except Exception as e:
        return error(message=str(e), status_code=500)
