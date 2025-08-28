def broadcastMessage(messageType, payload=None):
	"""Broadcast a message to all sessions."""
	if payload is None: payload = {}
	sessions = system.perspective.getSessionInfo()
	for s in sessions:
		for pageId in s.pageIds:
			try:
				system.perspective.sendMessage(messageType, payload=payload, scope="session", pageId=pageId, sessionId=s.id)
			except:
				pass