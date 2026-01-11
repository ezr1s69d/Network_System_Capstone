# ARP
---
## What is ARP?
ARP (Address Resolution Protocol) is a protocol used in IPv4 networks to map a logical _IP address_ to a physical _MAC address_ within the same local area network (LAN).

__Purpose:__
> Enable Ethernet communication by resolving IP addresses into MAC addresses.

## Why ARP is needed?
MAC address is needed while transferring data on the ethernet, but what the network only knows is IP address
- __IP Address (Layer 3)__: Identify who the destination is
- __MAC Address (Layer 2)__: Identifiy where to deliver the frame

## ARP packet format
```
<-------------32bits-------------->
===================================
| Hardware Type  | Protocol Type  |
|     Eth(1)     |  IPv4(0x0800)  |
===================================
|Hardware| Proto |    Operation   |
|  size  |  len  | 1:req  2:reply |
===================================
|       Sender MAC Address        | 
===================================
|        Sender IP Address        |
===================================
|      Reciever MAC Address       | --> Request: FF:FF:FF:FF:FF:FF
===================================
|       Reciever IP Address       |
===================================
```

## ARP Operating Process
- __Step 1__: Check __ARP cache__
  - sender check its ARP table
  - If IP --- MAC mapping exists: use it directly
  - If not: send ARP request
- __Step 2__: ARP request (Broadcast)
  - Sent as an __Ethernet Broadcast__
  - Destinaton MAC: ```FF:FF:FF:FF:FF:FF```
  - All devices in LAN recieve the ARP request
- __Step 3__: ARP Reply (Unicast)
  - Only the device which IP matches target IP in ARP request replies
  - Response is sent as __unicast__
  - Include sender's MAC address
- __Step 4__: Update ARP table
  - Requester stores IP --- MAC mapping
- __Step 5__: Data transmission

## Command

1. ping:\
   ```h1 ping h2```
2. show_table
    - show_table {host-name/switch-name}\
   ```show_table h1``` (show the ARP table in h1)\
   ```show_table s1``` (show the MAC table in s1)
    - show_table {all_hosts/all_switches}\
   ```show_table all_hosts``` (show the ARP tables of all hosts)\
   ```show_table all_switches``` (show the MAC tables of all switches)
3. clear:\
```clear h1``` (clear the ARP table in h1)\
```clear s1``` (clear the MAC table in s1)
4. exit:\
```exit```
5. If the entered command _is not_ “ping,” “show_table,”, “clear” or “exit”,\
print ```a wrong command```
