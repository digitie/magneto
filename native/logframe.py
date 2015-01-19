##  StyledTextCtrl Log Window Demo
#
# Last modified: 23 July 2006
#
# Tested On:
#       Window XP with Python 2.4 and wxPython 2.6.3 (Unicode)
#       Debian GNU/Linux 3.1 (Sarge) with Python 2.3 and wxPython 2.6.3 (Unicode)
#
# The purpose of this program is to illustrate a very simple but useful
# application of a StyledTextCtrl.
#
# The StyledTextCtrl is complicated and some people find it hard to get
# started with it.  This demo, shows that programers can start to reap the
# benefits of using a StyledTextCtrl with very little effort.
#
# Normally a wx.Text control is used for log windows, however, using a
# StyledTextCtrl has the advantage of allowing the user to zoom the text
# in the control using CTRL-+ and CTRL--.  This facility is availiable by
# default, you get if for free!, and you have the option of using coloured
# messages too.
#

import wx
import wx.stc as stc
import wx.lib.newevent
import logging
import time


from threading import *
import time
# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        for i in range(10):
            time.sleep(1)
            if self._want_abort:
                # Use a result of None to acknowledge the abort (of
                # course you can use whatever you'd like or even
                # a separate event type)
                wx.PostEvent(self._notify_window, ResultEvent(None))
                return
        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        wx.PostEvent(self._notify_window, ResultEvent(10))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


# create event type
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()


class wxLogHandler(logging.Handler):
    """
    A handler class which sends log strings to a wx object
    """
    def __init__(self, wxDest=None):
        """
        Initialize the handler
        @param wxDest: the destination object to post the event to 
        @type wxDest: wx.Window
        """
        logging.Handler.__init__(self)
        self.wxDest = wxDest
        self.level = logging.DEBUG

    def flush(self):
        """
        does nothing for this handler
        """


    def emit(self, record):
        """
        Emit a record.

        """
        try:
            msg = self.format(record)
            evt = wxLogEvent(message=msg,levelname=record.levelname)            
            wx.PostEvent(self.wxDest,evt)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class LoggingFrame(wx.Frame):

    def __init__(self, parent, logger):
        wx.Frame.__init__(self, parent, -1, 'Logging')
        f = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')


        self.log = wx.TextCtrl(self, value='', pos=wx.DefaultPosition, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
        self.log.SetFont(f)
        #tp = TestPanel(self, self.log)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(tp, 0, wx.EXPAND)
        sizer.Add(self.log, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        self.SetSize((600, 400))

        wxLog = wxLogHandler(self)
        wxLog.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        wxLog.setFormatter(formatter)
        
        #sqllogger = logging.getLogger('sqlalchemy.engine')
        #sqllogger.setLevel(logging.INFO)
        #sqllogger.addHandler(wxLog)
        logger.addHandler(wxLog)
        self.Bind(EVT_WX_LOG_EVENT, self.OnLog)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnLog(self, event):
        self.log.AppendText(event.message +'\n')
        self.RemoveOldLines()

    def RemoveOldLines(self, oldLines = 100):
        if self.log.GetNumberOfLines() <= oldLines:
            return
        totalCharLen = 0
        for i in range(oldLines):
            charLen = self.log.GetLineLength(i)
            totalCharLen += charLen

        self.log.Remove(0, totalCharLen)

    def OnClose(self, event):
        self.Hide() 

if __name__=="__main__":

    app = wx.PySimpleApp()
    win = LoggingFrame(logger = logger)
    win.Show(True)
    app.MainLoop()