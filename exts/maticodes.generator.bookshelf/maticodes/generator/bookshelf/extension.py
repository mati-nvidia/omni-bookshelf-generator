import omni.ext
import omni.ui as ui
from .generator import BookshelfGenerator

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[maticodes.generator.bookshelf] MyExtension startup")

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                
                with ui.HStack():
                    ui.Label("Width (cm): ")
                    self.width_model = ui.SimpleIntModel(150)
                    ui.IntField(model=self.width_model)
                
                with ui.HStack():
                    ui.Label("Height (cm): ")
                    self.height_model = ui.SimpleIntModel(200)
                    ui.IntField(model=self.height_model)

                with ui.HStack():
                    ui.Label("Depth (cm): ")
                    self.depth_model = ui.SimpleIntModel(25)
                    ui.IntField(model=self.depth_model)
                
                with ui.HStack():
                    ui.Label("Thickness (cm): ")
                    self.thickness_model = ui.SimpleIntModel(2)
                    ui.IntField(model=self.thickness_model)

                with ui.HStack():
                    ui.Label("Number of Shelves (cm): ")
                    self.num_shelves_model = ui.SimpleIntModel(3)
                    ui.IntField(model=self.num_shelves_model)

                def on_click():
                    BookshelfGenerator(
                        width=self.width_model.as_int,
                        height=self.height_model.as_int,
                        depth=self.depth_model.as_int,
                        thickness=self.thickness_model.as_int,
                        num_shelves=self.num_shelves_model.as_int,
                    )
                ui.Button("Click Me", clicked_fn=lambda: on_click())

    def on_shutdown(self):
        print("[maticodes.generator.bookshelf] MyExtension shutdown")
