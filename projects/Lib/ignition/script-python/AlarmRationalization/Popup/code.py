def showError(message, pageId=None):
	popupMessage("error", message, "Error", "Error", pageId)
	
def showMessage(message, pageId=None):
	popupMessage("info", message, "Text", "Message", pageId)
	
def popupMessage(icon, message, displayClass, title, pageId=None):
	params = {"icon":icon, "display":message, "class":displayClass}
	system.perspective.openPopup(id="message", view="AlarmRationalization/Message", params=params, title=title, showCloseIcon=True, draggable=True, resizable=True, modal=True, overlayDismiss=False, pageId=pageId)
	
def showConfirmation(message, function, params={}, title="Confirmation", pageId=None):
	params = {"icon":"help", "display":message, "class":"Text", "function":{"script":function, "params":params}}
	system.perspective.openPopup(id="confirmation", view="AlarmRationalization/Confirmation", params=params, title=title, showCloseIcon=True, draggable=True, resizable=True, modal=True, overlayDismiss=False, pageId=pageId)