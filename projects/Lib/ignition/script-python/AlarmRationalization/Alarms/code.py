def coalesce(value, defaultValue):
	if value == None:
		return defaultValue
	return value
	
def enumCoalesce(value, defaultValue):
	if value == None:
		return defaultValue
	elif type(value) != dict:
		return value.name()
	return value
# This function modified to work with signle project tag provider .. orignial one worked only with all tags provider in Gaeway level .
# this help to manage single project 	
# Change Script call from view in path AlarmRationalization/Statistics
def checkAlarms(): ## This function check all provider and working with MSSQL db , For Postgress code modified and commented in below lines
	alarmsWithRationalization = []
	alarmsWithRationalizationAttention = []
	alarmsWithoutRationalization = []
	start = system.date.toMillis(system.date.now())
	system.tag.writeBlocking(["AlarmRationalization/Running"], [True])
	
	config = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/Configuration"])[0].value))
				
	alarmsNeedAttention = {}
	alarmsNeedAttentionArray = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/AlarmsWithRationalizationAttention"])[0].value))
	for alarm in alarmsNeedAttentionArray:
		alarmsNeedAttention[alarm["tagPath"]] = alarm["alarmDetails"]["rationalization"]["rActionValue"]
	
	tagProviders = []
	results = system.tag.browse("")
	for i in results.getResults():
		tagProviders.append(str(i["name"]))
	
	for tagProvider in tagProviders:
		query = {
		  "options": {
		    "includeUdtMembers": True,
		    "includeUdtDefinitions": False
		  },
		  "condition": {
		    "attributes": {
		      "values": [
		        "alarm"
		      ],
		      "requireAll": True
		    }
		  },
		  "returnProperties": [
		    "name",
		    "alarms",
		    "tagType",
		    "quality"
		  ]
		}
		
		# First, we need to get all of the alarms current state by reading their metadata
		tagsToRead = []
		alarmResults = system.tag.query(tagProvider, query)
		for alarm in alarmResults:
			tagPath = str(alarm["fullPath"])
			for alarm in alarm["alarms"]:
				alarmName = alarm["name"]
				tagsToRead.extend([
					"%s/Alarms/%s.enabled" % (tagPath, alarmName),
					"%s/Alarms/%s.priority" % (tagPath, alarmName),
					"%s/Alarms/%s.mode" % (tagPath, alarmName),
					"%s/Alarms/%s.setpointA" % (tagPath, alarmName),
					"%s/Alarms/%s.inclusiveA" % (tagPath, alarmName),
					"%s/Alarms/%s.setpointB" % (tagPath, alarmName),
					"%s/Alarms/%s.inclusiveB" % (tagPath, alarmName),
					"%s/Alarms/%s.anyChange" % (tagPath, alarmName),
					"%s/Alarms/%s.bitOnZero" % (tagPath, alarmName),
					"%s/Alarms/%s.bitPosition" % (tagPath, alarmName),
					"%s/Alarms/%s.activeCondition" % (tagPath, alarmName),
					"%s.valueSource" % (tagPath),
					"%s.opcServer" % (tagPath),
					"%s.opcItemPath" % (tagPath),
					"%s/Alarms/%s.displayPath" % (tagPath, alarmName)
				])
		
		# Next, we need to see if any tag changes have occurred by looking at the audit logs
		lastCheck = system.tag.readBlocking(["AlarmRationalization/LastCheck"])[0].value
		## ___ This used for Postgress DB
		#auditRes = system.db.runPrepQuery("SELECT"+' "ACTION_TARGET", "EVENT_TIMESTAMP", "ACTION_VALUE" FROM audit_events WHERE "ACTION" in ('+"'tag edit','tag move', 'tag rename'"+') AND "EVENT_TIMESTAMP" > ? ORDER BY "EVENT_TIMESTAMP" ASC', [lastCheck])
		auditRes = system.db.runPrepQuery("SELECT action_target, event_timestamp, action_value FROM audit_events WHERE action in ('tag edit', 'tag move', 'tag rename') AND event_timestamp > ? ORDER BY event_timestamp ASC", [lastCheck])
		auditEvents = {}
		for row in auditRes:
			auditEvents[row["action_target"]] = {"eventTimestamp":row["event_timestamp"], "actionValue":row["action_value"]}
			#auditEvents[row["ACTION_TARGET"]] = {"EVENT_TIMESTAMP":row["EVENT_TIMESTAMP"], "ACTION_VALUE":row["ACTION_VALUE"]} ___ This used for Postgress DB
		
		# Now we can go through an look at the alarm config and current state
		if len(tagsToRead):
			alarmMetaValues = system.tag.readBlocking(tagsToRead)
		
			idx = 0
			wIdx = 0
			wAIdx = 0
			woIdx = 0
			for tag in alarmResults:
				tagName =  tag["name"]
				tagPath = str(tag["fullPath"])
				for alarm in tag["alarms"]:	
					alarmData = {
						"tagName":tagName, 
						"tagPath":tagPath, 
						"tagProvider":tagProvider,
						"alarmName":alarm["name"], 
						"alarmDetails": {
							"enabled": {"value":coalesce(alarmMetaValues[idx].value, True), "config":alarm.get("enabled", True)}, 
							"displayPath": {"value":coalesce(alarmMetaValues[14].value, ""), "config":alarm.get("displayPath", "")}, 
							"priority":{"value":enumCoalesce(alarmMetaValues[idx+1].value, "Diagnostic"), "config":enumCoalesce(alarm.get("priority", None), "Diagnostic")}, 
							"mode":{"value":enumCoalesce(alarmMetaValues[idx+2].value, "Equality"), "config":enumCoalesce(alarm.get("mode", None), "Equality")}, 
							"setpointA":{"value":alarmMetaValues[idx+3].value, "config":alarm.get("setpointA", 0)}, 
							"inclusiveA":{"value":alarmMetaValues[idx+4].value, "config":alarm.get("inclusiveA", True)}, 
							"setpointB":{"value":alarmMetaValues[idx+5].value, "config":alarm.get("setpointB", 0)}, 
							"inclusiveB":{"value":alarmMetaValues[idx+6].value, "config":alarm.get("inclusiveB", True)}, 
							"anyChange":{"value":alarmMetaValues[idx+7].value, "config":alarm.get("anyChange", False)}, 
							"bitOnZero":{"value":alarmMetaValues[idx+8].value, "config":alarm.get("bitOnZero", False)}, 
							"bitPosition":{"value":alarmMetaValues[idx+9].value, "config":alarm.get("bitPosition", 0)}, 
							"activeCondition":{"value":alarmMetaValues[idx+10].value, "config":alarm.get("activeCondition", False)},
							"valueSource":alarmMetaValues[idx+11].value,
							"opcServer":alarmMetaValues[idx+12].value,
							"opcItemPath":alarmMetaValues[idx+13].value,							
							"rationalization": {
								"rationalized":"rationalized" in alarm and alarm["rationalized"] in ("true", True, 1, "1"),
								"rFacility":alarm.get("rFacility", ""),
								"rProcessArea":alarm.get("rProcessArea", ""),
								"rClass":alarm.get("rClass", ""),
								"rDescription":alarm.get("rDescription", ""),
								"rConsequenceNoAction":alarm.get("rConsequenceNoAction", ""),
								"rSafetyImpact":int(alarm.get("rSafetyImpact", 0)),
								"rSafetyImpactDisplay":config["SafetyImpact"]["%d" % int(alarm.get("rSafetyImpact", 0))],
								"rEnvironmentalImpact":int(alarm.get("rEnvironmentalImpact", 0)),
								"rEnvironmentalImpactDisplay":config["EnvironmentalImpact"]["%d" % int(alarm.get("rEnvironmentalImpact", 0))],
								"rFinancialImpact":int(alarm.get("rFinancialImpact", 0)),
								"rFinancialImpactDisplay":config["FinancialImpact"]["%d" % int(alarm.get("rFinancialImpact", 0))],
								"rOperatorUrgency":int(alarm.get("rOperatorUrgency", 0)),
								"rOperatorUrgencyDisplay":config["OperatorUrgency"]["%d" % int(alarm.get("rOperatorUrgency", 0))]["name"],
								"rProbableCause":alarm.get("rProbableCause", ""),
								"rConfirmation":alarm.get("rConfirmation", ""),
								"rCorrectiveActions":alarm.get("rCorrectiveActions", ""),
								"rLastUpdated":alarm.get("rLastUpdated", ""),
								"rActionValue":alarmsNeedAttention.get(tagPath, "")
							}
						}
					}
					
					lastUpdated = alarmData["alarmDetails"]["rationalization"]["rLastUpdated"]
					if lastUpdated != "":
						lastUpdated = system.date.parse(lastUpdated, "yyyy-MM-dd HH:mm:ss")
						lastUpdated = system.date.addSeconds(lastUpdated, 60) # We need to avoid a rationalization that just happened
					
					if alarmData["alarmDetails"]["rationalization"]["rationalized"]:
						actionValue = alarmData["alarmDetails"]["rationalization"]["rActionValue"]
						if actionValue == "" and tagPath in auditEvents:
							if system.date.isAfter(auditEvents[tagPath]["eventTimestamp"], lastUpdated):
								actionValue = auditEvents[tagPath]["actionValue"]
					
						if actionValue != "":	
							alarmData["alarmDetails"]["idx"] = wAIdx
							alarmData["alarmDetails"]["rationalization"]["rActionValue"] = actionValue
							wAIdx += 1
							alarmsWithRationalizationAttention.append(alarmData)
						else:
							alarmData["alarmDetails"]["idx"] = wIdx
							wIdx += 1
							alarmsWithRationalization.append(alarmData)
					else:
						alarmData["alarmDetails"]["idx"] = woIdx
						woIdx += 1
						alarmsWithoutRationalization.append(alarmData)
				
					idx += 15
	
	sort(alarmsWithoutRationalization, alarmsWithRationalization, alarmsWithRationalizationAttention)
	
	end = system.date.toMillis(system.date.now())
	system.tag.writeBlocking(["AlarmRationalization/Running", "AlarmRationalization/AlarmsWithRationalization", "AlarmRationalization/AlarmsWithRationalizationAttention", "AlarmRationalization/AlarmsWithoutRationalization", "AlarmRationalization/LastCheck", "AlarmRationalization/LastCheckDurationMS"], [False, alarmsWithRationalization, alarmsWithRationalizationAttention, alarmsWithoutRationalization, system.date.now(), end-start])

def checkAlarms1(projectProvider): ## This function check speccific provider and working with Postgress db , For MSSQL code modified and commented in below lines
	alarmsWithRationalization = []
	alarmsWithRationalizationAttention = []
	alarmsWithoutRationalization = []
	start = system.date.toMillis(system.date.now())
	system.tag.writeBlocking(["AlarmRationalization/Running"], [True])
	
	config = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/Configuration"])[0].value))
				
	alarmsNeedAttention = {}
	alarmsNeedAttentionArray = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/AlarmsWithRationalizationAttention"])[0].value))
	for alarm in alarmsNeedAttentionArray:
		alarmsNeedAttention[alarm["tagPath"]] = alarm["alarmDetails"]["rationalization"]["rActionValue"]
	
	#tagProviders = []
	tagProvider = projectProvider  # this line added to work with single project
	#results = system.tag.browse("")
	#for i in results.getResults():
		#tagProviders.append(str(i["name"]))
	
	#for tagProvider in tagProviders:
	query = {
	  "options": {
	    "includeUdtMembers": True,
	    "includeUdtDefinitions": False
	  },
	  "condition": {
	    "attributes": {
	      "values": [
	        "alarm"
	      ],
	      "requireAll": True
	    }
	  },
	  "returnProperties": [
	    "name",
	    "alarms",
	    "tagType",
	    "quality"
	  ]
	}
	
	# First, we need to get all of the alarms current state by reading their metadata
	tagsToRead = []
	alarmResults = system.tag.query(tagProvider, query)
	for alarm in alarmResults:
		tagPath = str(alarm["fullPath"])
		for alarm in alarm["alarms"]:
			alarmName = alarm["name"]
			tagsToRead.extend([
				"%s/Alarms/%s.enabled" % (tagPath, alarmName),
				"%s/Alarms/%s.priority" % (tagPath, alarmName),
				"%s/Alarms/%s.mode" % (tagPath, alarmName),
				"%s/Alarms/%s.setpointA" % (tagPath, alarmName),
				"%s/Alarms/%s.inclusiveA" % (tagPath, alarmName),
				"%s/Alarms/%s.setpointB" % (tagPath, alarmName),
				"%s/Alarms/%s.inclusiveB" % (tagPath, alarmName),
				"%s/Alarms/%s.anyChange" % (tagPath, alarmName),
				"%s/Alarms/%s.bitOnZero" % (tagPath, alarmName),
				"%s/Alarms/%s.bitPosition" % (tagPath, alarmName),
				"%s/Alarms/%s.activeCondition" % (tagPath, alarmName),
				"%s.valueSource" % (tagPath),
				"%s.opcServer" % (tagPath),
				"%s.opcItemPath" % (tagPath),
				"%s/Alarms/%s.displayPath" % (tagPath, alarmName)
			])
	
	# Next, we need to see if any tag changes have occurred by looking at the audit logs
	lastCheck = system.tag.readBlocking(["AlarmRationalization/LastCheck"])[0].value
	#Below Line for MSSQL DB 
	#auditRes = system.db.runPrepQuery("SELECT action_target, event_timestamp, action_value FROM audit_events WHERE action in ('tag edit', 'tag move', 'tag rename') AND event_timestamp > ? ORDER BY event_timestamp ASC", [lastCheck])	
	auditRes = system.db.runPrepQuery("SELECT"+' "ACTION_TARGET", "EVENT_TIMESTAMP", "ACTION_VALUE" FROM audit_events WHERE "ACTION" in ('+"'tag edit','tag move', 'tag rename'"+') AND "EVENT_TIMESTAMP" > ? ORDER BY "EVENT_TIMESTAMP" ASC', [lastCheck])
	auditEvents = {}
	for row in auditRes:
		#auditEvents[row["action_target"]] = {"eventTimestamp":row["event_timestamp"], "actionValue":row["action_value"]}  # FOR MSSQL DB
		auditEvents[row["ACTION_TARGET"]] = {"eventTimestamp":row["EVENT_TIMESTAMP"], "actionValue":row["ACTION_VALUE"]}
	
	# Now we can go through an look at the alarm config and current state
	if len(tagsToRead):
		alarmMetaValues = system.tag.readBlocking(tagsToRead)
	
		idx = 0
		wIdx = 0
		wAIdx = 0
		woIdx = 0
		for tag in alarmResults:
			tagName =  tag["name"]
			tagPath = str(tag["fullPath"])
			for alarm in tag["alarms"]:	
				alarmData = {
					"tagName":tagName, 
					"tagPath":tagPath, 
					"tagProvider":tagProvider,
					"alarmName":alarm["name"], 
					"alarmDetails": {
						"enabled": {"value":coalesce(alarmMetaValues[idx].value, True), "config":alarm.get("enabled", True)}, 
						"displayPath": {"value":coalesce(alarmMetaValues[14].value, ""), "config":alarm.get("displayPath", "")}, 
						"priority":{"value":enumCoalesce(alarmMetaValues[idx+1].value, "Diagnostic"), "config":enumCoalesce(alarm.get("priority", None), "Diagnostic")}, 
						"mode":{"value":enumCoalesce(alarmMetaValues[idx+2].value, "Equality"), "config":enumCoalesce(alarm.get("mode", None), "Equality")}, 
						"setpointA":{"value":alarmMetaValues[idx+3].value, "config":alarm.get("setpointA", 0)}, 
						"inclusiveA":{"value":alarmMetaValues[idx+4].value, "config":alarm.get("inclusiveA", True)}, 
						"setpointB":{"value":alarmMetaValues[idx+5].value, "config":alarm.get("setpointB", 0)}, 
						"inclusiveB":{"value":alarmMetaValues[idx+6].value, "config":alarm.get("inclusiveB", True)}, 
						"anyChange":{"value":alarmMetaValues[idx+7].value, "config":alarm.get("anyChange", False)}, 
						"bitOnZero":{"value":alarmMetaValues[idx+8].value, "config":alarm.get("bitOnZero", False)}, 
						"bitPosition":{"value":alarmMetaValues[idx+9].value, "config":alarm.get("bitPosition", 0)}, 
						"activeCondition":{"value":alarmMetaValues[idx+10].value, "config":alarm.get("activeCondition", False)},
						"valueSource":alarmMetaValues[idx+11].value,
						"opcServer":alarmMetaValues[idx+12].value,
						"opcItemPath":alarmMetaValues[idx+13].value,							
						"rationalization": {
							"rationalized":"rationalized" in alarm and alarm["rationalized"] in ("true", True, 1, "1"),
							"rFacility":alarm.get("rFacility", ""),
							"rProcessArea":alarm.get("rProcessArea", ""),
							"rClass":alarm.get("rClass", ""),
							"rDescription":alarm.get("rDescription", ""),
							"rConsequenceNoAction":alarm.get("rConsequenceNoAction", ""),
							"rSafetyImpact":int(alarm.get("rSafetyImpact", 0)),
							"rSafetyImpactDisplay":config["SafetyImpact"]["%d" % int(alarm.get("rSafetyImpact", 0))],
							"rEnvironmentalImpact":int(alarm.get("rEnvironmentalImpact", 0)),
							"rEnvironmentalImpactDisplay":config["EnvironmentalImpact"]["%d" % int(alarm.get("rEnvironmentalImpact", 0))],
							"rFinancialImpact":int(alarm.get("rFinancialImpact", 0)),
							"rFinancialImpactDisplay":config["FinancialImpact"]["%d" % int(alarm.get("rFinancialImpact", 0))],
							"rOperatorUrgency":int(alarm.get("rOperatorUrgency", 0)),
							"rOperatorUrgencyDisplay":config["OperatorUrgency"]["%d" % int(alarm.get("rOperatorUrgency", 0))]["name"],
							"rProbableCause":alarm.get("rProbableCause", ""),
							"rConfirmation":alarm.get("rConfirmation", ""),
							"rCorrectiveActions":alarm.get("rCorrectiveActions", ""),
							"rLastUpdated":alarm.get("rLastUpdated", ""),
							"rActionValue":alarmsNeedAttention.get(tagPath, "")
						}
					}
				}
				
				lastUpdated = alarmData["alarmDetails"]["rationalization"]["rLastUpdated"]
				if lastUpdated != "":
					lastUpdated = system.date.parse(lastUpdated, "yyyy-MM-dd HH:mm:ss")
					lastUpdated = system.date.addSeconds(lastUpdated, 60) # We need to avoid a rationalization that just happened
				
				if alarmData["alarmDetails"]["rationalization"]["rationalized"]:
					actionValue = alarmData["alarmDetails"]["rationalization"]["rActionValue"]
					if actionValue == "" and tagPath in auditEvents:
						if system.date.isAfter(auditEvents[tagPath]["eventTimestamp"], lastUpdated):
							actionValue = auditEvents[tagPath]["actionValue"]
				
					if actionValue != "":	
						alarmData["alarmDetails"]["idx"] = wAIdx
						alarmData["alarmDetails"]["rationalization"]["rActionValue"] = actionValue
						wAIdx += 1
						alarmsWithRationalizationAttention.append(alarmData)
					else:
						alarmData["alarmDetails"]["idx"] = wIdx
						wIdx += 1
						alarmsWithRationalization.append(alarmData)
				else:
					alarmData["alarmDetails"]["idx"] = woIdx
					woIdx += 1
					alarmsWithoutRationalization.append(alarmData)
			
				idx += 15

	sort(alarmsWithoutRationalization, alarmsWithRationalization, alarmsWithRationalizationAttention)
	
	end = system.date.toMillis(system.date.now())
	system.tag.writeBlocking(["AlarmRationalization/Running", "AlarmRationalization/AlarmsWithRationalization", "AlarmRationalization/AlarmsWithRationalizationAttention", "AlarmRationalization/AlarmsWithoutRationalization", "AlarmRationalization/LastCheck", "AlarmRationalization/LastCheckDurationMS"], [False, alarmsWithRationalization, alarmsWithRationalizationAttention, alarmsWithoutRationalization, system.date.now(), end-start])

def sort(alarmsWithoutRationalization, alarmsWithRationalization, alarmsWithRationalizationAttention):
	alarmsWithoutRationalization.sort(key=lambda x:x["tagPath"])
	alarmsWithRationalization.sort(key=lambda x:x["tagPath"])
	alarmsWithRationalizationAttention.sort(key=lambda x:x["tagPath"])
	
	idx = 0
	for alarm in alarmsWithoutRationalization:
		alarm["alarmDetails"]["idx"] = idx
	
	idx = 0
	for alarm in alarmsWithRationalization:
		alarm["alarmDetails"]["idx"] = idx
		
	idx = 0
	for alarm in alarmsWithRationalizationAttention:
		alarm["alarmDetails"]["idx"] = idx

def getAlarmObject(inTagPath, inAlarmName):
	ret = {}
	
	config = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/Configuration"])[0].value))
	
	tagProvider = "default"
	tagPath = inTagPath
	if "]" in inTagPath:
		tagProvider = inTagPath[0:inTagPath.find("]")+1][1:-1]
		tagPath = inTagPath[inTagPath.find("]")+1:]
	
	query = {
	  "options": {
	    "includeUdtMembers": True,
	    "includeUdtDefinitions": False
	  },
	  "condition": {
	    "path": tagPath,
	    "attributes": {
	      "values": [
	        "alarm"
	      ],
	      "requireAll": True
	    }
	  },
	  "returnProperties": [
	    "name",
	    "alarms",
	    "tagType",
	    "quality"
	  ]
	}
	
	tagsToRead = []
	alarmResults = system.tag.query(tagProvider, query)
	for alarm in alarmResults:
		tagName =  alarm["name"]
		tagPath = str(alarm["fullPath"])
		for alarm in alarm["alarms"]:
			alarmName = alarm["name"]
			if alarmName == inAlarmName:
				tagsToRead.extend([
					"%s/Alarms/%s.enabled" % (tagPath, alarmName),
					"%s/Alarms/%s.priority" % (tagPath, alarmName),
					"%s/Alarms/%s.mode" % (tagPath, alarmName),
					"%s/Alarms/%s.setpointA" % (tagPath, alarmName),
					"%s/Alarms/%s.inclusiveA" % (tagPath, alarmName),
					"%s/Alarms/%s.setpointB" % (tagPath, alarmName),
					"%s/Alarms/%s.inclusiveB" % (tagPath, alarmName),
					"%s/Alarms/%s.anyChange" % (tagPath, alarmName),
					"%s/Alarms/%s.bitOnZero" % (tagPath, alarmName),
					"%s/Alarms/%s.bitPosition" % (tagPath, alarmName),
					"%s/Alarms/%s.activeCondition" % (tagPath, alarmName),
					"%s.valueSource" % (tagPath),
					"%s.opcServer" % (tagPath),
					"%s.opcItemPath" % (tagPath),
					"%s/Alarms/%s.displayPath" % (tagPath, alarmName)
				])
				
				alarmMetaValues = system.tag.readBlocking(tagsToRead)
								
				ret = {
					"tagName":tagName, 
					"tagPath":tagPath, 
					"tagProvider":tagProvider,
					"alarmName":alarm["name"], 
					"alarmDetails": {
						"enabled": {"value":coalesce(alarmMetaValues[0].value, True), "config":alarm.get("enabled", True)}, 
						"displayPath": {"value":coalesce(alarmMetaValues[14].value, ""), "config":alarm.get("displayPath", "")}, 
						"priority":{"value":enumCoalesce(alarmMetaValues[1].value, "Diagnostic"), "config":enumCoalesce(alarm.get("priority", None), "Diagnostic")}, 
						"mode":{"value":enumCoalesce(alarmMetaValues[2].value, "Equality"), "config":enumCoalesce(alarm.get("mode", None), "Equality")}, 
						"setpointA":{"value":alarmMetaValues[3].value, "config":alarm.get("setpointA", 0)}, 
						"inclusiveA":{"value":alarmMetaValues[4].value, "config":alarm.get("inclusiveA", True)}, 
						"setpointB":{"value":alarmMetaValues[5].value, "config":alarm.get("setpointB", 0)}, 
						"inclusiveB":{"value":alarmMetaValues[6].value, "config":alarm.get("inclusiveB", True)}, 
						"anyChange":{"value":alarmMetaValues[7].value, "config":alarm.get("anyChange", False)}, 
						"bitOnZero":{"value":alarmMetaValues[8].value, "config":alarm.get("bitOnZero", False)}, 
						"bitPosition":{"value":alarmMetaValues[9].value, "config":alarm.get("bitPosition", 0)}, 
						"activeCondition":{"value":alarmMetaValues[10].value, "config":alarm.get("activeCondition", False)},
						"valueSource":alarmMetaValues[11].value,
						"opcServer":alarmMetaValues[12].value,
						"opcItemPath":alarmMetaValues[13].value,							
						"rationalization": {
							"rationalized":"rationalized" in alarm and alarm["rationalized"] in ("true", True, 1, "1"),
							"rFacility":alarm.get("rFacility", ""),
							"rProcessArea":alarm.get("rProcessArea", ""),
							"rClass":alarm.get("rClass", ""),
							"rDescription":alarm.get("rDescription", ""),
							"rConsequenceNoAction":alarm.get("rConsequenceNoAction", ""),
							"rSafetyImpact":int(alarm.get("rSafetyImpact", 0)),
							"rSafetyImpactDisplay":config["SafetyImpact"]["%d" % int(alarm.get("rSafetyImpact", 0))],
							"rEnvironmentalImpact":int(alarm.get("rEnvironmentalImpact", 0)),
							"rEnvironmentalImpactDisplay":config["EnvironmentalImpact"]["%d" % int(alarm.get("rEnvironmentalImpact", 0))],
							"rFinancialImpact":int(alarm.get("rFinancialImpact", 0)),
							"rFinancialImpactDisplay":config["FinancialImpact"]["%d" % int(alarm.get("rFinancialImpact", 0))],
							"rOperatorUrgency":int(alarm.get("rOperatorUrgency", 0)),
							"rOperatorUrgencyDisplay":config["OperatorUrgency"]["%d" % int(alarm.get("rOperatorUrgency", 0))]["name"],
							"rProbableCause":alarm.get("rProbableCause", ""),
							"rConfirmation":alarm.get("rConfirmation", ""),
							"rCorrectiveActions":alarm.get("rCorrectiveActions", ""),
							"rLastUpdated":alarm.get("rLastUpdated", ""),
							"rActionValue":""
						}
					}
				}
				
				break
	
	return ret
									
def validateRationalization(tagPath, alarmName, enabled, priority, idx, attention, rationalization):
	if rationalization["rFacility"] == "":
		return (False, "Please select a facility")
	elif rationalization["rProcessArea"] == "":
		return (False, "Please select a process area")	
	elif rationalization["rDescription"] == "":
		return (False, "Please enter in a description")	
	elif rationalization["rClass"] == "":
		return (False, "Please select an alarm class")	
	
	if enabled:
		if rationalization["rProbableCause"] == "":
			return (False, "Please enter in a probable cause")	
		elif rationalization["rConfirmation"] == "":
			return (False, "Please enter in a confirmation")	
		elif rationalization["rCorrectiveActions"] == "":
			return (False, "Please enter in correction actions")	
		elif rationalization["rConsequenceNoAction"] == "":
			return (False, "Please enter in a consequence for no action")	
	
	return (True, None)
		
def saveRationalization(alarmsWithoutRationalization, alarmsWithRationalization, alarmsWithRationalizationAttention, tagPath, alarmName, enabled, priority, idx, attention, rationalization):
	provider = tagPath[0:tagPath.find("]")+1]
	simplePath = tagPath[tagPath.find("]")+1:]
	basePath = "%s%s" % (provider, "/".join(simplePath.split("/")[0:-1]))
	tagName = simplePath.split("/")[-1]
	
	rationalized = rationalization["rationalized"]
	
	alarmDetails = {
		"name": alarmName,
		"priority": priority,
		"enabled": enabled
	}
	
	for key in rationalization:
		alarmDetails[key] = rationalization[key]
	
	alarmDetails["rationalized"] = True
	alarmDetails["rLastUpdated"] = system.date.format(system.date.now(), "yyyy-MM-dd HH:mm:ss")
	
	tags = [
		{
			"name":tagName,
			"alarms":[
				alarmDetails
			]
		}
	]
	
	code = system.tag.configure(basePath, tags, "m")[0]
	if not code.isGood():
		AlarmRationalization.Popup.showMessage("Error updating tag alarm (%s:%s) with quality %s" % (tagPath, alarmName, code.toValue().value))
	else:
		if not rationalized:
			alarmObj = alarmsWithoutRationalization.pop(idx)
			alarmsWithRationalization.append(alarmObj)
		else:
			if attention:
				alarmObj = alarmsWithRationalizationAttention.pop(idx)
				alarmsWithRationalization.append(alarmObj)
			else:
				alarmObj = alarmsWithRationalization[idx]
		
		alarmObj["alarmDetails"]["rationalization"] = rationalization
		alarmObj["alarmDetails"]["enabled"] = {"value":enabled, "config":enabled}
		alarmObj["alarmDetails"]["priority"] = {"value":priority, "config":priority}
		alarmObj["alarmDetails"]["rationalization"]["rActionValue"] = ""
	
def validateAndSaveRationalization(tagPath, alarmName, enabled, priority, idx, attention, rationalization):
	validateAndSaveRationalizations([{"tagPath":tagPath, "alarmName":alarmName, "enabled":enabled, "priority":priority, "idx":idx, "attention":attention, "rationalization":rationalization}])

def validateAndSaveRationalizations(alarms):
	results = system.tag.readBlocking(["AlarmRationalization/AlarmsWithRationalization", "AlarmRationalization/AlarmsWithoutRationalization", "AlarmRationalization/AlarmsWithRationalizationAttention"])
	alarmsWithRationalization = system.util.jsonDecode(str(results[0].value))
	alarmsWithoutRationalization = system.util.jsonDecode(str(results[1].value))
	alarmsWithRationalizationAttention = system.util.jsonDecode(str(results[2].value))
	
	for alarm in alarms:
		(success, errorMessage) = validateRationalization(alarm["tagPath"], alarm["alarmName"], alarm["enabled"], alarm["priority"], alarm["idx"], alarm["attention"], alarm["rationalization"])
		if not success:
			AlarmRationalization.Popup.showMessage(errorMessage + ("" if len(alarms) == 1 else " on alarm '%s' on tag '%s'" % (alarm["alarmName"], alarm["tagPath"])))
			return
	
	for alarm in alarms:
		saveRationalization(alarmsWithoutRationalization, alarmsWithRationalization, alarmsWithRationalizationAttention, alarm["tagPath"], alarm["alarmName"], alarm["enabled"], alarm["priority"], alarm["idx"], alarm["attention"], alarm["rationalization"])
	
	sort(alarmsWithoutRationalization, alarmsWithRationalization, alarmsWithRationalizationAttention)

	system.tag.writeBlocking(["AlarmRationalization/AlarmsWithRationalization", "AlarmRationalization/AlarmsWithoutRationalization", "AlarmRationalization/AlarmsWithRationalizationAttention"], [alarmsWithRationalization, alarmsWithoutRationalization, alarmsWithRationalizationAttention])
	
	system.perspective.navigate(view="AlarmRationalization/Dashboard")
	system.perspective.closeDock("alarmConfig")
	AlarmRationalization.Popup.showMessage("Alarm%s rationalized successfully" % ("s" if len(alarms) > 1 else ""))
			
def export(alarmList):
	alarms = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/%s" % alarmList])[0].value))

	headers = ["tagPath", "alarm", "enabled", "facility", "processArea", "description", "class", "probableCause", "confirmation", "correctiveActions", "consequenceNoAction", "safetyImpact", "environmentalImpact", "financialImpact", "operatorUrgency"]
	data = []
	
	for alarm in alarms:
		data.append([alarm["tagPath"], alarm["alarmName"], alarm["alarmDetails"]["enabled"]["value"], alarm["alarmDetails"]["rationalization"]["rFacility"], alarm["alarmDetails"]["rationalization"]["rProcessArea"], alarm["alarmDetails"]["rationalization"]["rDescription"], alarm["alarmDetails"]["rationalization"]["rClass"], alarm["alarmDetails"]["rationalization"]["rProbableCause"], alarm["alarmDetails"]["rationalization"]["rConfirmation"], alarm["alarmDetails"]["rationalization"]["rCorrectiveActions"], alarm["alarmDetails"]["rationalization"]["rConsequenceNoAction"], alarm["alarmDetails"]["rationalization"]["rSafetyImpact"], alarm["alarmDetails"]["rationalization"]["rEnvironmentalImpact"], alarm["alarmDetails"]["rationalization"]["rFinancialImpact"], alarm["alarmDetails"]["rationalization"]["rOperatorUrgency"]])
		
	ds = system.dataset.toDataSet(headers, data)
	csv = system.dataset.toCSV(ds)
	system.perspective.download("%s.csv" % alarmList, csv)
	
def importFromCSV(csvData):
	import csv
	import traceback
	
	config = system.util.jsonDecode(str(system.tag.readBlocking(["AlarmRationalization/Configuration"])[0].value))
	results = system.tag.readBlocking(["AlarmRationalization/AlarmsWithRationalization", "AlarmRationalization/AlarmsWithoutRationalization", "AlarmRationalization/AlarmsWithRationalizationAttention"])
	alarmsWithRationalization = system.util.jsonDecode(str(results[0].value))
	alarmsWithoutRationalization = system.util.jsonDecode(str(results[1].value))
	alarmsWithRationalizationAttention = system.util.jsonDecode(str(results[2].value))
	alarmsWithRationalizationList = ["tagPath:%s:/alarmName:%s" % (alarm["tagPath"], alarm["alarmName"]) for alarm in alarmsWithRationalization]
	alarmsWithoutRationalizationList = ["tagPath:%s:/alarmName:%s" % (alarm["tagPath"], alarm["alarmName"]) for alarm in alarmsWithoutRationalization]
	alarmsWithRationalizationAttentionList = ["tagPath:%s:/alarmName:%s" % (alarm["tagPath"], alarm["alarmName"]) for alarm in alarmsWithRationalizationAttention]
	
	alarmsToRationalize = []
	
	lines = csvData.splitlines()
	reader = csv.reader(lines)
	reader.next()
	rowIdx = 1
	for row in reader:
		tagPath = row[0]
		alarmName = row[1]
		alarmPath = "tagPath:%s:/alarmName:%s" % (tagPath, alarmName)
		enabled = str(row[2]).lower() == "true"
		priority = "Diagnostic"
		idx = None
		rationalized = False
		attention = False
		
		try:
			idx = alarmsWithoutRationalizationList.index(alarmPath)
		except:
			pass
			
		if idx == None:
			try:
				idx = alarmsWithRationalizationList.index(alarmPath)
				rationalized = True
			except:
				pass
				
		if idx == None:
			try:
				idx = alarmsWithRationalizationAttentionList.index(alarmPath)
				rationalized = True
				attention = True
			except:
				pass
		
		if idx == None:
			AlarmRationalization.Popup.showMessage("Alarm '%s' from tag '%s' was not found. Either run the rationalization check or verify the tag exists before trying again." % (alarmName, tagPath))
			return
		
		try:
			impact = max(int(row[11]), int(row[12]), int(row[13]))
			states = config["OperatorUrgency"][str(int(row[14]))]["states"]
			for stateIdx in states:
				if str(stateIdx) == str(impact):
					priority = states[str(stateIdx)]
					break
		
			rationalization = {
				"rationalized":rationalized,
				"rFacility":row[3],
				"rProcessArea":row[4],
				"rDescription":row[5],
				"rClass":row[6],
				"rProbableCause":row[7],
				"rConfirmation":row[8],
				"rCorrectiveActions":row[9],
				"rConsequenceNoAction":row[10],
				"rSafetyImpact":int(row[11]),
				"rSafetyImpactDisplay":config["SafetyImpact"]["%d" % int(row[11])],
				"rEnvironmentalImpact":int(row[12]),
				"rEnvironmentalImpactDisplay":config["EnvironmentalImpact"]["%d" % int(row[12])],
				"rFinancialImpact":int(row[13]),
				"rFinancialImpactDisplay":config["FinancialImpact"]["%d" % int(row[13])],
				"rOperatorUrgency":int(row[14]),
				"rOperatorUrgencyDisplay":config["OperatorUrgency"]["%d" % int(row[14])]["name"]
			}
		except:
			AlarmRationalization.Popup.showMessage("Error parsing CSV on row %d. Most likely Safety Impact, Environmental Impact, Financial Impact, or Operator Urgency are not valid integers." % rowIdx)
			system.util.getLogger("AlarmRationalization").error(traceback.format_exc())
			return
		
		alarmsToRationalize.append({"tagPath":tagPath, "alarmName":alarmName, "enabled":enabled, "priority":priority, "idx":idx, "attention":attention, "rationalization":rationalization})
		rowIdx += 1
	
	validateAndSaveRationalizations(alarmsToRationalize)