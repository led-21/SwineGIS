# -*- coding: utf-8 -*-
"""Validation rules for swine facility planning inputs."""

from typing import List
from .models import FacilitySpecification, ShapeType
from .standards import SWINE_STANDARDS


class ValidationError(ValueError):
    """Raised when facility parameters violate physical or functional constraints."""
    pass


def validate_specification(spec: FacilitySpecification) -> List[str]:
    """Validate specification and return a list of agronomic/engineering warnings.

    :raises ValidationError: If parameters are physically impossible or out of bounds.
    :returns: List of non-fatal warnings (advisory notes).
    """
    warnings: List[str] = []

    # Count validation
    if spec.count < 1:
        raise ValidationError("A quantidade de unidades deve ser no mínimo 1.")
    if spec.count > 50:
        raise ValidationError("O número máximo suportado por operação em série é 50 unidades.")

    # Spacing validation
    if spec.spacing < 0:
        raise ValidationError("O espaçamento entre galpões não pode ser negativo.")

    # Geometry validation based on shape
    if spec.shape_type == ShapeType.RECTANGULAR:
        if spec.length <= 0:
            raise ValidationError("O comprimento do galpão deve ser maior que zero.")
        if spec.width <= 0:
            raise ValidationError("A largura do galpão deve ser maior que zero.")
        if spec.length < spec.width:
            warnings.append(
                f"O comprimento ({spec.length}m) é menor que a largura ({spec.width}m). "
                "Em galpões rurais, a dimensão maior geralmente define a extensão longitudinal."
            )
        # Check standard width thresholds
        std = SWINE_STANDARDS.get(spec.facility_type)
        if std and "max_recommended_width_m" in std:
            max_w = std["max_recommended_width_m"]
            if spec.width > max_w:
                warnings.append(
                    f"Largura ({spec.width}m) superior à recomendada ({max_w}m) para "
                    f"{spec.facility_type.value}. Pode demandar ventilação túnel forçada e climatização."
                )

    elif spec.shape_type == ShapeType.CIRCULAR:
        if spec.radius <= 0:
            raise ValidationError("O raio da estrutura circular deve ser maior que zero.")
        if spec.radius > 250:
            warnings.append(
                f"Raio de {spec.radius}m é excepcionalmente grande para uma única estrutura zootécnica."
            )

    # Spacing check for biosecurity and air flow
    std = SWINE_STANDARDS.get(spec.facility_type)
    if std and spec.count > 1:
        min_sp = std.get("min_spacing_between_sheds", 10.0)
        if spec.spacing < min_sp:
            warnings.append(
                f"Espaçamento de {spec.spacing}m é inferior ao mínimo recomendado ({min_sp}m) "
                f"para ventilação e isolamento sanitário entre galpões de {spec.facility_type.value}."
            )

    return warnings
