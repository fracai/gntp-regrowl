from gntp import *
import urllib2
import Growl
import logging

def register_send(self):
	'''
	Resend a GNTP Register message to Growl running on a local OSX Machine
	'''
	logging.getLogger('ReGrowl').info('Sending local registration')
	
	#Local growls only need a list of strings
	notifications=[]
	defaultNotifications = []
	for notice in self.notifications:
		notifications.append(notice['Notification-Name'])
		if notice.get('Notification-Enabled',True):
			defaultNotifications.append(notice['Notification-Name'])
	
	appIcon = get_resource(self,'Application-Icon')
	
	growl = Growl.GrowlNotifier(
		applicationName			= self.headers['Application-Name'],
		notifications			= notifications,
		defaultNotifications	= defaultNotifications,
		applicationIcon			= appIcon,
	)
	growl.register()
	return self.encode()
	
def notice_send(self):
	'''
	Resend a GNTP Notify message to Growl running on a local OSX Machine
	'''
	logging.getLogger('ReGrowl').info('Sending local notification')
	
	growl = Growl.GrowlNotifier(
		applicationName			= self.headers['Application-Name'],
		notifications			= [self.headers['Notification-Name']]
	)
	
	noticeIcon = get_resource(self,'Notification-Icon')
	
	growl.notify(
		noteType = self.headers['Notification-Name'],
		title = self.headers['Notification-Title'],
		description=self.headers.get('Notification-Text',''),
		icon=noticeIcon
	)
	return self.encode()

def get_resource(self,key):
	logging.getLogger('ReGrowl').info('Getting resource')
	try:
		resource = self.headers.get(key,'')
		if resource.startswith('x-growl-resource://'):
			resource = resource.split('://')
			return self.resources.get(resource[1])['Data']
		elif resource.startswith('http'):
			resource = resource.replace(' ', '%20')
			icon = urllib2.urlopen(resource,None,5)
			return icon.read()
		else:
			return None
	except Exception,e:
		print e
		return None
	
def add_origin_info(self):
	self.add_header('Origin-Machine-Name',platform.node())
	self.add_header('Origin-Software-Name','ReGrowl Server')
	self.add_header('Origin-Software-Version','0.1')
	self.add_header('Origin-Platform-Name',platform.system())
	self.add_header('Origin-Platform-Version',platform.platform())

GNTPRegister.send = register_send
GNTPNotice.send = notice_send

GNTPOK.add_origin_info = add_origin_info
GNTPError.add_origin_info = add_origin_info


