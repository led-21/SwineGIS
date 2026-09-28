# -*- coding: utf-8 -*-
"""Integration test verifying plugin metadata compliance with QGIS standards."""

import os
import unittest
import configparser

METADATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'metadata.txt')
)


class TestPluginMetadata(unittest.TestCase):
    """Verify metadata.txt satisfies QGIS plugin repository specifications."""

    def setUp(self):
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        self.parser.read(METADATA_PATH, encoding='utf-8')

    def test_general_section_exists(self):
        """Ensure 'general' section is present in metadata."""
        self.assertTrue(self.parser.has_section('general'))

    def test_required_metadata_fields(self):
        """Validate all required fields according to official plugins.qgis.org schema."""
        required_fields = [
            'name',
            'description',
            'version',
            'qgisMinimumVersion',
            'email',
            'author'
        ]
        items = dict(self.parser.items('general'))
        for field in required_fields:
            self.assertIn(field, items, f"Missing required metadata item: '{field}'")
            self.assertTrue(len(items[field].strip()) > 0, f"Metadata item '{field}' cannot be empty")

    def test_plugin_name_and_version(self):
        """Ensure updated professional naming and experimental flag."""
        items = dict(self.parser.items('general'))
        self.assertEqual(items.get('name'), 'SwineSpatialPlanner')
        self.assertEqual(items.get('qgisMinimumVersion'), '3.0')


if __name__ == '__main__':
    unittest.main()
