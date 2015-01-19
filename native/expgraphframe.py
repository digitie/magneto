"""
This demo demonstrates how to draw a dynamic mpl (matplotlib) 
plot in a wxPython application.

It allows "live" plotting as well as manual zooming to specific
regions.

Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.

Note: press Enter in the 'manual' text box to make a new value 
affect the plot.

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008
"""
import os
import wx

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
#from matplotlib.figure import Figure
import pylab
import itertools as it

import smithplot

from matplotlib.figure import Figure            

from wxmplplot import wxmplitf

from core.listobject import *


CHART_COLORS = ('b','g','r','c','m','y','k',)

class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value

class ImpedanceGraphPopup(wx.Menu):
    def __init__(self, frame):
        wx.Menu.__init__(self)

        self.frame = frame

        item = wx.MenuItem(self, wx.NewId(), "Show &X labels", kind=wx.ITEM_CHECK)
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnShowXLabels, item)
        if self.frame.showXLabel:
            self.Check(item.GetId(), True)

        item = wx.MenuItem(self, wx.NewId(), "Show &Y labels", kind=wx.ITEM_CHECK)
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnShowYLabels, item)
        if self.frame.showYLabel:
            self.Check(item.GetId(), True)

        item = wx.MenuItem(self, wx.NewId(), "Show &Grid", kind=wx.ITEM_CHECK)
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnShowGrid, item)
        if self.frame.enableGrid:
            self.Check(item.GetId(), True)

        item = wx.MenuItem(self, wx.NewId(), "Show &Legend", kind=wx.ITEM_CHECK)
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnShowLegend, item)
        if self.frame.enableLegend:
            self.Check(item.GetId(), True)

    def OnShowXLabels(self, event):
        self.frame.showXLabel = not self.frame.showXLabel
        self.frame.draw_plot()

    def OnShowYLabels(self, event):
        self.frame.showYLabel = not self.frame.showYLabel
        self.frame.draw_plot()

    def OnShowGrid(self, event):
        self.frame.enableGrid = not self.frame.enableGrid
        self.frame.draw_plot()

    def OnShowLegend(self, event):
        self.frame.enableLegend = not self.frame.enableLegend
        self.frame.draw_plot()

'''

        frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)
        ret = self.plotFunction(frame.get_figure())
        if ret is not None:
            frame.panel.lined = ret
        frame.draw()
        frame.Show()
        '''

class SmithchartGraphFrame(wxmplitf.PlotFrame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    '''self, parent, id, title, lock, **kwargs)'''
    def __init__(self, parent, id, title, lock = None, exp_ids = [], **kwargs):

        '''frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)'''
        wxmplitf.PlotFrame.__init__(self, parent, id, title, lock = None, dpi=96)

        self.exp_ids = exp_ids
        self.datas = []    
        self.plot()

    def plot(self):
        self.datas = getExpSmithByExpIds(self.exp_ids)
        #axes = self.get_figure().add_subplot(1, 1, 1, projection='smith', axes_norm=50)
        axes = self.get_figure().gca(projection='smith', axes_norm=50)            

        for data, color in zip(tuple(self.datas), it.cycle(CHART_COLORS)):
            axes.plot(data.get_y(), color, label = data.get_legend(), markevery=1000)    
        self.draw()

class ReturnLossGraphFrame(wxmplitf.PlotFrame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    '''self, parent, id, title, lock, **kwargs)'''
    def __init__(self, parent, id, title, lock = None, exp_ids = [], **kwargs):

        '''frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)'''
        wxmplitf.PlotFrame.__init__(self, parent, id, title, lock = None, dpi=96)

        self.exp_ids = exp_ids
        self.datas = []    
        self.plot()

    def plot(self):
        self.datas = getReflectionData(self.exp_ids)
        axes = self.get_figure().gca()
        axes.set_title('Mag (dB)', size=8)

        axes.set_xlabel('Frequency [Hz]')
        axes.set_ylabel('Return Loss [dB]')

        pylab.setp(axes.get_xticklabels(), fontsize=8)
        pylab.setp(axes.get_yticklabels(), fontsize=8)
            
        axes.grid(True)        

        for data, color in zip(tuple(self.datas), it.cycle(CHART_COLORS)):
            axes.plot(data.get_x(), data.get_y(), color, label = data.get_legend())    
        self.draw()


class ImpedanceGraphFrame(wxmplitf.PlotFrame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    '''self, parent, id, title, lock, **kwargs)'''
    def __init__(self, parent, id, title, lock = None, exp_ids = [], type = 're', **kwargs):

        '''frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)'''
        wxmplitf.PlotFrame.__init__(self, parent, id, title, lock = None, dpi=96)

        self.exp_ids = exp_ids
        self.type = type
        self.datas = []    
        self.plot()

    def plot(self):
        self.datas = getImpedanceData(self.exp_ids, self.type)
        axes = self.get_figure().gca()
        if self.type == 'im':
            axes.set_title('Im(z)', size=8)
        elif self.type == 'mag':
            axes.set_title('Mag(z)', size=8)
        else:
            axes.set_title('Re(z)', size=8)

        axes.set_xlabel('Frequency [Hz]')
        axes.set_ylabel('Impedance [Ohm]')

        pylab.setp(axes.get_xticklabels(), fontsize=8)
        pylab.setp(axes.get_yticklabels(), fontsize=8)
            
        axes.grid(True)        

        for data, color in zip(tuple(self.datas), it.cycle(CHART_COLORS)):
            axes.plot(data.get_x(), data.get_y(), color, label = data.get_legend())    
        self.draw()

class DataCursor(object):
    text_template = 'x: %0.2f\ny: %0.2f'
    x, y = 0.0, 0.0
    xoffset, yoffset = -20, 20
    text_template = 'x: %0.2f\ny: %0.2f'

    def __init__(self, ax):
        self.ax = ax
        self.annotation = ax.annotate(self.text_template, 
                xy=(self.x, self.y), xytext=(self.xoffset, self.yoffset), 
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                )
        self.annotation.set_visible(False)

    def __call__(self, event):
        self.event = event
        # xdata, ydata = event.artist.get_data()
        # self.x, self.y = xdata[event.ind], ydata[event.ind]
        self.x, self.y = event.mouseevent.xdata, event.mouseevent.ydata
        if self.x is not None:
            self.annotation.xy = self.x, self.y
            self.annotation.set_text(self.text_template % (self.x, self.y))
            self.annotation.set_visible(True)
            event.canvas.draw()

class DCvsFreqGraphFrame(wxmplitf.PlotFrame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    
    def __init__(self, parent, id, title, lock = None, exp_ids = [], **kwargs):

        '''frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)'''
        wxmplitf.PlotFrame.__init__(self, parent, id, title, lock = None, dpi=96)
        '''
    def __init__(self, parent = None, exp_ids = [], type = 'dc'):
        wx.Frame.__init__(self, parent, -1, self.title)
        '''

        self.exp_ids = exp_ids
        self.datas = []

        self.plot()
        '''
    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)        
        self.canvas.mpl_connect('button_press_event', self.context_menu)    
        self.canvas.mpl_connect('pick_event', DataCursor(self.axes))    

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
                       
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)   
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        
        self.draw_plot()
        '''

    def plot(self):
        self.datas = getDCFieldVsFrequency(self.exp_ids)    
        axes = self.get_figure().gca()

        axes.set_title('Frequency vs DC Field', size=8)
        axes.set_xlabel('DC Field [A/m]')
        axes.set_ylabel('Resonant Frequency [Hz]')
        
        pylab.setp(axes.get_xticklabels(), fontsize=8)
        pylab.setp(axes.get_yticklabels(), fontsize=8)
            
        axes.grid(True)    

        for data, color in zip(tuple(self.datas), it.cycle(CHART_COLORS)):
            axes.plot(data.get_x(), data.get_y(), color)
            axes.plot(data.get_x(), data.get_y(), color + '^', label = data.get_legend(), picker=5)  

        axes.legend(framealpha=0, prop={'size':8})
        axes.ticklabel_format(useOffset=False)
        self.draw()
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        
        self.draw_plot()
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')
class ARvsFreqGraphFrame(wxmplitf.PlotFrame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    
    def __init__(self, parent, id, title, lock = None, exp_ids = [], **kwargs):

        '''frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)'''
        wxmplitf.PlotFrame.__init__(self, parent, id, title, lock = None, dpi=96)
        '''
    def __init__(self, parent = None, exp_ids = [], type = 'dc'):
        wx.Frame.__init__(self, parent, -1, self.title)
        '''

        self.exp_ids = exp_ids
        self.datas = []

        self.plot()
        '''
    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)        
        self.canvas.mpl_connect('button_press_event', self.context_menu)    
        self.canvas.mpl_connect('pick_event', DataCursor(self.axes))    

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
                       
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)   
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        
        self.draw_plot()
        '''

    def plot(self):
        self.datas = getPatchARVsFrequency(self.exp_ids)    
        axes = self.get_figure().gca()

        axes.set_title('Frequency vs Aspect Ratio', size=8)
        axes.set_xlabel('Aspect Ratio')
        axes.set_ylabel('Resonant Frequency [Hz]')
        
        pylab.setp(axes.get_xticklabels(), fontsize=8)
        pylab.setp(axes.get_yticklabels(), fontsize=8)
            
        axes.grid(True)    

        for data, color in zip(tuple(self.datas), it.cycle(CHART_COLORS)):
            axes.plot(data.get_x(), data.get_y(), color)
            axes.plot(data.get_x(), data.get_y(), color + '^', label = data.get_legend(), picker=5)  

        axes.legend(framealpha=0, prop={'size':8})
        axes.ticklabel_format(useOffset=False)
        self.draw()
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        
        self.draw_plot()
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

class ACvsFreqGraphFrame(wxmplitf.PlotFrame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    
    def __init__(self, parent, id, title, lock = None, exp_ids = [], **kwargs):

        '''frame = wxmplitf.PlotFrame(None, -1, self.title, lock = None,
            dpi=self.dpi)'''
        wxmplitf.PlotFrame.__init__(self, parent, id, title, lock = None, dpi=96)
        '''
    def __init__(self, parent = None, exp_ids = [], type = 'dc'):
        wx.Frame.__init__(self, parent, -1, self.title)
        '''

        self.exp_ids = exp_ids
        self.datas = []

        self.plot()
        '''
    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)        
        self.canvas.mpl_connect('button_press_event', self.context_menu)    
        self.canvas.mpl_connect('pick_event', DataCursor(self.axes))    

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
                       
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)   
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        
        self.draw_plot()
        '''

    def plot(self):
        self.datas = getACFieldVsFrequency(self.exp_ids)    
        axes = self.get_figure().gca()

        axes.set_title('Frequency vs AC Field', size=8)
        axes.set_xlabel('AC Power [dBm]')
        axes.set_ylabel('Resonant Frequency [Hz]')
        
        pylab.setp(axes.get_xticklabels(), fontsize=8)
        pylab.setp(axes.get_yticklabels(), fontsize=8)
            
        axes.grid(True)    

        for data, color in zip(tuple(self.datas), it.cycle(CHART_COLORS)):
            axes.plot(data.get_x(), data.get_y(), color)
            axes.plot(data.get_x(), data.get_y(), color + '^', label = data.get_legend(), picker=5)  

        axes.legend(framealpha=0, prop={'size':8})
        axes.ticklabel_format(useOffset=False)
        self.draw()
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        
        self.draw_plot()
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = ImpedanceGraphFrame()
    app.frame.Show()
    app.MainLoop()

