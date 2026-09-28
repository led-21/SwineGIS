# coding=utf-8
"""Test package initialization with graceful fallback when QGIS is not installed in current Python env."""

try:
    import qgis  # pylint: disable=W0611  # NOQA
except ImportError:
    pass