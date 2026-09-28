# -*- coding: utf-8 -*-
"""Generates QGIS vector layers from planning results."""

from typing import Tuple, Optional
try:
    from ..core.domain.models import PlanningResult, ShapeType
except (ImportError, ValueError):
    from core.domain.models import PlanningResult, ShapeType

try:
    from qgis.core import (
        QgsVectorLayer,
        QgsField,
        QgsFeature,
        QgsGeometry,
        QgsPointXY,
        QgsProject,
        QgsCoordinateReferenceSystem,
        QgsFillSymbol,
        QgsSingleSymbolRenderer,
    )
    from qgis.PyQt.QtCore import QVariant
    from qgis.PyQt.QtGui import QColor, Qt
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False


class SwineLayerGenerator:
    """Creates styled QGIS vector layers representing facilities and biosecurity buffers."""

    @classmethod
    def create_qgis_layers(
        cls,
        planning_result: PlanningResult,
        crs_authid: str,
        add_to_project: bool = True
    ) -> Tuple[Optional["QgsVectorLayer"], Optional["QgsVectorLayer"]]:
        """Convert a PlanningResult into QGIS vector layers.

        :returns: Tuple containing (facilities_layer, buffers_layer).
        """
        if not HAS_QGIS:
            return None, None

        # 1. Create Facilities Layer
        facilities_layer = QgsVectorLayer(
            f"Polygon?crs={crs_authid}",
            f"Instalações - {planning_result.specification.facility_type.value}",
            "memory"
        )
        fac_provider = facilities_layer.dataProvider()

        fac_provider.addAttributes([
            QgsField("id", QVariant.String),
            QgsField("tipo", QVariant.String),
            QgsField("forma", QVariant.String),
            QgsField("unidade", QVariant.Int),
            QgsField("area_m2", QVariant.Double, len=10, prec=2),
            QgsField("capacidade_animais", QVariant.Int),
            QgsField("buffer_sanitario_m", QVariant.Double, len=6, prec=1),
        ])
        facilities_layer.updateFields()

        # 2. Create Buffers Layer
        buffers_layer = QgsVectorLayer(
            f"Polygon?crs={crs_authid}",
            f"Buffers de Biosseguridade - {planning_result.specification.facility_type.value}",
            "memory"
        )
        buf_provider = buffers_layer.dataProvider()

        buf_provider.addAttributes([
            QgsField("id", QVariant.String),
            QgsField("tipo", QVariant.String),
            QgsField("raio_buffer_m", QVariant.Double, len=6, prec=1),
            QgsField("finalidade", QVariant.String),
        ])
        buffers_layer.updateFields()

        # 3. Populate features
        facility_features = []
        buffer_features = []

        for fac in planning_result.facilities:
            # Facility polygon
            qgs_pts = [QgsPointXY(x, y) for x, y in fac.polygon_coords]
            geom = QgsGeometry.fromPolygonXY([qgs_pts])

            feat = QgsFeature(facilities_layer.fields())
            feat.setGeometry(geom)
            feat.setAttribute("id", fac.identifier)
            feat.setAttribute("tipo", fac.facility_type.value)
            feat.setAttribute("forma", fac.shape_type.value)
            feat.setAttribute("unidade", fac.unit_index)
            feat.setAttribute("area_m2", fac.footprint_m2)
            feat.setAttribute("capacidade_animais", fac.capacity_heads if fac.capacity_heads is not None else 0)
            feat.setAttribute("buffer_sanitario_m", planning_result.metrics.recommended_buffer_m)
            facility_features.append(feat)

            # Buffer polygon
            if fac.buffer_polygon_coords:
                buf_pts = [QgsPointXY(x, y) for x, y in fac.buffer_polygon_coords]
                buf_geom = QgsGeometry.fromPolygonXY([buf_pts])

                buf_feat = QgsFeature(buffers_layer.fields())
                buf_feat.setGeometry(buf_geom)
                buf_feat.setAttribute("id", f"BUF_{fac.identifier}")
                buf_feat.setAttribute("tipo", fac.facility_type.value)
                buf_feat.setAttribute("raio_buffer_m", planning_result.metrics.recommended_buffer_m)
                buf_feat.setAttribute("finalidade", "Isolamento sanitário e dispersão de ventilação")
                buffer_features.append(buf_feat)

        fac_provider.addFeatures(facility_features)
        facilities_layer.updateExtents()

        buf_provider.addFeatures(buffer_features)
        buffers_layer.updateExtents()

        # Apply simple visual styling
        cls._apply_symbology(facilities_layer, buffers_layer)

        if add_to_project:
            # Add buffers below facilities for clear visual hierarchy
            QgsProject.instance().addMapLayer(buffers_layer)
            QgsProject.instance().addMapLayer(facilities_layer)

        return facilities_layer, buffers_layer

    @classmethod
    def _apply_symbology(cls, fac_layer: "QgsVectorLayer", buf_layer: "QgsVectorLayer"):
        """Apply clean styles to distinguish facilities from biosecurity buffers."""
        try:
            # Facility style: Amber/Terracotta fill with dark border
            fac_symbol = QgsFillSymbol.createSimple({
                "color": "220,110,60,220",
                "color_border": "120,40,20,255",
                "width_border": "0.6",
                "style": "solid",
            })
            fac_layer.setRenderer(QgsSingleSymbolRenderer(fac_symbol))
            fac_layer.triggerRepaint()

            # Buffer style: Translucent light blue/grey with dashed border
            buf_symbol = QgsFillSymbol.createSimple({
                "color": "70,130,180,45",
                "color_border": "40,90,140,200",
                "width_border": "0.4",
                "style": "solid",
                "border_style": "dash",
            })
            buf_layer.setRenderer(QgsSingleSymbolRenderer(buf_symbol))
            buf_layer.triggerRepaint()
        except Exception:
            # Fail gracefully if advanced symbol configuration is restricted
            pass
