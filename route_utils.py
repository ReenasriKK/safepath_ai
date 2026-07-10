import hashlib
import random
from typing import List, Dict
from models import Hazard, db


def deterministic_random(seed_str: str):
    h = hashlib.md5(seed_str.encode('utf-8')).hexdigest()
    seed = int(h[:8], 16)
    return random.Random(seed)


def generate_routes(source: str, destination: str, count: int = 3) -> List[Dict]:
    """Generate `count` deterministic route options between source/destination.

    This is a lightweight simulation: it samples hazards from the `Hazard` table
    to produce per-route detected hazards which the safety engine can score.
    """
    r = deterministic_random(source + '|' + destination)
    routes = []
    # gather available hazard types
    try:
        hazard_rows = Hazard.query.all()
        hazard_types = [h.hazard_type for h in hazard_rows] if hazard_rows else ['Pothole','Garbage','Construction Area']
    except Exception:
        hazard_types = ['Pothole','Garbage','Construction Area']

    for i in range(count):
        # distance between 2 and 20 km
        distance = round(r.uniform(2.0 + i*1.0, 8.0 + i*4.0), 2)
        # time in minutes
        eta = int(distance / 40 * 60 + r.randint(2,15))
        # choose 0-3 hazards
        num_haz = r.randint(0,3)
        hazards = []
        for j in range(num_haz):
            lbl = r.choice(hazard_types)
            hazards.append({'label': lbl, 'confidence': round(r.uniform(0.3,0.98),2)})

        routes.append({
            'name': f'Route {chr(65+i)}',
            'distance_km': distance,
            'eta_min': eta,
            'hazards': hazards
        })

    return routes
