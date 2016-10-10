__author__ = 'jaime'

import wx
import textwrap

class MultilineRadioButton(wx.RadioButton):
        def __init__(self, parent, id=-1, label=wx.EmptyString, wrap=10, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.RadioButtonNameStr):
            wx.RadioButton.__init__(self,parent,id,'',pos,size,style,validator,name)
            self._label = label
            self._wrap = wrap
            lines = self._label.split('\n')
            self._wrappedLabel = []
            for line in lines:
                self._wrappedLabel.extend(textwrap.wrap(line,self._wrap))

            self._textHOffset = 20
            dc = wx.ClientDC(self)
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            dc.SetFont(font)
            maxWidth = 0
            totalHeight = 0
            lineHeight = 0
            for line in self._wrappedLabel:
                width, height = dc.GetTextExtent(line)
                maxWidth = max(maxWidth,width)
                lineHeight = height
                totalHeight += lineHeight

            self._textHeight = totalHeight

            self.SetInitialSize(wx.Size(self._textHOffset + maxWidth,totalHeight))
            self.Bind(wx.EVT_PAINT, self.OnPaint)

        def OnPaint(self, event):
            dc = wx.PaintDC(self)
            self.Draw(dc)
            self.RefreshRect(wx.Rect(0,0,self._textHOffset,self.GetSize().height))
            event.Skip()

        def Draw(self, dc):
            dc.Clear()
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            dc.SetFont(font)
            height = self.GetSize().height
            if height > self._textHeight:
                offset = height / 2 - self._textHeight / 2
            else:
                offset = 0
            for line in self._wrappedLabel:
                width, height = dc.GetTextExtent(line)
                dc.DrawText(line,self._textHOffset,offset)
                offset += height


class HFrame(wx.Frame):
   def __init__(self,pos=wx.DefaultPosition):
       wx.Frame.__init__(self,None,title="Hello World",size=wx.Size(600,400),pos=pos)

       self.panel = wx.Panel(self,-1)
       sizer = wx.BoxSizer(wx.HORIZONTAL)

       cb = MultilineRadioButton(self.panel,-1,label="This is a very very long label for the control!",wrap=10)
       sizer.Add(cb,1)

       cb = MultilineRadioButton(self.panel,-1,label="This is a very very long label for the control!",wrap=10)
       sizer.Add(cb,1)

       cb = MultilineRadioButton(self.panel,-1,label="This is a very very long label for the control!",wrap=10)
       sizer.Add(cb,1)

       self.panel.SetSizer(sizer)
       sizer.Layout()


class VFrame(wx.Frame):
   def __init__(self,pos=wx.DefaultPosition):
       wx.Frame.__init__(self,None,title="Hello World",size=wx.Size(600,400),pos=pos)

       self.panel = wx.Panel(self,-1)
       sizer = wx.BoxSizer(wx.VERTICAL)

       cb = MultilineRadioButton(self.panel,-1,label="This is a very very long label for the control!",wrap=10)
       sizer.Add(cb,1)

       cb = MultilineRadioButton(self.panel,-1,label="This is a very very long label for the control!",wrap=10)
       sizer.Add(cb,1)

       cb = MultilineRadioButton(self.panel,-1,label="This is a very very long label for the control!",wrap=10)
       sizer.Add(cb,1)

       self.panel.SetSizer(sizer)
       sizer.Layout()


app = wx.App(redirect=False)
htop = HFrame(pos=wx.Point(0,50))
htop.Show()
vtop = VFrame(pos=wx.Point(650,50))
vtop.Show()
app.MainLoop()
