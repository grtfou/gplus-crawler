# -*- coding: utf-8 -*-
import os
import wx

import configure as conf

from gplus_crawler import gplus_photo_crawler

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title,  pos=(400, 400), size=(500,200))

        # A button
        self.button =wx.Button(self, label="Go Download!", pos=(300, 60))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)

        # the edit control - one line version.
        self.lblname = wx.StaticText(self, label="google+ id:", pos=(20,60))
        self.picasa_id = wx.TextCtrl(self, value="", pos=(150, 60), size=(140,-1))
        self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextEnter, self.picasa_id)

        # Setting up the menu.
        aboutmenu= wx.Menu()

        menuAbout = aboutmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = aboutmenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(aboutmenu, "&About") # Adding the "aboutmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Show(True)

    def EvtTextEnter(self, event):
        self.OnClick(event)

    def OnClick(self, event):
        #print self.picasa_id.Value
        my_exe = gplus_photo_crawler()
        print my_exe.main(self.picasa_id.Value)
        #event.Skip()

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        about_txt = conf.MENU_ABOUT_TXT
        dlg = wx.MessageDialog(self, about_txt, conf.MENU_ABOUT_TITLE, wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

app = wx.App(False)
frame = MainWindow(None, conf.UI_TITLE)
app.MainLoop()