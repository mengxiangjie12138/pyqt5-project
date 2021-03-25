from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QFileDialog, \
    QVBoxLayout, QHBoxLayout, QComboBox, QTextBrowser, QMessageBox, QToolButton, QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.Qt import Qt

import sys
from os import listdir, makedirs, remove, stat
from os.path import join, exists, isdir, getsize
from shutil import move, copy
from time import ctime

# 打开文件夹窗口后如果不选择直接取消会报错
# 第二次出现弹窗会多控件

image_suffix = ['jpg', 'png', 'jpeg', 'bmp', 'gif']
dir_button_icon = r'icons/dir.png'
target_dir_select_button_icon = r'icons/fast_select.png'


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Fast Image Classifier Tool')
        self.resize(800, 500)

        self.source_dir_label = QLabel('原目录', self)
        self.source_dir_line = QLineEdit(self)
        self.source_dir_button = QToolButton(self)
        self.source_dir_button.setIcon(QIcon(dir_button_icon))
        self.source_dir_button.clicked.connect(self.push_source_dir_button)
        self.image_label = QLabel('', self)
        self.image_box = QComboBox(self)
        self.image_box.currentIndexChanged.connect(self.change_image_box)
        self.target_dir_label = QLabel('目标目录', self)
        self.target_dir_line = QLineEdit(self)
        self.target_dir_button = QToolButton(self)
        self.target_dir_button.setIcon(QIcon(dir_button_icon))
        self.target_dir_button.clicked.connect(self.push_target_dir_button)
        self.target_dir_select_button = QToolButton(self)
        self.target_dir_select_button.setIcon(QIcon(target_dir_select_button_icon))
        self.target_dir_select_button.clicked.connect(self.push_target_dir_select_button)
        self.move_button = QPushButton('移动', self)
        self.move_button.clicked.connect(self.push_move_button)
        self.copy_button = QPushButton('复制', self)
        self.copy_button.clicked.connect(self.push_copy_button)
        self.close_button = QPushButton('关闭', self)
        self.close_button.clicked.connect(self.close)
        self.log_box = QTextBrowser()

        self.under_source_dir_label = QLabel('原目录下文件夹', self)
        self.all_dir_box = QComboBox()
        self.all_dir_box.addItem('')
        self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
        self.all_image_box = QTextBrowser()

        self.contrast_window = QDialog()

        self.grid_layout1 = QGridLayout()
        self.grid_layout2 = QGridLayout()
        self.h_layout1 = QHBoxLayout()
        self.v_layout1 = QVBoxLayout()
        self.v_layout2 = QVBoxLayout()
        self.h_layout2 = QHBoxLayout()
        self.layout()

    def push_source_dir_button(self):
        self.all_dir_box.currentIndexChanged.disconnect(self.change_all_dir_box)
        print('push_source_dir_button:断开右侧目录盒子的链接防止目录被改变')
        dir_path = QFileDialog.getExistingDirectory()
        print('push_source_dir_button:选择了文件夹{}'.format(dir_path))
        self.source_dir_line.setText(dir_path)
        self.image_box.clear()
        self.all_image_box.clear()
        self.all_dir_box.clear()
        self.all_dir_box.addItem('')
        print('push_source_dir_button:初始化几个需要变动的控件')
        flag = 0
        for file_name in listdir(dir_path):
            file_path = join(dir_path, file_name)
            if image_suffix.count(file_name.split('.')[-1]):
                flag += 1
                if flag == 1:
                    self.image_label.setPixmap(QPixmap(file_path))
                self.image_box.addItem(file_name)
                self.all_image_box.append(file_name)
            if isdir(file_path):
                self.all_dir_box.addItem(file_name)
        if len(self.target_dir_line.text()) == 0:
            self.target_dir_line.setText(dir_path + '/')
            print('push_source_dir_button:如果目标目录为空，将原目录填入')
        self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
        print('push_source_dir_button:接续右侧目录盒子的链接')

    def push_target_dir_button(self):
        dir_path = QFileDialog.getExistingDirectory()
        print('push_target_dir_button:成功获取目录{}'.format(dir_path))
        self.target_dir_line.setText(dir_path)

    def push_target_dir_select_button(self):
        target_dir_name = self.all_dir_box.currentText()
        if len(target_dir_name) == 0:
            return
        else:
            target_dir_ = self.target_dir_line.text()
            if target_dir_[-1] == '/':
                target_dir = target_dir_ + target_dir_name
            else:
                target_dir = target_dir_ + '/' + target_dir_name
            self.target_dir_line.setText(target_dir)

    def change_image_box(self):
        source_dir = self.source_dir_line.text()
        image_name = self.image_box.currentText()
        image_path = join(source_dir, image_name)
        self.image_label.setPixmap(QPixmap(image_path))

    def change_all_dir_box(self):
        self.all_image_box.clear()
        source_dir_ = self.source_dir_line.text()
        dir_name = self.all_dir_box.currentText()
        if self.all_dir_box.currentText() == '':
            source_dir = source_dir_
        else:
            source_dir = join(source_dir_, dir_name)
        for file_name in listdir(source_dir):
            if image_suffix.count(str(file_name).split('.')[-1]):
                self.all_image_box.append(file_name)

    def push_move_or_copy_button(self, mode):
        def make_dirs(path):
            dir_list = path.split('/')
            the_dir = dir_list[0]
            if exists(the_dir) is not True:
                makedirs(the_dir)
            for index in range(len(dir_list)):
                if index >= 1:
                    the_dir += '/{}'.format(dir_list[index])
                    if exists(the_dir) is not True:
                        makedirs(the_dir)

        self.all_dir_box.currentIndexChanged.disconnect(self.change_all_dir_box)
        if len(self.source_dir_line.text()) == 0:
            QMessageBox.warning(self, "警告", "原目录为空")
            self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
            return
        if len(self.target_dir_line.text()) == 0:
            QMessageBox.warning(self, '警告', '目标目录为空')
            self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
            return
        source_dir = self.source_dir_line.text()
        target_dir = self.target_dir_line.text()

        if source_dir == target_dir or source_dir == target_dir[:-1]:
            QMessageBox.warning(self, '警告', '原目录与目标目录相同')
            self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
            return

        make_dirs(target_dir)
        image_name = self.image_box.currentText()
        source_path = join(source_dir, image_name)
        target_path = join(target_dir, image_name)
        print('push_move_or_copy_button:成功获取基本信息')

        if mode == 'move':
            if exists(target_path):
                print('push_move_or_copy_button:存在同名文件')
                self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
                self.show_contract_window(mode)
                return
            else:
                move(source_path, target_path)
                print('push_move_or_copy_button:成功移动文件')
        elif mode == 'copy':
            if exists(target_path):
                print('push_move_or_copy_button:存在同名文件')
                self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)
                self.show_contract_window(mode)
                return
            else:
                copy(source_path, target_path)
                print('push_move_or_copy_button:成功复制文件')

        self.image_box.clear()
        self.all_image_box.clear()
        self.all_dir_box.clear()
        self.all_dir_box.addItem('')
        for file_name in listdir(source_dir):
            file_path = join(source_dir, file_name)
            if image_suffix.count(file_name.split('.')[-1]):
                self.image_box.addItem(file_name)
                self.all_image_box.append(file_name)
            if isdir(file_path):
                self.all_dir_box.addItem(file_name)
        if mode == 'move':
            self.log_box.append('成功移动图片{}'.format(image_name))
        elif mode == 'copy':
            self.log_box.append('成功复制图片{}'.format(image_name))
        self.all_dir_box.currentIndexChanged.connect(self.change_all_dir_box)

    def push_move_button(self):
        self.push_move_or_copy_button('move')

    def push_copy_button(self):
        self.push_move_or_copy_button('copy')

    def show_contract_window(self, mode):
        def push_replace_button():
            remove(target_path)
            print('show_contract_window-push_replace_button:删除目标文件，方便后续复制或剪切')
            self.push_move_or_copy_button(mode)
            print('show_contract_window-push_replace_button:删除目标文件后再进行复制或剪切就不会出现文件重名的问题了')
            self.contrast_window.close()

        def layout():
            grid_layout.addWidget(source_file_label, 0, 0, 1, 1)
            grid_layout.addWidget(target_file_label, 0, 1, 1, 1)
            grid_layout.addWidget(source_file_size_label, 1, 0, 1, 1)
            grid_layout.addWidget(target_file_size_label, 1, 1, 1, 1)
            grid_layout.addWidget(source_file_create_time_label, 2, 0, 1, 1)
            grid_layout.addWidget(target_file_create_time_label, 2, 1, 1, 1)
            grid_layout.addWidget(source_file_alter_time_label, 3, 0, 1, 1)
            grid_layout.addWidget(target_file_alter_time_label, 3, 1, 1, 1)
            grid_layout.addWidget(source_image_label, 4, 0, 1, 1)
            grid_layout.addWidget(target_image_label, 4, 1, 1, 1)

            h_layout.addWidget(replace_button)
            h_layout.addWidget(cancel_button)

            v_layout.addLayout(grid_layout)
            v_layout.addLayout(h_layout)
            self.contrast_window.setLayout(v_layout)

        def size_format(size):
            if size < 1000:
                return '%i' % size + 'size'
            elif 1000 <= size < 1000000:
                return '%.2f' % float(size / 1000) + 'KB'
            elif 1000000 <= size < 1000000000:
                return '%.2f' % float(size / 1000000) + 'MB'
            elif 1000000000 <= size < 1000000000000:
                return '%.2f' % float(size / 1000000000) + 'GB'
            elif 1000000000000 <= size:
                return '%.2f' % float(size / 1000000000000) + 'TB'

        def time_format(time_data):
            time_list = time_data.split(' ')
            return "Year:%s / Month:%s / Day:%s / Hour:%s / Min:%s" % (
                time_list[0], time_list[1], time_list[2], time_list[3],
                time_list[4])

        source_dir = self.source_dir_line.text()
        target_dir = self.target_dir_line.text()
        image_name = self.image_box.currentText()
        source_path = join(source_dir, image_name)
        target_path = join(target_dir, image_name)
        source_file_size = getsize(source_path)
        target_file_size = getsize(target_path)
        source_file_create_time = ctime(stat(source_path).st_ctime)
        target_file_create_time = ctime(stat(target_path).st_ctime)
        source_file_alter_time = ctime(stat(source_path).st_mtime)
        target_file_alter_time = ctime(stat(target_path).st_mtime)

        self.contrast_window.setWindowTitle('文件对比窗口')
        source_file_label = QLabel('原文件', self.contrast_window)
        source_image_label = QLabel('', self.contrast_window)
        source_image_label.setPixmap(QPixmap(source_path))
        source_file_size_label = QLabel('文件大小：' + size_format(source_file_size), self.contrast_window)
        source_file_create_time_label = QLabel('创建时间：' + time_format(source_file_create_time), self.contrast_window)
        source_file_alter_time_label = QLabel('修改时间：' + time_format(source_file_alter_time), self.contrast_window)
        target_file_label = QLabel('目标文件', self.contrast_window)
        target_image_label = QLabel('', self.contrast_window)
        target_image_label.setPixmap(QPixmap(target_path))
        target_file_size_label = QLabel('文件大小：' + size_format(target_file_size), self.contrast_window)
        target_file_create_time_label = QLabel('创建时间：' + time_format(target_file_create_time), self.contrast_window)
        target_file_alter_time_label = QLabel('修改时间：' + time_format(target_file_alter_time), self.contrast_window)
        replace_button = QPushButton('替换', self.contrast_window)
        replace_button.clicked.connect(push_replace_button)
        cancel_button = QPushButton('取消', self.contrast_window)
        cancel_button.clicked.connect(self.contrast_window.close)

        grid_layout = QGridLayout()
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        layout()

        self.contrast_window.exec_()

    def layout(self):
        self.grid_layout1.addWidget(self.source_dir_label, 0, 0, 1, 1)
        self.grid_layout1.addWidget(self.source_dir_line, 0, 1, 1, 1)
        self.grid_layout1.addWidget(self.source_dir_button, 0, 2, 1, 1)

        self.grid_layout2.addWidget(self.target_dir_label, 0, 0, 1, 1)
        self.grid_layout2.addWidget(self.target_dir_line, 0, 1, 1, 1)
        self.grid_layout2.addWidget(self.target_dir_button, 0, 2, 1, 1)
        self.grid_layout2.addWidget(self.target_dir_select_button, 0, 3, 1, 1)

        self.h_layout1.addWidget(self.move_button)
        self.h_layout1.addWidget(self.copy_button)
        self.h_layout1.addWidget(self.close_button)

        self.v_layout1.addLayout(self.grid_layout1)
        self.v_layout1.addWidget(self.image_label)
        self.v_layout1.addWidget(self.image_box)
        self.v_layout1.addLayout(self.grid_layout2)
        self.v_layout1.addLayout(self.h_layout1)
        self.v_layout1.addWidget(self.log_box)

        self.v_layout2.addWidget(self.under_source_dir_label)
        self.v_layout2.addWidget(self.all_dir_box)
        self.v_layout2.addWidget(self.all_image_box)

        self.h_layout2.addLayout(self.v_layout1)
        self.h_layout2.addLayout(self.v_layout2)

        self.setLayout(self.h_layout2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())
