def Mode(path, mode):
 
    results = system.tag.browse(path, {})
     
    # Loop through every item in the results and check if opcitempath has value
    for result in results.getResults():
#		print result['fullPath']
		
		# we have opc tag so it is opc tag
		if system.tag.readBlocking([str(result['fullPath']) + ".opcItemPath"])[0].value != "": 
			
			if mode == True: # Sim ON
				
				# Read the OPC value to write to memory
				if str(system.tag.read( str(result['fullPath'])) ) == 'Good':
					value = system.tag.read(str(result['fullPath'])).value
					system.tag.writeBlocking([str(result['fullPath']) + ".valueSource"],["memory"])
					system.tag.write(str(result['fullPath']), value)
				else: # if quality is bad no valid value so just change to memory
					system.tag.writeBlocking([str(result['fullPath']) + ".valueSource"],["memory"])

			else: # Sim OFF
				system.tag.writeBlocking([str(result['fullPath']) + ".valueSource"],["opc"])
 
        # If the item has children, call the function to repeat the process but starting at the child.
		if result['hasChildren'] == True:
			Mode(result['fullPath'], mode)
