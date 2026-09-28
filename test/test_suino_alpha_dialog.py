# coding=utf-8
"""Dialog test."""

import unittest

__author__ = 'adriano.godoy@gmail.com'
__date__ = '2025-10-18'
__copyright__ = 'Copyright 2025, Adriano Lopes Godoy'

try:
    from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog
    from suino_alpha_dialog import SuinoAlphaDialog
    from .utilities import get_qgis_app
    QGIS_APP, _, _, _ = get_qgis_app()
    HAS_QT = True
except ImportError:
    HAS_QT = False
    QGIS_APP = None


class SuinoAlphaDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        if not HAS_QT or QGIS_APP is None:
            self.skipTest("PyQt/QGIS application not available")
        self.dialog = SuinoAlphaDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""
        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)


if __name__ == "__main__":
    unittest.main()
