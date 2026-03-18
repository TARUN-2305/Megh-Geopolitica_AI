"""
REAL worker registry and matching
Uses SQLite for persistence and TF-IDF for skill matching
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime

class WorkerRegistry:
    def __init__(self, db_path="backend/data/workers.db"):
        self.db_path = db_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.vectorizer = TfidfVectorizer()
        self.skill_vectors = None
        self.worker_ids = []
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Workers table
        c.execute('''
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                skills TEXT,  -- JSON array
                location_lat REAL,
                location_lng REAL,
                current_hotel_id INTEGER,
                status TEXT DEFAULT 'available',
                daily_wage INTEGER,
                registered_date TIMESTAMP
            )
        ''')
        
        # Job openings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS job_openings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id INTEGER NOT NULL,
                skill_required TEXT,
                daily_wage INTEGER,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT DEFAULT 'open'
            )
        ''')
        
        # Placements table
        c.execute('''
            CREATE TABLE IF NOT EXISTS placements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER,
                hotel_id INTEGER,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                daily_wage INTEGER,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_worker(self, name: str, phone: str, skills: List[str], 
                       lat: float, lng: float, wage: int) -> int:
        """Register a new worker"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO workers (name, phone, skills, location_lat, location_lng, 
                               daily_wage, registered_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, json.dumps(skills), lat, lng, 
              wage, datetime.now(), 'available'))
        
        worker_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Invalidate skill vectors cache
        self.skill_vectors = None
        
        return worker_id
    
    def create_job(self, hotel_id: int, skill_required: str, 
                  wage: int, days: int) -> int:
        """Create a temporary job opening"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO job_openings (hotel_id, skill_required, daily_wage,
                                    start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (hotel_id, skill_required, wage, 
              datetime.now(), 
              datetime.now().replace(day=(datetime.now().day + days) % 28 + 1), # Simple wrap
              'open'))
        
        job_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def match_workers_to_job(self, job_id: int, top_k: int = 5) -> List[Dict]:
        """Find best workers for a job using TF-IDF similarity"""
        conn = sqlite3.connect(self.db_path)
        
        # Get job details
        job = conn.execute('''
            SELECT hotel_id, skill_required, daily_wage 
            FROM job_openings WHERE id = ?
        ''', (job_id,)).fetchone()
        
        if not job:
            return []
        
        # Get all available workers
        workers = conn.execute('''
            SELECT id, name, skills, location_lat, location_lng, daily_wage
            FROM workers WHERE status = 'available'
        ''').fetchall()
        
        conn.close()
        
        if not workers:
            return []
        
        # Build skill vectors
        worker_skills = [json.loads(w[2]) for w in workers]
        job_skills = [job[1]]
        
        # Combine all skills for vectorization
        all_skills = [' '.join(skills) for skills in worker_skills] + job_skills
        
        # Fit TF-IDF
        vectors = self.vectorizer.fit_transform(all_skills)
        worker_vectors = vectors[:-1]
        job_vector = vectors[-1]
        
        # Calculate similarities
        similarities = cosine_similarity(job_vector, worker_vectors).flatten()
        
        # Get top matches
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        matches = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold
                w = workers[idx]
                matches.append({
                    'worker_id': w[0],
                    'name': w[1],
                    'skills': json.loads(w[2]),
                    'similarity': float(similarities[idx]),
                    'distance_km': self._calculate_distance(
                        (w[3], w[4]), 
                        self._get_hotel_location(job[0])
                    )
                })
        
        return matches
    
    def _get_hotel_location(self, hotel_id):
        """Get hotel coordinates from database"""
        # This would query the hotels table
        # For now return mock
        return (12.97, 77.59)  # Malleswaram
    
    def _calculate_distance(self, loc1, loc2):
        """Calculate distance between two points"""
        from geopy.distance import geodesic
        return round(geodesic(loc1, loc2).kilometers, 1)

# FastAPI endpoint to use this
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
registry = WorkerRegistry()

class WorkerData(BaseModel):
    name: str
    phone: str
    skills: List[str]
    lat: float
    lng: float
    wage: int

@router.post("/register")
async def register_worker(data: WorkerData):
    """Register a new worker"""
    worker_id = registry.register_worker(
        name=data.name,
        phone=data.phone,
        skills=data.skills,
        lat=data.lat,
        lng=data.lng,
        wage=data.wage
    )
    return {"success": True, "worker_id": worker_id}

@router.get("/match/{job_id}")
async def match_workers(job_id: int):
    """Match workers to a job"""
    matches = registry.match_workers_to_job(job_id)
    return {"success": True, "matches": matches}
