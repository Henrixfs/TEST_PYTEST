from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class ValidationResult:
    approved: bool
    reason: str = ""


class PaymentValidator:
    """Valida pagos mediante una cadena de reglas configurables.

    Cada regla es una función que recibe (amount, spent_today) y retorna None
    si es válida o un str con el motivo del rechazo.
    """

    def __init__(self, min_amount: float, daily_limit: float):
        if min_amount < 0:
            raise ValueError("El monto mínimo no puede ser negativo.")
        if daily_limit < 0:
            raise ValueError("El límite diario no puede ser negativo.")
        self.rules: List[Callable[[float, float], Optional[str]]] = [
            self._check_minimum(min_amount),
            self._check_daily_limit(daily_limit),
        ]

    def validate(self, amount: float, spent_today: float) -> ValidationResult:
        for rule in self.rules:
            reason = rule(amount, spent_today)
            if reason:
                return ValidationResult(approved=False, reason=reason)
        return ValidationResult(approved=True)

    @staticmethod
    def _check_minimum(min_amount: float) -> Callable[[float, float], Optional[str]]:
        def rule(amount: float, _: float) -> Optional[str]:
            if amount < min_amount:
                return f"El monto es inferior al mínimo ({min_amount})."
            return None

        return rule

    @staticmethod
    def _check_daily_limit(daily_limit: float) -> Callable[[float, float], Optional[str]]:
        def rule(amount: float, spent_today: float) -> Optional[str]:
            if spent_today + amount > daily_limit:
                return "Se supera el límite diario de transacciones."
            return None

        return rule
