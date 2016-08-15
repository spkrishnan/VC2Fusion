# VC2Fusion

Enterprise campus networks that have two-tier traditional architecture with MC-LAG at the core or distribution and Virtual Chassis at the access layer can be converted to Junos Fusion.

The converted Virtual Chassis is called a Satellite Device Cluster in Junos Fusion Enterprise. When migrating from traditional architecture to Junos Fusion Enterprise, the migration need not be done for the whole system. Enterprise can slowly migrate one or few Virtual Chassis to Satellite Device cluster in Junos Fusion Enterprise. Rest of the closets or Virtual Chassis can function in traditional mode. 

This project helps customers to migrate a Virtual Chassis to Satellite Device cluster in Junos Fusion Enterprise. Here is an example of changes made by this script

- Enable LLDP on AD1, AD2 and the Virtual Chassis
      - set protocols lldp interface all
      - delete protocols lldp disable

- Delete current configuration on the cascade port
      - delete interfaces xe-2/1/1
      - delete interfaces xe-3/1/1

- Change the interface to a cascade port
      - set interfaces xe-2/1/1 cascade-port
      - set interfaces xe-3/1/1 cascade-port

- Set chassis satellite configuration for the cluster
      - set chassis satellite-management cluster Closet1 cluster-id 10
      - set chassis satellite-management cluster Closet1 cascade-ports xe-2/1/1
      - set chassis satellite-management cluster Closet1 cascade-ports xe-3/1/1
      - set chassis satellite-management cluster Closet1 fpc 120 member-id 0
      - set chassis satellite-management cluster Closet1 fpc 120 system-id 84:b5:9c:c2:79:e0
      - set chassis satellite-management cluster Closet1 fpc 121 member-id 1
      - set chassis satellite-management cluster Closet1 fpc 121 system-id 10:0e:7e:a1:3f:20
      - set chassis satellite-management cluster Closet1 fpc 122 member-id 2
      - set chassis satellite-management cluster Closet1 fpc 122 system-id 84:0e:7e:a1:2f:10
      - set chassis satellite-management auto-satellite-conversion satellite 120
      - set chassis satellite-management auto-satellite-conversion satellite 121
      - set chassis satellite-management auto-satellite-conversion satellite 121


### EXECUTING THIS SCRIPT WILL CAUSE OUTAGE FOR THE VIRTUAL CHASSIS. This script will also make changes to the Aggregation Devices. Please analyze the consequences and take necessary precaustions before executing the script ###

Steps to initiate the migration

Step1: Ensure that you have PYeZ packages installed

Step2: Ensure that the Aggregation Devices are enabled for Junos Fusion Enterprise

Step3: Copy all files in this project in one directory

Step4: Edit "data_input.yml" file and provide details about "AD1", "AD2", Username, Password, Home Directory

Step5: Execute the python script to convert a Virtual Chassis to Satellite Device Cluster 
- python v2fconverter.py Virtual-Chassis-IP Cluster-Name Cluster-ID Starting-FPC-Number-for-the-Cluster
      - For example, "python v2fconverter.py '10.105.5.134' Closet1 10 120" 
       
       
       
       
