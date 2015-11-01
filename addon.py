import xbmcaddon
import xbmc
import urllib2
import CommonFunctions
import pyxbmct.addonwindow as pyxbmct

ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4

plugin = "Remote Control"
__version__ = '0.1.0'

common = CommonFunctions
common.plugin = plugin + ' ' + __version__

addon 		= xbmcaddon.Addon()
addonname 	= addon.getAddonInfo('name')

ip = addon.getSetting('ipaddress')
path = addon.getSetting('path')

close_string = addon.getLocalizedString(30101)


def scrapeWebinterface(url):
	socketdatas = []

	response = urllib2.urlopen("http://"+url)
	html = response.read()
	ret = common.parseDOM(html, "TD", attrs = { "class": "outer" })
	socketnames = common.parseDOM(ret, "H3")
	urls = common.parseDOM(ret, "A", ret = "HREF")

	for url in urls:
		housecode = url[7:12]
		switch = url[20:22]
		state = url[30:31]
		if state == "0":
			state = 1
		else:
			state = 0
		socketdata = [housecode, switch, state]
		socketdatas.append(socketdata)

	socketdict = dict(zip(socketnames, socketdatas))
	return socketdict

urlwebinterface = ip+path	
sockets = scrapeWebinterface(urlwebinterface)
numofsockets = len(sockets.keys())

# Create a window instance.
window = pyxbmct.AddonDialogWindow(plugin)

height = 100 + numofsockets * 50
rows = 1 + numofsockets
# Set the window width, height and the grid resolution: 5 rows, 3 columns.
window.setGeometry(400, height, rows, 3)


clickcount = 1
def moveup():
	global clickcount
	global count
	global position
	if clickcount <= count:
		position = count-clickcount
		window.setFocus(radiobuttons[count-clickcount])
		clickcount = clickcount + 1

def movedown():
	global clickcount
	global count
	global position
	if position < count-1:
		position = position+1
		window.setFocus(radiobuttons[position])
		clickcount = clickcount - 1
	elif position == count-1:
		clickcount = clickcount - 1
		position = position+1
		window.setFocus(button)

count = 0
controlurls = []
radiobuttons = []
for key, value in sockets.iteritems():
	radiobuttons.append("radiobutton"+str(count))
	radiobuttons[count] = pyxbmct.RadioButton(key)
	window.placeControl(radiobuttons[count], count, 0, columnspan=3)
	if str(value[2]) == '1':
		swstate='0'
	else:
		swstate='1'
	controlurl = "http://" + urlwebinterface + "?group=" + value[0] + "&switch=" + value[1] + "&action=" + swstate
	controlurls.append(controlurl)
	if value[2] == 1:
		radiobuttons[count].setSelected(True)

	count = count + 1


position = count
for x in range(count):
	window.connect(radiobuttons[x],lambda var=x:urllib2.urlopen(controlurls[var]))

button = pyxbmct.Button(close_string)
window.placeControl(button, count, 1)
window.setFocus(button)
window.connect(button, window.close)
window.connect(pyxbmct.ACTION_NAV_BACK, window.close)
window.connect(pyxbmct.ACTION_MOVE_DOWN, movedown)
window.connect(pyxbmct.ACTION_MOVE_UP, moveup)
window.doModal()
del window