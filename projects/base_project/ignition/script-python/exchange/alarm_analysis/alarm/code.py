## Common Var ##
QUERY_BASE = 'Alarms/{}/{}'

## Alarm Queries ##
def alarmHistory(dbType, startDate, endDate, active, clear, ack, limit, minPriority, maxPriority):
	""" 
		Return alarm history data for alarms between input dates that fit the input criteria.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
			active - Whether to return alarms that are active (bool)
			clear - Whether to return alarms that are cleared (bool)
			ack - Whether to return alarms that are acknowledged (bool)
			limit - Limit for number of alarms to pull (int)
			minPriority - Minimum priority to return alarms for (int)
			maxPriority - Max priority to return alarms for (int)
		Returns:
			dataset of alarm journal data
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarm History')
	params = {'startDate': startDate, 'endDate': endDate, 'limit': limit}
	result = system.db.runNamedQuery(nQuery, params)
	return system.db.toPyDataSet(result)
	
def alarmSummary(dbType, startDate, endDate, limit):
	""" 
		Return alarm summary data for ???.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
			limit - Limit for number of alarms to pull (int)
		Returns:
			dataset of alarm journal data
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarm Summary')
	params = {'startDate': startDate, 'endDate': endDate, 'limit': limit}
	result = system.db.runNamedQuery(nQuery, params)
	return result
	
def alarmSummaryTable(dbType, startDate, endDate):
	""" 
		Return data for an alarm summary table
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
		Returns:
			dataset of alarm summary
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarm Summary Table')
	params = {'startDate': startDate, 'endDate': endDate}
	result = system.db.runNamedQuery(nQuery, params)
	return summaryTable(jsonify(result, False))
	
def alarms(dbType, startDate, endDate):
	""" 
		Return all alarm journal data between the input dates.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
		Returns:
			dataset of alarm journal data
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarms')
	params = {'startDate': startDate, 'endDate': endDate}
	result = system.db.runNamedQuery(nQuery, params)
	return system.db.toPyDataSet(result)
	
def alarmByHour(dbType, startDate, endDate):
	""" 
		Return alarm duration and count between input dates by hour.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
		Returns:
			dataset of alarm data by hour
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarms By Hour')
	params = {'startDate': startDate, 'endDate': endDate}
	result = system.db.runNamedQuery(nQuery, params)
	return jsonify(result)
	
def alarmDuration(dbType, startDate, endDate, limit):
	""" 
		Return alarms with the longest duration.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
			limit - Limit the number of alarms to return duration for (int)
		Returns:
			dataset of longest duration alarms
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarms Duration')
	params = {'startDate': startDate, 'endDate': endDate, 'limit': limit}
	result = system.db.runNamedQuery(nQuery, params)
	return jsonify(result)

def alarmFrequency(dbType, startDate, endDate, limit):
	""" 
		Return alarms with the highest frequency.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
			limit - Limit the number of alarms to return frequency for (int)
		Returns:
			dataset of most frequent alarms
	"""
	nQuery = QUERY_BASE.format(dbType, 'Alarms Frequency')
	params = {'startDate': startDate, 'endDate': endDate, 'limit': limit}
	result = system.db.runNamedQuery(nQuery, params)
	return jsonify(result)
	
def longestDuration(dbType, startDate, endDate):
	""" 
		Return the alarm with the longest duration between the input dates.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
		Returns:
			dataset of alarm with longest duration
	"""
	nQuery = QUERY_BASE.format(dbType, 'Longest Duration Alarm')
	params = {'startDate': startDate, 'endDate': endDate}
	result = system.db.runNamedQuery(nQuery, params)
	return jsonify(result, False)
	
def mostFrequent(dbType, startDate, endDate):
	""" 
		Return the most frequenct alarm between input dates.
		Args:
			startDate - Start range for dates to pull alarms from (datetime)
			endDate - End range for dates to pull alarms from (datetime)
		Returns:
			dataset of most frequent alarm
	"""
	nQuery = QUERY_BASE.format(dbType, 'Most Frequent Alarm')
	params = {'startDate': startDate, 'endDate': endDate}
	result = system.db.runNamedQuery(nQuery, params)
	return result
		
## Helper Functions ##
def summaryTable(ds):
	""" Take in Alarm Summary Table query dataset and convert tabulated summary table """
	priorities = ["Diagnostic", "Low", "Medium", "High", "Critical"]
	rows = []
	for priority in priorities:
		newRow = None
		for row in ds:
			if priority == row["Priority"]:
				newRow = row
		if newRow == None:
			newRow = ({"Priority":priority, "total":0, "active":0, "unacknowledged":0, "cleared":0, "acknowledgeTime":0, "clearTime":0, "totalTime":0})
		rows.append(newRow)
	return rows
	
def jsonify(ds, returnNull=True):
	""" Take in dataset and convert to a json like form """
	headers = ds.getColumnNames()
	rowCount = ds.getRowCount()
	if rowCount > 0:
		form = [{h: ds.getValueAt(row, h) for h in headers} for row in range(rowCount)]
	else:
		form = None if returnNull else [{h: '' for h in headers}]
	return form
	
