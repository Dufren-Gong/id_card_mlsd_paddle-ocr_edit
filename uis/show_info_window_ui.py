from PyQt6 import QtWidgets, QtCore
    
class Row_One():
    def __init__(self,
                 centralwidget,
                 tip_label_shape: tuple,
                 exit_button_shape: tuple,
                 ) -> None:
        self.centralwidget = centralwidget
        self.init_one_tip_label(tip_label_shape)
        self.init_one_column_three_exit_pushbutton(exit_button_shape)

    def init_one_tip_label(self, shape):
        self.tip_label = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.tip_label.setGeometry(QtCore.QRect(*shape))
        self.tip_label.setObjectName("tip_label")
        # 设置 QLabel 文本可以通过鼠标选择
        self.tip_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

    def init_one_column_three_exit_pushbutton(self, shape):
        self.exit_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.exit_button.setGeometry(QtCore.QRect(*shape))
        self.exit_button.setObjectName("exit_button")
        self.exit_button.setText("好的")
        self.exit_button.setStyleSheet("""
            QPushButton {
                border-width: 1px;          /* 边缘宽度 */
                border-style: solid;        /* 边缘样式 */
                border-color: black;          /* 边缘颜色 */
                background-color: lightgray;/* 背景颜色 */
            }
        """)
