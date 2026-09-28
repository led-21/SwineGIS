# -*- coding: utf-8 -*-
"""Agronomic and technical standards for swine facilities.

Parameters are based on technical guidelines for swine facility design
(e.g., Embrapa Swine & Poultry technical circulars, rural engineering literature).
All values represent experimental / planning defaults and can be adapted.
"""

from typing import Dict, Any
from .models import FacilityType


SWINE_STANDARDS: Dict[FacilityType, Dict[str, Any]] = {
    FacilityType.FINISHING: {
        "m2_per_head": 1.00,             # ~1.0 m2 per finishing pig (>100kg)
        "recommended_buffer_m": 50.0,    # standard biosecurity boundary
        "sanitary_isolation_m": 100.0,   # distance from public roads / boundaries
        "min_spacing_between_sheds": 15.0, # distance for natural cross-ventilation
        "max_recommended_width_m": 16.0, # max width for natural ventilation without fans
        "default_shape": "Retangular",
        "description": "Galpão destinado à terminação de suínos (30 a 110+ kg)."
    },
    FacilityType.NURSERY: {
        "m2_per_head": 0.35,             # ~0.30 - 0.40 m2 per nursery piglet
        "recommended_buffer_m": 50.0,
        "sanitary_isolation_m": 100.0,
        "min_spacing_between_sheds": 12.0,
        "max_recommended_width_m": 14.0,
        "default_shape": "Retangular",
        "description": "Galpão para leitões desmamados até fase de crescimento."
    },
    FacilityType.GESTATION: {
        "m2_per_head": 2.50,             # ~2.2 - 2.8 m2 per sow in group housing
        "recommended_buffer_m": 60.0,
        "sanitary_isolation_m": 120.0,
        "min_spacing_between_sheds": 15.0,
        "max_recommended_width_m": 16.0,
        "default_shape": "Retangular",
        "description": "Alojamento de porcas em gestação (coletiva ou mista)."
    },
    FacilityType.FARROWING: {
        "m2_per_head": 4.50,             # ~4.2 - 5.0 m2 per farrowing crate + circ
        "recommended_buffer_m": 60.0,
        "sanitary_isolation_m": 120.0,
        "min_spacing_between_sheds": 15.0,
        "max_recommended_width_m": 14.0,
        "default_shape": "Retangular",
        "description": "Maternidade com celas parideiras e escamoteador térmico."
    },
    FacilityType.WEAN_TO_FINISH: {
        "m2_per_head": 0.85,
        "recommended_buffer_m": 50.0,
        "sanitary_isolation_m": 100.0,
        "min_spacing_between_sheds": 15.0,
        "max_recommended_width_m": 16.0,
        "default_shape": "Retangular",
        "description": "Sistema de ciclo contínuo do desmame ao abate na mesma baia."
    },
    FacilityType.QUARANTINE: {
        "m2_per_head": 3.00,
        "recommended_buffer_m": 100.0,   # strict biosecurity isolation
        "sanitary_isolation_m": 250.0,   # isolation from commercial herds
        "min_spacing_between_sheds": 30.0,
        "max_recommended_width_m": 12.0,
        "default_shape": "Retangular",
        "description": "Isolamento sanitário de animais de reposição e novos lotes."
    },
    FacilityType.FEED_SILO: {
        "m2_per_head": None,             # storage unit, not animal housing
        "recommended_buffer_m": 15.0,
        "sanitary_isolation_m": 30.0,
        "min_spacing_between_sheds": 8.0,
        "max_recommended_width_m": 20.0,
        "default_shape": "Circular",
        "description": "Silos aéreos verticais metálicos para estocagem de ração."
    },
    FacilityType.MANURE_LAGOON: {
        "m2_per_head": None,             # environmental unit
        "recommended_buffer_m": 150.0,   # odor and environmental protection zone
        "sanitary_isolation_m": 300.0,   # isolation from water springs and dwellings
        "min_spacing_between_sheds": 25.0,
        "max_recommended_width_m": 100.0,
        "default_shape": "Circular",     # or rectangular
        "description": "Lagoa de estabilização anaeróbia / esterqueira para biofertilizante."
    },
    FacilityType.COMPOSTING: {
        "m2_per_head": None,
        "recommended_buffer_m": 80.0,
        "sanitary_isolation_m": 150.0,
        "min_spacing_between_sheds": 15.0,
        "max_recommended_width_m": 20.0,
        "default_shape": "Retangular",
        "description": "Composteira coberta para destinação de carcaças e resíduos orgânicos."
    }
}
