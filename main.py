import numpy as np
from random import random, randrange
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QLineEdit, QVBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt, QRect, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QBrush, QIntValidator
from PyQt5 import sip



class Piece(QWidget):

    colorForZeros = QColor('blue')
    colorForOnes = QColor('red')
    colorForKeyCoordinate = QColor('yellow')

    x = 0 # Horizontal board position
    y = 0 # Vertical board position
    value = 0 # determines the color
    isKeyCoordinate = False

    onStatusChanged = pyqtSignal()

    def __init__(self, x, y, value, isKeyCoordinate):
        super(Piece, self).__init__()
        self.x = x
        self.y = y
        self.value = value
        self.isKeyCoordinate = isKeyCoordinate
    
    def getFieldColor(self):
        if self.isKeyCoordinate:
            return self.colorForKeyCoordinate
        elif self.x % 2 and not self.y % 2 or self.y % 2 and not self.x % 2:
            return QColor('grey')
        return QColor('white')


    def getCircleColor(self):
        if self.value == 0:
            return self.colorForZeros
        return self.colorForOnes


    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.value == 0:
                self.value = 1
            else:
                self.value = 0
        if event.buttons() == Qt.RightButton:
            self.isKeyCoordinate = True
        self.update()        
        self.onStatusChanged.emit()


    @pyqtSlot(QWidget)
    def paintEvent(self, event):        
        fieldColor = self.getFieldColor()
        painter = QPainter(self)        
        brush = QBrush(fieldColor, Qt.SolidPattern)
        rect = QRect(0,0, self.geometry().width(), self.geometry().height())
        painter.fillRect(rect, brush)
        painter.drawRect(rect)

        circleColor = self.getCircleColor()
        painter.setBrush(QBrush(circleColor, Qt.SolidPattern))
        painter.drawEllipse(5, 5, self.geometry().width() - 10, self.geometry().height() - 10)



class ChessBoard(QWidget):

    boardSize = 8
    pieceValues = np.random.randint(0, 2, size=(boardSize,boardSize))
    keyCoordinate = [randrange(boardSize), randrange(boardSize)] # The field we want to determine

    pieces = [] # All the board pieces
    horizontalStats = [] # Text labels for rows
    verticalStats = [] # Text labels for columns

    def __init__(self, parent=None):
        super(ChessBoard, self).__init__(parent)
        self.parent = parent

        self.setupBoardData(8)
        self.setupUI()
        

    def setupBoardData(self, newBoardSize):
        self.boardSize = newBoardSize
        self.pieceValues = np.random.randint(0, 2, size=(self.boardSize,self.boardSize))
        self.keyCoordinate = [randrange(self.boardSize), randrange(self.boardSize)] # The field we want to determine


    def setupUI(self):
        self.pieces.clear()
        self.horizontalStats.clear()
        self.verticalStats.clear()

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.layout.addWidget(self.createControlPanel(), self.boardSize + 1, 0, 1, self.boardSize + 1)
        self.createGrid()


    def createControlPanel(self):
        groupBox = QGroupBox()

        self.labelDeterminant = QLabel('Determinant: ' + str(np.linalg.det(self.pieceValues)))

        self.buttonRandomize = QPushButton('Randomize Layout')
        self.buttonRandomize.clicked.connect(self.buttonRandClick)

        self.boardSizeLabel = QLabel(self)
        self.boardSizeLabel.setText('Board size:')

        self.boardSizeEdit = QLineEdit(self)
        self.boardSizeEdit.setMaxLength(1)
        self.boardSizeEdit.setValidator(QIntValidator(4, 8))
        self.boardSizeEdit.textChanged.connect(self.textChanged)

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelDeterminant)
        vbox.addWidget(self.buttonRandomize)
        vbox.addWidget(self.boardSizeLabel)
        vbox.addWidget(self.boardSizeEdit)
        groupBox.setLayout(vbox)

        return groupBox


    def textChanged(self, newNum):
        num = int(newNum)
        if num < 4 or num > 8:
            self.boardSizeEdit.selectAll()
            return
            
        self.deleteLayout(self.layout)
        self.setupBoardData(num)
        self.setupUI()


    def deleteLayout(self, cur_lay):        
        if cur_lay is not None:
            while cur_lay.count():
                item = cur_lay.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteLayout(item.layout())
            sip.delete(cur_lay)


    def buttonRandClick(self):
        self.keyCoordinate[0] = np.random.randint(0, self.boardSize)
        self.keyCoordinate[1] = np.random.randint(0, self.boardSize)
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                self.pieceValues[i, j] = np.random.randint(0,2)
                currentPiece = self.pieces[i*self.boardSize + j]
                currentPiece.value = self.pieceValues[i, j]
                currentPiece.isKeyCoordinate = self.keyCoordinate[0] == i and self.keyCoordinate[1] == j        
        self.redraw()


    def createGrid(self):
        for counterX, valueX in enumerate(self.pieceValues):
            for counterY, valueY in enumerate(valueX):
                if counterX == self.boardSize - 1:
                    pieceCounterX = QLabel("")
                    self.layout.addWidget(pieceCounterX, counterX + 1, counterY)
                    self.horizontalStats.append(pieceCounterX)
                if counterY == self.boardSize - 1:
                    pieceCounterY = QLabel("")
                    self.layout.addWidget(pieceCounterY, counterX, counterY + 1)
                    self.verticalStats.append(pieceCounterY)

                isKeyCoord = counterX == self.keyCoordinate[0] and counterY == self.keyCoordinate[1]
                piece = Piece(counterX, counterY, valueY, isKeyCoord)
                piece.onStatusChanged.connect(self.onPieceClicked)
                self.pieces.append(piece)
                self.layout.addWidget(piece, counterX, counterY)
        self.redraw()


    @pyqtSlot()
    def onPieceClicked(self):
        clickedX = self.sender().x
        clickedY = self.sender().y

        self.pieceValues[clickedX, clickedY] = self.sender().value

        currentKeyCoordinatePiece = self.pieces[self.keyCoordinate[0] * self.boardSize + self.keyCoordinate[1]]
        if currentKeyCoordinatePiece != self.sender():
            currentKeyCoordinatePiece.isKeyCoordinate = False
            self.keyCoordinate = [clickedX, clickedY]

        self.redraw()


    def redraw(self):
        self.labelDeterminant.setText('Determinant: ' + str(np.linalg.det(self.pieceValues)))
        
        for piece in self.pieces:
            piece.update()

        colZeros = np.count_nonzero(self.pieceValues == 0, axis=1)
        colOnes = np.count_nonzero(self.pieceValues == 1, axis=1)

        rowZeros = np.count_nonzero(self.pieceValues == 0, axis=0)
        rowOnes = np.count_nonzero(self.pieceValues == 1, axis=0)

        for e in range(self.boardSize):
            self.verticalStats[e].setText(" B:" + str(colZeros[e]) + " R:" + str(colOnes[e]))
            self.horizontalStats[e].setText(" B:" + str(rowZeros[e]) + " R:" + str(rowOnes[e]))



class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Chessboard Puzzle")
        self.setGeometry(0, 0, 600, 700)

        self.layout = QVBoxLayout(self)        
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(0)

        board = ChessBoard(self)
        self.layout.addWidget(board)



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
