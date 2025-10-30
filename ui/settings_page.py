#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置页面
配置目标文件夹、网络接口和源IP地址
"""

import os
import psutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QComboBox, QLabel, 
                             QFileDialog, QMessageBox, QGroupBox, QTextEdit,
                             QFrame, QSpacerItem, QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ModernMessageBox(QDialog):
    """现代化的消息框"""
    
    def __init__(self, parent, title, message, msg_type="info"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.init_ui(title, message, msg_type)
        
    def init_ui(self, title, message, msg_type):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        # 图标和标题
        title_layout = QHBoxLayout()
        
        # 根据消息类型选择图标和颜色
        if msg_type == "success":
            icon = "✅"
            color = "#28a745"
        elif msg_type == "error":
            icon = "❌"
            color = "#dc3545"
        elif msg_type == "warning":
            icon = "⚠️"
            color = "#ffc107"
        else:
            icon = "ℹ️"
            color = "#17a2b8"
            
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                color: {color};
                margin-right: 10px;
            }}
        """)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {color};
            }}
        """)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 消息内容
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #495057;
                line-height: 1.5;
                padding: 10px 0;
            }
        """)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
        ok_button.clicked.connect(self.accept)
        
        button_layout.addWidget(ok_button)
        
        layout.addLayout(title_layout)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


class ModernQuestionBox(QDialog):
    """现代化的确认对话框"""
    
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(450, 220)
        self.result = False
        self.init_ui(title, message)
        
    def init_ui(self, title, message):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        # 图标和标题
        title_layout = QHBoxLayout()
        
        icon_label = QLabel("❓")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #ffc107;
                margin-right: 10px;
            }
        """)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #ffc107;
            }
        """)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 消息内容
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #495057;
                line-height: 1.5;
                padding: 10px 0;
            }
        """)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
                min-width: 80px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        confirm_button = QPushButton("确定")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(title_layout)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

from database.db_manager import DatabaseManager

class SettingsPage(QWidget):
    """设置页面类"""
    
    settings_changed = pyqtSignal()  # 设置改变信号
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置页面背景
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("⚙️ 系统设置")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                font-weight: 700; 
                color: #343a40;
                margin: 20px 0;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid #007bff;
            }
        """)
        layout.addWidget(title_label)
        
        # 目标文件夹设置
        folder_group = QGroupBox("📁 目标文件夹设置")
        folder_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)
        folder_layout = QFormLayout(folder_group)
        
        # 目标文件夹
        folder_row_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("请选择包含PCAP文件的文件夹")
        self.folder_path_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: white;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #ced4da;
            }
        """)
        folder_row_layout.addWidget(self.folder_path_edit)
        
        self.browse_folder_btn = QPushButton("📂 浏览")
        self.browse_folder_btn.clicked.connect(self.browse_folder)
        self.browse_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        folder_row_layout.addWidget(self.browse_folder_btn)
        
        folder_layout.addRow("目标文件夹:", folder_row_layout)
        
        # 文件夹说明
        folder_info = QLabel("选择包含测试用例文件夹的根目录，每个子文件夹代表一个测试用例")
        folder_info.setStyleSheet("color: #666; font-size: 12px;")
        folder_info.setWordWrap(True)
        folder_layout.addRow("", folder_info)
        
        layout.addWidget(folder_group)
        
        # 网络设置组
        network_group = QGroupBox("🌐 网络接口设置")
        network_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)
        network_layout = QFormLayout(network_group)
        
        # 网络接口选择
        interface_row_layout = QHBoxLayout()
        self.interface_combo = QComboBox()
        self.interface_combo.setMinimumWidth(300)
        self.interface_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                color: #495057;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #007bff;
            }
            QComboBox:hover {
                border-color: #ced4da;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
                margin-right: 5px;
            }
        """)
        interface_row_layout.addWidget(self.interface_combo)
        
        self.refresh_interfaces_btn = QPushButton("🔄 刷新")
        self.refresh_interfaces_btn.clicked.connect(self.refresh_network_interfaces)
        self.refresh_interfaces_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        interface_row_layout.addWidget(self.refresh_interfaces_btn)
        
        interface_row_layout.addStretch()
        
        network_layout.addRow("网络接口:", interface_row_layout)
        
        # 源IP地址
        self.source_ip_edit = QLineEdit()
        self.source_ip_edit.setPlaceholderText("可选，留空使用接口默认IP")
        self.source_ip_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: white;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #ced4da;
            }
        """)
        network_layout.addRow("源IP地址:", self.source_ip_edit)
        
        # 目的IP地址
        self.dest_ip_edit = QLineEdit()
        self.dest_ip_edit.setPlaceholderText("可选，留空保持原始目的IP")
        self.dest_ip_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: white;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #ced4da;
            }
        """)
        network_layout.addRow("目的IP地址:", self.dest_ip_edit)
        
        # 网络说明
        network_info = QLabel("选择用于发送数据包的网络接口，源IP和目的IP地址可选择性设置")
        network_info.setStyleSheet("color: #666; font-size: 12px;")
        network_info.setWordWrap(True)
        network_layout.addRow("", network_info)
        
        layout.addWidget(network_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.reset_settings)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 初始化网络接口列表
        self.refresh_network_interfaces()
        
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择目标文件夹", 
            self.folder_path_edit.text() or os.path.expanduser("~")
        )
        
        if folder:
            self.folder_path_edit.setText(folder)
            
    def refresh_network_interfaces(self):
        """刷新网络接口列表"""
        self.interface_combo.clear()
        
        try:
            # 获取网络接口信息
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                # 跳过回环接口
                if interface_name.lower().startswith('lo'):
                    continue
                    
                # 检查接口是否启用
                if interface_name in stats and not stats[interface_name].isup:
                    continue
                    
                # 查找IPv4地址
                ipv4_addr = None
                for addr in addresses:
                    if addr.family == 2:  # AF_INET (IPv4)
                        ipv4_addr = addr.address
                        break
                        
                if ipv4_addr:
                    display_text = f"{interface_name} ({ipv4_addr})"
                    self.interface_combo.addItem(display_text, interface_name)
                    
        except Exception as e:
            dialog = ModernMessageBox(self, "警告", f"获取网络接口失败: {str(e)}", "warning")
            dialog.exec_()
            
    def load_settings(self):
        """加载设置"""
        # 加载文件夹路径
        folder_path = self.db_manager.get_setting('target_folder')
        if folder_path:
            self.folder_path_edit.setText(folder_path)
            
        # 加载网络接口
        network_interface = self.db_manager.get_setting('network_interface')
        if network_interface:
            # 查找匹配的接口
            for i in range(self.interface_combo.count()):
                if self.interface_combo.itemData(i) == network_interface:
                    self.interface_combo.setCurrentIndex(i)
                    break
                    
        # 加载源IP
        source_ip = self.db_manager.get_setting('source_ip')
        if source_ip:
            self.source_ip_edit.setText(source_ip)
            
        # 加载目的IP
        dest_ip = self.db_manager.get_setting('dest_ip')
        if dest_ip:
            self.dest_ip_edit.setText(dest_ip)
            
    def save_settings(self):
        """保存设置"""
        try:
            # 验证文件夹路径
            folder_path = self.folder_path_edit.text().strip()
            if folder_path and not os.path.exists(folder_path):
                dialog = ModernMessageBox(self, "警告", "指定的文件夹路径不存在", "warning")
                dialog.exec_()
                return
                
            # 验证源IP地址格式（如果提供）
            source_ip = self.source_ip_edit.text().strip()
            if source_ip:
                import ipaddress
                try:
                    ipaddress.IPv4Address(source_ip)
                except ipaddress.AddressValueError:
                    dialog = ModernMessageBox(self, "警告", "源IP地址格式不正确", "warning")
                    dialog.exec_()
                    return
                    
            # 验证目的IP地址格式（如果提供）
            dest_ip = self.dest_ip_edit.text().strip()
            if dest_ip:
                import ipaddress
                try:
                    ipaddress.IPv4Address(dest_ip)
                except ipaddress.AddressValueError:
                    dialog = ModernMessageBox(self, "警告", "目的IP地址格式不正确", "warning")
                    dialog.exec_()
                    return
                    
            # 保存设置
            self.db_manager.set_setting('target_folder', folder_path)
            
            current_interface = self.interface_combo.currentData()
            if current_interface:
                self.db_manager.set_setting('network_interface', current_interface)
                
            self.db_manager.set_setting('source_ip', source_ip)
            self.db_manager.set_setting('dest_ip', dest_ip)
            
            # 发送设置改变信号
            self.settings_changed.emit()
            
            dialog = ModernMessageBox(self, "成功", "设置已保存", "success")
            dialog.exec_()
            
        except Exception as e:
            dialog = ModernMessageBox(self, "错误", f"保存设置失败: {str(e)}", "error")
            dialog.exec_()
            
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.folder_path_edit.clear()
            self.interface_combo.setCurrentIndex(0)
            self.source_ip_edit.clear()
            self.dest_ip_edit.clear()
            
            # 清除数据库中的设置
            self.db_manager.set_setting('target_folder', '')
            self.db_manager.set_setting('network_interface', '')
            self.db_manager.set_setting('source_ip', '')
            self.db_manager.set_setting('dest_ip', '')
            
            # 发送设置改变信号
            self.settings_changed.emit()
            
            dialog = ModernMessageBox(self, "成功", "设置已重置", "success")
            dialog.exec_()