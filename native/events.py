import wx

HP8751A_COMPLETED = wx.NewEventType()
# bind to serial data receive events
EVT_HP8751A_COMPLETED = wx.PyEventBinder(HP8751A_COMPLETED, 0)

class HP8751ACompletedEvent(wx.PyCommandEvent):
    eventType = HP8751A_COMPLETED
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

HP8751A_CANCELED = wx.NewEventType()
# bind to serial data receive events
EVT_HP8751A_CANCELED = wx.PyEventBinder(HP8751A_CANCELED, 0)

class HP8751ACanceledEvent(wx.PyCommandEvent):
    eventType = HP8751A_CANCELED
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

HP8751A_PROGRESS = wx.NewEventType()
# bind to serial data receive events
EVT_HP8751A_PROGRESS = wx.PyEventBinder(HP8751A_PROGRESS, 0)

class HP8751AProgressEvent(wx.PyCommandEvent):
    eventType = HP8751A_PROGRESS
    def __init__(self, windowID, message, step):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.step = step
        self.message = message

    def Clone(self):
        self.__class__(self.GetId(), self.message, self.step)


XLS_WRITE_COMPLETED = wx.NewEventType()
# bind to serial data receive events
EVT_XLS_WRITE_COMPLETED = wx.PyEventBinder(XLS_WRITE_COMPLETED, 0)

class XlsxWriteCompletedEvent(wx.PyCommandEvent):
    eventType = XLS_WRITE_COMPLETED
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

XLS_WRITE_CANCELED = wx.NewEventType()
# bind to serial data receive events
EVT_XLS_WRITE_CANCELED = wx.PyEventBinder(XLS_WRITE_CANCELED, 0)

class XlsxWriteCanceledEvent(wx.PyCommandEvent):
    eventType = XLS_WRITE_CANCELED
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

XLS_WRITE_PROGRESS = wx.NewEventType()
# bind to serial data receive events
EVT_XLS_WRITE_PROGRESS = wx.PyEventBinder(XLS_WRITE_PROGRESS, 0)

class XlsxWriteProgressEvent(wx.PyCommandEvent):
    eventType = XLS_WRITE_PROGRESS
    def __init__(self, windowID, message, step):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.step = step
        self.message = message

    def Clone(self):
        self.__class__(self.GetId(), self.message, self.step)
