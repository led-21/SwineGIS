# -*- coding: utf-8 -*-
"""Integration tests for PyQGIS layer creation and CRS handling."""

import unittest
from core.domain.models import (
    FacilitySpecification,
    FacilityType,
    ShapeType,
)
from core.services.planner import SwineFacilityPlannerService
from gis.layer_generator import SwineLayerGenerator
from gis.crs_handler import CRSHandler

try:
    from qgis.core import QgsApplication
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False


class TestGISIntegration(unittest.TestCase):
    """Test PyQGIS layer creation and CRS integration."""

    def setUp(self):
        if not HAS_QGIS:
            self.skipTest("PyQGIS environment not available")

    def test_crs_handler_defaults(self):
        """Verify fallback CRS authid when outside active QGIS session."""
        authid = CRSHandler.get_project_crs_authid(default="EPSG:31982")
        self.assertEqual(authid, "EPSG:31982")

    def test_layer_generator(self):
        """Verify vector layers creation when PyQGIS is available."""
        spec = FacilitySpecification(
            facility_type=FacilityType.FINISHING,
            shape_type=ShapeType.RECTANGULAR,
            length=80.0,
            width=12.0,
            count=1,
            center_x=0.0,
            center_y=0.0,
        )
        plan_result = SwineFacilityPlannerService.plan_layout(spec, crs_auth_id="EPSG:31982")
        fac_layer, buf_layer = SwineLayerGenerator.create_qgis_layers(
            plan_result,
            crs_authid="EPSG:31982",
            add_to_project=False
        )
        self.assertIsNotNone(fac_layer)
        self.assertIsNotNone(buf_layer)
        self.assertEqual(fac_layer.featureCount(), 1)
        self.assertEqual(buf_layer.featureCount(), 1)


if __name__ == '__main__':
    unittest.main()
