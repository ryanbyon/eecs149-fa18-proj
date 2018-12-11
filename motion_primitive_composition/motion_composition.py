#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Motion composition main file

Author: Ahad Rauf
"""

import os, sys
import numpy as np
import threading
from math import pi

from PyQt5 import QtWidgets

motion_primitive_composition_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(motion_primitive_composition_path)
from motion_primitive_composition.differential_dynamics import RotatingDubinsModel
from motion_primitive_composition.error_visualization import ErrorVisualizationWindow

from typing import List, Dict, Union


def boundingBoxIntersection(boundingBox, window: ErrorVisualizationWindow, wall_booleans: List[List[bool]]) -> bool:
    """
    Returns whether the bounding box intersects any of the walls

    :param boundingBox: The bounding box
    :param window: The display window (used to get system parameters)
    :param wall_booleans: A 2D array of booleans saying whether wall_booleans[i][j] contains a wall or not
    :return: True if the bounding box intersects a wall, False otherwise
    """
    xmin_cm, xmax_cm = boundingBox[0]
    ymin_cm, ymax_cm = boundingBox[1]
    xmin_px, ymin_px = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels((xmin_cm, ymin_cm))
    xmax_px, ymax_px = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels((xmax_cm, ymax_cm))
    ymin_px, ymax_px = minimax(ymin_px, ymax_px)
    R, C = len(wall_booleans), len(wall_booleans[0])
    for i in range(int(xmin_px * C // window.windowSize[0]), int(xmax_px * C // window.windowSize[0] + 1)):
        for j in range(int(ymin_px * R // window.windowSize[1]), int(ymax_px * R // window.windowSize[1] + 1)):
            if i < 0 or i >= len(wall_booleans) or j < 0 or j >= len(wall_booleans[0]):
        		    return True
            if wall_booleans[i][j]:
                return True
    return False


def addDubinsBoundingBox(name: str, window: ErrorVisualizationWindow, dubinsBoundingBox, color: str = 'red') -> None:
    """
    Adds a bounding box to the visualization.

    :param name: The name of the bounding box, for record-keeping
    :param window: The display window
    :param dubinsBoundingBox: The
    :param color: A PyQt5 color (see options in "Predefined Colors" here:
                  http://pyqt.sourceforge.net/Docs/PyQt4/qcolor.html)
    :return: None
    """
    x_min, y_min = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(
        (dubinsBoundingBox[0][0], dubinsBoundingBox[1][0]))
    x_max, y_max = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(
        (dubinsBoundingBox[0][1], dubinsBoundingBox[1][1]))
    #window.addForegroundBox(name, x_min, y_min, x_max - x_min, y_max - y_min, color=color)


def minimax(a, b):
    return (a, b) if a < b else (b, a)


def execute_motion_composition(startPosition, wall_booleans, actionSequence) -> list:
    """
    Old inputs: carStartPositionFile: str, wallBooleansFile: str, strategyFile: str
    Note: All file paths should be given relative to the eecs149-fa18-proj folder.
          For example, 'maze_images/wall_booleans.npy' is accepted.
    :param carStartPositionFile: The file containing the car's start position. 
    :param wallBooleansFile: The file containing the maze's wall positions (stored as bool values)
    :param strategyFile: The file containing the strategy to be executed
    
    :return: The inputs needed be sent to the car as an Nx2 array
             (every row = [angle to send in radians, distance to move in cm])
    """
    app = QtWidgets.QApplication(sys.argv)

    # Initialize window
    # TOTAL_WIDTH_INCHES = 42 + 15 / 16
    TOTAL_WIDTH_INCHES = 28 + 13 / 16
    TOTAL_HEIGHT_INCHES = 28 + 13 / 16
    INCH_TO_CM = 2.54
    physicalSpace = (TOTAL_WIDTH_INCHES * INCH_TO_CM, TOTAL_HEIGHT_INCHES * INCH_TO_CM)
    windowSizeX = 800
    windowSizeY = windowSizeX * TOTAL_HEIGHT_INCHES // TOTAL_WIDTH_INCHES
    window = ErrorVisualizationWindow(physicalSpace=physicalSpace, windowSizeWithoutLog=(windowSizeX, windowSizeY))

    # Define walls
    # wall_booleans = np.load(motion_primitive_composition_path + '/' + wallBooleansFile)
    GRID_SIZE_Y_INCHES = TOTAL_HEIGHT_INCHES / len(wall_booleans)
    GRID_SIZE_X_INCHES = TOTAL_WIDTH_INCHES / len(wall_booleans[0])
    gridSizeX = window.mapPhysicalDimensionsToPixels(GRID_SIZE_X_INCHES * INCH_TO_CM, axis=0)
    gridSizeY = window.mapPhysicalDimensionsToPixels(GRID_SIZE_Y_INCHES * INCH_TO_CM, axis=1)
    for i in range(len(wall_booleans)):
        for j in range(len(wall_booleans[0])):
            if wall_booleans[i][j]:
                pass
                #window.addBackgroundBox('wall_' + str(i) + ',' + str(j), j * gridSizeX, i * gridSizeY, gridSizeX,
                #                        gridSizeY)

    # Adding in the car
    CAR_RADIUS = 1 / INCH_TO_CM  # Adjust
    carRadius = window.mapPhysicalDimensionsToPixels(CAR_RADIUS, axis=0)

    # startPosition = np.load(motion_primitive_composition_path + '/' + carStartPositionFile)
    startPosition[1] = TOTAL_HEIGHT_INCHES * INCH_TO_CM - startPosition[1]
    
    carCoordinates = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(
        startPosition[0:2])  # Start position given in image coordinates
    #window.log('Car coordinates:', carCoordinates)
    #window.addForegroundCircle('car', *carCoordinates, carRadius)

    def removeAllBoundingBoxes(delay_ms=1000):
        pass
        #window.delayGUI(delay_ms)
        #window.removeAllForegroundPaintObjects()
        #window.addForegroundCircle('car', *carCoordinates, carRadius)

    db = RotatingDubinsModel()
    x, y, theta, v, omega, dt = db.variables
    inputsMoveForward = {x: startPosition[0], y: startPosition[1], theta: startPosition[2], v: 28.83451398,
                         omega: 0.1500567293, dt: 0.3}
    errorsMoveForward = {x: 0, y: 0, theta: 0, v: 3 * 1.334704641, omega: 3 * 0.02230989018, dt: 0}
    inputsRotate = {x: startPosition[0], y: startPosition[1], theta: startPosition[2], v: 0.7851747434,
                    omega: 7.48657308, dt: 0.3}
    errorsRotate = {x: 0, y: 0, theta: 0, v: 3 * 0.4296893495, omega: 3 * 1.07694169, dt: 0}
    symbolMapping = [x, y, theta]

    # actionSequence = np.load(motion_primitive_composition_path + '/' + strategyFile)
    allTimes = []
    numActions = 0

    def reinitializeInputs():
        inputsMoveForward[x] = inputsRotate[x] = startPosition[0]
        inputsMoveForward[y] = inputsRotate[y] = startPosition[1]
        inputsMoveForward[theta] = inputsRotate[theta] = startPosition[2]

        nonlocal numActions
        numActions = 0

    def updateActionSequence(name, *actions, color: Union[str, None] = 'red'):
        print('Action Sequence:', actions)
        allPredictedInputs = []
        allErrors = []
        for action in actions:
            if action[0] == 0:  # Move forward
                inputs = inputsMoveForward.copy()
                inputs[dt] = action[1] / inputs[v]
                allTimes.append(action[1] / inputs[v])
                allPredictedInputs.append(inputs)
                allErrors.append(errorsMoveForward.copy())
            elif action[1] == 0:  # Rotate
                inputs = inputsRotate.copy()
                inputs[dt] = action[0] / inputs[omega]
                allTimes.append(action[0] / inputs[omega])
                allPredictedInputs.append(inputs)
                allErrors.append(errorsRotate.copy())
        boundingBoxGenerator = db.calculateSequenceOfErrorMargins(allPredictedInputs, allErrors, symbolMapping, False,
                                                                  window.log)

        boundingBoxes = []
        colors = ['red', 'green', 'blue',
                  'darkRed', 'darkGreen', 'darkBlue',
                  'cyan', 'magenta', 'yellow',
                  'darkCyan', 'darkMagnenta', 'darkYellow']
        for i, boundingBox in enumerate(boundingBoxGenerator):
            if color in colors:
                addDubinsBoundingBox(name + '_' + str(i), window, boundingBox, color=color)
            else:
                addDubinsBoundingBox(name + '_' + str(i), window, boundingBox, color=colors[i % len(colors)])
            #window.delayGUI(100)
            boundingBoxes.append(boundingBox)

        lastBoundingBox = boundingBoxes[-1]
        newX = (lastBoundingBox[0][0] + lastBoundingBox[0][1]) / 2
        newY = (lastBoundingBox[1][0] + lastBoundingBox[1][1]) / 2
        newTheta = (lastBoundingBox[2][0] + lastBoundingBox[2][1]) / 2
        print('Updating inputs for moving forward:', inputsMoveForward, newX, newY, newTheta)
        inputsMoveForward[x] = newX
        inputsMoveForward[y] = newY
        inputsMoveForward[theta] = newTheta
        inputsRotate[x] = newX
        inputsRotate[y] = newY
        inputsRotate[theta] = newTheta

        nonlocal numActions
        numActions += 1
        return boundingBoxes

    MAX_DEPTH = 3
    def pathPlanning(actionSequence, depth=0) -> list:
        print('Path planning for action sequence:', actionSequence, 'at depth', depth)
        #if depth > MAX_DEPTH:
        #    raise ValueError('This algorithm cannot converge within', MAX_DEPTH,
        #                     'iterations. Does the car intersect the wall?')
        removeAllBoundingBoxes(delay_ms=1000)
        boundingBoxes = updateActionSequence('first_trial', *actionSequence, color=None)
        for i, boundingBox in enumerate(boundingBoxes):
            intersectsWall = boundingBoxIntersection(boundingBox, window, wall_booleans)
            print('Movement', i, 'intersects the wall:', intersectsWall)
            """
            if intersectsWall and i > 0:
                return actionSequence[:i]  # You can do all moves up until move i without crashing
            elif intersectsWall and i == 0 and depth <= MAX_DEPTH:
                reinitializeInputs()
                return pathPlanning(actionSequence[:1] / 2, depth=depth + 1)
            """
            if intersectsWall and i > 0 and depth > MAX_DEPTH:
                return actionSequence[:i]  # You can do all moves up until move i without crashing
            elif intersectsWall and i > 0 and depth <= MAX_DEPTH:
                reinitializeInputs()
                return pathPlanning(list(actionSequence[:i]) + list([actionSequence[i]/2]), depth=depth+1)
            elif intersectsWall and i == 0 and depth > MAX_DEPTH:
                raise ValueError('This algorithm cannot converge within', MAX_DEPTH, 'iterations. Does the car intersect the wall?')
            elif intersectsWall and i == 0 and depth <= MAX_DEPTH:
                reinitializeInputs()
                return pathPlanning(actionSequence[:1] / 2, depth=depth + 1)
            #"""
        return actionSequence  # If none of the bounding boxes intersects the wall, you're set to go!

    plannedActionSequence = actionSequence[:6]
    print(plannedActionSequence)
    proposedActionSequence = pathPlanning(plannedActionSequence)
    print(proposedActionSequence)

    # Display final movement
    reinitializeInputs()
    removeAllBoundingBoxes(delay_ms=1000)
    boundingBoxes = updateActionSequence('final_execution', *proposedActionSequence, color='blue')
    print('Bounding boxes of final movement:', boundingBoxes)

    # Characterize movement runtime
    print("Theoretical runtime:", sum(allTimes))
    START_TIME = 30
    TIME_PER_COMPUTATION_STEP = 10
    print('Theoretical runtime, adding in heuristics for computation time:',
          sum(allTimes) + START_TIME + TIME_PER_COMPUTATION_STEP * (numActions - 1))

    #window.delayGUI(delay_ms=4000)
    app.closeAllWindows()
    return proposedActionSequence

    # sys.exit(app.exec_())


if __name__ == '__main__':
    # TOTAL_WIDTH_INCHES = 42 + 15 / 16
    # TOTAL_HEIGHT_INCHES = 28 + 13 / 16
    # INCH_TO_CM = 2.54
    # physicalSpace = (TOTAL_WIDTH_INCHES * INCH_TO_CM, TOTAL_HEIGHT_INCHES * INCH_TO_CM)
    # windowSizeX = 800
    # windowSizeY = windowSizeX * TOTAL_HEIGHT_INCHES // TOTAL_WIDTH_INCHES
    # # Defining dimensions
    # WALL_WIDTH_INCHES = 7 / 16
    # NUM_PASSAGES_X, NUM_PASSAGES_Y = (6, 4)
    # PASSAGE_SPACING_X_INCHES = (TOTAL_WIDTH_INCHES - (NUM_PASSAGES_X + 1) * WALL_WIDTH_INCHES) / NUM_PASSAGES_X
    # PASSAGE_SPACING_Y_INCHES = (TOTAL_HEIGHT_INCHES - (NUM_PASSAGES_Y + 1) * WALL_WIDTH_INCHES) / NUM_PASSAGES_Y
    #
    # startPosition = ((WALL_WIDTH_INCHES + PASSAGE_SPACING_X_INCHES / 2) * INCH_TO_CM,
    #                  (0.5 * PASSAGE_SPACING_Y_INCHES + WALL_WIDTH_INCHES) * INCH_TO_CM,
    #                  pi / 2)
    #
    # np.save('../maze_images/car_start_position', startPosition)
    # wallSizeX = window.mapPhysicalDimensionsToPixels(WALL_WIDTH_INCHES * INCH_TO_CM, axis=0)
    # wallSizeY = window.mapPhysicalDimensionsToPixels(WALL_WIDTH_INCHES * INCH_TO_CM, axis=1)
    # passageSizeX = window.mapPhysicalDimensionsToPixels(PASSAGE_SPACING_X_INCHES * INCH_TO_CM, axis=0)
    # passageSizeY = window.mapPhysicalDimensionsToPixels(PASSAGE_SPACING_Y_INCHES * INCH_TO_CM, axis=1)

    actionSequence = execute_motion_composition(carStartPositionFile='maze_images/car_start_position.npy',
                                                wallBooleansFile='maze_images/wall_booleans.npy',
                                                strategyFile='maze_images/path_array.npy')
    print(actionSequence)
    sys.exit(0)
