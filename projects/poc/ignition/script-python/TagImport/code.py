##############################################################################################################
# Code to create tags based on CSV file.
# Northvolt - Revolt Plant
# -----------------------------------------------------------------------------------------------------------
# Revision History
# v1.0 18 Feb 2025 - P.Weir
# v1.1 21 Feb 2025 - P.Weir: Added Eurodia Columns(Sequence), AI DataTytpe
# v1.2 04 Mar 2025 - K.Hafez: Added Eurodia Vlv, Mtr, MtrF, DI
#############################################################################################################

#############################################################################################################
#	DECLARATIONS
#############################################################################################################

# Import Python's built-in csv library
import csv

# Check existing CSV file folder
import glob

# Ask the user to find the CSV in the local file system.
path = system.file.openFile("csv")

# Extra Check if file has been selected
def checkCSVfolder (filepath):
	csv = next(iter(glob.glob(filepath)), None)
	if csv is not None:
		return 1
		
	else:
		#print ('CSV File does not exist')
		return 0
		pass
	
#Create Folders
def createfolder (line):
	### CREATE FOLDERS - STRUCTURE FOLDER TAG
	# Folders are nodes with a 'tagType' set to 'Folder'.
	# Each folder can contain a 'tags' value, which containers other tags and folders.
	# Each line in CSV file contain the FBS structure to allocate the new tags.
	baseTagProvider = '[' + line[13] + ']'
	try:
		Tags={'tagType': 'Folder',
			'name': line[0],
			'tags' : [
			            {
			            'name': line[1],
			            'tagType': 'Folder',
			            'tags': [
				                    {
				                    'name': line[2],
				                    'tagType': 'Folder',
				                    'tags': [
							                    {
							                    'name': line[3],
							                    'tagType': 'Folder',
							                    'tags': [
								                    		{
										                    'name': line[4],
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
		
		system.tag.configure(basePath = baseTagProvider, tags = Tags, collisionPolicy = "o")
	except Exception as e:
		return "Folder cannot be created: Something is wrong with the FBS name structure"	
		
### CREATE UDT INSTANCE TAG	
def createUDTTag (line):        
    # get parameters from CSV file
	baseTagPath = '[' + line[13] + ']' + line[0] + '/' + line[1] + '/' + line[2] + '/'+ line[3] + '/' + line[4]
	udtLib = line[11] 
#	tagType = line[12] 
	tagName = line[5]
	try:
		# Check the UDT Path for each TAG
		typeId = '[' + line[13] + ']' + "_types_/" + line[14] + '/' + line[12]
		# typeId = line[14] + '/' + line[12]
		tagType = "UdtInstance"
		# Parameters to pass in.
	#	motorNum = "5"
		  
		# Configure the Tag.
		tag = {
		            "name": tagName,         
		            "typeId" : typeId,
		            "tagType" : tagType,
	#	            "parameters" : {
	#	              "motorNum" : motorNum
	#	              }
		       }
		 
		# Set the collision policy to Abort. That way if a tag already exists at the base path,
		# we will not override the Tag. If you are overwriting an existing Tag, then set this to "o".
		collisionPolicy = "o"
		  
		# Create the Tag.
		result = system.tag.configure(baseTagPath, [tag], collisionPolicy)
		#Return status result
		return result
	except Exception as e:
		return "Error: Create UDT Tag Function"

# SET PARAMETERS		
def setParamTag (line):
	# Retrieving the existing configuration is much easier than typing it all out.	
	tagFolder = '[' + line[13] + ']' + line[0] + '/' + line[1] + '/' + line[2] + '/'+ line[3] + '/' + line[4]
	tagPath = tagFolder +'/' + line[5]
	udtLib = line[11]
	udtType = line[12]
	tagfbs = line[0] + '/' + line[1] + '/' + line[2] + '/'+ line[3] + '/' + line[4] +'/' + line[5]
	result = tag = system.tag.getConfiguration(tagPath)
	if "Unknown" in str(result):
		return result
	# This line is accessing the first tag in our results (the UDT Definition), then returns the
	# 'parameters' dictionary, which then provides access to individual parameters.
	# Check the UDT type to choose for each TAG
	try:
	    #Check the UDT type
	    #Set parameters for opcFBSLib - Read Only FBS Types
		if udtLib == 'opcFBSLib':
			tag[0]['parameters']['p1OPCServer'] = line[6]
			tag[0]['parameters']['p2OPCPath'] = line[7]
			tag[0]['parameters']['p3Interface'] = line[8]
			tag[0]['parameters']['P4Site'] = line[0]
			tag[0]['parameters']['p5Area'] = line[1]
			tag[0]['parameters']['p6ProcessCell'] = line[2]
			tag[0]['parameters']['p7Unit'] = line[3]
			tag[0]['parameters']['p8Module'] = line[4]
			tag[0]['parameters']['pStorageProvider'] = line[9]
			tag[0]['parameters']['pTagGroup'] = line[10]
			
		#Set parameters for opcFBSLib_v1 - Read/Write FBS Types
		elif (udtLib == 'opcFBSLib_v1') or (udtLib == 'poc'):
			tag[0]['parameters']['p1OPCServer'] = line[6]
			tag[0]['parameters']['p2OPCPath'] = line[7]
			tag[0]['parameters']['p3Interface'] = line[8]
			tag[0]['parameters']['p4Area'] = line[1]
			tag[0]['parameters']['p5ProcessCell'] = line[2]
			tag[0]['parameters']['p6Unit'] = line[3]
			tag[0]['parameters']['p7Module'] = line[4]
			tag[0]['parameters']['pStorageProvider'] = line[9]
			tag[0]['parameters']['pTagGroup'] = line[10]
			tag[0]['parameters']['pTagReferencePath'] = line[15]
		
		#Set parameters for FC_H1_MBF01 - Coperion Types
		elif udtLib == 'FC_H1_MBF01':
			tag[0]['parameters']['PTagGroup'] = line[10]
			tag[0]['parameters']['pStorageProvider'] = line[9]
			tag[0]['parameters']['pDescription'] = line[20]
			if udtType == 'AI':
				tag[0]['parameters']['pTagPathAnalog'] = line[15]
				tag[0]['parameters']['pTagAINameTIA'] = line[16]
			elif udtType == 'AnlLib':
				tag[0]['parameters']['pTagPathAnalog'] = line[15]
			elif udtType == 'DI':
				tag[0]['parameters']['pTagPathSensor'] = line[15]
				tag[0]['parameters']['pTagSensorNameTIA'] = line[16]
			elif udtType == 'Feeder':
				tag[0]['parameters']['pTagPathFeedersKtron'] = line[15]
				tag[0]['parameters']['pTagPathGeneralState'] = line[17]
				tag[0]['parameters']['pTagPathInterlocks'] = line[18]
				tag[0]['parameters']['pFeederNumber'] = line[19]
			elif udtType == 'Mtr':
				tag[0]['parameters']['pTagPathMotors'] = line[15]
				tag[0]['parameters']['pTagMotorNameTIA'] = line[16]
			elif udtType == 'Totalizer':
				tag[0]['parameters']['pTagPath'] = line[15]
				tag[0]['parameters']['pTagOpcNameTIA'] = line[16]
			elif udtType == 'Vlv':
				tag[0]['parameters']['pTagPathValves'] = line[15]
				tag[0]['parameters']['pTagValveNameTIA'] = line[16]		
			
			
		#Set parameters for Eurodia IRX Types
		elif udtLib == 'Eurodia':
			if udtType == 'AI':
				tag[0]['parameters']['p1refProvider'] = line[15] # Name of reference tag Tag provider 
				tag[0]['parameters']['p2refPath'] = line[16] # Path to reference tag
				tag[0]['parameters']['p3refName'] = line[17] # Name of reference tag
				tag[0]['parameters']['p4StorageProvider'] = line[9]
				tag[0]['parameters']['p5Description'] = line[20]			
			elif udtType == 'Vlv':
				tag[0]['parameters']['p1refProvider'] = line[15] # Name of reference tag Tag provider 
				tag[0]['parameters']['p2refPath'] = line[16] # Path to reference tag
				tag[0]['parameters']['p3refName'] = line[17] # Name of reference tag
				tag[0]['parameters']['p4StorageProvider'] = line[9]
				tag[0]['parameters']['p5Description'] = line[20]
			elif udtType == 'Mtr':
				tag[0]['parameters']['p1refProvider'] = line[15] # Name of reference tag Tag provider 
				tag[0]['parameters']['p2refPath'] = line[16] # Path to reference tag
				tag[0]['parameters']['p3refName'] = line[17] # Name of reference tag
				tag[0]['parameters']['p4StorageProvider'] = line[9]
				tag[0]['parameters']['p5Description'] = line[20]
			elif udtType == 'MtrF':
				tag[0]['parameters']['p1refProvider'] = line[15] # Name of reference tag Tag provider 
				tag[0]['parameters']['p2refPath'] = line[16] # Path to reference tag
				tag[0]['parameters']['p3refName'] = line[17] # Name of reference tag
				tag[0]['parameters']['p4StorageProvider'] = line[9]
				tag[0]['parameters']['p5Description'] = line[20]
			elif udtType == 'DI':
				tag[0]['parameters']['p1refProvider'] = line[15] # Name of reference tag Tag provider 
				tag[0]['parameters']['p2refPath'] = line[16] # Path to reference tag
				tag[0]['parameters']['p3refName'] = line[17] # Name of reference tag
				tag[0]['parameters']['p4StorageProvider'] = line[9]
				tag[0]['parameters']['p5Description'] = line[20]
			elif udtType == 'Columns':
				tag[0]['parameters']['OPCp0'] = line[6] # OPC Server
				tag[0]['parameters']['OPCp1'] = line[7] # OPC Item Path
				tag[0]['parameters']['OPCp2'] = line[8] # OPC interface or Asociated DB
				tag[0]['parameters']['p1StorageProvider'] = line[9]
				tag[0]['parameters']['p2TagGroup'] = line[10]				

		# Overwrite the existing configuration.
		collisionPolicy = "o"
		  
		# Write the new configuration to our existing UDT Definition.
		# Note that the first parameter is to the parent folder of the Definition,
		# not a path to the Definition.
		result = system.tag.configure(tagFolder, tag, collisionPolicy)
		#Return status result
		return result
	except Exception as e:
		return "Error: Set Parameters Function"

################################################################################################################
#	EXECUTE MAIN CODE
################################################################################################################
try:	
	if checkCSVfolder (path):
		with open(path, 'r') as a_file:
			reader_csv = csv.reader(a_file)
			first_line = next(reader_csv)
			i = 0
			j = 0
			k = 0
			 #Remove BOM
			if first_line[0].startswith('\ufeff'):
			 	first_line[0] = first_line[0][1:]
			#Read all lines into a list
			lines = list(reader_csv)
			line_count = sum(1 for row in lines)
						
			#Call to execute functions
			for line in lines:
				#Create Folder
				tagPath = line[0] + '/' + line[1] + '/' + line[2] + '/'+ line[3] + '/' + line[4] +'/' + line[5]
				statusFolder = createfolder (line)
				#Create Tag
				statusUDT = createUDTTag (line)
				sUDT = str(statusUDT)
				i += 1
				#print (statusUDT)
				if statusUDT:
					if ("Good" in sUDT) or ("already exists" in sUDT):
						j += 1
					print (str(i) + " - " + tagPath + " creating tag: " + sUDT)
				#Set Parameters
				statusParam = setParamTag (line)
				sParam = str(statusParam)
				if statusParam:
					if "Good" in sParam:
						k += 1
					print (str(k) + " - " + tagPath + " setting parameters: " + sParam)
				#Print tag information
				#if not statusUDT and not statusParam:

			#Print information at the end of process
			pSuc = round((j/float(line_count))*100,1)
			pSuc1 = round((k/float(line_count))*100,1)
			fmsg = '\nTags created-exist/Total: ' + str(j) + '/' + str(line_count) + '----' + str(pSuc) + '% Success'
			fmsg1 = 'Tags configured/Total: ' + str(k) + '/' + str(line_count) + '----' + str(pSuc1) + '% Success\n'
			print (fmsg)
			print (fmsg1)
			timenow = system.date.now()
			print (timenow)						
	else:
		print ("File does not Exist - Not possible to continue")
	
except Exception as e:
	print ("Error in the execution main code")