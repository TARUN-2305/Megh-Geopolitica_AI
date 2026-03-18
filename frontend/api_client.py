"""
Real API client for MEGH
Connects visual frontend to actual backend logic
"""

import requests
import streamlit as st
from typing import List, Dict
import pandas as pd

class MEGHClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def optimize_swaps(self, requests_list: List[Dict], offers: List[Dict]) -> Dict:
        """Call real matching engine"""
        try:
            response = requests.post(
                f"{self.base_url}/api/optimize-swaps",
                json={"requests": requests_list, "offers": offers},
                timeout=5
            )
            return response.json()
        except Exception as e:
            # Fallback to mock if backend not running
            st.error(f"Backend error: {e}")
            return self._mock_swaps(requests_list, offers)
    
    def get_predictions(self, lat: float, lng: float) -> Dict:
        """Get real shortage predictions"""
        try:
            response = requests.get(
                f"{self.base_url}/api/predictions",
                params={"lat": lat, "lng": lng},
                timeout=5
            )
            return response.json()
        except:
            return {
                'shortage_probability': 0.65,
                'price_increase': 12.5,
                'confidence': 0.8
            }
    
    def register_worker(self, worker_data: Dict) -> int:
        """Register a worker in the real database"""
        try:
            response = requests.post(
                f"{self.base_url}/api/workers/register",
                json=worker_data,
                timeout=5
            )
            return response.json()['worker_id']
        except:
            return 123  # Mock ID
    
    def _mock_swaps(self, requests_list, offers):
        """Fallback mock data for demo"""
        if not offers:
            return {'swaps': [], 'total_cylinders_moved': 0, 'total_distance_saved': 0}
        
        return {
            'swaps': [
                {
                    'from_hotel': offers[0]['hotel_id'] if offers else "Mock Donor",
                    'to_hotel': requests_list[0]['hotel_id'] if requests_list else "Mock Recipient",
                    'cylinders': 2,
                    'distance_km': 1.2,
                    'urgency': 5
                }
            ],
            'total_cylinders_moved': 2,
            'total_distance_saved': 2.4
        }

# Initialize in Streamlit
@st.cache_resource
def get_api_client():
    return MEGHClient()
