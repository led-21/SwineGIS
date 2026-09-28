# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'adriano.godoy@gmail.com'
__date__ = '2025-10-18'
__copyright__ = 'Copyright 2025, Adriano Lopes Godoy'

import unittest

try:
    from qgis.PyQt.QtGui import QIcon
    import resources  # pylint: disable=unused-import
    HAS_QT = True
except ImportError:
    HAS_QT = False


class SuinoAlphaResourcesTest(unittest.TestCase):
    """Test compiled Qt resources work properly."""

    def test_icon_png(self):
        """Test plugin icon resource is accessible."""
        if not HAS_QT:
            self.skipTest("PyQt/QGIS not available in current environment")

        path = ':/plugins/suino_alpha/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull(), "Icon resource should not be null")


if __name__ == "__main__":
    unittest.main()
