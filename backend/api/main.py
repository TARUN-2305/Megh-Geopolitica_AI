from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import re
import os

app = FastAPI(title="MEGH API", description="Backend API for MEGH Geopolitical Resilience Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MEGH API is online", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include routers
from backend.core.layer2_hive.matching_optimization import router as swaps_router
from backend.core.layer3_heart.worker_registry import router as workers_router

app.include_router(swaps_router, prefix="/api", tags=["Swaps"])
app.include_router(workers_router, prefix="/api/workers", tags=["Workers"])

@app.post("/api/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Handle incoming WhatsApp messages from Twilio.
    Format: "HOTEL_ID surplus/shortage QTY"
    Example: "12 surplus 5"
    """
    # Simple regex parsing
    match = re.search(r'(\d+)\s+(surplus|shortage)\s+(\d+)', Body, re.I)
    
    if match:
        hotel_id = int(match.group(1))
        action = match.group(2).lower()
        qty = int(match.group(3))
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        DB_PATH = os.path.join(BASE_DIR, "backend", "data", "hotels.db")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            if action == 'surplus':
                # Increase stock
                c.execute("UPDATE hotels SET lpg_stock = MIN(lpg_capacity, lpg_stock + ?) WHERE id = ?", (qty, hotel_id))
            else:
                # Decrease stock
                c.execute("UPDATE hotels SET lpg_stock = MAX(0, lpg_stock - ?) WHERE id = ?", (qty, hotel_id))
            
            if c.rowcount > 0:
                conn.commit()
                response_msg = f"✅ Updated: Hotel {hotel_id} stock adjusted by {qty} units."
            else:
                response_msg = f"❌ Error: Hotel ID {hotel_id} not found."
            conn.close()
        except Exception as e:
            response_msg = f"❌ DB Error: {str(e)}"
    else:
        response_msg = "⚠️ Invalid format. Use: HOTEL_ID surplus/shortage QTY (e.g. '12 surplus 5')"

    # Return TwiML (Required by Twilio)
    from fastapi.responses import Response
    twiml = f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{response_msg}</Message></Response>"
    return Response(content=twiml, media_type="application/xml")
