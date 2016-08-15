# VC2Fusion

Enterprise campus networks that have two-tier traditional architecture with MC-LAG at the core or distribution and Virtual Chassis at the access layer can be converted to Junos Fusion.

The converted Virtual Chassis is called a Satellite Device Cluster in Junos Fusion Enterprise. When migrating from traditional architecture to Junos Fusion Enterprise, the migration need not be done for the whole system. Enterprise can slowly migrate one or few Virtual Chassis to Satellite Device cluster in Junos Fusion Enterprise. Rest of the closets or Virtual Chassis can function in traditional mode. 

This project helps customers to migrate a Virtual Chassis to Satellite Device cluster in Junos Fusion Enterprise. This script will make the following changes.

- Enable LLDP on AD1, AD2 and the Virtual Chassis
      set protocols lldp interface all
- delete current configuration on the cascade port
      delete interfaces <interface name>
- Change the interface to a cascade port
      set interfaces xe-2/1/1 cascade-port
- Set chassis satellite configuration for the cluster
      set chassis satellite-management cluster <Cluster Name> cluster-id <Cluster ID>
      set chassis satellite-management cluster <Cluster Name> cascade-ports <Cascade Port>
      set chassis satellite-management cluster <Cluster Name> fpc <FPC ID> member-id <ID>
      set chassis satellite-management cluster <Cluster Name> fpc <FPC ID> system-id <MAC Address>
      set chassis satellite-management auto-satellite-conversion satellite <FPC ID>



### EXECUTING THIS SCRIPT WILL CAUSE OUTAGE FOR THE VIRTUAL CHASSIS. This script will also make changes to the Aggregation Devices. Please analyze the consequences and take necessary precaustions before executing the script ###

Steps to initiate the migration

Step1: Ensure that you have PYeZ packages installed

Step2: Ensure that the Aggregation Devices are enabled for Junos Fusion Enterprise

Step3: Copy all files in this project in one directory

Step4: Edit "data_input.yml" file and provide details about "AD1", "AD2", Username, Password, Home Directory

Step5: Execute the python script to convert a Virtual Chassis to Satellite Device Cluster 
       python v2fconverter.py <Virtual Chassis IP> <Cluster Name> <Cluster ID> <Starting FPC Number for the Cluster>
       
