#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Motion composition main file

Author: Ahad Rauf
"""

import os, sys
import numpy as np
from math import pi

from PyQt5 import QtWidgets

motion_primitive_composition_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(motion_primitive_composition_path)
from motion_primitive_composition.dynamics import RotatingDubinsModel
from motion_primitive_composition.error_visualization import ErrorVisualizationWindow

from typing import List, Dict


def boundingBoxIntersection(boundingBox, window: ErrorVisualizationWindow, wall_booleans: List[List[bool]]):
    xmin_cm, xmax_cm = boundingBox[0]
    ymin_cm, ymax_cm = boundingBox[1]
    xmin_px, ymin_px = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels((xmin_cm, ymin_cm))
    xmax_px, ymax_px = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels((xmax_cm, ymax_cm))
    ymin_px, ymax_px = minimax(ymin_px, ymax_px)
    R, C = len(wall_booleans), len(wall_booleans[0])
    # print(xmin_px, xmax_px, ymin_px, ymax_px)
    # print(R, C)
    # print(window.windowSize)
    # print(int(xmin_px * C // window.windowSize[0]), int(xmax_px * C // window.windowSize[0] + 1))
    # print(int(ymin_px * R // window.windowSize[1]), int(ymax_px * R // window.windowSize[1] + 1))
    # print(wall_booleans)
    # print(wall_booleans[int(xmin_px * C // window.windowSize[0]):int(xmax_px * C // window.windowSize[0] + 1)][
    #       int(ymin_px * R // window.windowSize[1]):int(ymax_px * R // window.windowSize[1] + 1)])
    for i in range(int(xmin_px * C // window.windowSize[0]), int(xmax_px * C // window.windowSize[0] + 1)):
        for j in range(int(ymin_px * R // window.windowSize[1]), int(ymax_px * R // window.windowSize[1] + 1)):
            if wall_booleans[i][j]:
                return True
    return False


def addDubinsBoundingBox(name, window, dubinsBoundingBox, color: str = 'red'):
    x_min, y_min = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(
        (dubinsBoundingBox[0][0], dubinsBoundingBox[1][0]))
    x_max, y_max = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(
        (dubinsBoundingBox[0][1], dubinsBoundingBox[1][1]))
    window.addForegroundBox(name, x_min, y_min, x_max - x_min, y_max - y_min, color=color)


def minimax(a, b):
    return (a, b) if a < b else (b, a)


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Initialize window
    TOTAL_WIDTH_INCHES = 42 + 15 / 16
    TOTAL_HEIGHT_INCHES = 28 + 13 / 16
    INCH_TO_CM = 2.54
    physicalSpace = (TOTAL_WIDTH_INCHES * INCH_TO_CM, TOTAL_HEIGHT_INCHES * INCH_TO_CM)
    windowSizeX = 800
    windowSizeY = windowSizeX * TOTAL_HEIGHT_INCHES // TOTAL_WIDTH_INCHES
    window = ErrorVisualizationWindow(physicalSpace=physicalSpace, windowSizeWithoutLog=(windowSizeX, windowSizeY))

    # Defining dimensions
    WALL_WIDTH_INCHES = 7 / 16
    NUM_PASSAGES_X, NUM_PASSAGES_Y = (6, 4)
    PASSAGE_SPACING_X_INCHES = (TOTAL_WIDTH_INCHES - (NUM_PASSAGES_X + 1) * WALL_WIDTH_INCHES) / NUM_PASSAGES_X
    PASSAGE_SPACING_Y_INCHES = (TOTAL_HEIGHT_INCHES - (NUM_PASSAGES_Y + 1) * WALL_WIDTH_INCHES) / NUM_PASSAGES_Y
    wallSizeX = window.mapPhysicalDimensionsToPixels(WALL_WIDTH_INCHES * INCH_TO_CM, axis=0)
    wallSizeY = window.mapPhysicalDimensionsToPixels(WALL_WIDTH_INCHES * INCH_TO_CM, axis=1)
    passageSizeX = window.mapPhysicalDimensionsToPixels(PASSAGE_SPACING_X_INCHES * INCH_TO_CM, axis=0)
    passageSizeY = window.mapPhysicalDimensionsToPixels(PASSAGE_SPACING_Y_INCHES * INCH_TO_CM, axis=1)

    # Define walls
    wall_booleans = np.load(motion_primitive_composition_path + '/maze_images/wall_booleans.npy')
    GRID_SIZE_Y_INCHES = TOTAL_HEIGHT_INCHES / len(wall_booleans)
    GRID_SIZE_X_INCHES = TOTAL_WIDTH_INCHES / len(wall_booleans[0])
    gridSizeX = window.mapPhysicalDimensionsToPixels(GRID_SIZE_X_INCHES * INCH_TO_CM, axis=0)
    gridSizeY = window.mapPhysicalDimensionsToPixels(GRID_SIZE_Y_INCHES * INCH_TO_CM, axis=1)
    for i in range(len(wall_booleans)):
        for j in range(len(wall_booleans[0])):
            if wall_booleans[i][j]:
                window.addBackgroundBox('wall_' + str(i) + ',' + str(j), j * gridSizeX, i * gridSizeY, gridSizeX,
                                        gridSizeY)

    # Adding in the car
    print(PASSAGE_SPACING_X_INCHES)
    CAR_RADIUS = 11 / INCH_TO_CM  # Adjust
    carRadius = window.mapPhysicalDimensionsToPixels(CAR_RADIUS, axis=0)

    startPosition = ((WALL_WIDTH_INCHES + PASSAGE_SPACING_X_INCHES / 2) * INCH_TO_CM,
                     (0.5 * PASSAGE_SPACING_Y_INCHES + WALL_WIDTH_INCHES) * INCH_TO_CM,
                     pi / 2)

    carCoordinates = window.mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(startPosition[0:2])
    window.log('Car coordinates:', carCoordinates)
    window.addForegroundCircle('car', *carCoordinates, carRadius)

    def removeAllWalls(delay=1000):
        window.delayGUI(1000)
        window.removeAllForegroundPaintObjects()
        window.addForegroundCircle('car', *carCoordinates, carRadius)

    db = RotatingDubinsModel()
    x, y, theta, v, omega, dt = db.variables
    inputsMoveForward = {x: startPosition[0], y: startPosition[1], theta: startPosition[2], v: 28.83451398,
                         omega: 0.1500567293, dt: 0.3}
    errorsMoveForward = {x: 0, y: 0, theta: 0, v: 3 * 1.334704641, omega: 3 * 0.02230989018, dt: 0}
    inputsRotate = {x: startPosition[0], y: startPosition[1], theta: startPosition[2], v: 0.7851747434,
                    omega: 740.2410825, dt: 0.3}
    errorsRotate = {x: 0, y: 0, theta: 0, v: 3 * 0.4296893495, omega: 3 * 25.1694945, dt: 0}
    symbolMapping = [x, y, theta]

    def reinitializeInputs():
        inputsMoveForward[x] = inputsRotate[x] = startPosition[0]
        inputsMoveForward[y] = inputsRotate[y] = startPosition[1]
        inputsMoveForward[theta] = inputsRotate[theta] = startPosition[2]

    # actionSequence = [[40, 0], [0, -pi/2], [20, 0]]
    actionSequence = np.load(motion_primitive_composition_path + '/maze_images/path_array.npy')
    allTimes = []
    numActions = 0

    def updateActionSequence(name, *actions, color='red'):
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
        boundingBoxes = db.calculateSequenceOfErrorMargins(allPredictedInputs, allErrors, symbolMapping, False,
                                                           window.log)
        for i, boundingBox in enumerate(boundingBoxes):
            addDubinsBoundingBox(name + '_' + str(i), window, boundingBox, color=color)

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
        # print(inputsMoveForward)
        # print(errorsMoveForward)
        # print(inputsRotate)
        # print(errorsRotate)

        nonlocal numActions
        numActions += 1
        return boundingBoxes

    MAX_DEPTH = 5

    def pathPlanning(actionSequence, depth=0):
        print('Path planning for action sequence:', actionSequence, 'at depth', depth)
        if depth > MAX_DEPTH:
            raise ValueError('This algorithm cannot converge within', MAX_DEPTH,
                             'iterations. Does the car intersect the wall?')
        removeAllWalls(1000)
        boundingBoxes = updateActionSequence('first_trial', *actionSequence, color='red')
        for i, boundingBox in enumerate(boundingBoxes):
            intersectsWall = boundingBoxIntersection(boundingBox, window, wall_booleans)
            if intersectsWall and i > 0:
                return actionSequence[:i]  # You can do all moves up until move i without crashing
            elif intersectsWall and i == 0:
                return pathPlanning(actionSequence[:1] / 2, depth=depth + 1)
        return actionSequence  # If none of the bounding boxes intersects the wall, you're set to go!

    plannedActionSequence = actionSequence
    print(plannedActionSequence)
    proposedActionSequence = pathPlanning(plannedActionSequence)
    print(proposedActionSequence)

    reinitializeInputs()
    removeAllWalls(1000)
    boundingBoxes = updateActionSequence('final_execution', *proposedActionSequence, color='blue')
    print('Bounding boxes of final movement:', boundingBoxes)

    # N = 10
    # for i in range(N):
    #     updateActionSequence('move' + str(i), actionSequence[1] / N, color=['red', 'yellow'][i % 2])
    # print(actionSequence[:10])
    # updateActionSequence('move1', actionSequence[0], actionSequence[1] / 2, color='red')
    # updateActionSequence('move2', [-30 * pi/180, 0], color='blue')
    # updateActionSequence('move3', actionSequence[1] / 2, color='red')
    # updateActionSequence(*actionSequence[2:6], color='yellow')
    # # updateActionSequence(actionSequence[8], color='yellow')
    # updateActionSequence(actionSequence[1] / 2, color='red')
    # updateActionSequence(actionSequence[1] / 2, color='yellow')
    # updateActionSequence(actionSequence[1] / 2)
    # updateActionSequence([-0.001, 0])
    # updateActionSequence(actionSequence[1] / 3)
    # updateActionSequence('move1', *actionSequence[:5])
    # for i in range()

    # Tests
    # print(window.mapPhysicalDimensionsToPixels(physicalSpace[0], axis=0),
    #       window.mapPhysicalDimensionsToPixels(physicalSpace[1], axis=1))
    # print(wallSizeX, wallSizeY)
    # print(passageSizeX, passageSizeY)
    # print(NUM_PASSAGES_X * passageSizeX + (NUM_PASSAGES_X + 1) * wallSizeX)
    # print(NUM_PASSAGES_Y * passageSizeY + (NUM_PASSAGES_Y + 1) * wallSizeY)
    print("Theoretical runtime:", sum(allTimes))

    START_TIME = 30
    TIME_PER_COMPUTATION_STEP = 10
    print('Theoretical runtime, adding in heuristics for computation time:',
          sum(allTimes) + START_TIME + TIME_PER_COMPUTATION_STEP * (numActions - 1))

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
