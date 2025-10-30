#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCAP播放器主程序
类似于科来数据包播放器，增加了文件夹列表功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager

def main():
    """主函数"""
    # 设置高DPI支持（必须在创建QApplication之前）
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("PCAP播放器")
    app.setApplicationVersion("1.0.0")
    
    # 初始化数据库
    db_manager = DatabaseManager()
    db_manager.init_database()
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()