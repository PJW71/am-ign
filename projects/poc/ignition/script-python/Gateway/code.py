# =======================================================
# Update onlines devices list
# =======================================================
def getClients():
	sessions = system.perspective.getSessionInfo()	
	devices = []
	
	for device in sessions:
		client = {}
		if device['userAgent'].find('Android') != -1:
			client['OS'] = 'Android'
		elif device['userAgent'].find('Windows') != -1:	
			client['OS'] = 'Windows'
		elif device['userAgent'].find('iPhone') != -1:	
			client['OS'] = 'iPhone'
		elif device['userAgent'].find('Mac') != -1:	
				client['OS'] = 'Mac'
		else:		
			client['OS'] = 'Desinger'
			
		client['username'] = device['username']
		#client['authorized'] = device['authorized']	
		client['IP'] = device['clientAddress']
		seconds = device['uptime']/1000
		uptime = Util.secondsToText(seconds)
		client['uptime'] = uptime
		devices.append(client)
	
	system.tag.writeBlocking(['[default]System/devices'], [system.util.jsonEncode(devices)])



# =======================================================
#
# =======================================================
def getSystemPerformance():

	from java.lang.management import ManagementFactory

	bean = ManagementFactory.getOperatingSystemMXBean()
	gigs = 2**20
	totalMem = bean.getTotalPhysicalMemorySize()
	freeMem  = bean.getFreePhysicalMemorySize()
	
	TotalMemory = totalMem/gigs
	FreeMemory =  freeMem/gigs
	UsedMemory =  (totalMem-freeMem)/gigs
	TotalCPULoad = bean.getSystemCpuLoad() * 100
	JVMCPULoad = bean.getProcessCpuLoad() * 100
	
	def callback(a):
		pass
		return
	
	system.tag.writeAsync(["[default]System/Max Memory",
						   "[default]System/Free Memory",
						   "[default]System/Used Memory",
						   "[default]System/CPU Usage"],
						   [TotalMemory, 
							FreeMemory,
							UsedMemory,
							TotalCPULoad],callback)



def initAlarms():

	# Get default tag Provider of the project
	prov = str(system.tag.getConfiguration('', False)[0]["path"])
	prov = prov.replace("]", "").replace("[", "")
	
	# Save project prov for other function like alarm stat
	system.util.getGlobals()[system.util.getProjectName() + ' prov'] = prov
	
	
	# if no AAlrm folder create it
	if not system.tag.exists("ALARM/Priority/Critical"):
			
		# Alarm tag structure
		conf = {
		  "name": "ALARM",
		  "tagType": "Folder",
		  "tags": [
		    {
		      "name": "Priority",
		      "tagType": "Folder",
		      "tags": [
		        {
		          "eventScripts": [
		            {
		              "eventid": "valueChanged",
		              "script": "\tif previousValue.value \\u003c currentValue.value and currentValue.value !\\u003d 0: # we have new alarm\n\t\t# only pass file path to play in client if there is no higher pririty sound\n\t\tif system.tag.read(\\u0027[default]ALARM/Priority/Sound File\\u0027).value \\u003d\\u003d \\u0027\\u0027:\n\t\t\tsystem.tag.write(\\u0027[default]ALARM/Priority/Sound File\\u0027, \"/AM.mp3\")"
		            }
		          ],
		          "valueSource": "memory",
		          "name": "Medium",
		          "value": 0,
		          "tagType": "AtomicTag"
		        },
		        {
		          "valueSource": "memory",
		          "name": "Low",
		          "value": 1,
		          "tagType": "AtomicTag"
		        },
		        {
		          "eventScripts": [
		            {
		              "eventid": "valueChanged",
		              "script": "\tif previousValue.value \\u003c currentValue.value and currentValue.value !\\u003d 0: # we have new alarm\n\t\t# new method only pass file path to play in client\n\t\tsystem.tag.write(\\u0027[default]ALARM/Priority/Sound File\\u0027,\\u0027\\u0027 if system.tag.read(\"[default]ALARM/Priority/mute\").value else \"/AH.mp3\")"
		            }
		          ],
		          "valueSource": "memory",
		          "name": "High",
		          "value": 1,
		          "tagType": "AtomicTag"
		        },
		        {
		          "valueSource": "memory",
		          "expression": "if({[.]Total} !\\u003d {[.]Previous} // we have new alarm event play sound\r\n, True , False )",
		          "dataType": "Boolean",
		          "name": "mute",
		          "value": False,
		          "tagType": "AtomicTag"
		        },
		        {
		          "valueSource": "memory",
		          "name": "Diagnostic",
		          "value": 0,
		          "tagType": "AtomicTag"
		        },
		        {
		          "valueSource": "memory",
		          "dataType": "String",
		          "name": "Sound File",
		          "value": "",
		          "tagType": "AtomicTag"
		        },
		        {
		          "eventScripts": [
		            {
		              "eventid": "valueChanged",
		              "script": "\tif previousValue.value \\u003c currentValue.value and currentValue.value !\\u003d 0: # we have new alarm\n\t\t# only pass file path to play in client\n\t\tsystem.tag.write(\\u0027[default]ALARM/Priority/Sound File\\u0027,\"/AH.mp3\")"
		            }
		          ],
		          "valueSource": "memory",
		          "name": "Critical",
		          "value": 1,
		          "tagType": "AtomicTag"
		        }
		      ]
		    },
		    {
		      "valueSource": "memory",
		      "dataType": "String",
		      "name": "LastUnAckUIID",
		      "value": "f37a94d3-e39c-4f76-aa39-3b200adcacb2",
		      "tagType": "AtomicTag"
		    },
		    {
		      "valueSource": "memory",
		      "dataType": "String",
		      "name": "LastUnAckTagPath",
		      "value": "NSR/BSTR C/PI162C/ESD",
		      "tagType": "AtomicTag"
		    },
		    {
		      "valueSource": "memory",
		      "sourceTagPath": "",
		      "name": "Total",
		      "value": 3,
		      "tagType": "AtomicTag"
		    },
		    {
		      "valueSource": "memory",
		      "dataType": "String",
		      "name": "LastUnack",
		      "value": "NSR/BSTR C/PI162C/ESD ",
		      "tagType": "AtomicTag"
		    }
		  ]
		}
		# Create it if it doesnt exist
		system.tag.configure("", conf, "a")

# =======================================================
#
# =======================================================
def getAlarmStat():
	
	prov = system.util.getGlobals()[system.util.getProjectName() + ' prov']
	source = ["*prov:" + prov +"*"]
	
	alarmList = system.alarm.queryStatus(state=["ActiveUnacked",'ClearUnacked'], source = source)
	system.tag.write('ALARM/Total',len(alarmList))
	
	# Get no. of total Critical alarms
	Al = len(system.alarm.queryStatus(priority = "Critical", state=["ActiveUnacked",'ClearUnacked'], source = source))
	system.tag.write('ALARM/Priority/Critical',Al)
	
	# Get no. of total High alarms
	Al = len(system.alarm.queryStatus(priority = "High", state=["ActiveUnacked",'ClearUnacked'], source = source))
	system.tag.write('ALARM/Priority/High',Al)
	
	# Get no. of total Medium alarms
	Al = len(system.alarm.queryStatus(priority = "Medium", state=["ActiveUnacked",'ClearUnacked'], source = source))
	system.tag.write('ALARM/Priority/Medium',Al)
	
	# Get no. of total Low alarms
	Al = len(system.alarm.queryStatus(priority = "Low", state=["ActiveUnacked",'ClearUnacked'], source = source))
	system.tag.write('ALARM/Priority/Low',Al)
	
	# Get no. of total Unack alarm
	Al = len(system.alarm.queryStatus(state=['ClearUnacked', 'ActiveUnacked'], source = source))
	system.tag.write('ALARM/Total',Al)
	
	#Get last Unack Alarm
	
	if len(alarmList) > 0:
		
		alarmList = system.dataset.sort(alarmList.getDataset(),3,False)
		
		IUUD = alarmList.getValueAt(0,0)
		displayPath = str(alarmList.getValueAt(0,2))
		source = str(alarmList.getValueAt(0,1))
		# Trim source to actual valid tagPath
		prov = source.split(":/tag:")[0]
		prov = prov.split("prov:")[-1]
		source = source.split(":/tag:")[-1] # get rid of prov:...:/tag:
		tagPath = source.split(":/alm:")[0] # get rid of :/alm:...		

	#	time = alarmList.getValueAt(0,3)
	#	time = system.date.format(time, 'yyyy/MM/dd HH:mm:ss.SSS')
	#	value += time
	else:
		value = ""
		tagPath = ""
		displayPath = ""
		IUUD = ""
	system.tag.writeBlocking(['ALARM/LastUnack', 'ALARM/LastUnAckTagPath', 'ALARM/LastUnAckUIID'] , [displayPath, tagPath, IUUD])	
	
	
	
	