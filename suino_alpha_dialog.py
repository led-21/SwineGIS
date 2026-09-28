# -*- coding: utf-8 -*-
"""Backward compatibility wrapper for SuinoAlphaDialog."""

from .ui.dialog import SwineSpatialPlannerDialog

# Alias for legacy compatibility
SuinoAlphaDialog = SwineSpatialPlannerDialog

__all__ = ["SuinoAlphaDialog", "SwineSpatialPlannerDialog"]
