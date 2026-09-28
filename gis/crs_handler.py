# -*- coding: utf-8 -*-
"""CRS helper and coordinate transformation utilities for PyQGIS."""

import math
from typing import Tuple, Optional

try:
    from qgis.core import (
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsProject,
        QgsPointXY,
    )
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False


class CRSHandler:
    """Manages Coordinate Reference System detection, validation, and coordinate projection."""

    @classmethod
    def get_project_crs_authid(cls, default: str = "EPSG:31982") -> str:
        """Get current QGIS project CRS authid, defaulting to SIRGAS 2000 / UTM zone 22S if unset."""
        if not HAS_QGIS:
            return default
        project = QgsProject.instance()
        crs = project.crs()
        if crs.isValid() and crs.authid():
            return crs.authid()
        return default

    @classmethod
    def is_projected(cls, crs_authid: str) -> bool:
        """Check if CRS authid uses metric units (projected)."""
        if not HAS_QGIS:
            return not (crs_authid.upper() in ("EPSG:4326", "WGS84", "CRS:84"))
        crs = QgsCoordinateReferenceSystem(crs_authid)
        if not crs.isValid():
            return False
        # If map units are meters
        return not crs.isGeographic()

    @classmethod
    def transform_point(
        cls,
        x: float,
        y: float,
        source_authid: str,
        dest_authid: str
    ) -> Tuple[float, float]:
        """Transform coordinate point between two CRS systems."""
        if source_authid.upper() == dest_authid.upper():
            return (x, y)

        if not HAS_QGIS:
            return (x, y)

        src_crs = QgsCoordinateReferenceSystem(source_authid)
        dst_crs = QgsCoordinateReferenceSystem(dest_authid)

        if not src_crs.isValid() or not dst_crs.isValid():
            return (x, y)

        transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
        pt = transform.transform(QgsPointXY(x, y))
        return (pt.x(), pt.y())
