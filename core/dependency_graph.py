from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import math


class TextBox(QtWidgets.QGraphicsSimpleTextItem):
    def __init__(self, is_dir, *args):
        super(TextBox, self).__init__(*args)
        self.is_dir = is_dir

    def paint(self, painter, options, widget):
        bg = QtCore.Qt.lightGray if self.is_dir else QtCore.Qt.gray
        rect = self.boundingRect()
        rect.adjust(-3, -3, 3, 3)
        painter.fillRect(rect, bg)

        super(TextBox, self).paint(painter, options, widget)


class DirectoryViz(QtWidgets.QMainWindow):
    def __init__(self):
        super(DirectoryViz, self).__init__()
        self.setWindowTitle('Graph')
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)
        layout.addWidget(self.view)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.width = 0
        self.items_by_path = {}
        # self.graph_directory_tree()

    def get_max_width(self, source):
        all_items = []
        for root, dirs, files in os.walk(source):
            for d in dirs:
                if not d.startswith('.') and not d.startswith('__'):
                    all_items.append(d)
            for f in files:
                if f.endswith('.py') and '__' not in f:
                    all_items.append(str(os.path.join(root, f)))

        all_names = [item.split('\\')[-1].split('.')[0] for item in all_items]
        sorted_names = sorted(all_names, key=lambda nm: len(nm))
        metrics = QtGui.QFontMetrics(QtGui.QFont())
        longest = metrics.width(sorted_names[-1])

        return longest

    def graph_directory_tree(self, source):
        self.scene.clear()
        row = 0
        column = 0
        self.width = self.get_max_width(source)
        # print self.width
        self.graph_dir(source, row, column)

    def graph_dir(self, path, current_row, current_column):
        this_row = current_row
        this_column = current_column
        for item in sorted(os.listdir(path), key=lambda p: len(p.split('.'))):
            item_path = str(os.path.join(path, item))
            if item.startswith('.') or item.startswith('__'):
                continue
            is_dir = os.path.isdir(item_path)
            if not is_dir:
                if not item.endswith('.py') or '__' in item:
                    continue
            # print item
            text_box = TextBox(is_dir, item)
            text_box.setPos(this_column * self.width, this_row * 25)
            self.scene.addItem(text_box)
            self.items_by_path[item_path] = text_box

            if os.path.isdir(item_path):
                this_row = self.graph_dir(item_path, this_row, this_column + 1)
            else:
                this_row += 1

        return this_row

    def graph_connection(self, source_path, dest_path):
        src = self.items_by_path.get(source_path)
        dest = self.items_by_path.get(dest_path)
        print src, dest
        if not src or not dest:
            return

        src_bound = src.boundingRect()
        src_pos = src.pos() + QtCore.QPointF(src_bound.width(),src_bound.height() * 0.5)
        dest_pos = dest.pos() + QtCore.QPointF(0,dest.boundingRect().height() * 0.5)

        path = QtGui.QPainterPath(src_pos)
        offset = QtCore.QPointF(self.width * 0.5, 0.0)
        path.cubicTo(src_pos+offset, dest_pos - offset,dest_pos)
        path_item = QtWidgets.QGraphicsPathItem(path)
        self.scene.addItem(path_item)

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        oldPos = self.view.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)

        newPos = self.view.mapToScene(event.pos())

        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = DirectoryViz()
    w.show()
    app.exec_()