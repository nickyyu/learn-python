import sys
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
                             QLabel, QPushButton, QFrame, QStackedWidget, QComboBox,
                             QFormLayout, QDialog, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt

# --- 数据库操作类 ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("gitflow_master.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 需求主表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                req_num TEXT UNIQUE,
                title TEXT,
                status TEXT,
                dev_branch TEXT,
                uat_branch TEXT,
                pre_branch TEXT
            )
        """)
        # 需求与项目关联表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirement_repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                req_num TEXT,
                repo_name TEXT
            )
        """)
        self.conn.commit()

    def add_requirement(self, data):
        try:
            self.cursor.execute("INSERT INTO requirements (req_num, title, status, dev_branch, uat_branch, pre_branch) VALUES (?,?,?,?,?,?)", data)
            self.conn.commit()
            return True
        except: return False

    def update_requirement(self, req_num, data):
        self.cursor.execute("UPDATE requirements SET title=?, status=?, dev_branch=?, uat_branch=?, pre_branch=? WHERE req_num=?", (*data, req_num))
        self.conn.commit()

    def add_repo_to_req(self, req_num, repo_name):
        self.cursor.execute("INSERT INTO requirement_repos (req_num, repo_name) VALUES (?,?)", (req_num, repo_name))
        self.conn.commit()

# --- 追加项目对话框 ---
class AddRepoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("追加 Git 项目")
        layout = QVBoxLayout(self)
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("输入 Git 项目名称 (例如: user-service)")
        btn = QPushButton("保存关联")
        btn.clicked.connect(self.accept)
        layout.addWidget(QLabel("项目名称:"))
        layout.addWidget(self.repo_input)
        layout.addWidget(btn)

# --- 项目卡片组件 ---
class ProjectCard(QFrame):
    def __init__(self, repo_name, req_info):
        super().__init__()
        self.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 5px; background: white; padding: 10px; }")
        self.setFixedSize(180, 120)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"项目: {repo_name}"))
        
        btn_create = QPushButton("创建分支")
        btn_create.clicked.connect(lambda: QMessageBox.information(self, "Git操作", f"正在校验并创建分支: {req_info['dev_branch']}"))
        
        btn_merge = QPushButton("合并到UAT")
        btn_merge.clicked.connect(lambda: QMessageBox.information(self, "Git操作", f"正在合并至: {req_info['uat_branch']}"))
        
        layout.addWidget(btn_create)
        layout.addWidget(btn_merge)

# --- 主窗口 ---
class GitFlowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("GitFlow Master - 需求与多仓管理")
        self.resize(1100, 800)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)

        # 1. 左侧面板
        self.setup_left_panel()
        # 2. 右侧面板 (StackedWidget 用于切换详情和表单)
        self.right_panel = QStackedWidget()
        self.main_layout.addWidget(self.left_panel, 1)
        self.main_layout.addWidget(self.right_panel, 3)

        self.refresh_req_list()

    def setup_left_panel(self):
        self.left_panel = QWidget()
        layout = QVBoxLayout(self.left_panel)
        
        self.add_btn = QPushButton("+ 添加新需求")
        self.add_btn.clicked.connect(self.show_add_form)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索需求...")
        
        self.req_list = QListWidget()
        self.req_list.itemClicked.connect(self.show_req_detail)
        
        layout.addWidget(self.add_btn)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.req_list)

    def show_add_form(self):
        form_widget = self.create_req_form(is_edit=False)
        self.switch_right_widget(form_widget)

    def create_req_form(self, is_edit=False, data=None):
        form_page = QWidget()
        layout = QVBoxLayout(form_page)
        form = QFormLayout()
        
        num_edit = QLineEdit(data['req_num'] if data else "")
        num_edit.setEnabled(not is_edit) # 编号为主键，编辑时不许改
        title_edit = QLineEdit(data['title'] if data else "")
        status_combo = QComboBox()
        status_combo.addItems(["开发中", "测试中", "上线完成"])
        if data: status_combo.setCurrentText(data['status'])
        
        dev_edit = QLineEdit(data['dev_branch'] if data else "feat/")
        uat_edit = QLineEdit(data['uat_branch'] if data else "test")
        pre_edit = QLineEdit(data['pre_branch'] if data else "release")

        form.addRow("需求编号:", num_edit)
        form.addRow("需求标题:", title_edit)
        form.addRow("需求状态:", status_combo)
        form.addRow("开发分支:", dev_edit)
        form.addRow("UAT分支:", uat_edit)
        form.addRow("PRE分支:", pre_edit)
        
        save_btn = QPushButton("保存到本地")
        save_btn.clicked.connect(lambda: self.save_req(
            [num_edit.text(), title_edit.text(), status_combo.currentText(), dev_edit.text(), uat_edit.text(), pre_edit.text()],
            is_edit
        ))
        
        layout.addLayout(form)
        layout.addWidget(save_btn)
        layout.addStretch()
        return form_page

    def save_req(self, data, is_edit):
        if is_edit:
            self.db.update_requirement(data[0], data[1:])
        else:
            if not self.db.add_requirement(data):
                QMessageBox.warning(self, "错误", "需求编号已存在！")
                return
        self.refresh_req_list()
        self.show_req_detail_by_num(data[0])

    def refresh_req_list(self):
        self.req_list.clear()
        self.db.cursor.execute("SELECT req_num, title FROM requirements")
        for row in self.db.cursor.fetchall():
            item = QListWidgetItem(f"{row[0]} - {row[1]}")
            item.setData(Qt.UserRole, row[0])
            self.req_list.addItem(item)

    def show_req_detail(self, item):
        self.show_req_detail_by_num(item.data(Qt.UserRole))

    def show_req_detail_by_num(self, req_num):
        # 获取需求详情
        self.db.cursor.execute("SELECT * FROM requirements WHERE req_num=?", (req_num,))
        req = self.db.cursor.fetchone()
        keys = ['id', 'req_num', 'title', 'status', 'dev_branch', 'uat_branch', 'pre_branch']
        req_info = dict(zip(keys, req))

        detail_page = QWidget()
        main_vbox = QVBoxLayout(detail_page)

        # 上半部分：详情展示
        upper_frame = QFrame()
        upper_frame.setFrameShape(QFrame.StyledPanel)
        upper_layout = QFormLayout(upper_frame)
        upper_layout.addRow("需求编号:", QLabel(req_info['req_num']))
        upper_layout.addRow("需求标题:", QLabel(req_info['title']))
        upper_layout.addRow("当前状态:", QLabel(req_info['status']))
        upper_layout.addRow("开发分支:", QLabel(req_info['dev_branch']))
        
        edit_btn = QPushButton("修改需求信息")
        edit_btn.clicked.connect(lambda: self.switch_right_widget(self.create_req_form(True, req_info)))
        upper_layout.addWidget(edit_btn)
        
        main_vbox.addWidget(QLabel("### 需求详情"))
        main_vbox.addWidget(upper_frame)

        # 下半部分：项目卡片
        main_vbox.addWidget(QLabel("### 关联项目卡片"))
        scroll = QScrollArea()
        scroll_content = QWidget()
        self.card_layout = QHBoxLayout(scroll_content)
        
        # 加载项目卡片
        self.db.cursor.execute("SELECT repo_name FROM requirement_repos WHERE req_num=?", (req_num,))
        for r in self.db.cursor.fetchall():
            self.card_layout.addWidget(ProjectCard(r[0], req_info))
            
        add_repo_btn = QPushButton("+ 追加项目")
        add_repo_btn.setFixedSize(100, 100)
        add_repo_btn.clicked.connect(lambda: self.append_repo(req_num))
        self.card_layout.addWidget(add_repo_btn)
        self.card_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        main_vbox.addWidget(scroll)
        
        self.switch_right_widget(detail_page)

    def append_repo(self, req_num):
        dialog = AddRepoDialog(self)
        if dialog.exec():
            repo_name = dialog.repo_input.text()
            if repo_name:
                self.db.add_repo_to_req(req_num, repo_name)
                self.show_req_detail_by_num(req_num)

    def switch_right_widget(self, widget):
        if self.right_panel.count() > 0:
            current = self.right_panel.currentWidget()
            self.right_panel.removeWidget(current)
        self.right_panel.addWidget(widget)
        self.right_panel.setCurrentWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitFlowApp()
    window.show()
    sys.exit(app.exec())