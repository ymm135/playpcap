#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def check_database():
    db = DatabaseManager()
    
    print("=== 数据库设置检查 ===")
    print(f"target_folder: '{db.get_setting('target_folder')}'")
    print(f"network_interface: '{db.get_setting('network_interface')}'")
    print(f"source_ip: '{db.get_setting('source_ip')}'")
    print(f"dest_ip: '{db.get_setting('dest_ip')}'")
    
    # 检查target_folder是否是目录
    target_folder = db.get_setting('target_folder')
    if target_folder:
        print(f"\ntarget_folder 是否存在: {os.path.exists(target_folder)}")
        print(f"target_folder 是否是目录: {os.path.isdir(target_folder)}")
        
        if os.path.isdir(target_folder):
            print(f"目录内容:")
            try:
                files = os.listdir(target_folder)
                pcap_files = [f for f in files if f.endswith('.pcap')]
                print(f"  PCAP文件: {pcap_files}")
            except Exception as e:
                print(f"  读取目录失败: {e}")

if __name__ == "__main__":
    check_database()