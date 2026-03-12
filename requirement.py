/* ================================
   全局字体
================================ */

* {
    font-family: "Microsoft YaHei";
    font-size: 14px;
}


/* ================================
   主窗口
================================ */

QMainWindow {
    background-color: #f5f7fa;
}


/* ================================
   按钮
================================ */

QPushButton {
    background-color: #409EFF;
    color: white;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #66b1ff;
}

QPushButton:pressed {
    background-color: #3a8ee6;
}

QPushButton:disabled {
    background-color: #c0c4cc;
}


/* 次要按钮 */

QPushButton#secondary {
    background-color: white;
    color: #606266;
    border: 1px solid #dcdfe6;
}

QPushButton#secondary:hover {
    background-color: #ecf5ff;
    color: #409EFF;
}


/* 危险按钮 */

QPushButton#danger {
    background-color: #f56c6c;
}

QPushButton#danger:hover {
    background-color: #f78989;
}


/* ================================
   输入框
================================ */

QLineEdit {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 5px 8px;
    min-height: 28px;
    background: white;
}

QLineEdit:focus {
    border: 1px solid #409EFF;
}


/* ================================
   下拉框
================================ */

QComboBox {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 28px;
    background: white;
}

QComboBox:hover {
    border: 1px solid #409EFF;
}

QComboBox::drop-down {
    border: none;
}


/* ================================
   表格
================================ */

QTableWidget {
    border: 1px solid #ebeef5;
    background: white;
    gridline-color: #ebeef5;
    selection-background-color: #ecf5ff;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #ecf5ff;
    color: #303133;
}


/* ================================
   表头
================================ */

QHeaderView::section {
    background-color: #f5f7fa;
    border: none;
    border-bottom: 1px solid #ebeef5;
    padding: 6px;
    font-weight: bold;
}


/* ================================
   Tab
================================ */

QTabWidget::pane {
    border: 1px solid #dcdfe6;
}

QTabBar::tab {
    background: #f5f7fa;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background: white;
    border-bottom: 2px solid #409EFF;
}


/* ================================
   ScrollBar
================================ */

QScrollBar:vertical {
    border: none;
    background: #f0f0f0;
    width: 8px;
}

QScrollBar::handle:vertical {
    background: #c0c4cc;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #909399;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}


/* ================================
   分组框
================================ */

QGroupBox {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    margin-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px;
}


/* ================================
   ToolBar
================================ */

QToolBar {
    background: white;
    border-bottom: 1px solid #ebeef5;
}


/* ================================
   菜单
================================ */

QMenuBar {
    background: white;
}

QMenuBar::item:selected {
    background: #ecf5ff;
}

QMenu {
    background: white;
    border: 1px solid #ebeef5;
}

QMenu::item:selected {
    background: #ecf5ff;
}