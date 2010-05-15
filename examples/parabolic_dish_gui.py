
import enthought.traits.api as t_api
import enthought.traits.ui.api as tui
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene

from tracer.mayavi_ui.scene_view import TracerScene

import numpy as N
from tracer.ray_bundle import solar_disk_bundle
from tracer.models.tau_minidish import standard_minidish
from tracer import spatial_geometry as G

class DishScene(TracerScene):
    refl = t_api.Float(1.)
    concent = t_api.Float(450)
    disp_num_rays = t_api.Int(10)
    fmap_num_rays = t_api.Int(100000)
    
    def __init__(self):
        dish, source = self.create_dish_source()
        TracerScene.__init__(self, dish, source)
        self.set_background((0., 0.5, 1.))
    
    def create_dish_source(self):
        dish, f, W, H = standard_minidish(1., self.concent, self.refl, 1., 1.)
        # Add GUI annotations to the dish assembly:
        for surf in dish.get_homogenizer().get_surfaces():
            surf.resolution = 1000.
            surf.colour = (1., 0., 0.)
        dish.get_receiver_surf().resolution = 1000.
        dish.get_main_reflector().colour = (0., 0., 1.)

        source = solar_disk_bundle(self.disp_num_rays,
            N.c_[[0., 0., f + H + 0.5]], N.r_[0., 0., -1.], 0.5, 0.00465)
        source.set_energy(N.ones(self.disp_num_rays)*1000./self.disp_num_rays)
        
        return dish, source

    @t_api.on_trait_change('refl, concent')
    def recreate_dish(self, new):
        dish, source = self.create_dish_source()
        self.set_assembly(dish)
        self.set_source(source)
    
    view = tui.View(
        tui.Item('_scene', editor=SceneEditor(scene_class=MayaviScene),
            height=500, width=500, show_label=False),
        tui.HGroup('-', 
            tui.Item('concent', editor=tui.TextEditor(evaluate=float, auto_set=False)), 
            tui.Item('refl', editor=tui.TextEditor(evaluate=float, auto_set=False))))

if __name__ == '__main__':
    scene = DishScene()
    scene.configure_traits()

