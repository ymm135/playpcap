#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据包发送器
使用scapy库读取和发送PCAP文件
"""

import os
import time
from typing import Optional

try:
    from scapy.all import rdpcap, sendp, get_if_list, get_if_addr
    from scapy.layers.inet import IP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

class PacketSender:
    """数据包发送器类"""
    
    def __init__(self):
        """初始化发送器"""
        if not SCAPY_AVAILABLE:
            raise ImportError("需要安装scapy库: pip install scapy")
            
    def get_available_interfaces(self):
        """获取可用的网络接口列表
        
        Returns:
            网络接口名称列表
        """
        try:
            return get_if_list()
        except Exception:
            return []
            
    def get_interface_ip(self, interface: str) -> Optional[str]:
        """获取网络接口的IP地址
        
        Args:
            interface: 网络接口名称
            
        Returns:
            IP地址，如果获取失败返回None
        """
        try:
            return get_if_addr(interface)
        except Exception:
            return None
            
    def send_pcap_file(self, pcap_file: str, interface: str, source_ip: Optional[str] = None, dest_ip: Optional[str] = None) -> bool:
        """发送PCAP文件中的数据包
        
        Args:
            pcap_file: PCAP文件路径
            interface: 网络接口名称
            source_ip: 可选的源IP地址，如果提供则修改数据包的源IP
            dest_ip: 可选的目的IP地址，如果提供则修改数据包的目的IP
            
        Returns:
            发送是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(pcap_file):
                print(f"PCAP文件不存在: {pcap_file}")
                return False
                
            # 读取PCAP文件
            print(f"正在读取PCAP文件: {pcap_file}")
            packets = rdpcap(pcap_file)
            
            if not packets:
                print("PCAP文件中没有数据包")
                return False
                
            print(f"读取到 {len(packets)} 个数据包")
            
            # 发送数据包
            sent_count = 0
            for i, packet in enumerate(packets):
                try:
                    # 创建数据包副本以避免修改原始数据包
                    packet_to_send = packet.copy()
                    
                    # 如果指定了源IP或目的IP，修改数据包的IP地址
                    # 检查IP地址是否为有效的非空字符串
                    valid_source_ip = source_ip and source_ip.strip()
                    valid_dest_ip = dest_ip and dest_ip.strip()
                    
                    if packet_to_send.haslayer(IP) and (valid_source_ip or valid_dest_ip):
                        if valid_source_ip:
                            packet_to_send[IP].src = valid_source_ip
                        if valid_dest_ip:
                            packet_to_send[IP].dst = valid_dest_ip
                        # 重新计算校验和
                        del packet_to_send[IP].chksum
                        # 检查并重新计算传输层校验和
                        try:
                            from scapy.layers.inet import TCP, UDP
                            if packet_to_send.haslayer(TCP):
                                del packet_to_send[TCP].chksum
                            elif packet_to_send.haslayer(UDP):
                                del packet_to_send[UDP].chksum
                        except Exception:
                            pass  # 如果无法处理传输层，继续发送
                            
                    # 发送数据包
                    sendp(packet_to_send, iface=interface, verbose=False)
                    sent_count += 1
                    
                    # 添加小延迟以避免网络拥塞
                    if i % 100 == 0:
                        time.sleep(0.001)  # 1ms延迟
                        
                except Exception as e:
                    print(f"发送第 {i+1} 个数据包时出错: {str(e)}")
                    continue
                    
            print(f"成功发送 {sent_count}/{len(packets)} 个数据包")
            return sent_count > 0
            
        except Exception as e:
            print(f"发送PCAP文件时出错: {str(e)}")
            return False
            
    def send_packets_with_timing(self, pcap_file: str, interface: str, 
                               source_ip: Optional[str] = None, 
                               dest_ip: Optional[str] = None,
                               preserve_timing: bool = True) -> bool:
        """按照原始时间间隔发送数据包
        
        Args:
            pcap_file: PCAP文件路径
            interface: 网络接口名称
            source_ip: 可选的源IP地址
            dest_ip: 可选的目的IP地址
            preserve_timing: 是否保持原始时间间隔
            
        Returns:
            发送是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(pcap_file):
                print(f"PCAP文件不存在: {pcap_file}")
                return False
                
            # 读取PCAP文件
            print(f"正在读取PCAP文件: {pcap_file}")
            packets = rdpcap(pcap_file)
            
            if not packets:
                print("PCAP文件中没有数据包")
                return False
                
            print(f"读取到 {len(packets)} 个数据包")
            
            # 发送数据包
            sent_count = 0
            last_time = None
            
            for i, packet in enumerate(packets):
                try:
                    # 创建数据包副本以避免修改原始数据包
                    packet_to_send = packet.copy()
                    
                    # 如果指定了源IP或目的IP，修改数据包的IP地址
                    # 检查IP地址是否为有效的非空字符串
                    valid_source_ip = source_ip and source_ip.strip()
                    valid_dest_ip = dest_ip and dest_ip.strip()
                    
                    if packet_to_send.haslayer(IP) and (valid_source_ip or valid_dest_ip):
                        if valid_source_ip:
                            packet_to_send[IP].src = valid_source_ip
                        if valid_dest_ip:
                            packet_to_send[IP].dst = valid_dest_ip
                        # 重新计算校验和
                        del packet_to_send[IP].chksum
                        # 检查并重新计算传输层校验和
                        try:
                            from scapy.layers.inet import TCP, UDP
                            if packet_to_send.haslayer(TCP):
                                del packet_to_send[TCP].chksum
                            elif packet_to_send.haslayer(UDP):
                                del packet_to_send[UDP].chksum
                        except Exception:
                            pass  # 如果无法处理传输层，继续发送
                    
                    # 计算时间间隔
                    if preserve_timing and hasattr(packet, 'time'):
                        current_time = float(packet.time)
                        if last_time is not None:
                            delay = current_time - last_time
                            if delay > 0 and delay < 10:  # 最大延迟10秒
                                time.sleep(delay)
                        last_time = current_time
                        
                    # 发送数据包
                    sendp(packet_to_send, iface=interface, verbose=False)
                    sent_count += 1
                    
                except Exception as e:
                    print(f"发送第 {i+1} 个数据包时出错: {str(e)}")
                    continue
                    
            print(f"成功发送 {sent_count}/{len(packets)} 个数据包")
            return sent_count > 0
            
        except Exception as e:
            print(f"发送PCAP文件时出错: {str(e)}")
            return False
            
    def validate_interface(self, interface: str) -> bool:
        """验证网络接口是否有效
        
        Args:
            interface: 网络接口名称
            
        Returns:
            接口是否有效
        """
        try:
            available_interfaces = self.get_available_interfaces()
            return interface in available_interfaces
        except Exception:
            return False