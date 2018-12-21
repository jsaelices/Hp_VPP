__author__ = 'Jaime Saelices'
__copyright__ = 'Copyright 2016, Jaime Saelices'
__license__ = 'GPL'
__version__ = '0.1.0'
__email__ = 'jsaelices@gmail.com'
__status__ = 'dev'

import wx

class NewWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "")
        wx.Frame.CenterOnScreen(self)
        wx.Panel(self)