# Import libraries
import xml.etree.ElementTree as ET
import os
from zipfile import ZipFile

from com.inductiveautomation.ignition.gateway import IgnitionGateway
context = IgnitionGateway.get()
dataDirectory = str(context.getSystemManager().getDataDir().getAbsolutePath())
rootTempDir = os.path.join(os.path.dirname(dataDirectory), 'temp', 'icon_import')
perspectiveIconFolder = os.path.join(dataDirectory, 'modules', 'com.inductiveautomation.perspective', 'icons')

protectedLibraries = ['ignition', 'material', 'symbol_mimic', 'symbol_p&id', 'symbol_simple']

def log(message):
	"""Send a message to the Icon Management Console."""
	exchange.perspective.broadcastMessage('iconManager_log', {
		'message': message
	})

def getLibraries():
	"""Returns a list of icon libraries."""
	libraries = []
	contents = os.listdir(perspectiveIconFolder)
	for file in contents:
		split_tup = os.path.splitext(file)
		if split_tup[1] == ".svg":
			name = split_tup[0]
			
			libraries.append(Library(name))
	return libraries	
	
def createLibrary(name):
	"""Create a new icon library."""
	if name in protectedLibraries:
		log('Cannot create library named <b>%s</b>, name is reserved.' % name)
		raise Exception("Library name is reserved")
	
	if name == "" or name is None:
		log('Cannot create library with no name.')
		raise Exception("Library must have a name")
	
	existingLibraries = getLibraries()
	
	if name in existingLibraries:
		log('Library name <b>%s</b> is not unique.' % name)
		raise Exception("Library must have a unique name")
	
	# Register xml namespace
	ET.register_namespace('', "http://www.w3.org/2000/svg")
	ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
	
	# Format xml document
	xml = ET.Element('svg')
	defs = ET.SubElement(xml, 'defs')
	style = ET.SubElement(defs, 'style')
	style.text = ".icon { display: none } .icon:target { display: inline }"

	# Create tree from xml object
	newTree = ET.ElementTree(xml)
		
	# Get library path
	libraryPath = os.path.join(perspectiveIconFolder, name+".svg")
	# Save xml to file
	newTree.write(libraryPath, encoding='utf-8',xml_declaration=True)
	
	log('Library <b>%s</b> was created.' % name)
	
class Library:
	"""Library helper class."""
	def __init__(self, name):
		self.name = name
		self.path = self.getPathFromName(name)
		self.tempPath = self.getTempPathFromName(name)

	@staticmethod
	def getPathFromName(name):
		"""Get the absolute file path of a library by name."""
		libraryFile = name + ".svg"
		libraryPath = os.path.join(perspectiveIconFolder, libraryFile)
		return libraryPath
		
	@staticmethod
	def getTempPathFromName(name):
		"""Get the absolute file path of a libraties temporary storage by name."""
		tempPath = os.path.join(rootTempDir, name)
		return tempPath

	def extractZip(self, filepath):
		"""Extract zip to temp folder."""
		with ZipFile(filepath, 'r') as zip_ref:
			zip_ref.extractall(self.tempPath)	
			
	@staticmethod
	def iterAttribFind(element, attrib, value=None):
		"""Returns all elements with given attribute"""
		if value is None:
			iterator = element.iterfind(".//*[@%s]" % attrib)
			
		else:
			iterator = element.iterfind(".//*[@%s='%s']" % (attrib, value))
		
		results = []
		for item in iterator:
			results.append(item)
		return results
			
	@staticmethod
	def getSVG(filepath, name):
		"""Return xml object for a SVG given a filepath and name."""
		tree = ET.parse(filepath)
		root = tree.getroot()
		attrib = root.attrib
		viewBox = attrib['viewBox']
		svg = ET.Element('svg', {"viewBox":viewBox})
	
		# Clear any conflicting attributes
		for element in root.iter():
			# List of attributes to remove
			attributes = ['class', 'id', 'data-name', 'fill']
			for attribute in attributes:
				element.attrib.pop(attribute, None)
		
		# Get top svg group
		svgGroup = root.find('g')
	
		# If no group exists create one
		if svgGroup is None:
			svgGroup = ET.Element('g')
			# Add elements to new group
			for element in root:
				svgGroup.append(element)
	
		# Add attributes to group
		svgGroup.attrib = {"class":"icon","id":name}
	
		# Add group to svg object
		svg.append(svgGroup)
	
		return svg
		
	@staticmethod
	def removeTag(tag, rootElement):
		"""Helper function to remove all tags of a specific name from a specified element."""
		for parent in rootElement.findall('.//%s/..' % tag ):
			for element in parent.findall('%s' % tag):
					parent.remove(element)

	def getName(self):
		"""Get the library name."""
		return self.name
		
	def getPath(self):
		"""Returns the abolute path."""
		return self.path
	
	def getTempPath(self):
		"""Get the temporary storage path."""
		return self.tempPath

	def removeIcons(self, icons):
		"""Removes icons from library. Accepts a list of icon paths."""
		libraryPath = self.path
				
		tree = ET.parse(libraryPath)
		root = tree.getroot()
		
		for icon in icons:
			name = icon.split('/')[1]
			iterator = root.iterfind(".//*[@id='%s']..." % name)
			for parent in iterator:
				root.remove(parent)
			log('Removed icon <b>%s</b> from library.' % (icon) )
			
		tree.write(libraryPath, encoding='utf-8',xml_declaration=True)
		exchange.perspective.broadcastMessage('iconManager_libraryModified', {'library': self.name})
		
	def getIcons(self):
		"""Returns the path of all icons in the library."""
		libraryPath = self.path
		
		tree = ET.parse(libraryPath)
		root = tree.getroot()
		
		icons = []
		
		attrib = 'id'
		
		elements = self.iterAttribFind(root, attrib)
		
		for element in elements:
			name = element.attrib['id']
			icons.append("%s/%s" % (self.name, name))
		
		return icons
	
	def rename(self, name):
		"""Rename this library."""
		if name in protectedLibraries:
			log('Failed to rename library, name <b>%s</b> is protected.' % (name))
			raise Exception("Cannot change name of protected library")
			
		if name == "" or name is None:
			log('Failed to rename library, name must not be empty.')
			raise Exception("Library must have a name")
		
		existingLibraries = getLibraries()
		
		if name in existingLibraries:
			log('Failed to rename library. Name <b>%s</b> is not unique.' % (name))
			raise Exception("Library must have a unique name")
			
		existingPath = self.path
		newPath = self.getPathFromName(name)
		
		os.rename(existingPath, newPath)
		
		log('Library <b>%s</b> was renamed to <b>%s</b>.' % (self.name, name))
			
	def delete(self):
		"""Delete this library."""
		
		if self.name in protectedLibraries:
			log('Cannot delete system library <b>%s</b>.' % (self.name))
			raise Exception("Library name is reserved")
		
		self.deleteTempFiles()
		
		os.remove(self.path)
		log('Library <b>%s</b> was deleted.' % (self.name))
	
	def importFiles(self, overwrite=False):
		"""Imports all files from the library's temp directory."""
		log('Starting icon import into <b>%s</b>.' % (self.name))
			
		# Unzip all .zip files in temp directory
		for path, subdirs, files in os.walk(self.tempPath):
			for f in files:
				# Check for zip file type
				if f.endswith('.zip'):
					log('Extracting compressed file <b>%s</b>.' % (f))
					
					# Add root directory to file
					filepath = os.path.join(path, f)
					self.extractZip(filepath)
					os.remove(filepath)
					log('Extracted compressed file <b>%s</b>.' % (f))
		
		libraryPath = self.path
		
		tree = ET.parse(libraryPath)
		root = tree.getroot()
		
		filepaths = []
		i = 0
		for path, subdirs, files in os.walk(self.tempPath):
				
			for file in files:
				i += 1

				# Check for svg file type and uniqueness
				if file.endswith('.svg'):
					# Add root directory to file
					filepath = os.path.join(path, file)
					filepaths.append(filepath)
		
		totalIcons = len(filepaths)
		successfulIcons = 0
		failedIcons = 0
		log('Preparing to import <b>%s icons</b>.' % (totalIcons))
		
		for filepath in filepaths:
			newIcon = ET.parse(filepath).getroot()
			if newIcon.get('viewBox') is None:
				newIcon.set("viewbox", "0 0 24 24")
			name = os.path.basename(filepath).replace('.svg', '')
			log('Importing icon <b>%s</b>...' % name)
			try:
				group = newIcon.find('g')
				
				if group is None:
					subElems = newIcon.findall('*')
					group = ET.Element('g')
					for elem in subElems:
						newIcon.remove(elem)
						group.append(elem)
					
					newIcon.append(group)
	
				group.set("class", "icon")
				group.set("id", name)
				
				root.append(newIcon)
				successfulIcons += 1
				log('Icon <b>%s</b> imported.' % (name))
			except:
				failedIcons += 1
				log('Icon <b>%s</b> failed to import. Skipping.' % (name))


		# Write to file					
		log('Writing XML to file at path <b>%s</b>.' % (libraryPath))
		tree.write(libraryPath, encoding='utf-8',xml_declaration=True)
		
		# Remove all temp files
		self.deleteTempFiles()
		log('<b>Import complete!</b>')
		exchange.perspective.broadcastMessage('iconManager_libraryModified', {'library': self.name})
		
	def getTempFiles(self):
		"""Returns a list of temp files."""
		
		directory = {}
		start = self.tempPath.rfind(os.sep) + 1
		for path, dirs, files in os.walk(self.tempPath):
		    folders = path[start:].split(os.sep)
		    subdir = dict.fromkeys(files)
		    parent = reduce(dict.get, folders[:-1], directory)
		    parent[folders[-1]] = subdir
		    
		tree = []
		for item in directory.get(self.name, []):
			tree.append({
				'label': item,
				'expanded': False,
				'items': []
			})
		return tree
	
	def createTempFile(self, event):
		"""Create temporary file."""
		if os.path.isdir(self.tempPath) is False:
			os.makedirs(self.tempPath)
			log('Created temporary folder <b>%s</b>.' % self.tempPath)
		event.file.copyTo('%s/%s' % (self.tempPath, event.file.name))
		log('Received file <b>%s</b>.' % (event.file.name))
		exchange.perspective.broadcastMessage('iconManager_refreshTempTree')
		
	
	def deleteTempFiles(self):
		"""Delete temp files created for import."""
		for path, subdirs, files in os.walk(self.tempPath, topdown=False):
			for file in files:
				filepath = os.path.join(path, file)
				os.remove(filepath)
				log('Deleted file <b>%s</b>.' % (filepath))
				
			for dir in subdirs:
				dirpath = os.path.join(path, dir)
				os.rmdir(dirpath)
				log('Deleted directory <b>%s</b>.' % (dirpath))
				
		if os.path.isdir(self.tempPath):
			os.rmdir(self.tempPath)
			log('Deleted directory <b>%s</b>.' % (self.tempPath))				
				
		exchange.perspective.broadcastMessage('iconManager_refreshTempTree')