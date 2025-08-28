def TankNotification (activitySubtitle,fbs,assetName,processValue,sp):
	import system
	url='https://northvolt0.webhook.office.com/webhookb2/12f8e36f-e815-461f-9446-819dd8ff2c91@706c5db9-5278-483b-b622-70084f823a12/IncomingWebhook/9eaea69b95f74bd390f34e6360707296/239fec42-5af4-438d-8864-e806f0187c94'
	#TestWebHock url
	#url='https://northvolt0.webhook.office.com/webhookb2/72889ebb-443d-45aa-a26d-5397cf82b1a3@706c5db9-5278-483b-b622-70084f823a12/IncomingWebhook/957fa16fbfc545c8b8470a9b60464f2f/2eace467-32ff-48e5-9977-77490fb5b9c2'
	contentType ="application/json"
	
	brutData = {
    "@type": "MessageCard",
	"@context": "http://schema.org/extensions",
	"themeColor": "0076D7",
	"summary": "Revolt Notification",
	"sections": [{
	        "activityTitle": "Revolt Ett - Low Tank Level - Notification",
	        "activitySubtitle": "**<font color='#f03232'>" + activitySubtitle + "</font>**",
	        "activityImage": "",
 # Below "facts" contained the function parameters "name" and "value"           
	        "facts": [{
	            "name": "Asset Name:",
	            "value": assetName},
	            {
	           	"name": "FBS:",
	            "value": fbs},
	            {
	           	"name": "Current Level (%):",
	            "value": processValue},	
	            {
	           	"name": "Set Point(%):",
	            "value": sp},            
	            {
	           	"name": "Event Time",
	            "value": system.date.now()},          
	        ]
	      }]
	   }
	postData = system.util.jsonEncode(brutData)
	result=system.net.httpPost(url,contentType,postData)
	return result 
#Notification("su",'HHH Alarm',22.4,'','','','','')

#[nv]F1/C1/SM1/SDM01/Alarm/Alarm