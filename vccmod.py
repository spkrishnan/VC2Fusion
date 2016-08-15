import yaml
from jinja2 import Template
import logging
import sys
import time
import os.path
from lxml import etree as ET
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from logging import *

vccAd1=''
vccAd2=''
vccUser=''
vccPassword=''
vccDir=''
vccTime=''

def readData():
	global vccAd1
	global vccAd2
	global vccUser
	global vccPassword
	global vccDir
	global vccTime
		
	with open('data_input.yml') as vccDatafhandle:
                vccDatafile = yaml.load(vccDatafhandle)
        vccAd1 = vccDatafile['AD1']
        vccAd2 = vccDatafile['AD2']
        vccUser = vccDatafile['user']
        vccPassword = vccDatafile['password']
        vccDir = vccDatafile['HomeDir'] + '/backup'
        vccTime = time.strftime("%Y%m%d-%H%M%S")
        vccDatafhandle.close()	


def backupConfig(vccCloset):
	readData()	
	vccAd1handle = Device(host=vccAd1,user=vccUser,password=vccPassword)
	vccAd2handle = Device(host=vccAd2,user=vccUser,password=vccPassword)
	vccClosethandle = Device(host=vccCloset,user=vccUser,password=vccPassword)	

	#Open connection to the switches
	vccAd1handle.open()
	vccAd2handle.open()
	vccClosethandle.open()


	#Create Backup Directory if it does not exist
	if not os.path.exists(vccDir):
		os.makedirs(vccDir)


	#Get configurations from the switches
	vccAd1config = vccAd1handle.rpc.get_config(options={'format':"text"})
	vccAd2config = vccAd2handle.rpc.get_config(options={'format':"text"})
	vccClosetconfig = vccClosethandle.rpc.get_config(options={'format':"text"})


        #Close connection to the switches
        vccAd1handle.close()
        vccAd2handle.close()
        vccClosethandle.close()


	#open files for backup
	vccFtemp = os.path.join(vccDir, vccAd1+'-'+vccTime+'.conf')
	vccAD1file = open(vccFtemp, "w")
	vccFtemp = os.path.join(vccDir, vccAd2+'-'+vccTime+'.conf')
	vccAD2file = open(vccFtemp, "w")
	vccFtemp = os.path.join(vccDir, vccCloset+'-'+vccTime+'.conf')
	vccClosetfile = open(vccFtemp, "w")

	#Write configs to files
	vccAD1file.write(ET.tostring(vccAd1config))
	vccAD2file.write(ET.tostring(vccAd2config))
	vccClosetfile.write(ET.tostring(vccClosetconfig))
	


	#Close files
	vccAD1file.close()
	vccAD2file.close()
	vccClosetfile.close()
		


def getSystemid(vccCloset):
	vccSysid = dict()	
	readData()
	vccClosethandle = Device(host=vccCloset,user=vccUser,password=vccPassword)
	
	#Open Connectino to the Virtual Chassis
	vccClosethandle.open()
	vccSystemid = vccClosethandle.rpc.get_chassis_mac_addresses()
	vccSystree = vccSystemid.getroottree()
	
	for child in vccSystree.getroot():
		child.find('chassis-mac-information')
		for x in child.iter('fpc-mac-information'):
			x_slot = x.find('slot')
			x_mac = x.find('mac-address')
			vccSysid[x_slot.text] = x_mac.text

	
	vccClosethandle.close()
	return vccSysid		

def fpcSidmap(vccSysid, fpcStart):
	fpcSys = dict()
	for key in vccSysid.keys():
		fpcId = int(key) + fpcStart
		fpcSys[fpcId] = vccSysid[key]
	return fpcSys


def checkEnlldp(vccCloset):
        readData()
        vccAd1handle = Device(host=vccAd1,user=vccUser,password=vccPassword)
        vccAd2handle = Device(host=vccAd2,user=vccUser,password=vccPassword)
        vccClosethandle = Device(host=vccCloset,user=vccUser,password=vccPassword)

        #Open connection to the switches
        vccAd1handle.open()
        vccAd2handle.open()
        vccClosethandle.open()
	
	vccAd1lldp = vccAd1handle.rpc.get_lldp_neighbors_information()
        vccAd2lldp = vccAd2handle.rpc.get_lldp_neighbors_information()
        vccClosetlldp = vccClosethandle.rpc.get_lldp_neighbors_information()


	vccAd1lldptree = vccAd1lldp.getroottree()
	vccAd2lldptree = vccAd2lldp.getroottree()
	vccClosetlldptree = vccClosetlldp.getroottree()


        vccAd1config = vccAd1handle.rpc.get_config()
        vccAd2config = vccAd2handle.rpc.get_config()
        vccClosetconfig = vccClosethandle.rpc.get_config()


        vccAd1Conftree = vccAd1config.getroottree()
        vccAd2Conftree = vccAd2config.getroottree()
        vccClosetConftree = vccClosetconfig.getroottree()



	enLldpcmd = 'set protocols lldp interface all'
	disLldpdiscmd = 'delete protocols lldp disable'


	#Check AD1 and enable LLDP if not enabled
	vccAd1lldptreenbrs = vccAd1lldptree.getroot().find('lldp-neighbors-information') 
        if vccAd1lldptreenbrs.find('lldp-neighbor-information') is None:
                print "LLDP disabled on AD1. Enabling LLDP"
		vccAd1Chandle = Config(vccAd1handle)
		vccAd1Chandle.load(enLldpcmd, format='set')
                if vccAd1Conftree.find('configuration/protocols/lldp/disable') is not None:
                        vccAd1Chandle.load(disLldpdiscmd, format='set')
		vccAd1Chandle.commit()
	else:
		print "LLDP already enabled on AD1"

        #Check AD2 and enable LLDP if not enabled
        vccAd2lldptreenbrs = vccAd2lldptree.getroot().find('lldp-neighbors-information') 
        if vccAd2lldptreenbrs.find('lldp-neighbor-information') is None:
                print "LLDP disabled on AD2. Enabling LLDP"
                vccAd2Chandle = Config(vccAd2handle)
                vccAd2Chandle.load(enLldpcmd, format='set')
                if vccAd2Conftree.find('configuration/protocols/lldp/disable') is not None:
                        vccAd2Chandle.load(disLldpdiscmd, format='set')
		vccAd2Chandle.commit()
	else:
		print "LLDP already enabled on AD2"
                             


        #Check Closet and enable LLDP if not enabled 
        vccClosetlldptreenbrs = vccClosetlldptree.getroot().find('lldp-neighbors-information')
        if vccClosetlldptreenbrs.find('lldp-neighbor-information') is None:
                print "LLDP disabled on Closet switch. Enabling LLDP"
                vccClosetChandle = Config(vccClosethandle)
                vccClosetChandle.load(enLldpcmd, format='set')
                if vccClosetConftree.find('configuration/protocols/lldp/disable') is not None:
                        vccClosetChandle.load(disLldpdiscmd, format='set')
		vccClosetChandle.commit()
	else:
		print "LLDP already enabled on the closet switch"



        #Close connection to the switches
        vccAd1handle.close()
        vccAd2handle.close()
        vccClosethandle.close()



def findCport(vccCloset):
	readData()
        vccAd1handle = Device(host=vccAd1,user=vccUser,password=vccPassword)
        vccAd2handle = Device(host=vccAd2,user=vccUser,password=vccPassword)
        vccClosethandle = Device(host=vccCloset,user=vccUser,password=vccPassword)

        #Open connection to the switches
        vccAd1handle.open()
        vccAd2handle.open()
        vccClosethandle.open()

        vccAd1lldp = vccAd1handle.rpc.get_lldp_neighbors_information()
        vccAd2lldp = vccAd2handle.rpc.get_lldp_neighbors_information()
        vccClosetlldp = vccClosethandle.rpc.get_lldp_neighbors_information()


        vccAd1lldptree = vccAd1lldp.getroottree()
        vccAd2lldptree = vccAd2lldp.getroottree()
        vccClosetlldptree = vccClosetlldp.getroottree()

	

	vccAd1lldplocal = vccAd1handle.rpc.get_lldp_local_info()
        vccAd2lldplocal = vccAd2handle.rpc.get_lldp_local_info()
        vccClosetlldplocal = vccClosethandle.rpc.get_lldp_local_info()


	vccAd1lldplocaltree = vccAd1lldplocal.getroottree()
        vccAd2lldplocaltree = vccAd2lldplocal.getroottree()
        vccClosetlldplocaltree = vccClosetlldplocal.getroottree()


	ad1Sysname = vccAd1lldplocaltree.find('lldp-local-info/lldp-local-system-name').text
	ad2Sysname = vccAd2lldplocaltree.find('lldp-local-info/lldp-local-system-name').text
	adCportdict = dict()
	adCportdict['AD1'] = []
	adCportdict['AD2'] = []
        vccClosetlldptreenbrs = vccClosetlldptree.getroot().find('lldp-neighbors-information')

        for child in vccClosetlldptreenbrs.iter('lldp-neighbor-information'):
		if child.find('lldp-remote-system-name').text == ad1Sysname:
			adCportdict['AD1'].append(child.find('lldp-remote-port-description').text)
		if child.find('lldp-remote-system-name').text == ad2Sysname:
			adCportdict['AD2'].append(child.find('lldp-remote-port-description').text)	


        #Close connection to the switches
        vccAd1handle.close()
        vccAd2handle.close()
        vccClosethandle.close()

	return adCportdict





def v2fmain(vccCloset,cName,cId,fpcStart):
        readData()

       	vccAd1handle = Device(host=vccAd1,user=vccUser,password=vccPassword)
        vccAd2handle = Device(host=vccAd2,user=vccUser,password=vccPassword)

        #Open connection to the switches
        vccAd1handle.open()
        vccAd2handle.open()


	#Backup Configurations from ADs and the Closet VC
        backupConfig(vccCloset)

        #Get System ID from Virtual Chassis
        vccSysid = getSystemid(vccCloset)

        #Check if LLDP is enabled. Otherwise, enable LLDP
        checkEnlldp(vccCloset)

        #Create FPC to Sysid mapping for the VC
        fpcSiddict = fpcSidmap(vccSysid, fpcStart)

        #Find the Cascade ports on the ADs connected to this VC
        adCportdict = findCport(vccCloset)

	vccAd1Chandle = Config(vccAd1handle)
	vccAd2Chandle = Config(vccAd2handle)
	
	cnameConfig = 'set chassis satellite-management cluster '+cName+' cluster-id '+cId
	vccAd1Chandle.load(cnameConfig, format='set')
	vccAd2Chandle.load(cnameConfig, format='set')


	#Configure Cascade Ports
	for ad in adCportdict:
		for cPort in adCportdict[ad]:
			delCpconfig = 'delete interfaces '+cPort
			confCport = 'set chassis satellite-management cluster '+cName+' cascade-ports '+cPort
			confInt = 'set interfaces '+cPort+' cascade-port'
			if ad == 'AD1':
				vccAd1Chandle.load(delCpconfig, format='set')
				vccAd1Chandle.load(confCport, format='set')
				vccAd1Chandle.load(confInt, format='set')
			elif ad == 'AD2':
				vccAd2Chandle.load(delCpconfig, format='set')
                                vccAd2Chandle.load(confCport, format='set')
				vccAd2Chandle.load(confInt, format='set')

	
	#Configure FPC to Satellite sysid mapping
	for fpc in fpcSiddict.keys():
		memId = fpc - fpcStart
		fpcMemberconf = 'set chassis satellite-management cluster '+cName+' fpc '+str(fpc)+' member-id '+str(memId)
		fpcSysconf = 'set chassis satellite-management cluster '+cName+' fpc '+str(fpc)+' system-id '+fpcSiddict[fpc]
		fpcAcconf = 'set chassis satellite-management auto-satellite-conversion satellite '+str(fpc)
		vccAd1Chandle.load(fpcMemberconf, format='set')
		vccAd1Chandle.load(fpcSysconf, format='set')
#		vccAd1Chandle.load(fpcAcconf, format='set')  
		vccAd2Chandle.load(fpcMemberconf, format='set')
		vccAd2Chandle.load(fpcSysconf, format='set')  
#		vccAd2Chandle.load(fpcAcconf, format='set')    


	#Commit Configuration to the ADs
	vccAd1Chandle.commit()
	vccAd1Chandle.commit()

        
	#Close connection to the switches
        vccAd1handle.close()
        vccAd2handle.close()
                                    

v2fmain('10.105.5.134', 'Closet1', '10', 120)                                                               
