from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新需求")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("例如：实现登录接口同步")
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("简述该需求的内容...")

        form.addRow("需求标题:", self.title_input)
        form.addRow("需求描述:", self.desc_input)
        
        layout.addLayout(form)

        # 添加标准按钮 (确定/取消)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) # 点击Ok关闭窗口并返回Accepted
        self.buttons.rejected.connect(self.reject) # 点击Cancel关闭窗口并返回Rejected
        layout.addWidget(self.buttons)

    def get_data(self):
        """返回用户输入的数据"""
        return {
            "title": self.title_input.text().strip(),
            "desc": self.desc_input.toPlainText().strip()
        }
		

		
def add_task(self, title, desc):
        """将新需求写入 SQLite 数据库"""
        if not title:
            return None
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (title, desc, status) VALUES (?, ?, ?)",
                (title, desc, "Open")
            )
            conn.commit()
            return cursor.lastrowid # 返回新插入行的 ID
			
			
			
@Slot()
    def on_add_task_clicked(self):
        """弹出对话框并保存数据"""
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['title']:
                QMessageBox.warning(self, "错误", "需求标题不能为空！")
                return

            # 1. 写入数据库
            new_id = self.db.add_task(data['title'], data['desc'])
            
            if new_id:
                # 2. 实时刷新左侧列表，无需重启软件
                self.refresh_task_list()
                QMessageBox.information(self, "成功", "需求已添加！")

    def refresh_task_list(self):
        """重新从数据库加载任务列表"""
        self.task_list.clear() # 清空 UI
        tasks = self.db.get_all_tasks() # 重新查询
        for task in tasks:
            item = QListWidgetItem(task['title'])
            item.setData(Qt.UserRole, task['id']) # 存入 ID
            self.task_list.addItem(item)