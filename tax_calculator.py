from __future__ import annotations


class TaxCalculator:
    """Calcula impuestos sobre montos de transacción.

    Soporta tasas personalizadas registradas por nombre.
    """

    RATES = {
        "IGV": 0.18,
        "IVA": 0.12,
        "EXONERADO": 0.0,
    }

    def calculate_tax(self, amount: float, rate: float) -> float:
        self._validate(amount, rate)
        return round(amount * rate, 2)

    def calculate_tax_by_name(self, amount: float, tax_name: str) -> float:
        key = tax_name.strip().upper()
        if key not in self.RATES:
            raise KeyError(f"Tasa '{tax_name}' no registrada.")
        return self.calculate_tax(amount, self.RATES[key])

    def total_with_tax(self, amount: float, rate: float) -> float:
        return round(amount + self.calculate_tax(amount, rate), 2)

    @staticmethod
    def _validate(amount: float, rate: float) -> None:
        if amount < 0:
            raise ValueError("El monto no puede ser negativo.")
        if not (0.0 <= rate <= 1.0):
            raise ValueError("La tasa debe estar entre 0 y 1.")
