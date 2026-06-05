# Lab Setup - Testing Chapter 1 Instructions

## System Check (Completed)

- **RAM**: 27.9 GB (✅ Exceeds 16GB requirement)
- **CPU**: x64-based PC (✅)
- **Virtualization**: Hypervisor present (✅)
- **VirtualBox**: ✅ Installed (v7.2.2)
- **C:\ISO directory**: ✅ Created (currently empty, ISOs in Downloads folder)

## Required Downloads

### 1. Windows Server 2022 Evaluation ISO ✅

- **URL**: https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022
- **Size**: ~4.5 GB
- **Status**: ✅ Downloaded (4.7 GB, Oct 13)
- **Location**: `C:\Users\seyam\Downloads\SERVER_EVAL_x64FRE_en-us.iso`
- **Action needed**: Move to `C:\ISO\Windows_Server_2022.iso`

> 💡 **Backup tip**: After you verify the download, copy the server ISO to a second location before you mount it in VirtualBox. If the working copy gets corrupted during install or later configuration, you’ll have a clean fallback.

### 2. Windows 11 Enterprise Evaluation ISO ⏸️

- **URL**: https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise
- **Size**: ~5-6 GB
- **Status**: ❌ Not downloaded yet
- **Action needed**: Download and save to `C:\ISO\Windows_11_Enterprise.iso`

> 💡 **Backup tip**: Keep a backup of the client ISO too. It saves time if you need to rebuild the VM, reattach media, or recover from a bad download.

## Next Steps

1. ✅ ~~Install VirtualBox using winget~~ (v7.2.2 installed)
2. Move Windows Server ISO to C:\ISO directory
3. Download Windows 11 Enterprise ISO
4. Create LAB-DC01 VM using VBoxManage commands from Chapter 1
5. Create LAB-WIN11 VM
6. Follow installation procedures

## Blockers Identified

- **ISO Downloads**: Cannot be automated via CLI due to Microsoft's authentication requirements
- **User Action Required**: Manual download of ISOs via web browser
- **Alternative**: Check if there's a direct download method or API access (unlikely for eval editions)

## Testing Status

- [x] VirtualBox installation (v7.2.2)
- [x] Windows Server 2022 ISO download (in Downloads folder)
- [ ] Move ISOs to C:\ISO directory
- [ ] Windows 11 Enterprise ISO download
- [ ] VM creation (LAB-DC01)
- [ ] VM creation (LAB-WIN11)
- [ ] Windows Server installation
- [ ] PowerShell configuration scripts
- [ ] Windows 11 client setup
- [ ] Domain join procedures

## Lab Reset / Rebuild Reference

If the current VMs become unstable or you want to start over from scratch, follow [vm_reset_rebuild_guide.md](vm_reset_rebuild_guide.md) for the full teardown and rebuild workflow.

## VM Startup Session - December 10, 2025

### Summary of Actions Taken

#### 1. Discovered Existing VMs

**TODO: Document with screenshots**

- Command used: `VBoxManage list vms`
- Found two VMs already created:
  - LAB-DC01 (Domain Controller)
  - LAB-CLIENT01 (Windows 11 Client)

#### 2. Inspected LAB-CLIENT01 Configuration

**TODO: Document with screenshots**

- Command: `VBoxManage showvminfo LAB-CLIENT01`
- Status: VM existed but had no storage controllers attached
- Configuration: 8GB RAM, 4 CPUs, EFI firmware, NAT networking

#### 3. Configured LAB-CLIENT01 Storage

**TODO: Document with screenshots**

- Added SATA controller: `VBoxManage storagectl LAB-CLIENT01 --name "SATA Controller" --add sata --controller IntelAhci --bootable on`
- Attached existing VDI: `VBoxManage storageattach LAB-CLIENT01 --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "C:\Users\seyam\VirtualBox VMs\LAB-CLIENT01\LAB-CLIENT01.vdi"`
- Added IDE controller: `VBoxManage storagectl LAB-CLIENT01 --name "IDE Controller" --add ide`
- Attached Windows 11 ISO: `VBoxManage storageattach LAB-CLIENT01 --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "C:\Users\seyam\Downloads\26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENTENTERPRISEEVAL_OEMRET_x64FRE_en-us.iso"`

#### 4. Started LAB-CLIENT01

**TODO: Document with screenshots**

- Command: `VBoxManage startvm LAB-CLIENT01`
- Result: VM booted successfully into Windows 11 installation

#### 5. Verified LAB-DC01 Status

**TODO: Document with screenshots**

- Command: `VBoxManage showvminfo LAB-DC01`
- Findings:
  - Windows Server 2022 already installed
  - Last powered off: October 21, 2025
  - Dual network configuration: NAT (NIC 1) + Internal Network 'LabNet' (NIC 2)
  - Storage: LAB-DC01.vdi already attached

#### 6. Started LAB-DC01

**TODO: Document with screenshots**

- Command: `VBoxManage startvm LAB-DC01`
- Result: Domain controller booted successfully

### VBoxManage Quick Reference

**TODO: Document these commands with screenshots for the manual**

```bash
# List all VMs
VBoxManage list vms

# List running VMs
VBoxManage list runningvms

# Show detailed VM information
VBoxManage showvminfo <VM-NAME>

# Start a VM
VBoxManage startvm <VM-NAME>

# Power off a VM
VBoxManage controlvm <VM-NAME> poweroff

# Gracefully shutdown a VM (requires Guest Additions)
VBoxManage controlvm <VM-NAME> acpipowerbutton

# Take a snapshot
VBoxManage snapshot <VM-NAME> take <SNAPSHOT-NAME>

# List snapshots
VBoxManage snapshot <VM-NAME> list
```

### Current Lab Status

- ✅ LAB-DC01: Running (Windows Server 2022, Domain Controller)
- ✅ LAB-CLIENT01: Running (Windows 11 Enterprise installation in progress)
- ✅ Both VMs configured and operational

### Next Steps

1. Complete Windows 11 installation on LAB-CLIENT01
2. Install VirtualBox Guest Additions on both VMs
3. Verify domain controller configuration on LAB-DC01
4. Join LAB-CLIENT01 to the domain
5. Begin PowerShell helpdesk training exercises

---

## Observations for Chapter 1 Improvements

1. **ISO Download Process**: Could add note that downloads are ~10GB total and may take 30-60 minutes on typical home internet
2. **Prerequisites Check**: Add PowerShell command to check available disk space before starting
3. **VirtualBox Installation**: Consider adding verification step after installation
4. **Network Configuration**: May need to clarify adapter selection if multiple adapters present
