import numpy as np
from random import randrange
from PyQt5 import QtCore, QtGui, QtWidgets


boarSize = 8
colorForZeros = QtGui.QColor('blue')
colorForOnes = QtGui.QColor('red')
colorForKeyCoordinate = QtGui.QColor('yellow')
pieceValues = np.random.randint(0, 2, size=(boarSize,boarSize))
keyCoordinate = [randrange(boarSize), randrange(boarSize)] # The field we want to determine


class Piece(QtWidgets.QWidget):

    x = 0 # Horizontal board position
    y = 0 # Vertical board position

    def __init__(self, x, y, parent = None):
        super(Piece, self).__init__(parent)
        self.x = x
        self.y = y
        self.parent = parent

    
    def getFieldColor(self):
        if self.x == keyCoordinate[0] and self.y == keyCoordinate[1]:
            return colorForKeyCoordinate
        elif self.x % 2 and not self.y % 2 or self.y % 2 and not self.x % 2:
            return QtGui.QColor('grey')
        return QtGui.QColor('white')


    def getCircleColor(self):
        if pieceValues[self.x, self.y] == 0:
            return colorForZeros
        return colorForOnes


    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if pieceValues[self.x, self.y] == 0:
                pieceValues[self.x, self.y] = 1
            else:
                pieceValues[self.x, self.y] = 0
        elif event.buttons() == QtCore.Qt.RightButton:
            keyCoordinate[0] = self.x
            keyCoordinate[1] = self.y
        self.parent.redraw() # Update the other pieces


    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def paintEvent(self, event):        
        fieldColor = self.getFieldColor()
        painter = QtGui.QPainter(self)        
        brush = QtGui.QBrush(fieldColor, QtCore.Qt.SolidPattern)
        rect = QtCore.QRect(0,0, self.geometry().width(), self.geometry().height())
        painter.fillRect(rect, brush)
        painter.drawRect(rect)

        circleColor = self.getCircleColor()
        painter.setBrush(QtGui.QBrush(circleColor, QtCore.Qt.SolidPattern))
        painter.drawEllipse(5, 5, self.geometry().width() - 10, self.geometry().height() - 10)



class ChessBoard(QtWidgets.QWidget):

    pieces = [] # All the board pieces
    horizontalStats = [] # Text labels for rows
    verticalStats = [] # Text labels for columns

    def __init__(self, parent=None):
        super(ChessBoard, self).__init__(parent)
        self.parent = parent

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.labelDeterminant = QtWidgets.QLabel('Determinant: ' + str(np.linalg.det(pieceValues)))
        self.layout.addWidget(self.labelDeterminant, boarSize + 2, 0, 1, boarSize + 2)
        
        self.fillGrid()


    def fillGrid(self):
        for counterX, valueX in enumerate(pieceValues):
            for counterY, valueY in enumerate(valueX):
                if counterX == boarSize - 1:
                    pieceCounterX = QtWidgets.QLabel("")
                    self.layout.addWidget(pieceCounterX, counterX + 1, counterY)
                    self.horizontalStats.append(pieceCounterX)
                if counterY == boarSize - 1:
                    pieceCounterY = QtWidgets.QLabel("")
                    self.layout.addWidget(pieceCounterY, counterX, counterY + 1)
                    self.verticalStats.append(pieceCounterY)

                piece = Piece(counterX, counterY, self)
                self.pieces.append(piece)
                self.layout.addWidget(piece, counterX, counterY)
        self.redraw()


    def redraw(self):
        self.labelDeterminant.setText('Determinant: ' + str(np.linalg.det(pieceValues)))

        for piece in self.pieces:
            piece.update()

        colZeros = np.count_nonzero(pieceValues == 0, axis=1)
        colOnes = np.count_nonzero(pieceValues == 1, axis=1)

        rowZeros = np.count_nonzero(pieceValues == 0, axis=0)
        rowOnes = np.count_nonzero(pieceValues == 1, axis=0)

        for e in range(boarSize):
            self.verticalStats[e].setText(" B:" + str(colZeros[e]) + " R:" + str(colOnes[e]))
            self.horizontalStats[e].setText(" B:" + str(rowZeros[e]) + " R:" + str(rowOnes[e]))



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Chessboard Puzzle")
        self.setGeometry(0, 0, 600, 600)

        layout = QtWidgets.QVBoxLayout(self)        
        layout.setContentsMargins(25, 25, 0, 0)
        layout.setSpacing(0)

        board = ChessBoard(self)
        layout.addWidget(board)



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
