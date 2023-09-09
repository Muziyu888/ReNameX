import os
import random
import string
import sys
from PySide6.QtWidgets import QFileDialog, QApplication, QWidget, QMessageBox
from Ui_rename import Ui_Form
from collections import Counter

class rename(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.folder_path = []
        self.file_type = None
        self.file_types = Counter()
        
        self.pushButton_2.clicked.connect(self.fun)
        self.pushButton.clicked.connect(self.choose)
        self.comboBox.currentIndexChanged.connect(self.combo_changed)
        
        self.setAcceptDrops(True)       

    def combo_changed(self):
        current_text = self.comboBox.currentText()
        self.file_type = current_text.split(" ")[0]
        self.settext()
        
    def all_files_type(self): 
        if not self.folder_path or not os.path.exists(self.folder_path):
            self.files = []
            return
        self.file_types.clear()
        for filename in os.listdir(self.folder_path):
            if os.path.isdir(os.path.join(self.folder_path, filename)):
                continue
            ext = os.path.splitext(filename)[-1]
            self.file_types[ext] += 1

        self.comboBox.clear()
        sorted_types = sorted(self.file_types.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types:
            self.comboBox.addItem(f"{ext}   {count} 个")
        total_files = sum(self.file_types.values())
        if len(self.file_types) >= 2:
            self.comboBox.addItem(f"所有文件   {total_files} 个")
          
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        self.folder_path = []
        path = []
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.folder_path = path
        self.settext()
        self.all_files_type()
    
    def choose(self):
        self.folder_path = QFileDialog.getExistingDirectory(None, "选择文件夹", "")
        self.settext()
        self.all_files_type()
    
    def settext(self):
        if not self.folder_path or not os.path.exists(self.folder_path):
            self.files = []
            return
        self.lineEdit.setText(self.folder_path)
        if self.file_type == "所有文件":
            self.files = [i for i in os.listdir(self.folder_path)]
        else:
            self.files = [i for i in os.listdir(self.folder_path) if os.path.splitext(i)[1].lower() == self.file_type] 
          
    def fun(self):
        if not self.files:
            QMessageBox.information(self, "描述", f"请先选择文件夹,并选择正确的文件格式")
            self.choose()
            return  

        msg = QMessageBox()
        msg.setWindowTitle("重要")
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"确认要对这 {len(self.files)} 个 {self.file_type} 文件进行重命名? \n这是一个不可逆的过程,执行后不可撤销.")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.button(QMessageBox.Ok).setText("确定执行") 
        msg.button(QMessageBox.Cancel).setText("取消")

        ret = msg.exec()
        
        if ret != QMessageBox.Ok:
            return

        self.files.sort(key=lambda x: x.lower())  # Sort ignoring case and special characters

        if self.file_type == "所有文件":
            # Group files by their extension and sort them based on the frequency
            files_by_type = {}
            for file in self.files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in files_by_type:
                    files_by_type[ext] = []
                files_by_type[ext].append(file)

            sorted_types = sorted(files_by_type.items(), key=lambda x: len(x[1]), reverse=True)
            self.files = [file for _, files in sorted_types for file in files]

        new_name = 1
        temp_suffix = "_temp_" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        # First round of renaming with temporary names
        for file in self.files:
            ext = os.path.splitext(file)[1]
            new_file = str(new_name) + temp_suffix + ext

            os.rename(os.path.join(self.folder_path, file), os.path.join(self.folder_path, new_file))
            new_name += 1

        # Second round to remove the temporary names
        new_name = 1
        for file in self.files:
            ext = os.path.splitext(file)[1]
            temp_file = str(new_name) + temp_suffix + ext
            final_file = str(new_name) + ext

            os.rename(os.path.join(self.folder_path, temp_file), os.path.join(self.folder_path, final_file))
            new_name += 1

        QMessageBox.information(self, "完成", f"重命名完成,本次批处理 {len(self.files)} 个文件 \n为确保不会误操作,我已清空输入路径,请重新选择")
        # Reset all variables and components
        
        self.folder_path = ''
        self.files = []
        
        self.comboBox.clear()
        self.lineEdit.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    windows = rename()
    windows.show()
    sys.exit(app.exec())