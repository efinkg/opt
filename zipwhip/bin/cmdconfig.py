import argparse
import zwconfig
import zwutil

parser = argparse.ArgumentParser(add_help=False, description='Manage the zipwhip.conf file.',
	epilog="Examples:\n\n\tsudo python cmdconfig.py --write --write-phonenum 5555551212 --write-password asdfasdf --write-region Newark,US --write-twitter cool --write-getnewsessionandclientid")
parser.add_argument('--read', action="store_true", help="Read the conf file.")
parser.add_argument('--read-phonenum', action="store_true", help='Return the Zipwhip account phone number')
parser.add_argument('--read-password', action="store_true", help='Return the Zipwhip account password')
parser.add_argument('--read-region', action="store_true", help='Return the Region for weather info')
parser.add_argument('--read-twitter', action="store_true", help='Return the Twitter search keyword(s)')
parser.add_argument('--read-sessionid', action="store_true", help='Return the SessionID')
parser.add_argument('--read-clientid', action="store_true", help='Return the ClientID')
parser.add_argument('--write', action="store_true", help="Write to the conf file.")
parser.add_argument('--write-phonenum', help='Zipwhip account phone number')
parser.add_argument('--write-password', help='Zipwhip account password')
parser.add_argument('--write-region', help='Region for weather info')
parser.add_argument('--write-twitter', help='Twitter search keyword(s)')
parser.add_argument('--write-getnewsessionandclientid', action="store_true")


'''
write_p = argparse.ArgumentParser(add_help=False, parents=[parser])
#write_p = argparse.ArgumentParser(add_help=False)
#write_p.add_argument('--read', action="store_true", help="Read the conf file")
write_p.add_argument('--phonenum', help='Zipwhip account phone number')
write_p.add_argument('--password', help='Zipwhip account password')
write_p.add_argument('--region', help='Region for weather info')
write_p.add_argument('--twitter', help='Twitter search keyword(s)')
write_p.add_argument('--getnewsessionandclientid', action="store_true")

read_p = argparse.ArgumentParser(add_help=False, parents=[parser])
#read_p = argparse.ArgumentParser(add_help=False)
read_p.add_argument('-pn', action="store_true", help="Print phonenum")
read_p.add_argument('-pw', action="store_true", help="Print password")
read_p.add_argument('-rg', action="store_true", help="Pring region")
read_p.add_argument('-tw', action="store_true", help="Print twitter search")
read_p.add_argument('-si', action="store_true", help="Print sessionid")
read_p.add_argument('-ci', action="store_true", help="Print clientid")

#all_p = argparse.ArgumentParser(parents=[read_p, write_p])
#all_p.add_argument('-r', '--read', action="store_true", help="Read the conf file.")
#all_p.add_argument('-ri', '--read_item', action="store_true", help="Read an individual item.")
#all_p.add_argument('-w', '--write', action="store_true", help="Write to the conf file.")
'''

args = parser.parse_args()

def writeConf():
	zwconf = zwconfig.ZwConfig()
	zwconf.phonenum = args.write_phonenum
	zwconf.password = args.write_password
	zwconf.region = args.write_region
	zwconf.twittersearch = args.write_twitter

	if (args.write_getnewsessionandclientid):
		print "Will get new sessionid and clientid..."
		#zwconf = zwconfig.ZwConfig()
		util = zwutil.ZwUtil(conf=zwconf)
		sessionid = util.getSessionId()
		zwconf.sessionid = sessionid
		clientid = util.getClientId()
		zwconf.clientid = clientid
		result = util.getConnectSessionIdToClientId()
		print "Final results. sessionid: %s, clientid: %s, connectResult: %s" %	(sessionid, clientid, result)
	
	zwconf.write()
	printConf()

def printConf():
	print "The zipwhip.conf config file contains:"
	zwconf = zwconfig.ZwConfig()
	print "phonenum = %s" % zwconf.phonenum
	print "password = %s" % zwconf.password
	print "sessionid = %s" % zwconf.sessionid
	print "clientid = %s" % zwconf.clientid
	print "region = %s" % zwconf.region
	print "twittersearch = %s" % zwconf.twittersearch


# Read zwconfig
zwconf = zwconfig.ZwConfig()
#print args

if (args.read_phonenum):
	print zwconf.phonenum
elif (args.read_password):
	print zwconf.password
elif (args.read_region):
	print zwconf.region
elif (args.read_twitter):
	print zwconf.twittersearch
elif (args.read_sessionid):
	print zwconf.sessionid
elif (args.read_clientid):
	print zwconf.clientid

elif (args.read):
	printConf()
	
elif (args.write):
	print "Will write data to conf file." #. phonenum=%s" % args.phonenum
	#wargs = write_p.parse_args()
	writeConf()
	
else:
	#print "You can call this app to read config as a whole (-r), or read an individual item (-ri), or write to the file by passing in paramenters (-w)"
	#printConf()
	#print "If you want to read the config file to stdout:"
	parser.print_help()
	#read_p.print_help()
	#write_p.print_help()
	#all_p.print_help()
