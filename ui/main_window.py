#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
包含菜单系统和页面切换功能
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QPushButton, QLabel, QFrame,
                             QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from .home_page import HomePage
from .settings_page import SettingsPage, ModernQuestionBox
from database.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PCAP播放器 v1.0.0")
        self.setMinimumSize(800, 600)
        
        # 设置窗口大小并居中显示
        self.resize(1200, 800)
        self.center_window()
        
        # 设置窗口图标
        self.setWindowIcon(QIcon("resources/ico/pcap.ico"))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建侧边栏
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # 创建页面容器
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 创建页面
        self.home_page = HomePage(self.db_manager)
        self.settings_page = SettingsPage(self.db_manager)
        
        # 添加页面到容器
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        # 连接信号
        self.settings_page.settings_changed.connect(self.home_page.refresh_folder_list)
        
        # 默认显示首页
        self.show_home_page()
        
        # 设置样式
        self.set_styles()
        
    def create_sidebar(self):
        """创建侧边栏"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # 应用标题
        title_label = QLabel("📡 PCAP播放器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 10px;
                background-color: #e9ecef;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        sidebar_layout.addWidget(title_label)
        
        # 添加一些间距
        sidebar_layout.addSpacing(10)
        
        # 菜单按钮
        self.home_btn = QPushButton("🏠 首页")
        self.home_btn.setCheckable(True)
        self.home_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                color: #495057;
                font-size: 14px;
                font-weight: 500;
                margin: 2px 0;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:checked {
                background-color: #007bff;
                color: white;
            }
        """)
        self.home_btn.clicked.connect(self.show_home_page)
        sidebar_layout.addWidget(self.home_btn)
        
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                color: #495057;
                font-size: 14px;
                font-weight: 500;
                margin: 2px 0;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:checked {
                background-color: #007bff;
                color: white;
            }
        """)
        self.settings_btn.clicked.connect(self.show_settings_page)
        sidebar_layout.addWidget(self.settings_btn)
        
        # 弹性空间
        sidebar_layout.addStretch()
        
        # 版本信息
        version_label = QLabel("📋 版本 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                padding: 10px;
                background-color: #e9ecef;
                border-radius: 6px;
                margin-top: 10px;
            }
        """)
        sidebar_layout.addWidget(version_label)
        
    def show_home_page(self):
        """显示首页"""
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.home_btn.setChecked(True)
        self.settings_btn.setChecked(False)
        
    def show_settings_page(self):
        """显示设置页面"""
        self.stacked_widget.setCurrentWidget(self.settings_page)
        self.home_btn.setChecked(False)
        self.settings_btn.setChecked(True)
        
    def set_styles(self):
        """设置样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
        
    def center_window(self):
        """将窗口居中显示"""
        # 获取屏幕几何信息
        screen = QApplication.desktop().screenGeometry()
        # 获取窗口几何信息
        window = self.geometry()
        # 计算居中位置
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        # 移动窗口到居中位置
        self.move(x, y)
        
    def closeEvent(self, event):
        """关闭事件"""
        dialog = ModernQuestionBox(self, '确认退出', '确定要退出PCAP播放器吗？')
        reply = dialog.exec_()
        
        if reply == dialog.Accepted:
            event.accept()
        else:
            event.ignore()