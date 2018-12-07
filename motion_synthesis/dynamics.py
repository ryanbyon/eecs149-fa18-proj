import numpy as np
import sympy
from typing import List, Union

class Dynamics:
    def __init__(self, variables: List[str], dynamics_models: list):
        self._variables = variables
        self._dynamics_models = dynamics_models

        self._symbols = [sympy.symbols(var) for var in variables]
        self._symbolic_dynamics_models = [dynamics_model(*self._symbols) for dynamics_model in dynamics_models]
        self._lambda_dynamics_models = [sympy.lambdify(tuple(self._symbols), symbolic_model, "numpy") for
                                        symbolic_model in self._symbolic_dynamics_models]

    def calculateErrorMargin(self, predictedValues: List[float], errors: List[float]):
        outputs = []
        for symbolic_model, lambda_model in zip(self._symbolic_dynamics_models, self._lambda_dynamics_models):
            outputBoundMax = lambda_model(*predictedValues)
            outputBoundMin = outputBoundMax
            for symbol, symbol_error in zip(self._symbols, errors):
                dF_dx =  sympy.lambdify(tuple(self._symbols), symbolic_model.diff(symbol), "numpy")
                outputBoundMax += dF_dx(*predictedValues)*symbol_error
                outputBoundMin -= dF_dx(*predictedValues)*symbol_error
            outputs.append((outputBoundMin, outputBoundMax))
        return outputs

if __name__ == '__main__':
    
