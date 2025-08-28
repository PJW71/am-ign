# Code to create tags based in CSV file.
# Northvolt - Revolt Plant
# Oct 2024

import csv

# Check existing CSV file folder
import glob

def checkCSVfolder (filepath):
	
	from os.path import basename
	
	#path = "C:/NV_Data/01 Automation/01 Revolt/02 Ignition/02 Scripts/Tags_import_Base"
	csv = next(iter(glob.glob(filepath + "*.csv")), None)
	if csv is not None:
		return 1
		
	else:
		#print ('CSV File does not exist')
		return 0
		pass

def createfolder (linha):
	### CREATE FOLDERS - STRUCTURE FOLDER TAG
	# Folders are nodes with a 'tagType' set to 'Folder'.
	# Each folder can contain a 'tags' value, which containers other tags and folders.
	# Each line in CSV file contain the FBS structure to allocate the new tags.
	
	Tags={'tagType': 'Folder',
		'name': linha[0],
		'tags' : [
		            {
		            'name': linha[1],
		            'tagType': 'Folder',
		            'tags': [
			                    {
			                    'name': linha[2],
			                    'tagType': 'Folder',
			                    'tags': [
						                    {
						                    'name': linha[3],
						                    'tagType': 'Folder',
						                    'tags': [
							                    		{
									                    'name': linha[4],
									                    'tagType': 'Folder',
									                    'tags': [{}]           
								                    	}
				                    				 ]                             
					                    	}
		                    			]                            
		                    	}
		            		]	                            
		            }
		        ]
			}
			
	system.tag.configure(basePath = '', tags = Tags, collisionPolicy = "o")

def createUDTTag (linha):
	### CREATE UDT INSTANCE TAG
        
    # get parameters from CSV file
	baseTagPath = linha[0] + '/' + linha[1] + '/' + linha[2] + '/'+ linha[3] + '/' + linha[4]
	udtLib = linha[12] 
	tagType = linha[13] 
	tagName = linha[5]
	result = 0
	# Check the UDT type to choose for each TAG
	if udtLib == 'opcFBS':
		typeId = "Revolt/SiOMELib/opcFBSLib/" + linha[14]
		#if tagType == 'PID':
			#typeId = "Revolt_Dev/NVRVLib/opcFBSLib/" + linha[14]
		#elif tagType == 'AI':
			#typeId = "Revolt_Dev/NVRVLib/opcFBSLib/" + linha[14]	
		result = 1
	elif udtLib == 'Coperion':
		typeId = "Revolt_Dev/FBSTypeLib/VendorsLib/Coperion/" + linha[14]
	else:
		result = 0
		print ("UDT Type cannot be found")
		
	tagType = "UdtInstance"
	# Parameters to pass in.
	motorNum = "1"
	  
	# Configure the Tag.
	tag = {
	            "name": tagName,         
	            "typeId" : typeId,
	            "tagType" : tagType,
	            "parameters" : {
	              "motorNum" : motorNum
	              }
	       }
	 
	# Set the collision policy to Abort. That way if a tag already exists at the base path,
	# we will not override the Tag. If you are overwriting an existing Tag, then set this to "o".
	collisionPolicy = "a"
	  
	# Create the Tag.
	system.tag.configure(baseTagPath, [tag], collisionPolicy)

def setParamTag (linha):
	# Retrieving the existing configuration is much easier than typing it all out.
	tagPath = '[' + linha[15] + ']' + linha[0] + '/' + linha[1] + '/' + linha[2] + '/'+ linha[3] + '/' + linha[4] +'/' + linha[5]
	tagFolder = '[' + linha[15] + ']' + linha[0] + '/' + linha[1] + '/' + linha[2] + '/'+ linha[3] + '/' + linha[4]
	udtLib = linha[12]
	udtType = linha[14]
	tag = system.tag.getConfiguration(tagPath)
	#print ("SetParamTag Inside") 
	#print (linha)
	# This line is accessing the first tag in our results (the UDT Definition), then returns the
	# 'parameters' dictionary, which then provides access to individual parameters.
	# Check the UDT type to choose for each TAG
	print (udtType)
	if udtLib == 'opcFBS':
		tag[0]['parameters']['p1OPCServer'] = linha[7]
		tag[0]['parameters']['p2OPCPath'] = linha[8]
		tag[0]['parameters']['p3Interface'] = linha[9]
		tag[0]['parameters']['P4Site'] = linha[0]
		tag[0]['parameters']['p5Area'] = linha[1]
		tag[0]['parameters']['p6ProcessCell'] = linha[2]
		tag[0]['parameters']['p7Unit'] = linha[3]
		tag[0]['parameters']['p8Module'] = linha[4]
		tag[0]['parameters']['pStorageProvider'] = linha[10]
		tag[0]['parameters']['pTagGroup'] = linha[11]   
	elif udtLib == 'Coperion':
		#SHOULD BE DEFINED IN NEW CSV FILE OR COLUMNS
		if udtType == 'Coperion_AI':
			tag[0]['parameters']['pTagOpcNameTIA'] = linha[16]
			tag[0]['parameters']['pTagPathAnalog'] = linha[15]
		if udtType == 'Coperion_AnlLib':
			tag[0]['parameters']['p3TagPath1'] = linha[16]
			tag[0]['parameters']['p3TagPath2'] = linha[17]
		elif udtType == 'Coperion_FeederMtr':
			tag[0]['parameters']['p3TagPath'] = linha[16]
			tag[0]['parameters']['p3TagPath2'] = linha[17]
			tag[0]['parameters']['p3TagPathAnalog'] = linha[18]
		else:
			tag[0]['parameters']['p3TagPath'] = linha[16]
		tag[0]['parameters']['P4TagGroup'] = linha[11]
		tag[0]['parameters']['pStorageProvider'] = linha[10]
		tag[0]['parameters']['pDescription'] = linha[19] 
		
	 
	# Overwrite the existing configuration.
	collisionPolicy = "o"
	  
	# Write the new configuration to our existing UDT Definition.
	# Note that the first parameter is to the parent folder of the Definition,
	# not a path to the Definition.
	system.tag.configure(tagFolder, tag, collisionPolicy)
	


# Open file
filepath = "C:/NV_Data/01 Automation/01 Revolt/02 Ignition/02 Scripts/zzt_Tags_import_Base_Coperion_1"
openfile = filepath.replace('/','\\') + '.csv'
if checkCSVfolder (filepath):
	with open(openfile, 'r') as arquivo:
	    leitor_csv = csv.reader(arquivo)
	    i = 0
	    for linha in leitor_csv:
	        createfolder (linha)
	        #continue
	   
		for linha in leitor_csv:
			createUDTTag (linha)
			i=i+1
			#print ("IF Create UDT")
			setParamTag (linha)
			
			tagPath = linha[0] + '/' + linha[1] + '/' + linha[2] + '/'+ linha[3] + '/' + linha[4] +'/' + linha[5]
			print ("TAG created:" + tagPath)
		fmsg = "Amount Tags created: " + str(i)
		print (fmsg)
					
else:
	print ("File " + filepath + " Does Not Exist - Not possible to create Tags")