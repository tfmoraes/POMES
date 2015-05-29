import wx

# widget que com um slider e um campo de texto
class SliderText(wx.Panel):
    def __init__(self, parent, id, label, value, Min, Max):
        wx.Panel.__init__(self, parent, id)
        self.label = label
        self.min = Min
        self.max = Max
        self.value = value
        self.build_gui()
        self.__bind_events_wx()
        self.Show()

    def build_gui(self):
        self.sliderctrl = wx.Slider(self, -1, self.value, self.min, self.max)
        self.textbox = wx.TextCtrl(self, -1, "%d" % self.value)


        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self,-1, self.label), 0, wx.EXPAND)
        sizer.Add(self.sliderctrl, 1, wx.EXPAND)
        sizer.Add(self.textbox, 0, wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()
        self.Update()
        self.SetAutoLayout(1)

    def __bind_events_wx(self):
        self.sliderctrl.Bind(wx.EVT_SCROLL, self.do_slider)
        self.Bind(wx.EVT_SIZE, self.onsize)

    def onsize(self, evt):
        print "OnSize"
        evt.Skip()

    def do_slider(self, evt):
        self.value =  self.sliderctrl.GetValue()
        self.textbox.SetValue("%d" % self.value)
        evt.Skip()

    def GetValue(self):
        return self.value
