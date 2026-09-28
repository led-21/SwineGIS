# -*- coding: utf-8 -*-
"""Integration test for the SwineSpatialPlannerDialog UI."""

import unittest

try:
    from qgis.PyQt.QtWidgets import QApplication, QDialogButtonBox, QDialog
    from ui.dialog import SwineSpatialPlannerDialog
    from core.domain.models import FacilityType, ShapeType
    # Initialize minimal Qt application if running inside GUI/QGIS environment
    app = QApplication.instance() or QApplication([])
    HAS_QT = True
except ImportError:
    HAS_QT = False


class TestSwineSpatialPlannerDialog(unittest.TestCase):
    """Verify dialog initialization, field toggling, and button boxes."""

    def setUp(self):
        if not HAS_QT:
            self.skipTest("PyQt5 / QGIS UI environment not available")
        self.dialog = SwineSpatialPlannerDialog(None)

    def tearDown(self):
        if hasattr(self, 'dialog'):
            self.dialog = None

    def test_dialog_initial_state(self):
        """Verify default populated fields and reactive preview."""
        self.assertIsNotNone(self.dialog)
        self.assertTrue(self.dialog.comboBox_type.count() > 0)
        self.assertTrue(self.dialog.comboBox_shape.count() > 0)
        self.assertIn("Área", self.dialog.label_summary_text.text())

    def test_shape_toggling(self):
        """Verify toggling shape disables/enables corresponding dimension fields."""
        # Find Circular
        for idx in range(self.dialog.comboBox_shape.count()):
            if self.dialog.comboBox_shape.itemData(idx) == ShapeType.CIRCULAR:
                self.dialog.comboBox_shape.setCurrentIndex(idx)
                break

        self.assertFalse(self.dialog.spinBox_length.isEnabled())
        self.assertFalse(self.dialog.spinBox_width.isEnabled())
        self.assertTrue(self.dialog.spinBox_radius.isEnabled())

    def test_dialog_accept_and_reject(self):
        """Verify OK and Cancel button box behavior."""
        btn_ok = self.dialog.button_box.button(QDialogButtonBox.Ok)
        btn_cancel = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        self.assertIsNotNone(btn_ok)
        self.assertIsNotNone(btn_cancel)


if __name__ == '__main__':
    unittest.main()
