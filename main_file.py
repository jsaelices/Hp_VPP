__author__ = 'Jaime Saelices'
__copyright__ = 'Copyright 2016, Jaime Saelices'
__license__ = 'GPL'
__version__ = '0.1.0'
__email__ = 'jsaelices@gmail.com'
__status__ = 'dev'

import wx
import os
import splash
import tempfile
import datetime as dt

class TabPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txtOne, 0, wx.ALL, 5)
        sizer.Add(txtTwo, 0, wx.ALL, 5)

        self.SetSizer(sizer)

class NodeTree(wx.TreeCtrl):
    def __init__(self, parent, id, position, size, style):
        global newFile
        tree_case = wx.TreeCtrl.__init__(self, parent, id, position, size, style)
        root = self.AddRoot(newFile)
        hc = self.AppendItem(root, 'Hydro components')
        ac = self.AppendItem(root, 'Aero components')
        ops = self.AppendItem(root, 'Opsets')
        rns = self.AppendItem(root, 'Runs')
        self.ExpandAll()

class nbk_reports(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        tabOne = TabPanel(self)
        self.AddPage(tabOne, "Hydro forces")
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, "Aero forces")
        self.AddPage(TabPanel(self), "Equilibrium")
        self.AddPage(TabPanel(self), "Global report")
        self.AddPage(TabPanel(self), "Graphs")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title="High Performance Velocity Prediction Program")

        #mySplash = splash.splashScreen()
        #mySplash.Show()

        menuBar = wx.MenuBar()
        self.CreateStatusBar()

        file_menu = wx.Menu()

        global new_run

        menuBar.Append(file_menu, "File")
        new_run = file_menu.Append(wx.ID_NEW, "New Run", "New VPP run for a yacht or fleet")
        self.Bind(wx.EVT_MENU, self.OnNewRun, new_run)
        open_run = file_menu.Append(wx.ID_OPEN, "Open Run", "Open a previous VPP project")
        self.Bind(wx.EVT_MENU, self.OnOpenRun, open_run)
        save = file_menu.Append(wx.ID_SAVE, "Save", "Save the project with initial name")
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        save_as = file_menu.Append(wx.ID_SAVEAS, "Save as", "Save the project with custom name")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, save_as)

        import_menu = wx.Menu()
        cfd_menu = wx.Menu()
        efd_menu = wx.Menu()

        file_menu.AppendMenu(wx.ID_ANY, "Import", import_menu)

        import_menu.AppendMenu(wx.ID_ANY, "CFD data", cfd_menu)

        aero_cfd = cfd_menu.Append(wx.ID_ANY, "CFD aero data", "Import aero data from CFD analysis")
        self.Bind(wx.EVT_MENU, self.OnImport_cfd_aero_data, aero_cfd)
        hydro_cfd = cfd_menu.Append(wx.ID_ANY, "CFD hydro data", "Import hydro data from CFD analysis")
        self.Bind(wx.EVT_MENU, self.OnImport_cfd_hydro_data, hydro_cfd)

        import_menu.AppendMenu(wx.ID_ANY, "EFD data", efd_menu)

        aero_efd = efd_menu.Append(wx.ID_ANY, "EFD aero data", "Import aero data from experimental tests")
        self.Bind(wx.EVT_MENU, self.OnImport_efd_aero_data, aero_efd)
        hydro_efd = efd_menu.Append(wx.ID_ANY, "EFD hydro data", "Import hydro data from experimental tests")
        self.Bind(wx.EVT_MENU, self.OnImport_efd_hydro_data, hydro_efd)

        export_menu = wx.Menu()

        file_menu.AppendSubMenu(export_menu, "Export")
        export_rep = export_menu.Append(wx.ID_ANY, "Report", "Export report as odt or pdf")
        self.Bind(wx.EVT_MENU, self.OnExport_rep, export_rep)
        export_gra = export_menu.Append(wx.ID_ANY, "Graph", "Export graph as a picture")
        self.Bind(wx.EVT_MENU, self.OnExport_gra, export_gra)
        file_menu.AppendSeparator()
        exit = file_menu.Append(wx.ID_EXIT, "Exit", "Exit from the application")
        self.Bind(wx.EVT_MENU, self.OnExit, exit)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        yacht_menu = wx.Menu()

        menuBar.Append(yacht_menu, "Yacht")
        newy = yacht_menu.Append(wx.ID_ANY, "New yacht", "Create new yacht to analyze")
        self.Bind(wx.EVT_MENU, self.OnNewy, newy)
        flota = yacht_menu.Append(wx.ID_ANY, "Flotation", "Flotation data")
        self.Bind(wx.EVT_MENU, self.OnFlota, flota)
        windag_h = yacht_menu.Append(wx.ID_ANY, "Windage", "Hull windage data")
        self.Bind(wx.EVT_MENU, self.OnWindag_h, windag_h)

        sails_menu = wx.Menu()

        menuBar.Append(sails_menu, "Sails")
        sails = sails_menu.Append(wx.ID_ANY, "Sails", "Sails definition")
        self.Bind(wx.EVT_MENU, self.OnSails, sails)
        sails_set = sails_menu.Append(wx.ID_ANY, "Sails set", "Group of sails used in analysis")
        self.Bind(wx.EVT_MENU, self.OnSails_set, sails_set)

        wind_menu = wx.Menu()

        menuBar.Append(wind_menu, "Wind")
        winds = wind_menu.Append(wx.ID_ANY, "Wind sets", "Wind speeds for analysis")
        self.Bind(wx.EVT_MENU, self.OnWinds, winds)
        winda = wind_menu.Append(wx.ID_ANY, "Wind angle sets", "Wind angles for analysis")
        self.Bind(wx.EVT_MENU, self.OnWinda, winda)

        rig_menu = wx.Menu()

        menuBar.Append(rig_menu, "Rig")
        rigt = rig_menu.Append(wx.ID_ANY, "Rig type", "Rig data")
        self.Bind(wx.EVT_MENU, self.OnRigt, rigt)
        windag_r = rig_menu.Append(wx.ID_ANY, "Windage", "Rig windage data")
        self.Bind(wx.EVT_MENU, self.OnWindag_r, windag_r)

        settings_menu = wx.Menu()

        menuBar.Append(settings_menu, "Settings")
        opsets = settings_menu.Append(wx.ID_ANY, "Opsets", "Analysis input data")
        self.Bind(wx.EVT_MENU, self.OnOpsets, opsets)
        hydrom = settings_menu.Append(wx.ID_ANY, "Hydro models", "Hydrodynamic models used for analysis")
        self.Bind(wx.EVT_MENU, self.OnHydrom, hydrom)
        aerom = settings_menu.Append(wx.ID_ANY, "Aero models", "Aerodynamic models used for analysis")
        self.Bind(wx.EVT_MENU, self.OnAerom, aerom)
        report_out = settings_menu.Append(wx.ID_ANY, "Report output", "Data showed on reports")
        self.Bind(wx.EVT_MENU, self.OnReport_out, report_out)
        graph_out = settings_menu.Append(wx.ID_ANY, "Graph output", "Graph type and data")
        self.Bind(wx.EVT_MENU, self.OnGraph_out, graph_out)

        run_menu = wx.Menu()

        menuBar.Append(run_menu, "Run VPP")

        run_yacht_menu = wx.Menu()

        run_menu.AppendSubMenu(run_yacht_menu, "Run yacht")
        ry_full = run_yacht_menu.Append(wx.ID_ANY, "Full data", "Run full analysis for current yacht")
        self.Bind(wx.EVT_MENU, self.OnRy_full, ry_full)
        ry_report = run_yacht_menu.Append(wx.ID_ANY, "Reports", "Run only for reports output for current yacht")
        self.Bind(wx.EVT_MENU, self.OnRy_report, ry_report)
        ry_graph = run_yacht_menu.Append(wx.ID_ANY, "Graphs", "Run only for graphs output for current yacht")
        self.Bind(wx.EVT_MENU, self.OnRy_graph, ry_graph)

        run_fleet_menu = wx.Menu()

        run_menu.AppendSubMenu(run_fleet_menu, "Run fleet")
        rf_full = run_fleet_menu.Append(wx.ID_ANY, "Full data", "Run full analysis for fleet")
        self.Bind(wx.EVT_MENU, self.OnRf_full, rf_full)
        rf_report = run_fleet_menu.Append(wx.ID_ANY, "Reports", "Run only for reports output for fleet")
        self.Bind(wx.EVT_MENU, self.OnRf_report, rf_report)
        rf_graph = run_fleet_menu.Append(wx.ID_ANY, "Graphs", "Run only for graphs output for fleet")
        self.Bind(wx.EVT_MENU, self.OnRf_graph, rf_graph)

        self.SetMenuBar(menuBar)
        self.Show(True)

        global fullPath
        fullPath = ""

    def OnNewRun(self, event):
        global new_run
        global curDir
        global tempFile
        global fullPath
        global newFile
        global newProject
        tmp = tempfile.mkstemp(text=True)
        f = open(tmp[1], "w")
        f.write("hp_VPP temporary file\n")
        f.write(str(dt.datetime.today()))
        tempFile = tmp[1]
        curDir = os.getcwd()
        extension = ".vpp"
        dlg = wx.TextEntryDialog(None, "Enter name of the new project:", "New project", "NewVPP")
        if dlg.ShowModal() == wx.ID_OK:
            newProject = dlg.GetValue()
            newFile = newProject + extension
            fullPath = os.path.join(curDir, newFile)
            self.showEnvironment()
            new_run.Enable(False)
            return fullPath
        else:
            pass
        self.Refresh()

    def showEnvironment(self):
        global newFile
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        leftPanel = wx.Panel(self.splitter, -1)
        leftBox = wx.BoxSizer(wx.VERTICAL)
        self.tree = NodeTree(leftPanel, 1, wx.DefaultPosition, wx.DefaultSize, wx.TR_NO_BUTTONS)
        leftBox.Add(self.tree, 1, wx.EXPAND|wx.FIXED_MINSIZE)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        leftPanel.SetSizerAndFit(leftBox)

        rightPanel = wx.Panel(self.splitter, -1)
        rightBox = wx.BoxSizer(wx.VERTICAL)
        nbk = nbk_reports(rightPanel)
        rightBox.Add(nbk, -1, wx.EXPAND)
        rightPanel.SetSizerAndFit(rightBox)
        self.splitter.SplitVertically(leftPanel, rightPanel)
        self.Centre()
        self.Refresh()

    def OnOpenRun(self, event):
        wildcard = "*.vpp"
        dlg = wx.FileDialog(self, "Open a VPP file", "", "",  wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            vppFile = os.path.split(dir)[1]
        else:
            pass

    def OnSave(self, event):
        global tempFile
        global newProject
        global fullPath
        global newFile
        global savedFile
        global savingPath
        global sfile
        sfile = ""
        try:
            if os.path.isfile(sfile):
                file = open(sfile, "wb")
                file.write("")
                file.close()
                message = "File " + str(sfile) + " overwritten successfully"
                wx.MessageBox(message)
            else:
                if not os.path.isfile(fullPath):
                    file = open(fullPath, "wb")
                    file.write("")
                    file.close()
                    message = "File " + str(newFile) + " saved successfully"
                    wx.MessageBox(message)
                else:
                    file = open(fullPath, "wb")
                    file.write("")
                    file.close()
                    message = "File " + str(newFile) + " overwritten successfully"
                    wx.MessageBox(message)
        except NameError:
            wx.MessageBox("Error determining the file to save!")

    def OnSaveAs(self, event):
        global tempFile
        global newProject
        global savedFile
        global newFile
        global fullPath
        global savingPath
        global sfile
        wildcard = "*.vpp"
        try:
            if not os.path.isfile(fullPath):
                dlg = wx.FileDialog(self, "Save as", "", "",  wildcard, wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                if dlg.ShowModal() == wx.ID_OK:
                    sfile = dlg.GetPath()
                    savingPath = os.path.dirname(dlg.GetPath())
                    savedFile = os.path.basename(dlg.GetPath())
                    file = open(sfile, "wb")
                    file.write("")
                    file.close()
                    dlg.Destroy()
                else:
                    pass
        except NameError:
            wx.MessageBox("No new project created!")

    def OnImport_cfd_aero_data(self, event):
        wildcard = "*.csv"
        dlg = wx.FileDialog(self, "Open a csv data file", "", "",  wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            csvFile = os.path.split(dir)[1]
        else:
            wx.MessageBox("No file to open")
        pass

    def OnImport_cfd_hydro_data(self, event):
        wildcard = "*.csv"
        dlg = wx.FileDialog(self, "Open a csv data file", "", "",  wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            csvFile = os.path.split(dir)[1]
        else:
            wx.MessageBox("No file to open")
        pass

    def OnImport_efd_aero_data(self, event):
        wildcard = "*.csv"
        dlg = wx.FileDialog(self, "Open a csv data file", "", "",  wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            csvFile = os.path.split(dir)[1]
        else:
            wx.MessageBox("No file to open")
        pass

    def OnImport_efd_hydro_data(self, event):
        wildcard = "*.csv"
        dlg = wx.FileDialog(self, "Open a csv data file", "", "",  wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            csvFile = os.path.split(dir)[1]
        else:
            wx.MessageBox("No file to open")
        pass

    def OnExport_rep(self, event):
        #EXPORT AS PDF FILE
        pass

    def OnExport_gra(self, event):
        #EXPORT AS IMAGE FILE OR PDF
        pass

    def OnExit(self, event):
        global tempFile
        global newProject
        global fullPath
        global newFile
        global sfile
        if os.path.isfile(fullPath):
            os.remove(fullPath)
            os.remove(tempFile)
            self.Destroy()
        else:
            dlg = wx.MessageDialog(None, "No saved file. Are you sure you want to exit?", "Warning",  wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.Destroy()
                os.remove(tempFile)
            else:
                pass


    def OnNewy(self, event):
        pass

    def OnFlota(self, event):
        pass

    def OnWindag_h(self, event):
        pass

    def OnSails(self, event):
        pass

    def OnSails_set(self, event):
        pass

    def OnWinds(self, event):
        pass

    def OnWinda(self, event):
        pass

    def OnRigt(self, event):
        pass

    def OnWindag_r(self, event):
        pass

    def OnOpsets(self, event):
        pass

    def OnHydrom(self, event):
        pass

    def OnAerom(self, event):
        pass

    def OnReport_out(self, event):
        pass

    def OnGraph_out(self, event):
        pass

    def OnRy_full(self, event):
        pass

    def OnRy_report(self, event):
        pass

    def OnRy_graph(self, event):
        pass

    def OnRf_full(self, event):
        pass

    def OnRf_report(self, event):
        pass

    def OnRf_graph(self, event):
        pass

    def OnSelChanged(self, event):
        pass

app = wx.App(False)
frame = MainFrame(None, "Hp_VPP")
app.MainLoop()
