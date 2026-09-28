# coding=utf-8
"""Tests for QGIS functionality."""

import os
import unittest

try:
    from qgis.core import (
        QgsProviderRegistry,
        QgsCoordinateReferenceSystem,
        QgsRasterLayer
    )
    from .utilities import get_qgis_app
    QGIS_APP, _, _, _ = get_qgis_app()
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False
    QGIS_APP = None


class QGISTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def setUp(self):
        if not HAS_QGIS or QGIS_APP is None:
            self.skipTest("QGIS environment not available")

    def test_qgis_environment(self):
        """QGIS environment has the expected providers"""
        r = QgsProviderRegistry.instance()
        self.assertIn('gdal', r.providerList())
        self.assertIn('ogr', r.providerList())

    def test_projection(self):
        """Test that QGIS properly parses a wkt string."""
        crs = QgsCoordinateReferenceSystem()
        wkt = (
            'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
            'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
            'PRIMEM["Greenwich",0.0],UNIT["Degree",'
            '0.0174532925199433]]'
        )
        crs.createFromWkt(wkt)
        auth_id = crs.authid()
        expected_auth_id = 'EPSG:4326'
        self.assertEqual(auth_id, expected_auth_id)


if __name__ == '__main__':
    unittest.main()
