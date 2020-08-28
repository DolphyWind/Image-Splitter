import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PIL import Image
from PIL.ImageQt import ImageQt

font = QtGui.QFont("Arial", 12)

def splitImage(filename, split_x, split_y, foldername, return_list = False):
    im = Image.open(filename)
    short_filename = filename.split('/')[-1]
    short_filename_no_ext = '.'.join(short_filename.split('.')[:-1])
    file_ext = '.' + short_filename.split('.')[-1]

    images = list()

    for y in range(0, im.height, im.height // split_y):
        for x in range(0, im.width, im.width // split_x):
            cropped = im.crop((x, y, x + (im.width // split_x), y + (im.height // split_y)))
            images.append(cropped.copy())

    if return_list:
        return images
    for i, im in enumerate(images):
        im.save(foldername + '/' + short_filename_no_ext + '_' + str(i) + file_ext)


def calcScale(image_size, targetSize: tuple):
    w, h = image_size
    x_ratio = targetSize[0] / w
    y_ratio = targetSize[1] / h
    scale = x_ratio if y_ratio > x_ratio else y_ratio
    return scale

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.windowSize = (800, 600)
        self.imageMaxSize = (self.windowSize[0] * 0.6, self.windowSize[1] * 0.6)
        self.imageLoaded = False
        self.folderSelected = False
        self.setWindowTitle("Image Splitter")
        self.setGeometry(0, 0, self.windowSize[0], self.windowSize[1])
        self.center()
        self.UI()

        self.show()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1)

        self.timer.timeout.connect(self.checkResized)
        self.timer.start()

    # Things would happen when window resized
    def checkResized(self):
        if self.width() * 0.6 != self.imageMaxSize[0] or self.height() * 0.6 != self.imageMaxSize[1]:
            self.windowSize = (self.width(), self.height())
            self.imageMaxSize = (self.windowSize[0] * 0.6, self.windowSize[1] * 0.6)
            self.imagePreview.setMaximumSize(int(self.imageMaxSize[0]), int(self.imageMaxSize[1]))
            if self.imageLoaded:
                scale = calcScale(self.original_image.size, self.imageMaxSize)
                resized = (int(self.original_image.width * scale), int(self.original_image.height * scale))
                self.pil_image = self.original_image.resize(resized, Image.ANTIALIAS)
                self.pil_image = self.pil_image.convert("RGBA")
                data = self.pil_image.tobytes('raw', 'RGBA')
                qim = QtGui.QImage(data, self.pil_image.size[0], self.pil_image.size[1], QtGui.QImage.Format_RGBA8888)
                self.imagePreview.setPixmap(QtGui.QPixmap.fromImage(qim))
                self.drawStripes()

    # Open File Dialog
    def loadFile(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', 'c:\\', "PNG files (*.png);;JPG files (*.jpg);;BMP files (*.bmp);;ICO files (*.ico)")
        if self.filename[0]:
            self.imageLoaded = True
            self.filename = self.filename[0]
            self.pil_image = Image.open(self.filename)
            self.original_image = self.pil_image.copy()
            scale = calcScale(self.pil_image.size, self.imageMaxSize)
            resized = (int(self.pil_image.width * scale), int(self.pil_image.height * scale))
            self.pil_image = self.pil_image.resize(resized, Image.ANTIALIAS)
            self.pil_image = self.pil_image.convert("RGBA")
            data = self.pil_image.tobytes('raw', 'RGBA')
            qim = QtGui.QImage(data, self.pil_image.size[0], self.pil_image.size[1], QtGui.QImage.Format_RGBA8888)
            self.imagePreview.setPixmap(QtGui.QPixmap.fromImage(qim))
            self.imagePreview.show()
            self.drawStripes()

    def drawStripes(self):
        if self.imageLoaded:
            im = self.pil_image.copy()
            pieceC = self.xSpinBox.value()
            pieceC = int(pieceC)
            per_pix = int(im.width / pieceC)
            for y in range(im.height):
                for x in range(per_pix, im.width, per_pix):
                    pix = im.getpixel((x, y))
                    pix = (255 - pix[0], 255 - pix[1], 255 - pix[2], 255)
                    im.putpixel((x, y), pix)

            pieceC = self.ySpinBox.value()
            pieceC = int(pieceC)
            per_pix = int(im.height / pieceC)
            for y in range(per_pix, im.height, per_pix):
                for x in range(im.width):
                    if True:
                        pix = im.getpixel((x, y))
                        pix = (255 - pix[0], 255 - pix[1], 255 - pix[2], 255)
                        im.putpixel((x, y), pix)
            im = im.convert("RGBA")
            data = im.tobytes('raw', 'RGBA')
            qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_RGBA8888)
            self.imagePreview.setPixmap(QtGui.QPixmap.fromImage(qim))

    # Select Folder Dialog
    def selectFolder(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder"))
        if file:
            self.folderSelected = True
            self.foldername = file

    def split(self):
        if self.imageLoaded and self.folderSelected:
            splitImage(self.filename, int(self.xSpinBox.value()), int(self.ySpinBox.value()), self.foldername)
            QtWidgets.QMessageBox.information(self, 'Operation Successfull!', 'Your image splitted successfully and saved to ' + self.foldername)
        else:
            QtWidgets.QMessageBox.critical(self, "Error!", "You must load an image and select a folder before splitting!")

    def makeGif(self):
        if self.imageLoaded and self.folderSelected:
            images = splitImage(self.filename, int(self.xSpinBox.value()), int(self.ySpinBox.value()), self.foldername, return_list=True)
            filename_no_ext = '.'.join(self.filename.split('/')[-1].split('.')[:-1])
            images[0].save(self.foldername + '/' + filename_no_ext + '.gif', save_all=True, append_images=images[1:], optimize=False, loop=0, duration=40)
            QtWidgets.QMessageBox.information(self, 'Operation Successfull!', 'Your gif file created successfully and saved to ' + self.foldername)
        else:
            QtWidgets.QMessageBox.critical(self, "Error!", "You must load an image and select a folder before making gif!")

    def UI(self):
        # Layouts
        self.mainHLayout = QtWidgets.QHBoxLayout()
        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.leftVLayout = QtWidgets.QVBoxLayout()
        self.rightVLayout = QtWidgets.QVBoxLayout()
        self.leftHLayout = QtWidgets.QHBoxLayout()
        self.rightHLayout = QtWidgets.QHBoxLayout()
        self.bottomHLayout = QtWidgets.QHBoxLayout()
        self.bottomVLayout = QtWidgets.QVBoxLayout()
        self.xAxisLayout = QtWidgets.QHBoxLayout()
        self.yAxisLayout = QtWidgets.QHBoxLayout()

        # Buttons
        self.selectFileButton = QtWidgets.QPushButton("Select File...")
        self.selectFileButton.setFont(font)
        self.selectFileButton.setMinimumSize(50, 40)
        self.selectFileButton.clicked.connect(self.loadFile)

        self.selectFolderButton = QtWidgets.QPushButton("Select Folder...")
        self.selectFolderButton.setFont(font)
        self.selectFolderButton.setMinimumSize(50, 40)
        self.selectFolderButton.clicked.connect(self.selectFolder)

        self.splitButton = QtWidgets.QPushButton("Split!")
        self.splitButton.setFont(font)
        self.splitButton.setMinimumSize(50, 40)
        self.splitButton.clicked.connect(self.split)

        self.makeGifButton = QtWidgets.QPushButton("Make Gif!")
        self.makeGifButton.setFont(font)
        self.makeGifButton.setMinimumSize(50, 40)
        self.makeGifButton.clicked.connect(self.makeGif)

        # Labels
        self.inputFileLabel = QtWidgets.QLabel("  Input File")
        self.inputFileLabel.setFont(font)

        self.outputFolderLabel = QtWidgets.QLabel("   Output Folder")
        self.outputFolderLabel.setFont(font)

        self.splitLabel_x = QtWidgets.QLabel("Split")
        self.splitLabel_x.setFont(font)

        self.splitLabel_y = QtWidgets.QLabel("Split")
        self.splitLabel_y.setFont(font)

        self.xAxisLabel = QtWidgets.QLabel("parts on x axis")
        self.xAxisLabel.setFont(font)

        self.yAxisLabel = QtWidgets.QLabel("parts on y axis")
        self.yAxisLabel.setFont(font)

        self.imagePreview = QtWidgets.QLabel()
        self.imagePreview.setMaximumSize(int(self.imageMaxSize[0]), int(self.imageMaxSize[1]))

        # Spin boxes
        self.xSpinBox = QtWidgets.QSpinBox()
        self.xSpinBox.setRange(1, 16)
        self.xSpinBox.setMaximumSize(50, 20)
        self.xSpinBox.valueChanged.connect(self.drawStripes)

        self.ySpinBox = QtWidgets.QSpinBox()
        self.ySpinBox.setRange(1, 16)
        self.ySpinBox.setMaximumSize(50, 20)
        self.ySpinBox.valueChanged.connect(self.drawStripes)

        # Design

        self.xAxisLayout.addWidget(self.splitLabel_x)
        self.xAxisLayout.addWidget(self.xSpinBox)
        self.xAxisLayout.addWidget(self.xAxisLabel)
        self.xAxisLayout.addStretch()

        self.yAxisLayout.addWidget(self.splitLabel_y)
        self.yAxisLayout.addWidget(self.ySpinBox)
        self.yAxisLayout.addWidget(self.yAxisLabel)
        self.yAxisLayout.addStretch()

        self.leftVLayout.addStretch()
        self.leftVLayout.addWidget(self.inputFileLabel)
        self.leftVLayout.addWidget(self.selectFileButton)
        self.leftVLayout.addStretch()
        self.leftVLayout.addLayout(self.xAxisLayout)
        self.leftVLayout.addLayout(self.yAxisLayout)
        self.leftVLayout.addStretch()
        self.leftVLayout.addWidget(self.outputFolderLabel)
        self.leftVLayout.addWidget(self.selectFolderButton)
        self.leftVLayout.addStretch()

        self.leftHLayout.addStretch()
        self.leftHLayout.addLayout(self.leftVLayout)
        self.leftHLayout.addStretch()

        self.rightVLayout.addStretch()
        self.rightVLayout.addWidget(self.imagePreview)
        self.rightVLayout.addStretch()

        self.rightHLayout.addStretch()
        self.rightHLayout.addLayout(self.rightVLayout)
        self.rightHLayout.addStretch()

        self.bottomHLayout.addStretch()
        self.bottomHLayout.addWidget(self.splitButton)
        self.bottomHLayout.addWidget(self.makeGifButton)
        self.bottomHLayout.addStretch()

        self.bottomVLayout.addStretch()
        self.bottomVLayout.addLayout(self.bottomHLayout)
        self.bottomVLayout.addStretch()

        self.mainHLayout.addLayout(self.leftHLayout)
        self.mainHLayout.addLayout(self.rightHLayout)

        self.mainVLayout.addLayout(self.mainHLayout)
        self.mainVLayout.addLayout(self.bottomVLayout)

        self.setLayout(self.mainVLayout)

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
