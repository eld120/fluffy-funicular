1 of 16

Powershell for Helpdesk
This manual is for those who want to be experts in a Microsoft Business I.T. Department. This manual is going to walk you through setting up a Virtual Windows Domain on your home workstation. Then teach you PowerShell coding and Best Practices to audit your network. You will then be able to use these scripts at your office.

Prerequisites
The recommended specs for your host workstation is 8 CPU's, 16 Gb of RAM and 500 Gb of free disk space. Also: Add Download Virtual Box VM software, current version of Windows Server and Client Pro trial versions.

Setting up/Installing Software
The order to install the software is as follows:

1. Virtual Box
2. Windows Server Virtual Machine (VM)
3. Windows Client

Virtual Box
[Insert download and installation procedures]

Windows Server
[Insert steps to download current trial version of Windows Server]

Configuration of Windows Server VM
When you are setting up the server VM, assign 2 CPU's, 4 Gb RAM, 250 Gb of Drive Space (Add more if needed), 2 NIC's, (1 NIC is to be configured as NAT, 1 NIC is to be Internal Only)

2 of 16

Hardware: Drives

- 2 Drives (1 drive 100 GB, 1 drive 250)

Configure / Install Server
During the installation of the Server, install the following Roles and Services:

- Active Directory Services
- Domain Controller
- Router
- DNS
- DHCP
- Group Policy (Manager?)
- Remote Admin Tools
- File Services
- File / Print Server

[Insert Screen Shots]

Note: Accept any additional Roles or Services suggested by the system.
The name of the Server should be the major role or service running on it.

Configuring Roles and Services

Domain Controller

- Select All Options - default settings

Router

- Default Options

DHCP

- The scope needs to be different from the host network. [Insert screenshots to find out how]

DNS

- Make sure you set up the reverse DNS for Group Policies. Group Policies will NOT replicate between servers. Domain Controllers use reverse DNS for security purposes to prevent rogue servers from pretending to be domain controllers.

Group Policies

- Default settings. We will change them as we set up our PowerShell audit scripts.

File / Print Services

- Create two directories: `D:\Users` and `D:\Data`.
- If you did not create a second partition, create one and move these folders there. These folders need to be "Shared". [Insert procedure]

Group Policies (File Server Repository)

- Now that the file services are configured, go back and set up a `SYS` and `VOL1` on the D: drive and configure a Group Policy Repository. [Insert Procedures]

Active Directory

- We'll work on this after the client is set up.

Windows Client

- [Insert the steps to download the current Windows Pro trial software]

Configuration of Client VM

- [screenshots of each prompt]
- When you setup the Client VM assign: 2 CPUs, 4 GB RAM, 250 GB hard drive space, 1 NIC (Internal Network Only) - disconnected

4 of 16

Installation of Client
During the installation of the Windows Client do not join it to the domain. Once the installation is complete, shut it down. Connect the NIC in the VM settings. Turn on the client and login. If you can't access the internet, check the Router and DNS settings. Below are the settings that should get you online. Your host Network may be different. [Insert Screen Shots]

Once the Server and client are fully patched (no more updates needed), create a backup of each VM. Follow these steps:

1. Shut down both VMs
2. Go to the folders where the VM files are stored
3. Select the folders
4. Press Ctrl + C (copy)
5. Press Ctrl + V (paste)

Configure Active Directory
Now turn on the Server, then login. Next turn on the client. [Insert Screenshots]

Switch to the Server. We are going to set up Active Directory. When the system configures A.D., it uses containers. We use Organizational Units and Organizations. PowerShell and Group Policies use these as well.
