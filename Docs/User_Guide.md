# PinokioCloud User Guide

## **Getting Started**

### **1. Launch the Application**
1. Open `launcher.ipynb` in Jupyter Lab or Jupyter Notebook
2. Execute all cells in order to initialize the system
3. The interface will load with four main tabs

### **2. Navigate the Interface**
- **🔍 Discover**: Browse available applications with search and filtering
- **📚 My Library**: Manage installed applications
- **🌐 Active Tunnels**: View running applications with external URLs
- **💻 Terminal**: View system logs and debug information

## **Application Lifecycle**

### **Installing Applications**
1. Use the **Discover** tab to find applications
2. Click **Install** to begin the installation process
3. Monitor progress in the **Terminal** tab
4. Application will appear in **My Library** when complete

### **Starting Applications**
1. Go to **My Library** tab
2. Find your installed application
3. Click **Start** to launch
4. If the application has a web interface, a URL will appear in **Active Tunnels**

### **Accessing Applications**
1. Check **Active Tunnels** tab for running applications
2. Click on tunnel URLs to access web interfaces
3. Multiple applications can run simultaneously

### **Stopping Applications**
1. Use **My Library** or **Active Tunnels** tabs
2. Click **Stop** to terminate the application
3. Tunnel URLs will be cleaned up automatically

### **Uninstalling Applications**
1. Go to **My Library** tab
2. Click **Uninstall** for the desired application
3. Environment and files will be completely removed

## **Advanced Features**

### **Application Certification**
- Some applications may require certification for full functionality
- Use **Certify** button when available
- Certification status is tracked in the system

### **Error Handling**
- All errors are displayed with full technical details in the **Terminal** tab
- The system remains stable even when individual applications fail
- Failed applications are marked with ERROR status for easy identification

### **System Status**
- The interface shows real-time status of all applications
- Busy states prevent conflicting operations
- All operations are queued and processed sequentially

## **Troubleshooting**

### **Common Issues**
- **Application won't start**: Check Terminal tab for error messages
- **No tunnel URL**: Some applications may not have web interfaces
- **Installation fails**: Verify system requirements and available resources

### **Getting Help**
- All system operations are logged in the **Terminal** tab
- Error messages include complete technical details
- The system is designed to provide maximum debugging information

## **System Requirements**
- Python 3.8+
- Jupyter Lab or Jupyter Notebook
- Internet connection for installations
- Sufficient disk space for applications