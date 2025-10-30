#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
用于管理SQLite数据库，存储应用程序设置和文件夹别名
"""

import sqlite3
import os
from typing import Optional, List, Tuple

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "pcap_player.db"):
        """初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
    def init_database(self):
        """初始化数据库，创建必要的表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建文件夹别名表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folder_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT UNIQUE NOT NULL,
                alias TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认设置
        default_settings = [
            ('target_folder', ''),
            ('network_interface', ''),
            ('source_ip', ''),
            ('dest_ip', ''),
        ]
        
        for key, value in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str) -> Optional[str]:
        """获取设置值
        
        Args:
            key: 设置键
            
        Returns:
            设置值，如果不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def set_setting(self, key: str, value: str):
        """设置配置值
        
        Args:
            key: 设置键
            value: 设置值
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_folder_alias(self, folder_path: str) -> Optional[str]:
        """获取文件夹别名
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            别名，如果不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT alias FROM folder_aliases WHERE folder_path = ?', (folder_path,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def set_folder_alias(self, folder_path: str, alias: str):
        """设置文件夹别名
        
        Args:
            folder_path: 文件夹路径
            alias: 别名
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO folder_aliases (folder_path, alias, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (folder_path, alias))
        
        conn.commit()
        conn.close()
    
    def get_all_folder_aliases(self) -> List[Tuple[str, str]]:
        """获取所有文件夹别名
        
        Returns:
            (文件夹路径, 别名) 的列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT folder_path, alias FROM folder_aliases ORDER BY alias')
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def delete_folder_alias(self, folder_path: str):
        """删除文件夹别名
        
        Args:
            folder_path: 文件夹路径
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM folder_aliases WHERE folder_path = ?', (folder_path,))
        
        conn.commit()
        conn.close()