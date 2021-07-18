from __future__ import annotations
import numpy as np
from typing import Tuple, Type


class Grade:

    def __init__(self, weights: Tuple[float], names: Tuple[str]) -> None:
        assert(len(weights) == len(names))
        self.weights = np.array(weights)
        self.names = np.array(names)

    def __call__(self, values: Tuple[float]) -> float:
        assert(len(self.weights) == len(values))
        return sum(self.weights * np.array(values))

    def __repr__(self) -> str:
        return 'Grade(' + 'weights: ' + str(self.weights) + ', names: ' + str(self.names) + ')'

    @staticmethod
    def from_string(formula: str) -> Grade:
        # splitting into terms by '+'
        terms = tuple(
            map(str.strip,
                formula.split('+')
                )
        )
        # splitting each terms into weight and mark by '*'
        weights_names = tuple(
            map(lambda s: s.split('*'),
                terms)
        )
        # tranforming data into two tuples : weights of marks and names of marks
        weights, names = tuple(
            zip(*weights_names)
        )
        # unifying numbers format
        weights = tuple(
            map(
                float,
                map(
                    lambda s: s.replace(',', '.'),
                    map(str.strip,
                        weights
                        )
                )
            )
        )
        # stripping marks' names
        names = tuple(
            map(
                str.strip,
                names
            )
        )
        return Grade(weights, names)
