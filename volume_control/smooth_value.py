from dataclasses import dataclass

@dataclass
class SmoothValue:
    alpha: float = 0.4
    value: float = None

    def update(self, x: float) -> float:
        if self.value is None:
            self.value = x
        else:
            self.value = self.alpha * x + (1 - self.alpha) * self.value
        return self.value
