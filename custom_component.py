from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QRect, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen


class PaintRectLabel(QLabel):
    x0, y0, x1, y1 = 0, 0, 0, 0
    flag = False
    mouse_release_signal = pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__enable_paint_rect_flag = False

    # 鼠标点击事件
    def mousePressEvent(self, event):
        if self.enable_paint_rect_flag:
            self.flag = True
            self.x0 = event.x()
            self.y0 = event.y()

    @property
    def enable_paint_rect_flag(self):
        return self.__enable_paint_rect_flag

    @enable_paint_rect_flag.setter
    def enable_paint_rect_flag(self, value: bool):
        self.__enable_paint_rect_flag = value

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if self.enable_paint_rect_flag:
            self.flag = False
            self.enable_paint_rect_flag = False
            self.mouse_release_signal.emit((self.x0, self.y0, self.x1, self.y1))

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.enable_paint_rect_flag:
            if self.flag:
                self.x1 = event.x()
                self.y1 = event.y()
                self.update()

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.drawRect(rect)
