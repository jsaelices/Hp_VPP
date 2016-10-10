__author__ = 'jaime'

import wx
import wx.wizard as wiz

class TitledPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        global sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        #title = wx.StaticText(self, -1, title)
        #title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        #sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        #sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)

def main():
        wizard = wx.wizard.Wizard(None, -1, "New yacht dialog")

        global sizer
        nhulls = ['Monohull', 'Catamaran', 'Trimaran']
        btype = ['Sloop', 'Ketch', 'Yawl', 'J-class']
        rtype = ['Fractional', 'Masthead']
        rud = ['Single', 'Twin', 'T-type single', 'T-type twin']
        keel = ['Fixed', 'Canting']
        other_app = ['Forward foil', 'Assymetrical daggerboards', 'L-type foils', 'DSS', 'Moustache']

        #prueba = [ select_multi, select_rig]

        page1 = TitledPage(wizard, "Number of hulls")
        page2 = TitledPage(wizard, "Boat type")

        select_number = wx.RadioBox(page1, -1, "Number of hulls", (0, 0), wx.DefaultSize, nhulls, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        select_multi = wx.RadioBox(page1, -1, "Boat type", (120,0), wx.DefaultSize, btype, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        select_rig = wx.RadioBox(page1, -1, "Rig type", (0, 100), wx.DefaultSize, rtype, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        select_rud = wx.RadioBox(page2, -1, "Rudder type", (0, 0), wx.DefaultSize, rud, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        select_keel = wx.RadioBox(page2, -1, "Keel type", (110, 0), wx.DefaultSize, keel, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        wx.CheckBox(page2, -1, "Forward foil", (0, 130))
        wx.CheckBox(page2, -1, "Assymetrical daggerboards", (0, 150))
        wx.CheckBox(page2, -1, "Moustache-type daggerboards", (0, 170))
        wx.CheckBox(page2, -1, "L-type foils", (0, 190))
        wx.CheckBox(page2, -1, "DSS", (0, 210))

        #sizer.Add(select_multi, 0, wx.ALIGN_TOP|wx.ALL, 5)
        #sizer.Add(select_rig, 0, wx.ALIGN_BOTTOM|wx.ALL, 5)

        wx.wizard.WizardPageSimple.Chain(page1, page2)
        wizard.FitToPage(page1)

        wizard.RunWizard(page1)

        wizard.Destroy()

# class newyachtDialog(wx.Frame):
#     def __init__(self):
#         wx.Frame.__init__(self, None, -1, "New yacht dialog")
#         panel = wx.Panel(self, -1)
#         nhulls = ['Monohull', 'Catamaran', 'Trimaran']
#         rtype = ['Sloop', 'Ketch', 'Yawl', 'J-class']
#         checkbox_number = wx.RadioBox(panel, -1, "Number of hulls", (0,0), wx.DefaultSize, nhulls, wx.RA_SPECIFY_COLS)
#         checkbox_multi = wx.RadioBox(panel, -1, "Rig type", (0,0), wx.DefaultSize, rtype, wx.RA_SPECIFY_COLS)
#
#         sizer = wx.BoxSizer(wx.HORIZONTAL)
#         sizer.Add(checkbox_number, 0, wx.ALL, 15)
#         sizer.Add(checkbox_multi, 0, wx.ALL, 15)
#         panel.SetSizer(sizer)

if __name__ == '__main__':
    app = wx.App()
    main()
    app.MainLoop()