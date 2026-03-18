import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
                             QLabel, QPushButton, QFrame, QScrollArea, QStackedWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

# --- 样式表：美化界面 ---
STYLE_SHEET = """
QMainWindow { background-color: #f5f5f5; }
QLineEdit { padding: 8px; border: 1px solid #ccc; border-radius: 4px; background: white; }
QListWidget { border: none; background-color: #ffffff; border-right: 1px solid #ddd; }
QListWidget::item { padding: 15px; border-bottom: 1px solid #eee; }
QListWidget::item:selected { background-color: #e3f2fd; color: #1976d2; border-left: 4px solid #1976d2; }
.Card { background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 10px; }
.Title { font-size: 18px; font-weight: bold; color: #333; }
.Branch { color: #666; font-family: 'Consolas'; background: #eee; padding: 2px; }
"""

class ProjectCard(QFrame):
    """项目卡片：显示单个 Repo 的状态"""
    def __init__(self, repo_name, status="Clean"):
        super().__init__()
        self.setObjectName("Card")
        self.setProperty("class", "Card")
        layout = QVBoxLayout(self)
        
        name_label = QLabel(repo_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        status_label = QLabel(f"状态: {status}")
        status_label.setStyleSheet(f"color: {'green' if status == 'Clean' else 'orange'};")
        
        btn_push = QPushButton("Push")
        btn_merge = QPushButton("提测")
        
        layout.addWidget(name_label)
        layout.addWidget(status_label)
        layout.addStretch()
        layout.addWidget(btn_push)
        layout.addWidget(btn_merge)
        self.setFixedSize(160, 140)

class RequirementDetail(QWidget):
    """右侧详情页"""
    def __init__(self, req_data):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # 头部信息
        title = QLabel(f"需求: {req_data['title']}")
        title.setProperty("class", "Title")
        branch = QLabel(f"统一分支: {req_data['branch']}")
        branch.setProperty("class", "Branch")
        
        layout.addWidget(title)
        layout.addWidget(branch)
        layout.addSpacing(20)
        
        # 项目展示区（流式布局模拟）
        layout.addWidget(QLabel("关联项目："))
        self.repo_layout = QHBoxLayout()
        for repo in req_data['repos']:
            self.repo_layout.addWidget(ProjectCard(repo))
        
        # 追加项目按钮
        add_btn = QPushButton("+ 追加项目")
        add_btn.setFixedSize(100, 100)
        add_btn.setStyleSheet("border: 2px dashed #ccc; background: transparent;")
        self.repo_layout.addWidget(add_btn)
        self.repo_layout.addStretch()
        
        repo_container = QWidget()
        repo_container.setLayout(self.repo_layout)
        layout.addWidget(repo_container)
        
        # 底部全局操作
        layout.addStretch()
        op_layout = QHBoxLayout()
        batch_push = QPushButton("一键全量推送")
        batch_push.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        batch_merge = QPushButton("一键合并至测试分支")
        batch_merge.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        
        op_layout.addWidget(batch_push)
        op_layout.addWidget(batch_merge)
        layout.addLayout(op_layout)

class GitFlowMaster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitFlow Master - 多仓协同控制台")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET)
        
        # 模拟数据
        self.data = [
            {"id": "REQ-101", "title": "登录指纹优化", "branch": "feat/login-fix", "repos": ["Auth-Server", "User-Web"]},
            {"id": "REQ-102", "title": "支付接口对接", "branch": "feat/pay-api", "repos": ["Payment-Service"]},
            {"id": "REQ-103", "title": "数据库迁移逻辑", "branch": "feat/db-migration", "repos": ["Data-Core", "Admin-CLI"]},
        ]

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- 左侧：搜索与列表 ---
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("?? 搜索需求 ID 或关键字...")
        self.search_bar.textChanged.connect(self.filter_list)
        
        self.req_list = QListWidget()
        for item in self.data:
            list_item = QListWidgetItem(f"{item['id']}\n{item['title']}")
            list_item.setData(Qt.UserRole, item) # 绑定原始数据
            self.req_list.addItem(list_item)
            
        self.req_list.itemClicked.connect(self.display_detail)
        
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.req_list)
        
        # --- 右侧：详情展示区 ---
        self.detail_stack = QStackedWidget()
        empty_label = QLabel("请在左侧选择一个需求开始工作")
        empty_label.setAlignment(Qt.AlignCenter)
        self.detail_stack.addWidget(empty_label)

        layout.addWidget(left_panel)
        layout.addWidget(self.detail_stack)

    def filter_list(self, text):
        """简单的列表过滤逻辑"""
        for i in range(self.req_list.count()):
            item = self.req_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def display_detail(self, list_item):
        """切换右侧显示的内容"""
        req_data = list_item.data(Qt.UserRole)
        detail_view = RequirementDetail(req_data)
        
        # 移除旧视图并添加新视图
        if self.detail_stack.count() > 1:
            old_widget = self.detail_stack.widget(1)
            self.detail_stack.removeWidget(old_widget)
            
        self.detail_stack.addWidget(detail_view)
        self.detail_stack.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitFlowMaster()
    window.show()
    sys.exit(app.exec())