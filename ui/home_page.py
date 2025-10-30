#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页
显示文件夹列表和PCAP文件，提供发包功能
"""

import os
import glob
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QPushButton, QLabel, QMessageBox,
                             QInputDialog, QProgressBar, QTextEdit, QSplitter,
                             QGroupBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon

from database.db_manager import DatabaseManager
from network.packet_sender import PacketSender
from .settings_page import ModernMessageBox, ModernQuestionBox

class PacketSendThread(QThread):
    """发包线程"""
    progress_updated = pyqtSignal(int, int)  # 当前进度, 总数
    file_processed = pyqtSignal(str)  # 处理的文件名
    finished_signal = pyqtSignal(bool, str)  # 是否成功, 消息
    
    def __init__(self, pcap_files, network_interface, source_ip, dest_ip=None):
        super().__init__()
        self.pcap_files = pcap_files
        self.network_interface = network_interface
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.packet_sender = PacketSender()
        
    def run(self):
        """运行发包任务"""
        try:
            total_files = len(self.pcap_files)
            for i, pcap_file in enumerate(self.pcap_files):
                self.file_processed.emit(os.path.basename(pcap_file))
                
                # 发送PCAP文件
                success = self.packet_sender.send_pcap_file(
                    pcap_file, self.network_interface, self.source_ip, self.dest_ip
                )
                
                if not success:
                    self.finished_signal.emit(False, f"发送文件失败: {pcap_file}")
                    return
                
                self.progress_updated.emit(i + 1, total_files)
                
            self.finished_signal.emit(True, f"成功发送 {total_files} 个文件")
            
        except Exception as e:
            self.finished_signal.emit(False, f"发包过程中出现错误: {str(e)}")

class HomePage(QWidget):
    """首页类"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.send_thread = None
        
        # 设置首页背景
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
        self.init_ui()
        self.refresh_folder_list()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("PCAP文件管理")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # 文件夹树形控件组
        tree_group = QGroupBox("测试用例文件夹")
        tree_layout = QVBoxLayout(tree_group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_folder_list)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        toolbar_layout.addWidget(self.refresh_btn)
        
        self.add_alias_btn = QPushButton("🏷️ 设置别名")
        self.add_alias_btn.clicked.connect(self.set_folder_alias)
        self.add_alias_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        toolbar_layout.addWidget(self.add_alias_btn)
        
        toolbar_layout.addStretch()
        tree_layout.addLayout(toolbar_layout)
        
        # 文件夹树
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["名称", "路径", "PCAP文件数", "操作"])
        self.folder_tree.setAlternatingRowColors(True)
        self.folder_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.folder_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f8f9fa;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid #dee2e6;
                padding: 10px;
                font-weight: 600;
                color: #495057;
            }
        """)
        tree_layout.addWidget(self.folder_tree)
        
        splitter.addWidget(tree_group)
        
        # 日志和进度组
        log_group = QGroupBox("发包日志")
        log_layout = QVBoxLayout(log_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #e9ecef;
                text-align: center;
                font-weight: 500;
                font-size: 12px;
                color: #495057;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 8px;
            }
        """)
        log_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("🟢 就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-weight: 500;
                font-size: 13px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid #28a745;
            }
        """)
        log_layout.addWidget(self.status_label)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: #495057;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #6c757d;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #495057;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        
        # 设置分割器比例
        splitter.setSizes([500, 200])
        
    def refresh_folder_list(self):
        """刷新文件夹列表"""
        self.folder_tree.clear()
        
        # 获取目标文件夹路径
        target_folder = self.db_manager.get_setting('target_folder')
        if not target_folder or not os.path.exists(target_folder):
            self.log_message("请先在设置中配置目标文件夹路径")
            return
            
        self.log_message(f"正在扫描文件夹: {target_folder}")
        
        # 扫描子文件夹
        try:
            for item in os.listdir(target_folder):
                item_path = os.path.join(target_folder, item)
                if os.path.isdir(item_path):
                    self.add_folder_item(item_path)
                    
            self.log_message("文件夹列表刷新完成")
            
        except Exception as e:
            self.log_message(f"扫描文件夹时出错: {str(e)}")
            
    def add_folder_item(self, folder_path: str):
        """添加文件夹项到树形控件"""
        folder_name = os.path.basename(folder_path)
        
        # 获取别名并格式化显示名称
        alias = self.db_manager.get_folder_alias(folder_path)
        if alias:
            display_name = f"{alias} ({folder_name})"
        else:
            display_name = folder_name
        
        # 统计PCAP文件数量
        pcap_files = glob.glob(os.path.join(folder_path, "*.pcap"))
        pcap_files.extend(glob.glob(os.path.join(folder_path, "*.pcapng")))
        pcap_count = len(pcap_files)
        
        # 创建树形项
        item = QTreeWidgetItem(self.folder_tree)
        item.setText(0, display_name)
        item.setText(1, folder_path)
        item.setText(2, str(pcap_count))
        item.setData(0, Qt.UserRole, folder_path)  # 存储完整路径
        
        # 添加发包按钮
        send_btn = QPushButton("📤 发包")
        send_btn.setMaximumWidth(90)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        send_btn.clicked.connect(lambda: self.send_folder_packets(folder_path))
        self.folder_tree.setItemWidget(item, 3, send_btn)
        
        # 添加PCAP文件子项
        for pcap_file in pcap_files:
            child_item = QTreeWidgetItem(item)
            child_item.setText(0, os.path.basename(pcap_file))
            child_item.setText(1, pcap_file)
            child_item.setText(2, "1")
            
            # 为单个文件添加发包按钮
            file_send_btn = QPushButton("📤 发包")
            file_send_btn.setMaximumWidth(90)
            file_send_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fd7e14;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e8650e;
                }
                QPushButton:pressed {
                    background-color: #d35400;
                }
            """)
            file_send_btn.clicked.connect(lambda checked, f=pcap_file: self.send_single_packet(f))
            self.folder_tree.setItemWidget(child_item, 3, file_send_btn)
            
    def on_item_double_clicked(self, item, column):
        """双击项目事件"""
        if item.parent() is None:  # 文件夹项
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
                
    def set_folder_alias(self):
        """设置文件夹别名"""
        current_item = self.folder_tree.currentItem()
        if not current_item or current_item.parent() is not None:
            dialog = ModernMessageBox(self, "警告", "请选择一个文件夹", "warning")
            dialog.exec_()
            return
            
        folder_path = current_item.data(0, Qt.UserRole)
        current_alias = self.db_manager.get_folder_alias(folder_path)
        
        alias, ok = QInputDialog.getText(
            self, "设置别名", 
            f"为文件夹设置别名:\n{folder_path}",
            text=current_alias or ""
        )
        
        if ok and alias.strip():
            self.db_manager.set_folder_alias(folder_path, alias.strip())
            current_item.setText(0, alias.strip())
            self.log_message(f"已设置别名: {alias.strip()}")
            
    def send_folder_packets(self, folder_path: str):
        """发送文件夹中的所有PCAP包"""
        # 检查网络设置
        network_interface = self.db_manager.get_setting('network_interface')
        source_ip = self.db_manager.get_setting('source_ip')
        dest_ip = self.db_manager.get_setting('dest_ip')
        
        if not network_interface:
            dialog = ModernMessageBox(self, "警告", "请先在设置中配置网络接口", "warning")
            dialog.exec_()
            return
            
        # 获取PCAP文件列表
        pcap_files = glob.glob(os.path.join(folder_path, "*.pcap"))
        pcap_files.extend(glob.glob(os.path.join(folder_path, "*.pcapng")))
        
        if not pcap_files:
            dialog = ModernMessageBox(self, "信息", "该文件夹中没有PCAP文件", "info")
            dialog.exec_()
            return
            
        # 确认发送
        dialog = ModernQuestionBox(
            self, "确认发送", 
            f"确定要发送文件夹 '{os.path.basename(folder_path)}' 中的 {len(pcap_files)} 个PCAP文件吗？"
        )
        reply = dialog.exec_()
        
        if reply == dialog.Accepted:
            self.start_packet_sending(pcap_files, network_interface, source_ip, dest_ip)
            
    def send_single_packet(self, pcap_file: str):
        """发送单个PCAP文件"""
        # 检查网络设置
        network_interface = self.db_manager.get_setting('network_interface')
        source_ip = self.db_manager.get_setting('source_ip')
        dest_ip = self.db_manager.get_setting('dest_ip')
        
        if not network_interface:
            dialog = ModernMessageBox(self, "警告", "请先在设置中配置网络接口", "warning")
            dialog.exec_()
            return
            
        # 确认发送
        dialog = ModernQuestionBox(
            self, "确认发送", 
            f"确定要发送文件 '{os.path.basename(pcap_file)}' 吗？"
        )
        reply = dialog.exec_()
        
        if reply == dialog.Accepted:
            self.start_packet_sending([pcap_file], network_interface, source_ip, dest_ip)
            
    def start_packet_sending(self, pcap_files, network_interface, source_ip, dest_ip=None):
        """开始发包任务"""
        # 检查是否有正在运行的线程
        if self.send_thread and self.send_thread.isRunning():
            dialog = ModernMessageBox(self, "警告", "发包任务正在进行中，请等待完成", "warning")
            dialog.exec_()
            return
        
        # 清理已完成的线程
        if self.send_thread and not self.send_thread.isRunning():
            self.send_thread.deleteLater()
            self.send_thread = None
            
        # 创建发包线程
        self.send_thread = PacketSendThread(pcap_files, network_interface, source_ip, dest_ip)
        self.send_thread.progress_updated.connect(self.update_progress)
        self.send_thread.file_processed.connect(self.update_current_file)
        self.send_thread.finished_signal.connect(self.on_send_finished)
        
        # 初始化进度条
        self.progress_bar.setMaximum(len(pcap_files))
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 禁用相关按钮
        self.refresh_btn.setEnabled(False)
        self.add_alias_btn.setEnabled(False)
        
        # 开始发送
        self.log_message(f"开始发送 {len(pcap_files)} 个PCAP文件...")
        self.send_thread.start()
        
    def update_progress(self, current, total):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"发送进度: {current}/{total}")
        
    def update_current_file(self, filename):
        """更新当前处理的文件"""
        self.log_message(f"正在发送: {filename}")
        
    def on_send_finished(self, success, message):
        """发包完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("就绪")
        
        # 清理线程 - 确保线程完全完成后再清理
        if self.send_thread:
            # 等待线程完全结束
            if self.send_thread.isRunning():
                self.send_thread.quit()
                self.send_thread.wait(1000)  # 等待最多1秒
            
            # 断开信号连接
            self.send_thread.progress_updated.disconnect()
            self.send_thread.file_processed.disconnect()
            self.send_thread.finished_signal.disconnect()
            
            # 删除线程对象
            self.send_thread.deleteLater()
            self.send_thread = None
        
        # 恢复按钮
        self.refresh_btn.setEnabled(True)
        self.add_alias_btn.setEnabled(True)
        
        # 显示结果
        if success:
            self.log_message(f"✓ {message}")
            dialog = ModernMessageBox(self, "成功", message, "success")
            dialog.exec_()
        else:
            self.log_message(f"✗ {message}")
            dialog = ModernMessageBox(self, "错误", message, "error")
            dialog.exec_()
            
    def log_message(self, message: str):
        """添加日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())