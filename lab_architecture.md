# PowerShell Helpdesk Lab Environment Documentation

## Lab Overview

This is a virtualized lab environment for PowerShell helpdesk training and practice. The lab consists of a Windows Server domain controller and Windows 11 Enterprise client machines.

**Purpose:** Hands-on training environment for IT helpdesk operations using PowerShell

**Created:** 2025-11-26

---

## Host System Specifications

- **Hostname:** FREEHUB
- **OS:** Microsoft Windows 11 Home (Build 26200)
- **System:** LENOVO 83DX
- **Processor:** AMD64 Family 25 Model 117 @ 2483 MHz
- **Total RAM:** 27,962 MB (~27.3 GB)
- **Available Disk Space:** 366 GB (C: drive)
- **Virtualization Platform:** Oracle VirtualBox 7.2.2r170484
- **Virtualization Features:** Enabled (Hyper-V detected)

---

## VM Architecture

### Existing VMs

#### LAB-DC01 (Domain Controller)
- **Role:** Active Directory Domain Controller / DNS Server
- **OS:** Windows Server 2022 (64-bit)
- **RAM:** 4096 MB (4 GB)
- **Status:** Powered Off
- **Storage:**
  - LAB-DC01.vdi (2.0 MB - System)
  - LAB-DC01-Data.vdi (2.0 MB - Data)
- **Location:** C:\Users\seyam\VirtualBox VMs\LAB-DC01\

### Planned VMs

#### LAB-CLIENT01 (Windows 11 Enterprise Client)
- **Role:** Domain-joined workstation for helpdesk practice
- **OS:** Windows 11 Enterprise 25H2 (Build 26200.6584)
- **Planned RAM:** 8192 MB (8 GB)
- **Planned Storage:** 60 GB (dynamically allocated)
- **ISO Source:** `C:\Users\seyam\Downloads\26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENTENTERPRISEEVAL_OEMRET_x64FRE_en-us.iso` (6.7 GB)

---

## Network Configuration

**Network Type:** TBD (NAT, Host-Only, or Internal Network)

---

## Installation Steps

### Windows 11 Enterprise VM Creation

#### Step 1: ISO Verification
- Downloaded Windows 11 Enterprise Evaluation (25H2)
- Build: 26200.6584.250915-1905
- File Size: 6.7 GB
- Verified: 2025-11-26

#### Step 2: VirtualBox VM Creation
*(In Progress)*

---

## System Requirements

### Minimum Host Requirements
- **RAM:** 24 GB total (8 GB for server + 8 GB for client + 8 GB for host OS)
- **Disk Space:** ~100 GB free for VMs and ISOs
- **CPU:** Virtualization extensions enabled (VT-x/AMD-V)

### Current Host Meets Requirements
- ✅ RAM: 27.3 GB available
- ✅ Disk Space: 366 GB free
- ✅ Virtualization: Enabled

---

## Notes

- This lab is designed for Windows Server and PowerShell administration practice
- All VMs use evaluation editions with 180-day activation periods
- LAB-DC01 already configured as domain controller (configuration details TBD)

---

## Change Log

- **2025-11-26:** Initial documentation created
- **2025-11-26:** Windows 11 Enterprise ISO downloaded and verified
- **2025-11-26:** LAB-CLIENT01 VM creation started
