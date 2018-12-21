__author__ = 'Jaime Saelices'
__copyright__ = 'Copyright 2016, Jaime Saelices'
__license__ = 'GPL'
__version__ = '0.1.0'
__email__ = 'jsaelices@gmail.com'
__status__ = 'dev'

import wx

class splashScreen(wx.SplashScreen):

    def __init__(self, parent=None):
        tobitmap = wx.Image(name= "graphics\\logo.png").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTER_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 4000
        wx.SplashScreen.__init__(self, tobitmap, splashStyle, splashDuration, parent)