"""
TODO:
    - Button to generate prototypes
    - Add support for gaps
    - Recheck book overflow math
    - Kit Command and/or undo group
    - Multiple bookshelves in one scene.
    - Let users provide their own prototypes
    - Optional backboard
    - add custom attributes to tag top-level xform as a bookshelf and list parameters used.
"""

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
        self.bookshelf_gen = BookshelfGenerator()
        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                def create_new():
                    self.bookshelf_gen.create_new()
                ui.Button("Create New", clicked_fn=lambda: create_new())
                def create_prototypes():
                    proto_container_path = self.bookshelf_gen.create_prototypes()
                    self.proto_container_model.set_value(str(proto_container_path))
                ui.Button("Create Default Prototypes", clicked_fn=lambda: create_prototypes())
                with ui.HStack():
                    ui.Label("Prototypes Path: ")
                    self.proto_container_model = ui.StringField().model
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
                    self.bookshelf_gen.generate(
                        width=self.width_model.as_int,
                        height=self.height_model.as_int,
                        depth=self.depth_model.as_int,
                        thickness=self.thickness_model.as_int,
                        num_shelves=self.num_shelves_model.as_int,
                        proto_container_path=self.proto_container_model.as_string
                    )
                ui.Button("Click Me", clicked_fn=lambda: on_click())

    def on_shutdown(self):
        print("[maticodes.generator.bookshelf] MyExtension shutdown")
