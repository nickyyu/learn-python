from PySide6.QtWidgets import QFormLayout, QDateEdit
from PySide6.QtCore import QDate

class ReqEditDialog(QDialog):
    def __init__(self, db, data=None):
        super().__init__()
        self.db = db
        self.original_data = data  # 如果 data 不为空，则是修改模式
        self.setWindowTitle("编辑需求" if data else "新增需求")
        self.setMinimumWidth(450)
        self.init_ui()
        
        if data:
            self.fill_data(data)

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 输入控件
        self.edit_id = QLineEdit()
        if self.original_data: self.edit_id.setEnabled(False) # 修改时主键通常不许变
        
        self.edit_title = QLineEdit()
        self.edit_status = QComboBox()
        self.edit_status.addItems(["待处理", "进行中", "已完成", "已发布"])
        
        # 使用 QDateEdit 优化日期输入
        self.edit_dev_time = QDateEdit(calendarPopup=True)
        self.edit_dev_time.setDate(QDate.currentDate())
        self.edit_uat_time = QDateEdit(calendarPopup=True)
        self.edit_online_time = QDateEdit(calendarPopup=True)
        
        self.edit_uat_branch = QLineEdit()
        self.edit_pre_branch = QLineEdit()

        form_layout.addRow("需求编号 *:", self.edit_id)
        form_layout.addRow("标题 *:", self.edit_title)
        form_layout.addRow("当前状态:", self.edit_status)
        form_layout.addRow("开发完成时间:", self.edit_dev_time)
        form_layout.addRow("UAT完成时间:", self.edit_uat_time)
        form_layout.addRow("上线时间:", self.edit_online_time)
        form_layout.addRow("UAT测试分支:", self.edit_uat_branch)
        form_layout.addRow("PRE测试分支:", self.edit_pre_branch)

        layout.addLayout(form_layout)

        btn_save = QPushButton("提交保存")
        btn_save.setStyleSheet("background-color: #28a745; color: white; height: 35px;")
        btn_save.clicked.connect(self.save_data)
        layout.addWidget(btn_save)

    def fill_data(self, data):
        """如果是修改模式，将现有数据填入表单"""
        # 注意：data 的索引取决于你数据库 SELECT 的顺序
        self.edit_id.setText(data[0])
        self.edit_title.setText(data[1])
        self.edit_status.setCurrentText(data[2])
        # 将文本日期转为 QDate
        if data[3]: self.edit_dev_time.setDate(QDate.fromString(data[3], "yyyy-MM-dd"))
        if data[4]: self.edit_uat_time.setDate(QDate.fromString(data[4], "yyyy-MM-dd"))
        if data[5]: self.edit_online_time.setDate(QDate.fromString(data[5], "yyyy-MM-dd"))
        self.edit_uat_branch.setText(data[6])
        self.edit_pre_branch.setText(data[7])

    def save_data(self):
        # 组装数据
        fields = (
            self.edit_title.text(),
            self.edit_status.currentText(),
            self.edit_dev_time.date().toString("yyyy-MM-dd"),
            self.edit_uat_time.date().toString("yyyy-MM-dd"),
            self.edit_online_time.date().toString("yyyy-MM-dd"),
            self.edit_uat_branch.text(),
            self.edit_pre_branch.text(),
            self.edit_id.text() # 作为 WHERE 条件的 ID 放在最后
        )

        cursor = self.db.conn.cursor()
        try:
            if self.original_data:
                # 执行修改
                sql = '''UPDATE requirements SET 
                         title=?, status=?, dev_time=?, uat_time=?, online_time=?, uat_branch=?, pre_branch=? 
                         WHERE req_id=?'''
                cursor.execute(sql, fields)
            else:
                # 执行新增 (这里需要重新排下序，因为 INSERT 的顺序和 UPDATE 不同)
                sql = '''INSERT INTO requirements 
                         (title, status, dev_time, uat_time, online_time, uat_branch, pre_branch, req_id) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                cursor.execute(sql, fields)
            
            self.db.conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))
			
			
# 在 MainWindow 的 init_ui 中添加
self.table.itemDoubleClicked.connect(self.on_table_double_clicked)

def on_table_double_clicked(self, item):
    # 1. 获取双击那一行的需求编号 (假设第一列是编号)
    row = item.row()
    req_id = self.table.item(row, 0).text()
    
    # 2. 从数据库获取详情
    full_data = self.db.get_req_detail(req_id)
    
    # 3. 弹出对话框（传入数据即为修改模式）
    if full_data:
        dialog = ReqEditDialog(self.db, data=full_data)
        if dialog.exec() == QDialog.Accepted:
            self.load_table_data() # 刷新主表