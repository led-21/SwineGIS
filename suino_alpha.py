# -*- coding: utf-8 -*-
"""Main plugin implementation for SwineSpatialPlanner (formerly SuinoAlpha)."""

import os.path
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

try:
    from qgis.core import Qgis
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False

# Initialize Qt resources
from .resources import *
# Import UI Dialog
from .ui.dialog import SwineSpatialPlannerDialog
# Import Core Planning Services & GIS Layer Generator
from .core.services.planner import SwineFacilityPlannerService
from .gis.layer_generator import SwineLayerGenerator
from .gis.crs_handler import CRSHandler


class SuinoAlpha:
    """QGIS Plugin Implementation for swine production spatial layout planning."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Locale & translation setup
        locale = QSettings().value('locale/userLocale', 'en')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            f'SuinoAlpha_{locale}.qm'
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr('&SwineSpatialPlanner')
        self.first_start = True
        self.dlg = None

    def tr(self, message):
        """Translate string using Qt translation API."""
        return QCoreApplication.translate('SuinoAlpha', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        """Add a toolbar icon and menu item for an action."""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar and self.iface:
            self.iface.addToolBarIcon(action)
        if add_to_menu and self.iface:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Create menu entries and toolbar icons in QGIS."""
        icon_path = ':/plugins/suino_alpha/icon.png'
        self.add_action(
            icon_path,
            text=self.tr('Planejar Instalações Suinícolas'),
            callback=self.run,
            parent=self.iface.mainWindow() if self.iface else None,
            status_tip=self.tr('Planejar layout espacial e buffers de biosseguridade para suinocultura')
        )
        self.first_start = True

    def unload(self):
        """Remove plugin menu items and toolbar icons from QGIS."""
        if not self.iface:
            return
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run workflow: display parameterization dialog, execute spatial calculations, and generate layers."""
        if self.first_start or self.dlg is None:
            self.first_start = False
            parent_widget = self.iface.mainWindow() if self.iface else None
            self.dlg = SwineSpatialPlannerDialog(parent=parent_widget, iface=self.iface)

        # Show dialog
        result = self.dlg.exec_() if hasattr(self.dlg, 'exec_') else self.dlg.exec()

        if result:
            try:
                # 1. Retrieve user specification
                spec = self.dlg.get_specification()

                # 2. Get current project CRS
                crs_authid = CRSHandler.get_project_crs_authid(default="EPSG:31982")

                # 3. Generate layout through domain service
                plan_result = SwineFacilityPlannerService.plan_layout(spec, crs_auth_id=crs_authid)

                # 4. Generate QGIS vector layers with biosecurity buffers
                fac_layer, buf_layer = SwineLayerGenerator.create_qgis_layers(
                    plan_result,
                    crs_authid=crs_authid,
                    add_to_project=True
                )

                # 5. Provide clean user feedback via QgsMessageBar
                if self.iface:
                    msg = (
                        f"{spec.count} unidade(s) de {spec.facility_type.value} criadas com sucesso. "
                        f"Área total: {plan_result.metrics.total_footprint_m2:.1f} m²"
                    )
                    if plan_result.metrics.estimated_capacity_heads:
                        msg += f" (Capacidade: {plan_result.metrics.estimated_capacity_heads:,} animais)."
                    self.iface.messageBar().pushMessage(
                        "SwineSpatialPlanner",
                        msg,
                        level=Qgis.Success if HAS_QGIS else 0,
                        duration=6
                    )

                    # If warnings were identified during validation, alert user
                    for warning in plan_result.metrics.warnings:
                        self.iface.messageBar().pushMessage(
                            "Aviso Agronômico / Biosseguridade",
                            warning,
                            level=Qgis.Warning if HAS_QGIS else 1,
                            duration=8
                        )

            except Exception as err:
                if self.iface and HAS_QGIS:
                    self.iface.messageBar().pushMessage(
                        "SwineSpatialPlanner - Erro",
                        f"Falha ao gerar camadas espaciais: {str(err)}",
                        level=Qgis.Critical,
                        duration=10
                    )
                else:
                    raise
