# -*- coding: utf-8 -*-
"""Dialog window implementation for facility planning."""

import os
from typing import Optional

from qgis.PyQt import uic, QtWidgets
try:
    from ..core.domain.models import FacilityType, ShapeType, FacilitySpecification
    from ..core.domain.standards import SWINE_STANDARDS
    from ..core.services.planner import SwineFacilityPlannerService
    from ..core.domain.validators import ValidationError
except (ImportError, ValueError):
    from core.domain.models import FacilityType, ShapeType, FacilitySpecification
    from core.domain.standards import SWINE_STANDARDS
    from core.services.planner import SwineFacilityPlannerService
    from core.domain.validators import ValidationError

UI_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "suino_alpha_dialog_base.ui"
)
FORM_CLASS, _ = uic.loadUiType(UI_PATH)


class SwineSpatialPlannerDialog(QtWidgets.QDialog, FORM_CLASS):
    """Interactive dialog for swine facility layout parameterization."""

    def __init__(self, parent=None, iface=None):
        super(SwineSpatialPlannerDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface

        self._populate_options()
        self._connect_signals()
        self._on_type_changed()
        self._update_preview()

    def _populate_options(self):
        """Populate combo boxes with domain values."""
        self.comboBox_type.clear()
        for ftype in FacilityType:
            self.comboBox_type.addItem(ftype.value, ftype)

        self.comboBox_shape.clear()
        for shape in ShapeType:
            self.comboBox_shape.addItem(shape.value, shape)

    def _connect_signals(self):
        """Bind UI events to reactive handlers."""
        self.comboBox_type.currentIndexChanged.connect(self._on_type_changed)
        self.comboBox_shape.currentIndexChanged.connect(self._on_shape_changed)

        self.spinBox_length.valueChanged.connect(self._update_preview)
        self.spinBox_width.valueChanged.connect(self._update_preview)
        self.spinBox_radius.valueChanged.connect(self._update_preview)
        self.spinBox_number.valueChanged.connect(self._update_preview)
        self.spinBox_spacing.valueChanged.connect(self._update_preview)

        if hasattr(self, "btn_capture_map_center"):
            self.btn_capture_map_center.clicked.connect(self._capture_map_center)

    def _on_type_changed(self):
        """Auto-configure shape and recommended defaults when facility type changes."""
        selected_type = self.comboBox_type.currentData()
        if not selected_type:
            return

        standards = SWINE_STANDARDS.get(selected_type, {})
        default_shape_str = standards.get("default_shape", "Retangular")

        for idx in range(self.comboBox_shape.count()):
            if self.comboBox_shape.itemText(idx) == default_shape_str:
                self.comboBox_shape.setCurrentIndex(idx)
                break

        # Defaults based on facility nature
        if selected_type == FacilityType.FEED_SILO:
            self.spinBox_radius.setValue(4.0)
            self.spinBox_number.setValue(2)
        elif selected_type == FacilityType.MANURE_LAGOON:
            self.spinBox_radius.setValue(20.0)
            self.spinBox_number.setValue(1)
        elif selected_type == FacilityType.FINISHING:
            self.spinBox_length.setValue(100.0)
            self.spinBox_width.setValue(12.0)
            self.spinBox_spacing.setValue(18.0)
        elif selected_type == FacilityType.NURSERY:
            self.spinBox_length.setValue(60.0)
            self.spinBox_width.setValue(10.0)
            self.spinBox_spacing.setValue(15.0)

        self._on_shape_changed()

    def _on_shape_changed(self):
        """Toggle input field availability according to selected geometry."""
        selected_shape = self.comboBox_shape.currentData()
        is_rect = (selected_shape == ShapeType.RECTANGULAR)

        self.spinBox_length.setEnabled(is_rect)
        self.spinBox_width.setEnabled(is_rect)
        self.label_length.setEnabled(is_rect)
        self.label_width.setEnabled(is_rect)

        self.spinBox_radius.setEnabled(not is_rect)
        self.label_radius.setEnabled(not is_rect)

        self._update_preview()

    def _update_preview(self):
        """Compute real-time estimates and display summary in dialog."""
        try:
            spec = self.get_specification()
            metrics = SwineFacilityPlannerService.calculate_metrics(spec)

            cap_str = f"{metrics.estimated_capacity_heads:,} animais" if metrics.estimated_capacity_heads else "N/A (estrutura auxiliar)"
            text = (
                f"📐 Área por Unidade: {metrics.unit_footprint_m2:.1f} m²  |  "
                f"Total ({spec.count} un): {metrics.total_footprint_m2:.1f} m²\n"
                f"🐖 Capacidade Total Estimada: {cap_str}\n"
                f"🛡️ Buffer de Biosseguridade Recomendado: {metrics.recommended_buffer_m:.0f} m  |  "
                f"Isolamento Sanitário: {metrics.sanitary_isolation_m:.0f} m"
            )

            if metrics.warnings:
                text += f"\n⚠️ Observação: {metrics.warnings[0]}"

            self.label_summary_text.setText(text)
        except Exception:
            self.label_summary_text.setText("Parâmetros em edição...")

    def _capture_map_center(self):
        """Obtain coordinate center from active QGIS map canvas."""
        if not self.iface:
            return
        canvas = self.iface.mapCanvas()
        if canvas:
            center = canvas.center()
            self.spinBox_x.setValue(center.x())
            self.spinBox_y.setValue(center.y())

    def get_specification(self) -> FacilitySpecification:
        """Construct validated FacilitySpecification domain object from user inputs."""
        facility_type = self.comboBox_type.currentData() or FacilityType.FINISHING
        shape_type = self.comboBox_shape.currentData() or ShapeType.RECTANGULAR

        return FacilitySpecification(
            facility_type=facility_type,
            shape_type=shape_type,
            length=self.spinBox_length.value(),
            width=self.spinBox_width.value(),
            radius=self.spinBox_radius.value(),
            count=self.spinBox_number.value(),
            spacing=self.spinBox_spacing.value(),
            center_x=self.spinBox_x.value(),
            center_y=self.spinBox_y.value(),
            rotation_deg=0.0,
        )

    def accept(self):
        """Validate input before accepting dialog."""
        try:
            spec = self.get_specification()
            # Perform validation
            SwineFacilityPlannerService.calculate_metrics(spec)
            super(SwineSpatialPlannerDialog, self).accept()
        except ValidationError as err:
            QtWidgets.QMessageBox.warning(
                self,
                "Validação de Parâmetros",
                f"Por favor, verifique os parâmetros inseridos:\n\n{str(err)}"
            )
        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self,
                "Erro Inesperado",
                f"Ocorreu um erro ao validar os dados:\n{str(err)}"
            )
