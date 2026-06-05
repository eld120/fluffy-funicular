# VM Reset and Rebuild Guide

This document describes how to tear down the current VirtualBox lab cleanly and start over with fresh virtual machines. Use this when the domain controller or client becomes unstable, networking is broken, or you simply want to rebuild from scratch.

## What this guide assumes

- You are working on the Windows host machine.
- The lab VMs are named `LAB-DC01` and `LAB-CLIENT01`.
- You want to delete the old VMs and provision new ones.
- You want to preserve your chapter notes and screenshots in the repository, not the VM state itself.

## Before you delete anything

1. Save any important documentation work in the repo.
2. Copy any screenshots you still need into `static/chapter_1` or a backup folder.
3. If you want a record of the current VM state, export or copy the VM folders before removal.
4. Make sure you are comfortable losing the current VM disks and configuration.

> ⚠️ **Warning**: If you choose the delete-all-files option, VirtualBox will remove the VM configuration and associated virtual disks. Do this only after you are sure nothing inside those VMs still matters.

## Stability preflight before you rebuild

Before creating the new VMs, reduce the common causes of VirtualBox instability on Windows hosts:

1. Reboot the host so you start from a clean state.
2. Close heavy background tools such as Docker Desktop, WSL-heavy terminals, browsers with many tabs, game launchers, and any other VM platform.
3. If VirtualBox guests have been crashing, freezing, or performing very poorly, check for Windows hypervisor features that can interfere with VirtualBox performance:
	- **Hyper-V**
	- **Windows Hypervisor Platform**
	- **Virtual Machine Platform**
	- **Core isolation / Memory Integrity**
4. If you change any of those settings, reboot the host again before testing VirtualBox.
5. During initial server build, run only `LAB-DC01` by itself. Do not run the client VM until the server is stable.

> 💡 **Why this matters**: On some Windows hosts, VirtualBox will still run while the Microsoft hypervisor layer is active, but guest performance can be dramatically worse. That can show up as sluggish settings screens, failed Windows Update sessions, or what looks like random crashing.

## Step 1 - Shut down both VMs cleanly

If the guests are responsive, shut them down from inside the VM:

1. Open the guest operating system.
2. Use **Start** → **Power** → **Shut down**.
3. Wait until the VM window closes or shows the machine is powered off.

**[SCREENSHOT: Windows shutdown menu inside the guest VM]**

If a guest is frozen, use VirtualBox from the host:

```bash
"/c/Program Files/Oracle/VirtualBox/VBoxManage" controlvm LAB-DC01 acpipowerbutton
"/c/Program Files/Oracle/VirtualBox/VBoxManage" controlvm LAB-CLIENT01 acpipowerbutton
```

If the guest still does not shut down, force it off:

```bash
"/c/Program Files/Oracle/VirtualBox/VBoxManage" controlvm LAB-DC01 poweroff
"/c/Program Files/Oracle/VirtualBox/VBoxManage" controlvm LAB-CLIENT01 poweroff
```

## Step 2 - Confirm nothing is running

Check the active VM list:

```bash
"/c/Program Files/Oracle/VirtualBox/VBoxManage" list runningvms
```

You want this to return no running machines before deletion.

**[SCREENSHOT: VBoxManage list runningvms showing no entries]**

## Step 3 - Remove the VMs from VirtualBox

### GUI method

1. Open **Oracle VirtualBox Manager**.
2. Right-click `LAB-CLIENT01` and select **Remove**.
3. Choose **Delete all files** if you want a full reset.
4. Repeat for `LAB-DC01`.

**[SCREENSHOT: VirtualBox right-click menu with Remove highlighted]**

**[SCREENSHOT: Remove confirmation dialog with Delete all files selected]**

### VBoxManage method

If you prefer the command line, unregister and delete each VM:

```bash
"/c/Program Files/Oracle/VirtualBox/VBoxManage" unregistervm LAB-CLIENT01 --delete
"/c/Program Files/Oracle/VirtualBox/VBoxManage" unregistervm LAB-DC01 --delete
```

> 💡 **Tip**: Delete the client first and the server second. The order does not technically matter, but this sequence matches the usual lab dependency flow.

## Step 4 - Remove leftover VM folders if needed

After deletion, check the VirtualBox VM directory on the host:

- `C:\Users\seyam\VirtualBox VMs\LAB-CLIENT01`
- `C:\Users\seyam\VirtualBox VMs\LAB-DC01`

If VirtualBox did not remove the folders, delete them manually in File Explorer.

**[SCREENSHOT: File Explorer showing the VirtualBox VMs folder before cleanup]**

## Step 5 - Verify the lab is fully wiped

Run these checks from the host:

```bash
"/c/Program Files/Oracle/VirtualBox/VBoxManage" list vms
"/c/Program Files/Oracle/VirtualBox/VBoxManage" list runningvms
```

The goal is to confirm the old lab machines are gone before you create new ones.

**[SCREENSHOT: VBoxManage list vms after deletion]**

## Step 6 - Rebuild the lab from scratch

Once the old VMs are gone, start fresh in this order:

1. Create `LAB-DC01`.
2. Attach the Windows Server ISO and boot into the graphical installer.
3. Configure **one** network adapter only for the initial install (use the external/NAT adapter so the server can reach updates during setup).
4. Set conservative VirtualBox defaults for the server VM:
   - `2 vCPU`
   - `4096 MB RAM`
   - Graphics controller: `VBoxSVGA`
   - Video memory: `128 MB`
   - `3D Acceleration: Off`
   - Adapter 1: `NAT`, with **Cable Connected** enabled
   - Do **not** add Adapter 2 yet
5. Install Windows Server using the Desktop Experience graphical setup.
6. Complete first boot, basic GUI configuration, and Windows Update before adding the second network adapter.
7. Add the second adapter for the internal/lab network (`LabNet`) after the server is installed and patched.
8. Configure the internal adapter with the server IP address and DNS settings in the GUI.
9. Install the server roles and promote the server to a domain controller using Server Manager and the AD DS wizard.
10. Create `LAB-CLIENT01`.
11. Attach the Windows 11 ISO.
12. Join the client to the domain.

For the exact build steps, refer back to `chapter_1.md`.

## Recommended rebuild order

Use this order so the dependencies are easy to reason about:

1. VirtualBox host configuration
2. Server VM creation
3. Server install with a single network adapter and the graphical installer
4. Server IP configuration after first boot in the GUI
5. Windows Update on the server
6. Add the second server NIC for the internal network
7. Configure the internal server IP and DNS settings in the GUI
8. Role installation through Server Manager
9. Domain promotion through the AD DS wizard
10. DHCP and DNS setup through the management consoles
11. Client VM creation
12. Client domain join

> 💡 **Why this order?** For this rebuild, we are intentionally keeping `LAB-DC01` simple during OS installation. A single adapter reduces the chance of choosing the wrong NIC while Windows is still being installed and updated. After the server is stable, we add the internal network adapter and continue with the domain controller and lab services.

> 💡 **Why the conservative display settings?** Windows Server does not benefit much from 3D acceleration in this lab. Keeping 3D off and using the Windows-oriented `VBoxSVGA` controller reduces one more source of instability while you are still trying to get the server patched and usable.

## If you want a cleaner starting point

If your goal is to keep the documentation but start over with fresh screenshots, consider this workflow instead of deleting the repo files:

1. Move old screenshots into a dated backup folder.
2. Keep the markdown files.
3. Rebuild the VMs.
4. Capture new screenshots for each step.
5. Update the manuscript with the fresh images.

That approach lets you preserve the writing while resetting only the lab machines.
