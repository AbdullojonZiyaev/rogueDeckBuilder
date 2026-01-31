#!/usr/bin/env python3
"""
Network Information Tool for Rogue Deck Builder Server
Helps identify the correct IP address for ZeroTier and local networks
"""

import socket
import subprocess
import platform
import re

def get_network_interfaces():
    """Get detailed network interface information"""
    interfaces = []
    
    try:
        # Try to get interface details using ip command (Linux)
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            current_interface = None
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # New interface line
                if line and line[0].isdigit() and ':' in line:
                    interface_name = line.split(':')[1].strip().split('@')[0]
                    current_interface = interface_name
                
                # IP address line
                elif 'inet ' in line and current_interface:
                    ip_part = line.split('inet ')[1].split('/')[0]
                    if not ip_part.startswith('127.') and not ip_part.startswith('169.254'):
                        interface_type = "Unknown"
                        priority = 5
                        
                        # Identify interface types with priorities
                        if 'zt' in current_interface.lower():
                            interface_type = "ZeroTier VPN"
                            priority = 1  # Highest priority for ZeroTier
                        elif current_interface.startswith('wlan') or current_interface.startswith('wifi'):
                            interface_type = "WiFi"
                            priority = 3
                        elif current_interface.startswith('eth') or current_interface.startswith('enp'):
                            interface_type = "Ethernet"
                            priority = 2
                        elif current_interface.startswith('docker'):
                            interface_type = "Docker"
                            priority = 6
                        elif current_interface.startswith('br-'):
                            interface_type = "Bridge"
                            priority = 7
                        elif 'tun' in current_interface.lower() or 'vpn' in current_interface.lower():
                            interface_type = "VPN/Tunnel"
                            priority = 1
                        
                        interfaces.append({
                            'name': current_interface,
                            'ip': ip_part,
                            'type': interface_type,
                            'priority': priority
                        })
        
        # Fallback to hostname -I if no interfaces found
        if not interfaces:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                ips = result.stdout.strip().split()
                for i, ip in enumerate(ips):
                    if not ip.startswith('127.') and not ip.startswith('169.254'):
                        interfaces.append({
                            'name': f'interface{i}',
                            'ip': ip,
                            'type': 'Unknown',
                            'priority': 5
                        })
    
    except Exception as e:
        # Final fallback - basic socket method
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if not local_ip.startswith('127.') and not local_ip.startswith('169.254'):
                interfaces.append({
                    'name': 'default',
                    'ip': local_ip,
                    'type': 'Unknown',
                    'priority': 5
                })
        except:
            pass
    
    # Sort by priority (lower number = higher priority)
    interfaces.sort(key=lambda x: x['priority'])
    return interfaces

def is_zerotier_network(ip):
    """Check if an IP looks like it's from ZeroTier"""
    # ZeroTier typically uses private IP ranges
    # Common patterns: 10.x.x.x, 172.16-31.x.x, 192.168.x.x
    # But can be customized, so this is just a hint
    try:
        parts = ip.split('.')
        if len(parts) == 4:
            first = int(parts[0])
            second = int(parts[1])
            
            if first == 10:
                return "Possible (10.x.x.x range)"
            elif first == 172 and 16 <= second <= 31:
                return "Possible (172.16-31.x.x range)"
            elif first == 192 and second == 168:
                return "Possible (192.168.x.x range)"
    except:
        pass
    return False

def main():
    print("🌐 === Network Information for Rogue Deck Builder Server ===")
    print()
    
    interfaces = get_network_interfaces()
    
    if not interfaces:
        print("❌ No network interfaces found!")
        return
    
    print("📡 Available Network Interfaces:")
    print("   (Ordered by recommended priority for gaming)")
    print()
    
    zerotier_found = False
    recommended_ip = None
    
    for i, interface in enumerate(interfaces):
        icon = "🔸"
        if interface['type'] == "ZeroTier VPN":
            icon = "🚀"
            zerotier_found = True
            if not recommended_ip:
                recommended_ip = interface['ip']
        elif "VPN" in interface['type']:
            icon = "🔐"
            if not recommended_ip:
                recommended_ip = interface['ip']
        
        print(f"{icon} {interface['type']}")
        print(f"   Interface: {interface['name']}")
        print(f"   IP Address: {interface['ip']}")
        
        zt_check = is_zerotier_network(interface['ip'])
        if zt_check:
            print(f"   ZeroTier: {zt_check}")
        
        print()
    
    if not recommended_ip:
        recommended_ip = interfaces[0]['ip']
    
    print("🎯 Recommendation:")
    if zerotier_found:
        print(f"   Use ZeroTier IP for gaming with friends: {recommended_ip}")
        print("   This will bypass WiFi network restrictions")
    else:
        print(f"   Recommended IP: {recommended_ip}")
        if len(interfaces) > 1:
            print("   Note: No ZeroTier interface detected")
    
    print()
    print("🚀 To start the server:")
    print(f"   python3 server.py {recommended_ip}")
    print("   or")
    print("   python3 server.py 0.0.0.0    # (binds to all interfaces)")
    
    print()
    print("🎮 For your friend to connect:")
    print(f"   Share this IP: {recommended_ip}")
    print("   Port: 8888")
    
    print()
    print("🔧 Troubleshooting:")
    print("   • Make sure ZeroTier is running on both computers")
    print("   • Both players should be in the same ZeroTier network")
    print("   • Check ZeroTier Central to ensure devices are online")
    print("   • Firewall: sudo ufw allow 8888")

if __name__ == "__main__":
    main()