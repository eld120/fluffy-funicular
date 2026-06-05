# Chapter 1: Building Your Windows Server Lab Environment

This manual is for aspiring helpdesk and desktop support professionals who want to operate like seasoned administrators in a Microsoft-centric environment. In this chapter you'll build a self-contained lab: a Windows Server domain controller, a Windows client, and the supporting services you need to explore Windows Server administration through the GUI first, with optional PowerShell follow-up where it helps.

## What you'll learn

By the end of this chapter, you will have:

- ✅ Installed Oracle VirtualBox and created two virtual machines
- ✅ Deployed Windows Server 2022 as a domain controller with Active Directory, DNS, DHCP, and file services
- ✅ Configured a Windows 11 Enterprise client and joined it to the domain
- ✅ Created an isolated lab network using VirtualBox Internal Networking
- ✅ Built foundational Windows Server administration skills through GUI-first configuration tasks
- ✅ Established a baseline environment for future automation and auditing exercises

## Lab topology

```
Internet
   │
   └─── [Host Workstation]
           │
           ├─── LAB-DC01 (Windows Server 2022)
           │     • IP: 172.16.10.10/24
           │     • Roles: AD DS, DNS, DHCP, File Server
           │     • 2 vCPU, 4 GB RAM, 350 GB storage (2 disks)
           │     • NIC1: NAT (Internet), NIC2: Internal Network (LabNet)
           │
           └─── LAB-WIN11 (Windows 11 Enterprise)
                 • IP: 172.16.10.50-.100 (DHCP)
                 • Domain Member: corp.lab
                 • 2 vCPU, 4 GB RAM, 250 GB storage
                 • NIC1: Internal Network (LabNet)
```

---

## Prerequisites

- **Hardware**: 8 physical or logical CPU cores, 16 GB RAM, and at least 500 GB of free SSD/HDD storage on the host workstation.
- **Virtualisation**: Hardware virtualisation (Intel VT-x/AMD-V) enabled in BIOS/UEFI. Verify from PowerShell:

```powershell
Get-ComputerInfo | Select-Object CsManufacturer,CsModel,HyperVisorPresent
```

- **Operating system**: Windows 10/11 Pro or Enterprise so you can use Hyper-V features if needed. macOS/Linux hosts are fine if the hardware requirements are met.
- **Software**: Oracle VirtualBox, Windows Server 2022 Evaluation ISO, Windows 11 Enterprise Evaluation ISO, and PowerShell 7 for the optional scripting follow-up labs.
- **Networking**: At least one spare IPv4 subnet that won't collide with your home LAN (for example `172.16.10.0/24`).

> 💡 **Download checklist**: Create a dedicated `C:\ISO` directory and place every ISO there so you can attach them quickly inside VirtualBox.

---

## Step 1 – Install Oracle VirtualBox

1. Browse to the [VirtualBox Downloads page](https://www.virtualbox.org/wiki/Downloads) and choose **Windows hosts**.
2. Save the installer (for example `VirtualBox-7.x.x-Win.exe`), then right-click and select **Run as administrator**.
3. Accept the default components (VirtualBox Application, USB support, Networking) and continue through the wizard. Allow Windows to install the device drivers when prompted.
4. Reboot the host PC after installation to ensure the VirtualBox network adapters finish binding to the OS.

![VirtualBox download page showing the Windows Hosts installer option](static/chapter_1/PXL_20250902_162315732.jpg)

> 📦 **Command-line install (optional)**: If you prefer automation, run PowerShell as admin and execute:
>
> ```powershell
> winget install --id Oracle.VirtualBox --exact --accept-source-agreements --accept-package-agreements
> ```
>
> The command reboots the network stack, so expect a short connectivity interruption while the installer runs.

---

## Step 2 – Download the operating system media

### Windows Server 2022 Evaluation (Domain Controller)

1. Navigate to [Microsoft Evaluation Center](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022).
2. Select **ISO** as the download format, sign in with a Microsoft account, and complete the short registration.
3. Choose **English (United States)** unless you have a localisation requirement and download the ISO (approx. 4.5 GB).
4. Rename the ISO to `Windows_Server_2022.iso` and store it in `C:\ISO` for clarity.

> 💡 **Backup tip**: After the download completes, keep a backup copy of the server ISO in a separate folder or external drive before mounting it in VirtualBox. If the ISO becomes corrupted during setup or later rebuilds, you can restore the backup instead of re-downloading.

![Microsoft Evaluation Center download confirmation page](static/chapter_1/PXL_20250902_162326462.jpg)

### Windows 11 Enterprise Evaluation (Client)

1. Browse to [Evaluate Windows 11 Enterprise](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise).
2. Select **ISO** as the download format, sign in with a Microsoft account, and complete the registration.
3. Choose your language and download the ISO (approx. 5-6 GB).
4. Save the file as `Windows_11_Enterprise.iso` in `C:\ISO`.

> 💡 **Backup tip**: Keep a second copy of the client ISO after the download finishes. That extra copy is useful if the ISO gets damaged, mounted incorrectly, or needs to be reused for a later rebuild.

![Windows 11 ISO download options](static/chapter_1/PXL_20250902_162337970.jpg)

---

## Step 3 – Create the Windows Server VM

Launch VirtualBox and create a new virtual machine with the following configuration:

| Setting              | Value                                                                       |
| -------------------- | --------------------------------------------------------------------------- |
| Name                 | `LAB-DC01`                                                                  |
| Type                 | Microsoft Windows                                                           |
| Version              | Windows 2022 (64-bit)                                                       |
| Base memory          | **4096 MB**                                                                 |
| Processors           | **2 vCPU**                                                                  |
| Graphics controller  | **VBoxSVGA**                                                                |
| Video memory         | **128 MB**                                                                  |
| 3D acceleration      | **Disabled**                                                                |
| Virtual optical disk | `C:\ISO\Windows_Server_2022.iso`                                            |
| Hard disks           | **SATA Controller** with `LAB-DC01.vdi` at **250 GB dynamically allocated** |

After the VM is created, tweak these advanced settings:

1. **System ▸ Motherboard**: Enable EFI, disable Floppy.
2. **System ▸ Processor**: Enable PAE/NX; leave nested virtualization disabled for now.
3. **Network**:
   - Adapter 1: **NAT** (Internet access for patching), with **Cable Connected** enabled.
   - Do **not** add Adapter 2 yet for the first install. We will add the internal `LabNet` adapter after Windows Server is installed and fully updated.
4. **Storage**: Add a second virtual hard disk (`D:`) sized **100 GB** on the same SATA controller.

![VirtualBox VM settings showing NAT and Internal Network adapters](static/chapter_1/PXL_20250902_162348015.jpg)

> 🛠️ **PowerShell shortcut**: Once VirtualBox is installed you can script VM creation. Here's a template to keep for later labs:
>
> ```powershell
> $vmName = "LAB-DC01"
> VBoxManage createvm --name $vmName --ostype "Windows2022_64" --register
> VBoxManage modifyvm $vmName --memory 4096 --cpus 2 --firmware efi --pae on --graphicscontroller vboxsvga --vram 128
> VBoxManage createhd --filename "$env:USERPROFILE\VirtualBox VMs\$vmName\$vmName.vdi" --size 256000
> VBoxManage storagectl $vmName --name "SATA" --add sata --controller IntelAhci
> VBoxManage storageattach $vmName --storagectl "SATA" --port 0 --device 0 --type hdd --medium "$env:USERPROFILE\VirtualBox VMs\$vmName\$vmName.vdi"
> VBoxManage storageattach $vmName --storagectl "SATA" --port 1 --device 0 --type dvddrive --medium "C:\ISO\Windows_Server_2022.iso"
> VBoxManage modifyvm $vmName --nic1 nat --cableconnected1 on
> ```

---

## Step 4 – Install Windows Server 2022

1. Start the `LAB-DC01` VM. At the language selection screen accept defaults and choose **Install Now**.
2. Pick **Windows Server 2022 Standard (Desktop Experience)**.
3. Accept the license, choose **Custom: Install Windows only**, and select the 250 GB drive as the OS disk. Leave the 100 GB disk unallocated—we'll initialize it via PowerShell in the next section.
4. Complete the graphical installation, set the Administrator password (record it securely in your lab notebook or password manager), then sign in to the desktop.

> 🖱️ **VirtualBox focus tip**: During the first install, keep the mouse and keyboard focus inside the VirtualBox window. If the cursor leaves the VM or the window loses focus, setup can look paused even though it is still waiting for input. Click back inside the VM if anything seems stuck.

![Windows Server setup ready to install screen](static/chapter_1/PXL_20250902_162400670.jpg)

### Initial GUI configuration

After the first login, Windows Server will automatically launch **Server Manager**. If it doesn't appear, click the **Start** button and select **Server Manager** from the menu.

> 💡 **Recommended rebuild path**: For a more stable first-time setup, keep `LAB-DC01` on a single NAT adapter until Windows Server is installed and fully patched. After Windows Update is complete, shut down the VM, add Adapter 2 as `Internal Network` named `LabNet`, then return to the steps below to identify and configure both adapters in the GUI.

#### Rename the computer (GUI method)

If you prefer to use the GUI before running PowerShell commands:

1. In **Server Manager** → **Local Server**, locate the **Computer name** property (should show something like `WIN-RANDOMTEXT`).
2. Click the computer name link to open **System Properties**.
3. Click the **Change** button, enter `LAB-DC01` as the new computer name, and click **OK**.
4. Click **OK** again, then **Restart Now** when prompted.
5. After the reboot, sign back in as Administrator.

#### Identify network adapters

Before configuring IP addresses, you need to identify which network adapter is which:

1. In Server Manager, click **Local Server** in the left pane.
2. Look for the **Ethernet** entries in the Properties section. You should see two adapters (both may show as "Ethernet" and "Ethernet 2" or similar).
3. Click on the first **Ethernet** link to open the **Network Connections** window.
4. Right-click each adapter and select **Status** → **Details** to see its configuration:
   - **Adapter 1** (NAT): Will show an IP address in the `10.0.2.x` range (typically `10.0.2.15`) with a default gateway of `10.0.2.2`. This is your **external/internet** connection.
   - **Adapter 2** (Internal Network "LabNet"): Will show either no IP address or an APIPA address (`169.254.x.x`) because it's not configured yet. This will be your **internal lab network**.

> 💡 **Pro tip**: You can rename the adapters for clarity. Right-click each adapter → **Rename**, and use names like `External-NAT` and `Internal-LabNet` so you can easily identify them.

#### Configure IP addresses (GUI method)

This is the part most people get stuck on: you need **one adapter that stays DHCP (external/NAT)** and **one adapter that becomes static (internal/LabNet)**.

1. From **Server Manager** → **Local Server**, click the **Ethernet** link to open **Network Connections**.

**[SCREENSHOT: Server Manager Local Server view showing the Ethernet link]**

2. (Recommended) Rename the adapters so the rest of the chapter is easier to follow:
   - Rename the NAT adapter to `External-NAT`
   - Rename the LabNet adapter to `Internal-LabNet`

**[SCREENSHOT: Network Connections showing renamed adapters]**

3. Configure the **external** adapter (`External-NAT`) to use DHCP (typical default):
   - Right-click `External-NAT` → **Properties**
   - Select **Internet Protocol Version 4 (TCP/IPv4)** → **Properties**
   - Ensure **Obtain an IP address automatically** and **Obtain DNS server address automatically** are selected
   - Click **OK**

**[SCREENSHOT: External-NAT IPv4 properties set to DHCP]**

4. Configure the **internal** adapter (`Internal-LabNet`) with a static IP:
   - Right-click `Internal-LabNet` → **Properties**
   - Select **Internet Protocol Version 4 (TCP/IPv4)** → **Properties**
    - Select **Use the following IP address** and enter:
       - IP address: `172.16.10.10`
       - Subnet mask: `255.255.255.0`
       - Default gateway: _(leave blank for now)_
   - Select **Use the following DNS server addresses** and enter:
     - Preferred DNS server: `127.0.0.1`
     - Alternate DNS server: _(leave blank)_
   - Click **OK** → **Close**

**[SCREENSHOT: Internal-LabNet IPv4 properties set to 172.16.10.10/24 and DNS 127.0.0.1]**

5. Verify the results:
   - Right-click each adapter → **Status** → **Details**
   - `External-NAT` should show `10.0.2.x` and a gateway of `10.0.2.2`
   - `Internal-LabNet` should show `172.16.10.10` and no gateway

**[SCREENSHOT: Adapter details showing External-NAT (10.0.2.x) and Internal-LabNet (172.16.10.10)]**

> ✅ **Why DNS = 127.0.0.1 right now?** After promotion, this server becomes your DNS server. Pointing the internal NIC at localhost ensures AD DS/DNS can register records locally.

> 📝 **Later update**: After DNS is fully installed and healthy, it’s also common to set the internal NIC’s DNS to `172.16.10.10` (itself). For the lab, either approach works as long as it’s consistent.

> 📘 **Note**: The PowerShell method below is optional. Use it later if you want a repeatable automation path; the GUI steps above are the primary workflow for this chapter.

### Post-install configuration (optional PowerShell)

Now that you understand the network adapter layout, you can open **PowerShell as Administrator** (right-click the Start button → **Windows PowerShell (Admin)**) and run the bootstrap script below if you want to automate the same setup you just completed in the GUI. This script will rename the server (if not done via GUI), configure the IP addresses, and install all roles in one pass:

> ⚠️ **Important**: The following commands are executed **inside the LAB-DC01 virtual machine**, not on your host computer.

```powershell
# Rename the computer to LAB-DC01
Rename-Computer -NewName 'LAB-DC01' -Force

# Get the second network adapter (Internal Network)
$interfaceInternal = Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.Name -like '*Ethernet*'} | Select-Object -Last 1

# Configure static IP on the internal network interface
New-NetIPAddress -InterfaceAlias $interfaceInternal.Name -IPAddress 172.16.10.10 -PrefixLength 24

# Point DNS to localhost (this server will be the DNS server)
Set-DnsClientServerAddress -InterfaceAlias $interfaceInternal.Name -ServerAddresses 127.0.0.1

# Install server roles and features
Install-WindowsFeature AD-Domain-Services, DHCP, DNS, File-Services, Print-Services, RSAT-AD-Tools, GPMC, Routing -IncludeManagementTools
Install-WindowsFeature FS-FileServer, FS-DFS-Namespace, FS-DFS-Replication

# Restart to apply the computer name change
Restart-Computer
```

> 🔐 **Why static IP first?** Domain controllers rely on consistent addressing. Configuring DNS to point to itself ensures the AD DS installation can register service records successfully.

#### Alternative: Install roles using the GUI

If you prefer to use the **Add Roles and Features Wizard** instead of PowerShell:

1. After renaming the computer and configuring network adapters, open **Server Manager** (it should launch automatically).
2. Click **Manage** in the top-right corner, then select **Add Roles and Features**.
3. Click **Next** through the "Before You Begin" screen.
4. Select **Role-based or feature-based installation** and click **Next**.
5. Ensure **Select a server from the server pool** is selected, and **LAB-DC01** is highlighted. Click **Next**.

6. **Select Server Roles** - Check the following boxes:
   - **Active Directory Domain Services** (when prompted, click **Add Features** to include management tools)
   - **DHCP Server** (click **Add Features**)
   - **DNS Server** (click **Add Features**)
   - **File and Storage Services** → expand and ensure **File Server** is checked
   - **Remote Access** (click **Add Features**) - we'll configure specific sub-roles in a moment
   - **Web Server (IIS)** (click **Add Features**)

7. Click **Next** to proceed to the **Select Features** screen.

8. **Select Features** - Check the following:
   - **Group Policy Management** (under Remote Server Administration Tools → Feature Administration Tools)
   - **Remote Server Administration Tools** → **Role Administration Tools**:
     - **AD DS and AD LDS Tools** (expand and check all)
     - **DHCP Server Tools**
     - **DNS Server Tools**
   - Click **Next**.

9. **Active Directory Domain Services** - Review the information screen and click **Next**.

10. **DHCP Server** - Review the information screen and click **Next**.

11. **DNS Server** - Review the information screen and click **Next**.

12. **Remote Access** - Review the information screen and click **Next**.

13. **Select Role Services for Remote Access** - Check the following:
    - **DirectAccess and VPN (RAS)**
    - **Routing**
    - **Web Application Proxy**
    - When prompted to add features for Web Application Proxy, click **Add Features**, then click **Next**.

14. **Web Server Role (IIS)** - Review the information screen and click **Next**.

15. **Select Role Services for Web Server (IIS)** - Accept the default selections (Web Server, Common HTTP Features, Health and Diagnostics, Performance, Security, Application Development, Management Tools) and click **Next**.

16. On the **Confirmation** screen, review your selections. You should see:
    - Active Directory Domain Services
    - DHCP Server
    - DNS Server
    - File and Storage Services
    - Remote Access (DirectAccess and VPN, Routing, Web Application Proxy)
    - Web Server (IIS)
17. Check the box for **Restart the destination server automatically if required**, then click **Install**.

18. The installation will take 5-10 minutes. Once complete, click **Close**. The server will restart automatically if you checked the restart option.

> 💡 **GUI first, PowerShell second**: The GUI wizard is the primary path for this chapter because it makes each role and feature visible while you learn. Keep the PowerShell method as an optional automation shortcut for later rebuilds.

### Prepare storage for shares and SYSVOL

In many production environments, you will have a single large disk that you need to partition or multiple disks to initialize. For this lab, we will use Disk Management to shrink our primary C: drive and create a new 100 GB partition (D: drive) for our data and shares.

You can perform this operation using either the GUI (Disk Management) or PowerShell.

#### GUI method (Disk Management)

1. **Open Disk Management:**
   - Right-click the **Start** button and select **Disk Management**.

**[SCREENSHOT: Start menu context menu with Disk Management highlighted]**

2. **Shrink the Primary Volume (C:):**
   - In the lower pane, right-click the `(C:)` volume and select **Shrink Volume...**.
   - The system will query the volume for available shrink space (this takes a moment).
   - In the **Enter the amount of space to shrink in MB** field, enter `102400` (which is exactly 100 GB).
   - Click **Shrink**.

**[SCREENSHOT: Shrink dialog box showing 102400 entered in the shrink amount box]**

3. **Create the New Volume (D:):**
   - You will now see 100 GB of **Unallocated** space next to your C: drive.
   - Right-click the **Unallocated** space and select **New Simple Volume...**.
   - The New Simple Volume Wizard will open. Click **Next**.
   - Leave the **Simple volume size in MB** at its maximum (102400) and click **Next**.
   - Ensure **Assign the following drive letter:** is set to `D` and click **Next**.
   - Select **Format this volume with the following settings:**
     - File system: **NTFS**
     - Allocation unit size: **Default**
     - Volume label: `Data`
     - Ensure **Perform a quick format** is checked.
   - Click **Next**, review your settings, and click **Finish**.

**[SCREENSHOT: Disk Management showing the C: drive and the newly created D: Data drive]**

#### PowerShell method

If you prefer to automate this process, open **PowerShell as Administrator** and run the following script to shrink the C: partition and create the D: drive:

```powershell
# Get the C: partition
$partitionC = Get-Partition -DriveLetter C

# Calculate the size to shrink (100 GB = 100 * 1024 * 1024 * 1024 bytes)
$shrinkSize = 100GB
$newSize = $partitionC.Size - $shrinkSize

# Shrink the C: partition
Resize-Partition -DriveLetter C -Size $newSize

# Find the unallocated space on Disk 0 and create a new 100GB partition
$disk = Get-Disk -Number 0
$maxSize = ($disk | Get-PartitionSupportedSize).SizeMax
New-Partition -DiskNumber 0 -UseMaximumSize -DriveLetter D | Format-Volume -FileSystem NTFS -NewFileSystemLabel 'Data' -Confirm:$false
```

#### Set up share directories and department folders

Now that the D: drive is ready, create the directory structure for user home folders and department shares. We will create folders for two departments — **HR** and **Accounting** — each with their own restricted permissions.

> 📘 **Why department folders?** In a real company, different teams need access to different data. NTFS permissions let you control exactly who can read, write, or modify files — even within a shared drive. This exercise mirrors how most organizations structure their file servers.

##### Create the directory structure

```powershell
# Top-level shared directories
New-Item -Path 'D:\Users'              -ItemType Directory
New-Item -Path 'D:\Data'               -ItemType Directory

# Department folders under Data
New-Item -Path 'D:\Data\HR'            -ItemType Directory
New-Item -Path 'D:\Data\Accounting'    -ItemType Directory
```

##### Create AD security groups for each department

Before setting permissions, create a dedicated Active Directory group for each department. This way you manage access by adding/removing users from groups, not by editing folder permissions every time someone changes roles.

```powershell
# Create department security groups in the Corp OU
New-ADGroup -Name "HR-Staff"          -GroupScope Global -GroupCategory Security -Path "OU=Corp,DC=corp,DC=lab"
New-ADGroup -Name "Accounting-Staff"  -GroupScope Global -GroupCategory Security -Path "OU=Corp,DC=corp,DC=lab"
```

##### Create network shares

```powershell
# Users home folder share (Domain Admins only — individual home folders come later)
New-SmbShare -Name "Users"      -Path "D:\Users"           -FullAccess   "CORP\Domain Admins"

# HR share — HR-Staff can read/write; Domain Admins have full control
New-SmbShare -Name "HR"         -Path "D:\Data\HR"         -FullAccess   "CORP\Domain Admins" -ChangeAccess "CORP\HR-Staff"

# Accounting share — Accounting-Staff can read/write; Domain Admins have full control
New-SmbShare -Name "Accounting" -Path "D:\Data\Accounting"  -FullAccess   "CORP\Domain Admins" -ChangeAccess "CORP\Accounting-Staff"
```

##### Set NTFS permissions on department folders

SMB share permissions control access over the network, but **NTFS permissions** are the real security layer — they apply both locally and via the network share. Set them explicitly so HR cannot browse the Accounting folder and vice versa.

```powershell
# Helper function: replace inherited permissions with explicit ones
function Set-FolderPermissions {
    param(
        [string]$FolderPath,
        [string]$Group,
        [string]$Permission = "Modify"
    )

    $acl = Get-Acl -Path $FolderPath

    # Remove inherited permissions so only explicit rules apply
    $acl.SetAccessRuleProtection($true, $false)

    # Grant SYSTEM and Domain Admins full control (always required)
    $adminRule  = New-Object System.Security.AccessControl.FileSystemAccessRule("BUILTIN\Administrators","FullControl","ContainerInherit,ObjectInherit","None","Allow")
    $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\SYSTEM","FullControl","ContainerInherit,ObjectInherit","None","Allow")

    # Grant the department group its access level
    $deptRule   = New-Object System.Security.AccessControl.FileSystemAccessRule($Group, $Permission, "ContainerInherit,ObjectInherit","None","Allow")

    $acl.AddAccessRule($adminRule)
    $acl.AddAccessRule($systemRule)
    $acl.AddAccessRule($deptRule)

    Set-Acl -Path $FolderPath -AclObject $acl
    Write-Host "Permissions set on $FolderPath for $Group ($Permission)" -ForegroundColor Green
}

# Apply permissions
Set-FolderPermissions -FolderPath "D:\Data\HR"          -Group "CORP\HR-Staff"         -Permission "Modify"
Set-FolderPermissions -FolderPath "D:\Data\Accounting"  -Group "CORP\Accounting-Staff" -Permission "Modify"
```

##### Verify permissions (GUI method)

After running the script, verify the permissions are correct using File Explorer:

1. Open **File Explorer** and navigate to `D:\Data`.
2. Right-click **HR** → **Properties** → **Security** tab.
3. You should see:
   - `BUILTIN\Administrators` — Full control
   - `NT AUTHORITY\SYSTEM` — Full control
   - `CORP\HR-Staff` — Modify
4. There should be **no** entry for `Accounting-Staff` or `Domain Users`.
5. Repeat the check for the **Accounting** folder.

**[SCREENSHOT: Security tab of D:\Data\HR showing HR-Staff Modify permissions only]**

**[SCREENSHOT: Security tab of D:\Data\Accounting showing Accounting-Staff Modify permissions only]**

##### Verify permissions (PowerShell)

```powershell
# View the effective NTFS access rules on each folder
Get-Acl -Path "D:\Data\HR"         | Format-List
Get-Acl -Path "D:\Data\Accounting" | Format-List

# Confirm the network shares are visible
Get-SmbShare | Where-Object { $_.Name -in @("HR","Accounting","Users") }
```

> ✅ **Test tip**: Once a domain user is created and added to `HR-Staff`, log into `LAB-CLIENT01` as that user and try to browse to `\\LAB-DC01\Accounting` — you should get an "Access Denied" error, confirming the isolation is working correctly.

![Server Manager shares view showing Users, HR, and Accounting shares](static/chapter_1/PXL_20250902_162411870.jpg)

---

## Step 5 – Promote the server to a domain controller

Configure Active Directory Domain Services and create the new forest using the GUI wizard first. Keep the PowerShell equivalent as an optional shortcut once you are comfortable with the GUI steps.

#### PowerShell method (Quick)

```powershell
Install-ADDSForest -DomainName "corp.lab" -DomainNetbiosName "CORP" -SafeModeAdministratorPassword (Read-Host -AsSecureString 'DSRM Password') -Force
```

#### GUI method (Step-by-step)

1. **Deployment Configuration:**
   - On the first screen of the **Active Directory Domain Services Configuration Wizard**, select **Add a new forest**.
   - For **Root domain name**, enter `corp.lab`.
   - Click **Next**.

**[SCREENSHOT: Deployment Configuration showing Add a new forest and corp.lab]**

2. **Domain Controller Options:**
   - Keep the **Forest functional level** and **Domain functional level** at **Windows Server 2016** (or the highest version available).
   - Ensure **Domain Name System (DNS) server** and **Global Catalog (GC)** are checked.
   - Enter and confirm a **Directory Services Restore Mode (DSRM) password** (this is for emergency repairs; record it in your lab notes).
   - Click **Next**.

**[SCREENSHOT: Domain Controller Options with DNS, GC, and DSRM password entered]**

3. **DNS Options:**
   - You may see a warning about DNS delegation. This is normal in a new lab forest. Click **Next**.

**[SCREENSHOT: DNS Options delegate warning screen]**

4. **Additional Options:**
   - Confirm the **NetBIOS domain name** is `CORP`. Click **Next**.

**[SCREENSHOT: Additional Options screen showing NetBIOS name CORP]**

5. **Paths:**
   - Keep the default paths for the **Database folder**, **Log files folder**, and **SYSVOL folder**. Click **Next**.

**[SCREENSHOT: Paths configuration screen]**

6. **Review Options:**
   - Review your selections. Click **Next**.

**[SCREENSHOT: Review Options summary screen]**

7. **Prerequisites Check:**
   - The wizard will verify that your server is ready. If all checks pass (you see a green checkmark at the top), click **Install**.
   - The server will begin the promotion process and will **automatically restart** when finished.

**[SCREENSHOT: Prerequisites Check showing successfully passed message]**

The server restarts automatically. Sign back in when prompted and ensure the NIC configuration still reflects the `172.16.10.x` address.

![Active Directory configuration wizard summary](static/chapter_1/PXL_20250902_162420002.jpg)

### Configure DNS and reverse lookup zone

You can configure DNS using the GUI first, then capture the PowerShell equivalent if you want an automation path. Both methods are provided below.

#### PowerShell method (Quick)

```powershell
# Create reverse lookup zone for the lab network
Add-DnsServerPrimaryZone -NetworkId "172.16.10.0/24" -ReplicationScope "Forest"

# Add PTR record for the domain controller
Add-DnsServerResourceRecordPtr -Name "10" -ZoneName "10.16.172.in-addr.arpa" -PtrDomainName "LAB-DC01.corp.lab"
```

#### GUI method (Step-by-step)

1. Open **Server Manager**, click **Tools** in the top-right corner, and select **DNS**.

**[SCREENSHOT: Server Manager Tools menu with DNS highlighted]**

2. In the **DNS Manager** console, expand **LAB-DC01** in the left pane.

3. **Create Reverse Lookup Zone:**
   - Right-click **Reverse Lookup Zones** and select **New Zone**.

   **[SCREENSHOT: Right-click menu on Reverse Lookup Zones]**
   - Click **Next** on the Welcome screen.
   - Select **Primary zone** and ensure **Store the zone in Active Directory** is checked. Click **Next**.

   **[SCREENSHOT: Zone Type selection with Primary zone selected]**
   - Select **To all DNS servers running on domain controllers in this domain: corp.lab**. Click **Next**.
   - Choose **IPv4 Reverse Lookup Zone** and click **Next**.

   **[SCREENSHOT: Reverse Lookup Zone type selection]**
   - For **Network ID**, enter `172.16.10` (this represents the 172.16.10.0/24 network). Click **Next**.

   **[SCREENSHOT: Network ID entry field with 172.16.10 entered]**
   - Select **Allow only secure dynamic updates (recommended for Active Directory)**. Click **Next**.
   - Click **Finish**.

4. **Add PTR Record for Domain Controller:**
   - Expand **Reverse Lookup Zones** and click on **10.16.172.in-addr.arpa**.
   - Right-click in the right pane and select **New Pointer (PTR)**.

   **[SCREENSHOT: New PTR record dialog]**
   - For **Host IP Address**, enter `172.16.10.10`.
   - Click **Browse** and navigate to **corp.lab** → **LAB-DC01**, or manually type `LAB-DC01.corp.lab` in the **Host name** field.
   - Click **OK**, then **OK** again to create the record.

   **[SCREENSHOT: Completed PTR record in DNS Manager]**

5. **Verify Forward Lookup Zones:**
   - Expand **Forward Lookup Zones** and click on **corp.lab**.
   - You should see Host (A) records for **LAB-DC01** and various service records (\_msdcs, \_sites, \_tcp, \_udp).

   **[SCREENSHOT: Forward lookup zone showing corp.lab records]**

> 📘 **Note**: Reverse DNS is essential for domain controllers. Group Policy replication and other AD services use PTR records to verify server identity and prevent rogue servers from joining the domain.

### Configure DHCP scope (isolated lab network)

After DNS is configured, set up DHCP to automatically assign IP addresses to client machines.

#### PowerShell method (Quick)

```powershell
# Authorize this DHCP server in Active Directory
Add-DhcpServerInDC -DnsName "LAB-DC01.corp.lab" -IpAddress 172.16.10.10

# Create a DHCP scope for client machines (.50-.100 range)
Add-DhcpServerv4Scope -Name "Lab Clients" -StartRange 172.16.10.50 -EndRange 172.16.10.100 -SubnetMask 255.255.255.0

# Configure DHCP options (DNS domain, DNS server, default gateway)
Set-DhcpServerv4OptionValue -DnsDomain "corp.lab" -DnsServer 172.16.10.10 -Router 172.16.10.1
```

#### GUI method (Step-by-step)

1. **Complete DHCP Post-Installation Configuration:**
   - In **Server Manager**, look for the yellow warning flag in the top-right corner (notifications).
   - Click the flag, then click **Complete DHCP configuration**.

   **[SCREENSHOT: Server Manager notification flag with DHCP post-deployment configuration]**
   - Click **Next** on the Description screen.
   - On the **Authorization** screen, select **Use the following user's credentials**, ensure **CORP\Administrator** is shown, and click **Commit**.

   **[SCREENSHOT: DHCP Post-Install Configuration Wizard - Authorization]**
   - Click **Close** when the configuration is complete.

2. **Open DHCP Management Console:**
   - In **Server Manager**, click **Tools** → **DHCP**.

   **[SCREENSHOT: Server Manager Tools menu with DHCP highlighted]**

3. **Verify DHCP Server Authorization:**
   - In the **DHCP** console, expand **LAB-DC01.corp.lab**.
   - You should see **IPv4** and **IPv6** with green checkmarks (authorized).

   **[SCREENSHOT: DHCP console showing authorized server with green icons]**

4. **Create a New Scope:**
   - Right-click **IPv4** and select **New Scope**.

   **[SCREENSHOT: Right-click menu on IPv4 with New Scope highlighted]**
   - Click **Next** on the Welcome screen.
   - **Scope Name**: Enter `Lab Clients`. Description (optional): `DHCP pool for lab workstations`. Click **Next**.

   **[SCREENSHOT: Scope Name dialog]**
   - **IP Address Range**:
     - Start IP address: `172.16.10.50`
     - End IP address: `172.16.10.100`
     - Length: `24`
     - Subnet mask: `255.255.255.0`
     - Click **Next**.

   **[SCREENSHOT: IP Address Range configuration]**
   - **Add Exclusions and Delay**: Leave blank (no exclusions needed for this lab). Click **Next**.
   - **Lease Duration**: Keep default **8 days**. Click **Next**.

   **[SCREENSHOT: Lease Duration dialog]**
   - **Configure DHCP Options**: Select **Yes, I want to configure these options now**. Click **Next**.

5. **Configure DHCP Options:**
   - **Router (Default Gateway)**: Enter `172.16.10.1` and click **Add**. Click **Next**.

   **[SCREENSHOT: Router/Default Gateway configuration with 172.16.10.1]**
   - **Domain Name and DNS Servers**:
     - Parent domain: Should show `corp.lab`
     - Server name: Enter `LAB-DC01` or `172.16.10.10`
     - Click **Resolve** to verify it resolves to `172.16.10.10`
     - Click **Add**
     - Click **Next**.

   **[SCREENSHOT: DNS Servers configuration with 172.16.10.10 added]**
   - **WINS Servers**: Leave blank. Click **Next**.
   - **Activate Scope**: Select **Yes, I want to activate this scope now**. Click **Next**.

   **[SCREENSHOT: Activate Scope dialog]**
   - Click **Finish**.

6. **Verify DHCP Configuration:**
   - In the DHCP console, expand **IPv4** → **Scope [172.16.10.0] Lab Clients**.
   - Click on **Address Pool** to see the available range (172.16.10.50 - 172.16.10.100).
   - Click on **Scope Options** to verify:
     - 003 Router: 172.16.10.1
     - 006 DNS Servers: 172.16.10.10
     - 015 DNS Domain Name: corp.lab

   **[SCREENSHOT: DHCP scope showing Address Pool and Scope Options]**

> ✅ **Scope design tip**: Keep DHCP leases away from statically-assigned addresses (DC, future servers). Reserving `.1-.49` for infrastructure gives you room to grow.

### Create initial OU structure

```powershell
# Create top-level organizational unit
New-ADOrganizationalUnit -Name "Corp" -Path "DC=corp,DC=lab"

# Create sub-OUs for different resource types
New-ADOrganizationalUnit -Name "Servers" -Path "OU=Corp,DC=corp,DC=lab"
New-ADOrganizationalUnit -Name "Workstations" -Path "OU=Corp,DC=corp,DC=lab"
New-ADOrganizationalUnit -Name "Service Accounts" -Path "OU=Corp,DC=corp,DC=lab"
```

Verify the OU structure in **Active Directory Users and Computers** (dsa.msc):

```powershell
# Open Active Directory Users and Computers
dsa.msc
```

![Group Policy Management Console showing freshly created OUs](static/chapter_1/PXL_20250902_162427968.jpg)

> 📘 **Next chapter preview**: We'll populate the central store with baseline audit policies once the client is joined to the domain, then automate the repeatable parts with PowerShell.

---

## Step 6 – Build the Windows 11 Client VM

Create another VM in VirtualBox with the following profile:

| Setting     | Value                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| Name        | `LAB-WIN11`                                                                                          |
| Type        | Microsoft Windows                                                                                    |
| Version     | Windows 11 (64-bit)                                                                                  |
| Base memory | **4096 MB**                                                                                          |
| Processors  | **2 vCPU**                                                                                           |
| Display     | Start with 3D acceleration **disabled**; enable it later only if the VM is stable and needs it      |
| Network     | Adapter 1 = **Internal Network (LabNet)** (leave **cable disconnected** box ticked for installation) |
| Storage     | 250 GB dynamically allocated VDI + `Windows_11_Enterprise.iso` mounted                               |

![VirtualBox client VM creation wizard summary](static/chapter_1/PXL_20250902_162411870.jpg)

### Install Windows 11

1. Power on `LAB-WIN11`, choose language preferences, then select **I don't have a product key**.
2. Pick **Windows 11 Enterprise**, accept the licence, and choose **Custom: Install Windows only**.
3. Install onto the available disk and complete the OOBE. When prompted to connect to the network, keep the adapter disconnected so you can create a local administrator account.
4. Once the desktop loads, install the VirtualBox Guest Additions for better drivers (Devices ▸ Insert Guest Additions CD Image).

> 🖱️ **VirtualBox focus tip**: The Windows 11 installer can appear to stall if the VM window loses focus. Keep the mouse inside the VirtualBox window during setup and click back into the guest if the installer seems unresponsive.

> 🔐 **Privacy hint**: During OOBE, decline sending diagnostic data and disable optional advertising IDs to keep the lab clean.

### Patch and capture the clean state

1. Shut down the VM, edit network settings to **reconnect** the Internal adapter (`LabNet`).
2. Boot the VM and configure the IP stack to use DHCP (default). Verify it receives an address from the server by running:

```powershell
# Display network configuration (should show DHCP assigned from 172.16.10.50-.100 range)
ipconfig /all

# Test connectivity to the domain controller
Test-Connection -ComputerName 172.16.10.10 -Count 4
```

3. Run **Settings ▸ Windows Update** until no additional patches remain.
4. Install PowerShell 7 for advanced scripting capabilities:

```powershell
# Install PowerShell 7 using winget
winget install --id Microsoft.PowerShell --accept-package-agreements --accept-source-agreements
```

5. Create a VM snapshot in VirtualBox labelled `Baseline Patched` so you can revert quickly during experiments (Machine ▸ Take Snapshot).

![Windows 11 network status showing DHCP configuration](static/chapter_1/PXL_20250902_162400670.jpg)

---

## Step 7 – Back up your virtual machines

Maintaining golden images saves hours of rebuild time. Follow this workflow after large configuration milestones:

1. Shut down both `LAB-DC01` and `LAB-WIN11` cleanly (`Start ▸ Power ▸ Shut down`).
2. In File Explorer browse to the VirtualBox VM folder (default `C:\Users\<you>\VirtualBox VMs`).
3. Copy each VM directory to an external drive or a `backups\chapter_1` folder, keeping the folder names intact.
4. Compress the copies (`Right-click ▸ Send to ▸ Compressed (zipped) folder`) to save space.

For scripted backups, from an elevated PowerShell session run:

```powershell
# Define source and destination paths with date stamp
$source = "$env:USERPROFILE\VirtualBox VMs"
$dest = "D:\VMBackups\$(Get-Date -Format 'yyyyMMdd')"

# Create backup directory
New-Item -Path $dest -ItemType Directory -Force | Out-Null

# Copy VM folders (this may take 10-20 minutes depending on disk speed)
Write-Host "Backing up LAB-DC01..." -ForegroundColor Cyan
Copy-Item -Path "$source\LAB-DC01" -Destination $dest -Recurse

Write-Host "Backing up LAB-WIN11..." -ForegroundColor Cyan
Copy-Item -Path "$source\LAB-WIN11" -Destination $dest -Recurse

Write-Host "Backup complete: $dest" -ForegroundColor Green
```

---

## Step 8 – Initial Active Directory tasks

With both VMs running and fully patched:

1. Sign into `LAB-DC01` as `CORP\Administrator`.
2. Open **Active Directory Users and Computers** and confirm the OU structure created earlier exists.
3. Create a helpdesk admin account via PowerShell:

```powershell
# Create a user account for lab testing
New-ADUser -Name "LAB Helpdesk" -SamAccountName "lab.helpdesk" -UserPrincipalName "lab.helpdesk@corp.lab" -AccountPassword (Read-Host -AsSecureString 'Password') -Enabled $true -Path "OU=Workstations,OU=Corp,DC=corp,DC=lab"

# Add the account to Domain Admins group for administrative access
Add-ADGroupMember -Identity "Domain Admins" -Members "lab.helpdesk"
```

4. Join the client to the domain (on `LAB-WIN11`, run PowerShell as Administrator):

```powershell
# Join the computer to the corp.lab domain
Add-Computer -DomainName corp.lab -Credential corp\Administrator -Restart
```

When prompted, enter the domain administrator password.

5. After the reboot, sign in with `corp\lab.helpdesk` and verify network shares are accessible:

```powershell
# Test access to the Data share
Test-Path \\LAB-DC01\Data

# View active SMB connections
Get-SmbConnection

# Map the Data share as a network drive (optional)
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\LAB-DC01\Data" -Persist
```

You're now ready to begin authoring PowerShell audit scripts and Group Policy baselines in the next chapter.

---

## Verification checklist

Before moving to the next chapter, verify your lab environment:

```powershell
# On LAB-DC01, run these verification commands:

# Check domain controller status
Get-ADDomainController

# Verify DNS is responding
nslookup LAB-DC01.corp.lab

# Test reverse DNS lookup
nslookup 172.16.10.10

# Check DHCP scope status
Get-DhcpServerv4Scope

# Verify Active Directory replication
repadmin /replsummary

# List all domain users
Get-ADUser -Filter * | Select-Object Name, SamAccountName
```

---

## Troubleshooting quick hits

- **VM won't start or is extremely unstable**: Ensure Hyper-V-related features are disabled when using VirtualBox on Windows hosts. Check `OptionalFeatures.exe` for **Hyper-V**, **Windows Hypervisor Platform**, and **Virtual Machine Platform**. Also review **Core isolation / Memory Integrity** in Windows Security. Reboot after making changes.
- **No DHCP lease on client**: Confirm Adapter 2 on `LAB-DC01` is set to `LabNet` in VirtualBox settings. Restart the `DHCP Server` service (`Restart-Service DHCPServer`) and run `ipconfig /renew` on the client.
- **No internet on the server during setup**: Confirm Adapter 1 on `LAB-DC01` is set to **NAT** and that **Cable Connected** is enabled in VirtualBox. During the first build, leave Adapter 2 disconnected or absent until Windows Update is finished.
- **DNS resolution fails**: Run `dcdiag /test:dns /v` on the server; check that the reverse lookup zone exists and contains PTR records. Verify the DNS service is running: `Get-Service DNS`.
- **Domain join fails**: Ensure the client can ping `172.16.10.10` and resolve `corp.lab`. Check the client's DNS settings point to `172.16.10.10`.
- **Slow performance or crashing while opening Settings/Server Manager**: Start with only the server VM running, keep the server at `2 vCPU` and `4096 MB` RAM, use `VBoxSVGA`, keep **3D acceleration disabled**, reduce the guest display resolution, and close other heavy host applications. If VirtualBox still feels unstable, the Windows hypervisor layer on the host is the next thing to investigate.

---

Next up: we will craft reusable PowerShell functions to audit Active Directory, build compliance reports, and deploy them via Group Policy.
