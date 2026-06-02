from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

logger = logging.getLogger(__name__)


@dataclass
class RefundResult:
    approved: bool
    refund_amount: float = 0.0
    reason: str = ""


class RefundProcessor:
    """Procesa reembolsos con política configurable.

    Soporta reembolsos totales y parciales.
    """

    def __init__(self, max_days: int = 30):
        if max_days <= 0:
            raise ValueError("max_days debe ser un entero positivo.")
        self.max_days = max_days

    def process(
        self,
        original_amount: float,
        refund_amount: float,
        purchase_date: date,
    ) -> RefundResult:
        self._validate_inputs(original_amount, refund_amount)

        days_elapsed = (date.today() - purchase_date).days
        logger.info(
            "Solicitud de reembolso: S/. %.2f | días: %d",
            refund_amount,
            days_elapsed,
        )

        if days_elapsed > self.max_days:
            return self._reject(
                f"Fuera del plazo permitido ({self.max_days} días)."
            )

        if refund_amount > original_amount:
            return self._reject(
                "El monto de reembolso supera el monto original."
            )

        return RefundResult(approved=True, refund_amount=round(refund_amount, 2))

    def _reject(self, reason: str) -> RefundResult:
        logger.warning("Reembolso rechazado: %s", reason)
        return RefundResult(approved=False, reason=reason)

    @staticmethod
    def _validate_inputs(original: float, refund: float) -> None:
        if original <= 0 or refund <= 0:
            raise ValueError("Los montos deben ser positivos.")
