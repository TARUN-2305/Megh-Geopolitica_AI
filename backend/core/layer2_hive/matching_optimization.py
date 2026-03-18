"""
REAL matching engine using PuLP optimization
Not a shell - this actually works
"""

import pulp
import numpy as np
from typing import List, Dict, Tuple
from geopy.distance import geodesic

class FuelSwapOptimizer:
    """
    Solves the optimal fuel redistribution problem:
    - Minimize total travel distance
    - Respect supply/demand constraints
    - Prioritize urgent requests
    """
    
    def __init__(self):
        self.donors = []  # Hotels with surplus
        self.recipients = []  # Hotels in need
        self.distances = {}  # (donor_idx, recipient_idx) -> km
        
    def add_hotel(self, hotel_id: str, location: Tuple[float, float], 
                  surplus: int = 0, demand: int = 0, urgency: int = 1):
        """Add a hotel to the optimization pool"""
        if surplus > 0:
            self.donors.append({
                'id': hotel_id,
                'loc': location,
                'supply': surplus,
                'urgency': 1  # Donors aren't urgent
            })
        if demand > 0:
            self.recipients.append({
                'id': hotel_id,
                'loc': location,
                'demand': demand,
                'urgency': urgency  # 1-5 scale, 5 most urgent
            })
    
    def calculate_distances(self):
        """Precompute all distances between donors and recipients"""
        for i, donor in enumerate(self.donors):
            for j, recipient in enumerate(self.recipients):
                dist = geodesic(donor['loc'], recipient['loc']).kilometers
                self.distances[(i, j)] = dist
    
    def solve(self) -> List[Dict]:
        """
        Solve the transportation problem
        Returns list of optimal swaps
        """
        if not self.donors or not self.recipients:
            return []
        
        self.calculate_distances()
        
        # Create problem
        prob = pulp.LpProblem("FuelSwap", pulp.LpMinimize)
        
        # Decision variables: x[i][j] = cylinders from donor i to recipient j
        x = pulp.LpVariable.dicts("route",
                                 ((i, j) for i in range(len(self.donors)) 
                                  for j in range(len(self.recipients))),
                                 lowBound=0,
                                 cat='Integer')
        
        # OBJECTIVE: Minimize weighted distance (urgency makes distance matter more)
        prob += pulp.lpSum([
            x[(i, j)] * self.distances[(i, j)] * (1 + 0.5 * self.recipients[j]['urgency'])
            for i in range(len(self.donors))
            for j in range(len(self.recipients))
        ])
        
        # CONSTRAINT: Donors can't give more than they have
        for i in range(len(self.donors)):
            prob += pulp.lpSum([x[(i, j)] for j in range(len(self.recipients))]) <= self.donors[i]['supply']
        
        # CONSTRAINT: Recipients get what they need
        for j in range(len(self.recipients)):
            prob += pulp.lpSum([x[(i, j)] for i in range(len(self.donors))]) >= self.recipients[j]['demand']
        
        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Extract results
        swaps = []
        for i in range(len(self.donors)):
            for j in range(len(self.recipients)):
                amount = int(x[(i, j)].varValue) if x[(i, j)].varValue else 0
                if amount > 0:
                    swaps.append({
                        'from_hotel': self.donors[i]['id'],
                        'to_hotel': self.recipients[j]['id'],
                        'cylinders': amount,
                        'distance_km': round(self.distances[(i, j)], 1),
                        'urgency': self.recipients[j]['urgency']
                    })
        
        return swaps


# FastAPI endpoint to use this
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SwapRequest(BaseModel):
    hotel_id: str
    lat: float
    lng: float
    demand: int
    urgency: int = 1

class SurplusOffer(BaseModel):
    hotel_id: str
    lat: float
    lng: float
    surplus: int

@router.post("/optimize-swaps")
async def optimize_swaps(requests: List[SwapRequest], offers: List[SurplusOffer]):
    """Real-time swap optimization"""
    optimizer = FuelSwapOptimizer()
    
    # Add all hotels
    for offer in offers:
        optimizer.add_hotel(
            hotel_id=offer.hotel_id,
            location=(offer.lat, offer.lng),
            surplus=offer.surplus
        )
    
    for req in requests:
        optimizer.add_hotel(
            hotel_id=req.hotel_id,
            location=(req.lat, req.lng),
            demand=req.demand,
            urgency=req.urgency
        )
    
    # Solve
    swaps = optimizer.solve()
    
    return {
        'success': True,
        'swaps': swaps,
        'total_cylinders_moved': sum(s['cylinders'] for s in swaps),
        'total_distance_saved': sum(s['distance_km'] * s['cylinders'] for s in swaps)
    }
