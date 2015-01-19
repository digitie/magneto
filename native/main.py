# -*- coding: UTF-8 -*-

import wx

from mainframe import MainFrame

class Magnificient(wx.App):
    def OnInit(self):
        self.InitUI()
        return True

    def InitUI(self):
        self.frame = MainFrame(None)
        self.frame.Show()
        self.frame.logFrame.Show(True)