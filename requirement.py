import sys
import sqlite3
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QDialog, QMessageBox, QInputDialog, QAbstractItemView)
from PySide6.QtCore import Qt

# ================= 数据库管理模块 =================
class DBManager:
    def __init__(self, db_name="req_management.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # 需求主表
        cursor.execute('''CREATE TABLE IF NOT EXISTS requirements (
                            req_id TEXT PRIMARY KEY,
                            title TEXT,
                            status TEXT)''')
        # 项目关联表
        cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            req_id TEXT,
                            project_name TEXT,
                            FOREIGN KEY(req_id) REFERENCES requirements(req_id))''')
        
        # 插入测试数据（如果表为空）
        cursor.execute("SELECT count(*) FROM requirements")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO requirements VALUES ('REQ-001', '自动化发布系统', '进行中')")
            cursor.execute("INSERT INTO requirements VALUES ('REQ-002', '数据看板优化', '待处理')")
            cursor.execute("INSERT INTO projects (req_id, project_name) VALUES ('REQ-001', 'Web-Portal')")
        self.conn.commit()

    def query_reqs(self, req_id="", status="全部"):
        cursor = self.conn.cursor()
        sql = "SELECT * FROM requirements WHERE 1=1"
        params = []
        if req_id:
            sql += " AND req_id LIKE ?"
            params.append(f"%{req_id}%")
        if status != "全部":
            sql += " AND status = ?"
            params.append(status)
        cursor.execute(sql, params)
        return cursor.fetchall()

    def get_projects(self, req_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT project_name FROM projects WHERE req_id = ?", (req_id,))
        return [row[0] for row in cursor.fetchall()]

    def add_project(self, req_id, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO projects (req_id, project_name) VALUES (?, ?)", (req_id, name))
        self.conn.commit()

    def del_project(self, req_id, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE req_id = ? AND project_name = ?", (req_id, name))
        self.conn.commit()

# ================= 弹窗模块 =================

# 1. 应用管理：新增/删除项目
class AppManageDialog(QDialog):
    def __init__(self, req_id, db):
        super().__init__()
        self.req_id, self.db = req_id, db
        self.setWindowTitle(f"应用管理 - {req_id}")
        self.resize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["项目名称", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        btn_add = QPushButton("+ 新增关联项目")
        btn_add.clicked.connect(self.add_item)
        
        layout.addWidget(btn_add)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        projs = self.db.get_projects(self.req_id)
        self.table.setRowCount(len(projs))
        for i, name in enumerate(projs):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            btn_del = QPushButton("删除")
            btn_del.setStyleSheet("color: red;")
            btn_del.clicked.connect(lambda ch=False, n=name: self.delete_item(n))
            self.table.setCellWidget(i, 1, btn_del)

    def add_item(self):
        name, ok = QInputDialog.getText(self, "新增项目", "请输入项目代码库名称:")
        if ok and name:
            self.db.add_project(self.req_id, name)
            self.refresh()

    def delete_item(self, name):
        if QMessageBox.question(self, "确认", f"确定删除项目 {name} 吗？") == QMessageBox.Yes:
            self.db.del_project(self.req_id, name)
            self.refresh()

# 2. 分支管理：Git操作模拟
class BranchManageDialog(QDialog):
    def __init__(self, req_id, db):
        super().__init__()
        self.req_id, self.db = req_id, db
        self.setWindowTitle(f"分支管理 - {req_id}")
        self.resize(600, 350)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["项目", "创建分支", "合并分支"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        projs = self.db.get_projects(self.req_id)
        self.table.setRowCount(len(projs))
        for i, name in enumerate(projs):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            b1, b2 = QPushButton("创建"), QPushButton("合并")
            b1.clicked.connect(lambda ch=False, n=name: self.op(n, "创建"))
            b2.clicked.connect(lambda ch=False, n=name: self.op(n, "合并"))
            self.table.setCellWidget(i, 1, b1)
            self.table.setCellWidget(i, 2, b2)

    def op(self, proj, type):
        branch, ok = QInputDialog.getText(self, f"{type}分支", f"项目 {proj}\n请输入分支名:")
        if ok: QMessageBox.information(self, "成功", f"已提交 Git {type} 指令: {branch}")

# 3. 发布管理：Jenkins构建
class PublishManageDialog(QDialog):
    def __init__(self, req_id, db):
        super().__init__()
        self.req_id, self.db = req_id, db
        self.setWindowTitle(f"发布管理 - {req_id}")
        self.resize(500, 300)
        layout = QVBoxLayout(self)
        
        self.env_box = QComboBox()
        self.env_box.addItems(["DEV", "SIT", "UAT", "PROD"])
        
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["项目", "Jenkins 构建"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(QLabel("选择目标环境:"))
        layout.addWidget(self.env_box)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        projs = self.db.get_projects(self.req_id)
        self.table.setRowCount(len(projs))
        for i, name in enumerate(projs):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            btn = QPushButton("?? 发起构建")
            btn.clicked.connect(lambda ch=False, n=name: self.build(n))
            self.table.setCellWidget(i, 1, btn)

    def build(self, proj):
        env = self.env_box.currentText()
        QMessageBox.information(self, "Jenkins", f"项目: {proj}\n环境: {env}\n状态: 构建队列已进入")

# ================= 主界面 =================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.setWindowTitle("内网需求研发管理平台")
        self.resize(1100, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 上半部：查询区
        search_frame = QFrame()
        search_frame.setFrameShape(QFrame.StyledPanel)
        search_layout = QHBoxLayout(search_frame)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("需求编号...")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "待处理", "进行中", "已完成", "已发布"])
        
        btn_search = QPushButton("查询")
        btn_search.setStyleSheet("background-color: #0078D4; color: white;")
        btn_search.clicked.connect(self.load_table_data)

        search_layout.addWidget(QLabel("编号:"))
        search_layout.addWidget(self.id_input)
        search_layout.addWidget(QLabel("状态:"))
        search_layout.addWidget(self.status_combo)
        search_layout.addWidget(btn_search)
        search_layout.addStretch()

        # 下半部：表格区
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["需求编号", "标题", "状态", "操作管理"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(search_frame)
        main_layout.addWidget(self.table)
        
        self.load_table_data()

    def load_table_data(self):
        data = self.db.query_reqs(self.id_input.text(), self.status_combo.currentText())
        self.table.setRowCount(len(data))
        for row, (rid, title, status) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(rid))
            self.table.setItem(row, 1, QTableWidgetItem(title))
            self.table.setItem(row, 2, QTableWidgetItem(status))
            self.table.setCellWidget(row, 3, self.create_ops(rid))

    def create_ops(self, rid):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(2, 2, 2, 2)
        
        b1, b2, b3 = QPushButton("应用"), QPushButton("分支"), QPushButton("发布")
        b1.clicked.connect(lambda: AppManageDialog(rid, self.db).exec())
        b2.clicked.connect(lambda: BranchManageDialog(rid, self.db).exec())
        b3.clicked.connect(lambda: PublishManageDialog(rid, self.db).exec())
        
        for b in [b1, b2, b3]: l.addWidget(b)
        return w

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置全局样式
    app.setStyleSheet("QPushButton { min-height: 25px; } QTableWidget { font-size: 13px; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())