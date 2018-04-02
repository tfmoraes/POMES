# -*- coding: utf-8*-
import wx
import sys
import os
from math import *
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
import numpy
from numpy import cos, sin,ogrid,pi
from vtk.util import numpy_support
from numpy import*

#from slider_text import SliderText
from FloatSliderText import FloatSliderText
from slider_text import SliderText
wildcard = "(*.stl)|*.stl"

def to_vtk(n_array, spacing):
   dz, dy, dx = n_array.shape
   n_array.shape = dx * dy * dz

   v_image = numpy_support.numpy_to_vtk(n_array)

   # Generating the vtkImageData
   image = vtk.vtkImageData()
   image.SetOrigin(0, 0, 0)
   image.SetDimensions(dx, dy, dz)
   image.SetSpacing(spacing)
   image.SetExtent(0, dx -1, 0, dy -1, 0, dz - 1)
   image.AllocateScalars(numpy_support.get_vtk_array_type(n_array.dtype), 1)
   image.GetPointData().SetScalars(v_image)

   image_copy = vtk.vtkImageData()
   image_copy.DeepCopy(image)

   n_array.shape = dz, dy, dx 
   return image_copy


def pontos(polydata):
    #return numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())
    return numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())


def get_normals(polydata):
    #normals = polydata.GetPointData().GetArray("Normals")
    normals = polydata.GetPointData().GetArray("Normals")
    print numpy_support.vtk_to_numpy(normals)
    

    return numpy_support.vtk_to_numpy(normals)


def fun_schwartzP(type_surface,rrr,espessura=(-0.3,0.8)):
    x,y,z=rrr
    neg,pos= espessura
    #neg=0.7
    #pos=0.2

    if type_surface=='Schwarz_P':
        f=cos(x)+cos(y)+ cos(z)
    elif type_surface=='Schwarz_D':
        f=sin(x)*sin(y)*sin(z)+sin(x)*cos(y)*cos(z)+cos(x)*sin(y)*cos(z)+cos(x)*cos(y)*sin(z)
    elif type_surface=="Gyroid":
        f=cos (x) * sin(y) + cos (y) * sin (z) + cos (z) * sin (x)
    elif type_surface=="Neovius":
        f=3*(cos (x) + cos (y) + cos (z)) + 4* cos (x) * cos (y) * cos (z)
    elif type_surface=="iWP":
        f=cos (x) * cos (y) + cos (y) * cos (z) + cos (z) * cos (x) - cos (x) * cos (y) * cos (z)
    elif type_surface=='P_W_Hybrid':
        f=4*(cos (x) * cos (y) + cos (y) * cos (z) + cos (z) * cos (x)) -3* cos (x) * cos (y) * cos (z)+2.4
    elif type_surface=='Skeletal_1':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f=10.0*(cx*cy + cy*cz + cz*cx) -  5.0*(cos(x*2) + cos(y*2) + cos (z*2))- 14.0
    elif type_surface=='Skeletal_2':
        cx = cos(4*x)
        cy = cos(4*y)
        cz = cos(4*z)
        xo = x - pi/4
        yo = y - pi/4
        zo = z - pi/4
        f =10.0*(sin(xo) * sin(yo) * sin(zo)+ sin(xo) * cos(yo) * cos(zo)+ cos(xo) * sin(yo) * cos(zo)+ cos(xo) * cos(yo) * sin(zo))-  0.7*(cx + cy + cz)- 11.0
    elif type_surface=='Skeletal_3':
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = 10.0*(cos(x) * sin(y) + cos(y) * sin(z) + cos(z) * sin(x))-  0.5*(cx*cy + cy*cz + cz*cx)- 14.0
    elif type_surface=='Skeletal_4':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f = 10.0*(cx + cy + cz) -  5.1*(cx*cy + cy*cz + cz*cx) - 14.6	


    M=numpy.array(((f > -neg) & (f < pos)) * 1.0)

    #print M.shape, (i+2 for i in M.shape)
    N = numpy.zeros([i+2 for i in M.shape])

    N[1:-1, 1:-1, 1:-1] = M

    return N


def desenhar_surface_above_bone(type_surface,elem_size,normals,malha, points,espessura=None):

    if elem_size is None:
        elem=6
    if espessura is None:
        espessura=-0.3, 0.8



    surface_controle_gride=[]
    app_polidata = vtk.vtkAppendPolyData()
    elems = elem_size
    pi = numpy.pi
    spacing = [0, 0, 0]

    spacing[0] = abs(pi*2)/elems
    spacing[1] = abs(pi*2)/elems
    spacing[2] = abs(pi*2)/elems

    control_ogrid=ogrid[-pi:pi:spacing[0],-pi:pi:spacing[1],-pi:pi:spacing[2]]
    surface_controle_gride.append(control_ogrid)

    M = fun_schwartzP(type_surface,control_ogrid,espessura)
    image=to_vtk(M,spacing)

    surf=vtk.vtkMarchingCubes()
    surf.SetInputData(image)
    surf.SetValue(0,-0.1)
    surf.SetValue(1,0.1)
    surf.Update()
    
    d = vtk.vtkDecimatePro()
    d.SetTargetReduction(0.7)
    d.SetInputData(surf.GetOutput())
    d.Update()
    
    surf = d
    

    xmin, xmax, ymin, ymax, zmin, zmax = surf.GetOutput().GetBounds()

    #cx = (xmax+xmin)/2.0
    #cy = (ymax+ymin)/2.0
    #cz = (zmax+zmin)/2.0
    cx = xmin
    cy = ymin
    cz = zmin  

    for n in points:
        x,y, z = malha[n]


        nx, ny, nz = normals[n]


        surrf1=vtk.vtkTransform()


        surrf1.PostMultiply()
        surrf1.Translate(-cx, -cy, -cz)
        #surrf1.Scale(0.1, 0.1, 0.1)
        surrf1.Scale(0.1, 0.1, 0.1)

        oz = numpy.array((0, 0, 1))
        oy = numpy.array((0, 1, 0))
        ox = numpy.array((1, 0, 0))

        on = numpy.array((nx, ny, nz))
        on = on / numpy.linalg.norm(on)

        anglex = numpy.degrees(numpy.arccos(numpy.dot(ox, on)))
        angley = numpy.degrees(numpy.arccos(numpy.dot(oy, on)))
        anglez = numpy.degrees(numpy.arccos(numpy.dot(oz, on)))

        print anglex, angley, anglez, len(normals), len(malha)

        axex = numpy.cross(on, ox)
        axex = axex / numpy.linalg.norm(axex)

        axey = numpy.cross(on, oy)
        axey = axey / numpy.linalg.norm(axey)

        axez = numpy.cross(oz, on)
        axez = axez / numpy.linalg.norm(axez)
        surrf1.RotateWXYZ(anglez, axez[0], axez[1], axez[2])
        surrf1.Translate(x, y, z)
        surr2=vtk.vtkTransformFilter()
        surr2.SetInputData(surf.GetOutput())
        surr2.SetTransform(surrf1)
        surr2.Update()

        app_polidata.AddInputData(surr2.GetOutput())
    app_polidata.Update()
    return app_polidata


class LeftPanel(wx.Panel):
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id, style=style)
        self.build_gui()
        self.__bind_events_wx()
        #self.__bind_events_pb()

        self.Show()

        # funcão para escrever o erro
        log_path = os.path.join('.' , 'vtkoutput.txt')
        fow = vtk.vtkFileOutputWindow()
        fow.SetFileName(log_path)
        ow = vtk.vtkOutputWindow()
        ow.SetInstance(fow)
        #-----------------------


    def build_gui(self):


        self.autores_densidade=wx.ComboBox(self, -1, "Schwarz_P", choices=("Schwarz_P", "Schwarz_D","Gyroid","Neovius","iWP",'P_W_Hybrid','Skeletal_1','Skeletal_2','Skeletal_3','Skeletal_4'),
                                    style=wx.CB_READONLY)


        self.Reset_counting=wx.Button(self,-1,"Rendering")

        #self.Reset_voxelization=wx.Button(self,-1,"Voxelization")

        self.number_of_element= SliderText(self, -1, 'N', 6, 0, 100)

        self.select_region=wx.CheckBox(self,-1, label='Selected')

        self.valor_demensao_buraco1=FloatSliderText(self, -1, ' + Hole size', 0.1, 0.1, 1, 0.1)
        self.valor_demensao_buraco2=FloatSliderText(self, -1, ' - Hole size', 1, 0.1, 1, 0.1)


        b_sizer = wx.BoxSizer(wx.VERTICAL)


	check_sizer = wx.BoxSizer(wx.HORIZONTAL)
	check_sizer.Add(wx.StaticText(self, -1, u"Selected region of interess") , 0, wx.EXPAND | wx.ALL, 10)
	check_sizer.Add(self.select_region, 0, wx.EXPAND)

        #b_sizer.Add(self.Reset_voxelization, 0)


  
	combo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        combo_sizer.Add(wx.StaticText(self, -1, u"Counting Type") , 0, wx.EXPAND | wx.ALL, 10)
        combo_sizer.Add(self.autores_densidade, 0)

      	b_sizer.AddSizer(combo_sizer)

	b_sizer.AddSizer(check_sizer)

        b_sizer.Add(wx.StaticText(self, -1, u"Element Number") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.number_of_element, 0, wx.EXPAND)


	b_sizer.Add(wx.StaticText(self, -1, u" Element Hole Size") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_demensao_buraco1, 0, wx.EXPAND)
        b_sizer.Add(self.valor_demensao_buraco2, 0, wx.EXPAND)
        b_sizer.Add(self.Reset_counting, 0)


        hbox=wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(b_sizer, 1, wx.EXPAND)


        self.SetSizer(hbox)

    def __bind_events_wx(self):
        #wx.EVT_CHECKBOX(self, self.select_region.GetId(), self.Select_region)
        self.select_region.Bind(wx.EVT_CHECKBOX, self.estado_seleciona)
        self.Reset_counting.Bind(wx.EVT_BUTTON,self.renderiza)

    def estado_seleciona(self, evt):
        pub.sendMessage('Altera estado seleciona vertices', self.select_region.GetValue())


    def __bind_events_pb(self):
        pub.subscribe(self._show_info, 'show info')


    def renderiza(self, evt):
        type_surface = self.autores_densidade.GetValue()
        e1 = self.valor_demensao_buraco1.GetValue()
        e2 = self.valor_demensao_buraco2.GetValue()
        espessura = (e1, e2)
        elem = self.number_of_element .GetValue()
        pub.sendMessage('recalcula surface', (type_surface, elem,espessura))


class PanelRight(wx.Panel):
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id,style=style)

        self.visaofrontal=VisaoFrontal(self, id=-1, style=wx.BORDER_SUNKEN)



        vbox=wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.visaofrontal, 1, wx.EXPAND)
        hbox=wx.BoxSizer()
        hbox.Add(vbox, 1, wx.EXPAND)

        self.SetSizer(hbox)


class VisaoFrontal(wx.Panel):
    def __init__(self, parent, id,style):
        wx.Panel.__init__(self, parent, id, style=style)

        self.x0 = 0
        self.x1 = 0
        self.y0 = 0
        self.y1 = 0


        self.estruturas = None
        self.actor_estrutura = None


        self.renderer = vtk.vtkRenderer()
        self.Interactor = wxVTKRenderWindowInteractor(self,-1, size = self.GetSize())
        self.Interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.Interactor.Render()

        istyle = vtk.vtkInteractorStyleTrackballCamera()

        self.Interactor.SetInteractorStyle(istyle)

        self.pd = None
        self.id_points = set()

        hbox=wx.BoxSizer(wx.VERTICAL)
        hbox.Add(wx.StaticText(self,-1, u'Global Counting Structure'))


        hbox.Add(self.Interactor,1, wx.EXPAND)
        self.SetSizer(hbox)

        self.pega_pontos = False
        istyle.AddObserver("LeftButtonPressEvent",self.Clik)
        istyle.AddObserver("LeftButtonReleaseEvent", self.Release)
        #istyle.AddObserver("MouseMoveEvent", self.OnMotion)
        pub.subscribe(self.altera_estado, 'Altera estado seleciona vertices')

        pub.subscribe(self.renderiza, 'recalcula surface')

        self.init_actor()
        self.adicionaeixos()
        #self.desenha_surface()
        self.renderer.ResetCamera()
        self.list_points=[]
        self.Picker=vtk.vtkPointPicker()



    def init_actor(self):
        self.mapper = vtk.vtkPolyDataMapper()


        self.SurfaceActor=vtk.vtkActor()
        self.SurfaceActor.SetMapper(self.mapper)
        #ultimo para adionar actor
        #exemplo
        self.renderer.AddActor(self.SurfaceActor)

        self.renderer.ResetCamera()

        self.Interactor.Render()

    def altera_estado(self, pubsub_evt):
        self.pega_pontos = pubsub_evt.data


    def _desenha_surface(self, pubsub_evt):
        type_surface, elem,espessura = pubsub_evt.data

        self.desenhar_surface_above_bone(type_surface, elem,espessura)



    def renderiza(self, pubsub_evt):
        if self.estruturas is not None:
            self.renderer.RemoveActor(self.actor_estrutura)
            del self.estruturas
            del self.actor_estrutura


        type_surface, elem,espessura = pubsub_evt.data
        estruturas = desenhar_surface_above_bone(type_surface, elem , self.normalsp, self.vertices, self.id_points,espessura)

        mapper_estrutura = vtk.vtkPolyDataMapper()
        mapper_estrutura.SetInputData(estruturas.GetOutput())

        actor_estrutura = vtk.vtkActor()
        actor_estrutura.SetMapper(mapper_estrutura)

        self.renderer.AddActor(actor_estrutura)

        self.renderer.Render()

        self.estruturas = estruturas
        self.actor_estrutura = actor_estrutura






    def adicionaeixos(self):
        axes = vtk.vtkAxesActor()
        self.marker = vtk.vtkOrientationMarkerWidget()
        self.marker.SetInteractor( self.Interactor )
        self.marker.SetOrientationMarker( axes )
        self.marker.SetViewport(0.75,0,1,0.25)
        self.marker.SetEnabled(1)



    def gravar_Modelo_stl(self, path):

        app_polidata = vtk.vtkAppendPolyData()
        app_polidata.AddInput(self.polydata)
        app_polidata.AddInput(self.estruturas.GetOutput())
        app_polidata.Update()

        write = vtk.vtkSTLWriter()
        write.SetInputData(app_polidata.GetOutput())
        write.SetFileTypeToBinary()
        write.SetFileName(path)
        write.Write()
        write.Update()






    def LerSTL(self, path):
        mesh= vtk.vtkSTLReader()
        mesh.SetFileName(path)
        mesh.Update()

        #self.pd  = mesh.GetOutput()
        self.polydata  = mesh.GetOutput()

        normals = vtk.vtkPolyDataNormals()
        #normals.SetInput(polydata)
        normals.SetInputData(mesh.GetOutput())
        normals.ComputeCellNormalsOn()
        normals.Update()

        #mudanças para aumentar a normal
        

        self.vertices =pontos(normals.GetOutput())
        self.normalsp = get_normals(normals.GetOutput())

        

        stlMapper = vtk.vtkPolyDataMapper()
        stlMapper.SetInputConnection(normals.GetOutputPort())
        
        stlActor = vtk.vtkLODActor()
        stlActor.SetMapper(stlMapper)


        self.renderer.AddActor(stlActor)
        self.Interactor.Render()



#    def Select_region(self, evt):


    def Clik(self,obj, evt):
        if self.pega_pontos:
            iren =self.Interactor
            ren = self.renderer
            x, y = iren.GetEventPosition()
            self.x0 = x
            self.y0 = y
        else:
            obj.StartRotate()


    def Release(self, obj, event):
        if self.pega_pontos:
            iren =self.Interactor
            ren = self.renderer
            x, y = iren.GetEventPosition()
            self.x1 = x
            self.y1 = y

            xmin = min(self.x0, self.x1)
            xmax = max(self.x0, self.x1)

            ymin = min(self.y0, self.y1)
            ymax = max(self.y0, self.y1)
            # Generate ids for labeling

            ids = vtk.vtkIdFilter()
            ids.SetInputData(self.polydata)
            ids.PointIdsOn()
            ids.CellIdsOn()
            ids.FieldDataOn()
            ids.Update()

            s = vtk.vtkSelectVisiblePoints()
            s.SetRenderer(self.renderer)
            s.SetInputData(ids.GetOutput())
            s.SelectionWindowOn()
            s.SetSelection(xmin, xmax, ymin, ymax)
            s.SelectInvisibleOff()
            s.Update()

            id_points = numpy_support.vtk_to_numpy(s.GetOutput().GetPointData().GetAbstractArray("vtkIdFilter_Ids"))
            print id_points
            self.id_points.update(id_points.tolist())
        else:
            obj.EndRotate()








class JanelaPrincipal(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(700, 650))

        #----------------------------------

        panel = wx.Panel(self, -1)

        self.currentDirectory = os.getcwd()

        self.RightPanel =PanelRight(self, id=-1, style=wx.BORDER_SUNKEN)
        self.LeftPanel =LeftPanel(self, id=-1, style=wx.BORDER_SUNKEN)


        hbox=wx.BoxSizer(wx.VERTICAL)
        hbox.Add(self.RightPanel, 9, wx.EXPAND)
        hbox.Add(self.LeftPanel, 1, wx.EXPAND)



        self.SetSizer(hbox)

        #criar menu

        MenuBar=wx.MenuBar()
        menu=wx.Menu()


        open_stl=menu.Append(-1, "&OPEN STL file ")
        guardar=menu.Append(-1, "&Save Project ")
        sair=menu.Append(-1, "&Exit")
        MenuBar.Append(menu, "File")

        self.SetMenuBar(MenuBar)

        # tratar os eventos
        self.Bind(wx.EVT_MENU, self.SairPrograma, sair)
        self.Bind(wx.EVT_MENU, self.guardar_stl_format, guardar)
        self.Bind(wx.EVT_MENU, self.open_stl_file, open_stl)




        self.Show()


    def SairPrograma(self,event):
         dial=wx.MessageDialog(None, 'Pretende sair do Programa ?',u'Questão', wx.YES_NO |wx.NO_DEFAULT | wx.ICON_QUESTION)
         ret=dial.ShowModal()
         if ret==wx.ID_YES:
             self.Destroy()



    def guardar_stl_format(self, evt):
        dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir=self.currentDirectory,
            defaultFile="", wildcard=wildcard, style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.RightPanel.visaofrontal.gravar_Modelo_stl(path)
        dlg.Destroy()


    def open_stl_file(self, evt):
        dlg = wx.FileDialog(
            self, message="OPEN file as ...",
            defaultDir=self.currentDirectory,
            defaultFile="", wildcard=wildcard, style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.RightPanel.visaofrontal.LerSTL(path)
        dlg.Destroy()




if __name__ == '__main__':
    app = wx.App(0)
    w = JanelaPrincipal(None, -1, 'Interface POMES')
    w.Show()
    app.MainLoop()
