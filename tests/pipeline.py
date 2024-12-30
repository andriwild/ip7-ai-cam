from typing import Generic, TypeVar, List

I = TypeVar("I")  # Input Typ der gesamten Pipeline
O = TypeVar("O")  # Output Typ der aktuellen Pipeline-Stufe
N = TypeVar("N")  # Neuer Output Typ nach Hinzufügen eines neuen Steps

class Step(Generic[I, O]):
    def process(self, data: I) -> O:
        raise NotImplementedError

class StepOne(Step[int, str]):
    def process(self, data: int) -> str:
        return str(data)

class StepTwo(Step[str, float]):
    def process(self, data: str) -> float:
        return float(data)

class StepThree(Step[float, bool]):
    def process(self, data: float) -> bool:
        return data > 0

class Pipeline(Generic[I, O]):
    def __init__(self, steps: List[Step[object, object]] | None = None):
        self.steps: List[Step[object, object]] = steps or []

    def add(self, step: Step[O, N]) -> "Pipeline[I, N]":
        # Hier wird der Outputtyp O des bisherigen Pipelineschritts
        # mit dem Inputtyp des neuen Steps abgeglichen.
        new_steps = self.steps.copy()
        new_steps.append(step)
        # Erzeugt eine neue Pipeline mit neuem Output-Typ N
        return Pipeline[I, N](new_steps)

    def run(self, data: I) -> O:
        current = data
        for s in self.steps:
            current = s.process(current)  # type: ignore
        return current  # type: ignore


# Beispiel: Eine Pipeline erstellen, die int -> str -> float -> bool wandelt
pipeline = Pipeline[int, int]() \
    .add(StepOne()) \
    .add(StepTwo()) \
    .add(StepThree())

# pipeline ist jetzt vom Typ Pipeline[int, bool]
result = pipeline.run(42)  # result wird ein bool sein (True oder False)
print(result)
