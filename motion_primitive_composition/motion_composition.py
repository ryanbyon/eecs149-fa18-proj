#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Motion composition main file

Author: Ahad Rauf
"""

import sys
import numpy as np

from PyQt5 import QtWidgets

from motion_primitive_composition.dynamics import RotatingDubinsModel
from motion_primitive_composition.error_visualization import ErrorVisualizationWindow

if __name__ == '__main__':
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

    window.addBackgroundBox('wall_left', 0, 0, wallSizeX, windowSizeY)
    window.addBackgroundBox('wall_top', 0, 0, windowSizeX, wallSizeX)
    window.addBackgroundBox('wall_right', windowSizeX - wallSizeX, 0, wallSizeX, windowSizeY)
    window.addBackgroundBox('wall_bottom', 0, windowSizeY - wallSizeY, windowSizeX, wallSizeY)
    window.addBackgroundBox('wall_left1_top', wallSizeX + passageSizeX, wallSizeY, wallSizeX, wallSizeY + passageSizeY)
    window.addBackgroundBox('wall_left1_bottom', wallSizeX + passageSizeX, 2 * passageSizeY + 2 * wallSizeY,
                            wallSizeX, 2 * passageSizeY + 3 * wallSizeY)
    window.addBackgroundBox('wall_left2_top', 2 * wallSizeX + 2 * passageSizeX, wallSizeY,
                            wallSizeX, 3 * wallSizeY + 3 * passageSizeY)
    window.addBackgroundBox('wall_left2_middle', 3 * wallSizeX + 3 * passageSizeX, wallSizeY + passageSizeY,
                            wallSizeX, 3 * wallSizeY + 2 * passageSizeY)
    window.addBackgroundBox('wall_right1_bottom', 5 * passageSizeX + 5 * wallSizeX, passageSizeY + wallSizeY,
                            wallSizeX, 3 * passageSizeY + 4 * wallSizeY)
    window.addBackgroundBox('wall_right2_top', 3 * passageSizeX + 3 * wallSizeX, passageSizeY + wallSizeY,
                            2 * passageSizeX + 3 * wallSizeX, wallSizeY)
    window.addBackgroundBox('wall_right2_bottom', 3 * passageSizeX + 3 * wallSizeX, 3 * passageSizeY + 3 * wallSizeY,
                            passageSizeX + 2 * wallSizeX, wallSizeY)

    # Adding in the car
    CAR_RADIUS_INCHES = PASSAGE_SPACING_X_INCHES / 2  # Adjust
    carRadius = window.mapPhysicalDimensionsToPixels(CAR_RADIUS_INCHES, axis=0)

    startPosition = ((WALL_WIDTH_INCHES + PASSAGE_SPACING_X_INCHES / 2) * INCH_TO_CM,
                     (3.5 * PASSAGE_SPACING_Y_INCHES + 3 * WALL_WIDTH_INCHES) * INCH_TO_CM)

    carCoordinates = window.mapPhysicalCoordinatesToPixels(startPosition)
    print(carCoordinates)
    window.addForegroundCircle('circ1', *carCoordinates, carRadius)
    # for i in range(50):
    #     window.log('hello')

    # Tests
    print(window.mapPhysicalDimensionsToPixels(physicalSpace[0], axis=0),
          window.mapPhysicalDimensionsToPixels(physicalSpace[1], axis=1))
    print(wallSizeX, wallSizeY)
    print(passageSizeX, passageSizeY)
    print(NUM_PASSAGES_X * passageSizeX + (NUM_PASSAGES_X + 1) * wallSizeX)
    print(NUM_PASSAGES_Y * passageSizeY + (NUM_PASSAGES_Y + 1) * wallSizeY)

    sys.exit(app.exec_())
