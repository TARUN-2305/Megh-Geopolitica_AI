"""
CAUSAL GRAPH DEFINITION
Uses pgmpy to create Directed Acyclic Graph of geopolitical impacts
All nodes and edges defined with conditional probability tables
"""

from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np

def build_causal_graph():
    """
    Returns a Bayesian Network with structure:
    
    Strait_Blockage -> Freight_Cost -> Import_Price -> Local_LPG_Price
    Conflict_Intensity -> Brent_Crude -> Import_Price
    Sanctions -> Brent_Crude
    USD_INR -> Import_Price
    Local_Inventory -> Shortage_Probability
    Import_Price -> Shortage_Probability
    """
    
    model = BayesianNetwork([
        ('Strait_Blockage', 'Freight_Cost'),
        ('Conflict_Intensity', 'Brent_Crude'),
        ('Sanctions', 'Brent_Crude'),
        ('Brent_Crude', 'Import_Price'),
        ('Freight_Cost', 'Import_Price'),
        ('USD_INR', 'Import_Price'),
        ('Import_Price', 'Local_LPG_Price'),
        ('Local_Inventory', 'Shortage_Probability'),
        ('Local_LPG_Price', 'Shortage_Probability')
    ])
    
    # Define CPDs (Conditional Probability Distributions)
    # Strait_Blockage: 0=no, 1=partial, 2=full
    cpd_strait = TabularCPD('Strait_Blockage', 3, [[0.7], [0.2], [0.1]])
    
    # Conflict_Intensity: 0=low, 1=medium, 2=high
    cpd_conflict = TabularCPD('Conflict_Intensity', 3, [[0.5], [0.3], [0.2]])
    
    # Sanctions: 0=none, 1=new, 2=severe
    cpd_sanctions = TabularCPD('Sanctions', 3, [[0.8], [0.15], [0.05]])
    
    # USD_INR: 0=stable, 1=rising, 2=falling
    cpd_usd = TabularCPD('USD_INR', 3, [[0.6], [0.3], [0.1]])
    
    # Local_Inventory: 0=high, 1=medium, 2=low
    cpd_inventory = TabularCPD('Local_Inventory', 3, [[0.3], [0.4], [0.3]])
    
    # Brent_Crude depends on Conflict and Sanctions
    # Values defined in a 3x9 matrix for the 3 levels of Brent_Crude given combinations of Conflict and Sanctions
    cpd_brent = TabularCPD('Brent_Crude', 3,
                          evidence=['Conflict_Intensity', 'Sanctions'],
                          evidence_card=[3, 3],
                          values=np.array([
                              # sanction0: price low, med, high for conflict 0,1,2
                              [0.8, 0.3, 0.1, 0.7, 0.2, 0.05, 0.6, 0.1, 0.02],
                              [0.15, 0.4, 0.3, 0.2, 0.4, 0.2, 0.25, 0.3, 0.1],
                              [0.05, 0.3, 0.6, 0.1, 0.4, 0.75, 0.15, 0.6, 0.88]
                          ]))
    
    # Simplified CPDs for other nodes for MVP
    cpd_freight = TabularCPD('Freight_Cost', 3, evidence=['Strait_Blockage'], evidence_card=[3],
                             values=[[0.8, 0.2, 0.05], [0.15, 0.5, 0.25], [0.05, 0.3, 0.7]])
    
    cpd_import = TabularCPD('Import_Price', 3, evidence=['Brent_Crude', 'Freight_Cost', 'USD_INR'], evidence_card=[3, 3, 3],
                            values=np.full((3, 27), 1/3)) # Uniform for now, update with real logic
    
    cpd_local = TabularCPD('Local_LPG_Price', 3, evidence=['Import_Price'], evidence_card=[3],
                           values=[[0.7, 0.2, 0.1], [0.2, 0.6, 0.2], [0.1, 0.2, 0.7]])
    
    cpd_shortage = TabularCPD('Shortage_Probability', 3, evidence=['Local_Inventory', 'Local_LPG_Price'], evidence_card=[3, 3],
                              values=np.full((3, 9), 1/3))
    
    model.add_cpds(cpd_strait, cpd_conflict, cpd_sanctions, cpd_usd, cpd_inventory, 
                   cpd_brent, cpd_freight, cpd_import, cpd_local, cpd_shortage)
    
    assert model.check_model()
    return model
