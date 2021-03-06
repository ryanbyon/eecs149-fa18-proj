#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Dynamics abstraction construction using symbolic variable representation

Author: Ahad Rauf
"""

import numpy as np
import sympy
import itertools
from typing import List, Union, Dict


class Dynamics:
    def __init__(self, constants: Dict[sympy.Symbol, float], variables: List[sympy.Symbol], dynamics):
        print("Creating dynamics model")
        self._constants = constants
        self._variables = variables
        self._dynamics = dynamics

    def calculateErrorMargins(self, predictedInputs: Dict[sympy.Symbol, float], errors: Dict[sympy.Symbol, float],
                              display: bool = True, log=print):
        log("Calculating error margins")
        assert all(symbol in self._constants or symbol in self._variables for symbol in predictedInputs)
        assert all(symbol in self._constants or symbol in self._variables for symbol in errors)

        # Make sure all predictedInputs have an associated error (even if it's zero)
        for predictedInput in predictedInputs:
            if predictedInput not in errors:
                errors[predictedInput] = 0

        allVariables = {**self._constants, **predictedInputs}
        if display:
            log("All variables:", allVariables)
        # predictedOutput = self._dynamics.subs(allVariables)
        # print('Normal predicted output: ', predictedOutput)

        log("Evaluating errors:")
        outputsForDifferentErrors = []
        relevantErrorVariables = {symb: error for symb, error in errors.items() if symb in predictedInputs}
        importantErrorVariables = {symb: error for symb, error in relevantErrorVariables.items() if error != 0}
        for modifiedErrorVariablesNum in range(len(importantErrorVariables) + 1):
            possibleModifiedErrorVariables = itertools.combinations(importantErrorVariables, modifiedErrorVariablesNum)
            for modifiedErrorVariables in possibleModifiedErrorVariables:
                # Calculate the error if modifiedErrorVariables had negative values instead
                newErrors = {symb: -error for symb, error in importantErrorVariables.items() if
                             symb in modifiedErrorVariables}
                allErrors = {**relevantErrorVariables, **newErrors}
                newValues = {}
                for symb in predictedInputs:
                    newValues[symb] = predictedInputs[symb] + allErrors[symb]
                calculatedValue = [float(x) for x in self._dynamics.subs(newValues).n()]

                if display:
                    log('Value with negative errors at', modifiedErrorVariables, ':', calculatedValue)
                outputsForDifferentErrors.append(calculatedValue)

                # Calculate the error if modifiedErrorVariables had zero error instead
                newErrors = {symb: 0 for symb, error in importantErrorVariables.items() if
                             symb in modifiedErrorVariables}
                allErrors = {**relevantErrorVariables, **newErrors}
                newValues = {}
                for symb in predictedInputs:
                    newValues[symb] = predictedInputs[symb] + allErrors[symb]
                calculatedValue = [float(x) for x in self._dynamics.subs(newValues).n()]

                if display:
                    log('Value with zero errors at', modifiedErrorVariables, ':', calculatedValue)
                outputsForDifferentErrors.append(calculatedValue)

        boundingBox = [(min(lst), max(lst)) for lst in list(zip(*outputsForDifferentErrors))]
        if display:
            log('Bounding box:', boundingBox)
            log('Returning bounding box')
        return boundingBox

    def calculateSequenceOfErrorMargins(self, predictedInputs: List[Dict[sympy.Symbol, float]],
                                        errors: List[Dict[sympy.Symbol, float]],
                                        outputSymbolMapping: List[sympy.Symbol], display: bool = True, log=print):
        """
        A generator function that calculates a sequence of bounding boxes as you continue to propagate the error forward

        :param predictedInputs:
        :param errors:
        :param outputSymbolMapping:
        :param display:
        :param log:
        :return:
        """
        updatedPredictedInput = {}
        updatedError = {}
        # outputBoundingBoxes = []
        for initialPredictedInput, initialError in zip(predictedInputs, errors):
            predictedInput = {**initialPredictedInput, **updatedPredictedInput}
            error = {**initialError, **updatedError}
            log(predictedInput)
            log(error)
            outputBoundingBox = self.calculateErrorMargins(predictedInput, error, display)
            # outputBoundingBoxes.append(outputBoundingBox)

            for symb, bounds in zip(outputSymbolMapping, outputBoundingBox):
                updatedPredictedInput[symb] = (bounds[0] + bounds[1]) / 2  # Average
                updatedError[symb] = (bounds[1] - bounds[0]) / 2  # Range / 2

            yield outputBoundingBox

        # return outputBoundingBoxes

    @property
    def variables(self):
        return self._variables


class RotatingDubinsModel(Dynamics):
    def __init__(self):
        print('Creating dubins model')
        constants = {}

        x, y, theta, v, omega, dt = sympy.symbols('x y theta v omega dt')
        variables = [x, y, theta, v, omega, dt]

        def dynamics(x: sympy.Symbol, y: sympy.Symbol, theta: sympy.Symbol, v: sympy.Symbol, omega: sympy.Symbol,
                     dt: sympy.Symbol):
            # linear_translation = v * sympy.sin(omega * dt) / omega + sympy.cos(omega * dt)
            # perp_translation = v * (1 - sympy.cos(omega * dt)) / omega + sympy.sin(
            #     omega * dt)  # perpendicular (to the left of main linear path)
            linear_translation = v * sympy.sin(omega * dt) / omega
            perp_translation = v * (1 - sympy.cos(omega * dt)) / omega
            return sympy.Matrix(
                [(x + linear_translation * sympy.cos(theta) - perp_translation * sympy.sin(theta),
                  y + linear_translation * sympy.sin(theta) + perp_translation * sympy.cos(theta),
                  theta + omega * dt)])
            # return x + v * sympy.cos(theta) * dt, y + v * sympy.sin(theta) * dt, theta + omega * dt

        dynamics_equation = dynamics(x, y, theta, v, omega, dt)

        super().__init__(constants, variables, dynamics_equation)


if __name__ == '__main__':
    db = RotatingDubinsModel()
    x, y, theta, v, omega, dt = db.variables
    predictedInputs = {x: 0, y: 0, theta: 0, v: 28.83451398, omega: 0.1500567293, dt: 1.6}
    errors = {x: 0, y: 0, theta: 0, v: 2 * 1.334704641, omega: 2 * 0.02230989018, dt: 0}

    import time

    startTime = time.time()
    db.calculateErrorMargins(predictedInputs, errors, False)
    endTime = time.time()
    print('Error margin execution time:', endTime - startTime)

    print("Testing multiple movements")
    allPredictedInputs = [predictedInputs, predictedInputs]
    allErrors = [errors, errors]
    symbolMapping = [x, y, theta]
    for boundingBox in db.calculateSequenceOfErrorMargins(allPredictedInputs, allErrors, symbolMapping, True):
        print(boundingBox)
