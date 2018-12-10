#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Error Visualization using PyQt5

Author: Ahad Rauf
"""

# Core Python imports
import sys
import time

# Graphics imports
from PyQt5 import QtWidgets, QtCore, QtGui, QtTest

# Miscellaneous helper imports
from typing import List, Tuple, Union


# noinspection PyShadowingNames
class ErrorVisualizationWindow(QtWidgets.QWidget):
    def __init__(self, physicalSpace: Tuple[float, float], windowSizeWithoutLog: Tuple[float, float] = (800, 600),
                 logWindowWidth: int = 300):
        super().__init__()
        self._physicalSpace = physicalSpace
        self._windowSize = windowSizeWithoutLog
        self._logWindowWidth = logWindowWidth

        self._backgroundPaintObjects = {}
        self._foregroundPaintObjects = {}

        self._initializeGraphics()

    """
    Public functions
    """

    def addBackgroundBox(self, name, top_left_x, top_left_y, width, height, color: str = 'black'):
        box = QtCore.QRect(top_left_x, top_left_y, width, height)
        self._backgroundPaintObjects[name] = ('rect', box, QtGui.QBrush(QtGui.QColor(color), QtCore.Qt.SolidPattern))
        self.update()

    def addForegroundBox(self, name, top_left_x, top_left_y, width, height, color: str = 'black'):
        box = QtCore.QRect(top_left_x, top_left_y, width, height)
        self._foregroundPaintObjects[name] = ('rect', box, QtGui.QBrush(QtGui.QColor(color), QtCore.Qt.SolidPattern))
        self.update()

    def addBackgroundCircle(self, name, center_x, center_y, radius, color: str = 'red'):
        ellipse = QtCore.QRect(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        self._backgroundPaintObjects[name] = ('ellipse', ellipse,
                                              QtGui.QBrush(QtGui.QColor(color), QtCore.Qt.SolidPattern))
        self.update()

    def addForegroundCircle(self, name, center_x, center_y, radius, color: str = 'red'):
        ellipse = QtCore.QRect(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        self._foregroundPaintObjects[name] = ('ellipse', ellipse,
                                              QtGui.QBrush(QtGui.QColor(color), QtCore.Qt.SolidPattern))
        self.update()

    def removePaintObject(self, name: str) -> None:
        """
        Error-less removal of paint objects from both background and foreground paint objects

        :param name: The name set for the object (see addBox() for an example)
        :return: None
        """
        self._backgroundPaintObjects.pop(name, None)
        self._foregroundPaintObjects.pop(name, None)

    def mapPhysicalDimensionsToPixels(self, physicalDimension: float, axis: int) -> float:
        return physicalDimension * self._windowSize[axis] // self._physicalSpace[axis]

    def mapPhysicalCoordinatesToPixels(self, physicalCoordinates: Tuple[float, float]) -> Tuple[float, float]:
        return (self.mapPhysicalDimensionsToPixels(physicalCoordinates[0], axis=0),
                self.mapPhysicalDimensionsToPixels(physicalCoordinates[1], axis=1))

    def mapPhysicalCoordinatesInStandardCoordinateFrameToPixels(self, physicalCoordinates: Tuple[float, float]) -> \
    Tuple[float, float]:
        return (self.mapPhysicalDimensionsToPixels(physicalCoordinates[0], axis=0),
                self.mapPhysicalDimensionsToPixels(self._physicalSpace[1] - physicalCoordinates[1], axis=1))

    def delayGUI(self, delay_ms: int):
        QtTest.QTest.qWait(delay_ms)

    def log(self, *text):
        toWrite = ""
        for textSnippet in text:
            toWrite += str(textSnippet) + " "
        self._logFrame.append(toWrite)

    """
    Overriden functions
    """

    def paintEvent(self, event: QtGui.QPaintEvent):
        qp = QtGui.QPainter(self)
        # br = QtGui.QBrush(QtGui.QColor('red'))
        # qp.setBrush(br)
        for name in self._backgroundPaintObjects:
            type, paintObject, brush = self._backgroundPaintObjects[name]
            if type == 'rect':
                qp.fillRect(paintObject, brush)
            elif type == 'ellipse':
                qp.setBrush(brush)
                qp.drawEllipse(paintObject)
        for name in self._foregroundPaintObjects:
            type, paintObject, brush = self._foregroundPaintObjects[name]
            if type == 'rect':
                qp.fillRect(paintObject, brush)
            elif type == 'ellipse':
                qp.setBrush(brush)
                qp.drawEllipse(paintObject)
        qp.end()

    """
    Private functions
    """

    def _initializeGraphics(self):
        self._mainLayout = QtWidgets.QHBoxLayout(self)
        # self._mainFrame = QtWidgets.QFrame(self)
        # self._mainFrame.setMaximumWidth(self._windowSize[0])

        self._logFrame = QtWidgets.QTextEdit(self)
        self._logFrame.setMaximumWidth(self._logWindowWidth)
        self._logFrame.setReadOnly(True)

        # self._mainLayout.addWidget(self._mainFrame)
        self._mainLayout.addStretch(1)
        self._mainLayout.addWidget(self._logFrame)

        self.setLayout(self._mainLayout)

        self.resize(self._windowSize[0] + self._logWindowWidth, self._windowSize[1])
        self._centerWindow()
        self.setWindowTitle('Error Visualization Window, EE 149 Final Project Fall 2018')
        self.show()

    def _centerWindow(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


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

    window.addForegroundCircle('circ1', 300, 300, 300)
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
