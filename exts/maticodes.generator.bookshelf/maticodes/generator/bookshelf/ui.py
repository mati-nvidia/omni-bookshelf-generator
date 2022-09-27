from omni.kit.property.usd.relationship import RelationshipEditWidget
import omni.ui as ui
import omni.usd
from pxr import Sdf
from .generator import BookshelfGenerator


class PrototypesRelEditWidget(RelationshipEditWidget):
    def __init__(self, stage, attr_name, prim_paths):
        kwargs = {
            "on_remove_target": self.on_change_cb,
            "target_picker_on_add_targets": self.on_change_cb
        }
        super().__init__(stage, attr_name, prim_paths, additional_widget_kwargs=kwargs)
    
    def on_change_cb(self, *args):
        self._set_dirty()


class BookshelfGenWindow(ui.Window):
    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(title, **kwargs)
        self._stage = omni.usd.get_context().get_stage()
        self.bookshelves = []
        self.bookshelves.append(BookshelfGenerator())
        self.current_index = 0
        self.current_bookshelf: BookshelfGenerator = self.bookshelves[self.current_index]
        self.frame.set_build_fn(self.build_frame)
        self._combo_changed_sub = None

    def get_bookshelves(self):
        self.bookshelves = []
        for prim in self._stage.Traverse():
            if prim.HasAttribute("bookshelf_gen:width"):
                self.bookshelves.append(BookshelfGenerator(prim.GetPath()))
        # TODO: self.current_index may not be valid anymore
        self.current_bookshelf: BookshelfGenerator = self.bookshelves[self.current_index]
    
    def build_frame(self):
        self.get_bookshelves()
        with ui.VStack():
            with ui.HStack():
                combo_model = ui.ComboBox(self.current_index,*[str(x.asset_root_path) for x in self.bookshelves]).model
                
                def combo_changed(item_model, item):
                    value_model = item_model.get_item_value_model(item)
                    self.current_bookshelf = self.bookshelves[value_model.as_int]
                    self.current_index = value_model.as_int
                    self.reload_frame()
                self._combo_changed_sub = combo_model.subscribe_item_changed_fn(combo_changed)
                def create_new():
                    self.current_bookshelf: BookshelfGenerator = BookshelfGenerator()
                    self.bookshelves.append(self.current_bookshelf)
                ui.Button("Create New", clicked_fn=lambda: create_new())

                def reload_frame():
                    self.reload_frame()
                ui.Button("Reload", clicked_fn=lambda: reload_frame())

            def create_default_prototypes():
                self.current_bookshelf.create_default_prototypes()
                self.proto_edit_widget.on_change_cb()
                
            ui.Button("Create Default Prototypes", clicked_fn=lambda: create_default_prototypes())
            # with ui.CollapsableFrame("Prototypes"):
            self.proto_edit_widget = PrototypesRelEditWidget(
                self._stage, 
                "prototypes", 
                [self.current_bookshelf.books_instancer_path]
            )
            
            

            with ui.HStack():
                ui.Label("Width (cm): ")
                self.width_model = ui.SimpleIntModel(int(self.current_bookshelf.width))
                ui.IntField(model=self.width_model)
            
            with ui.HStack():
                ui.Label("Height (cm): ")
                self.height_model = ui.SimpleIntModel(int(self.current_bookshelf.height))
                ui.IntField(model=self.height_model)

            with ui.HStack():
                ui.Label("Depth (cm): ")
                self.depth_model = ui.SimpleIntModel(int(self.current_bookshelf.depth))
                ui.IntField(model=self.depth_model)
            
            with ui.HStack():
                ui.Label("Thickness (cm): ")
                self.thickness_model = ui.SimpleIntModel(int(self.current_bookshelf.thickness))
                ui.IntField(model=self.thickness_model)

            with ui.HStack():
                ui.Label("Number of Shelves (cm): ")
                self.num_shelves_model = ui.SimpleIntModel(int(self.current_bookshelf.num_shelves))
                ui.IntField(model=self.num_shelves_model)

            def on_click():
                self.current_bookshelf.generate(
                    width=self.width_model.as_int,
                    height=self.height_model.as_int,
                    depth=self.depth_model.as_int,
                    thickness=self.thickness_model.as_int,
                    num_shelves=self.num_shelves_model.as_int
                )
            ui.Button("Click Me", clicked_fn=lambda: on_click())

    def reload_frame(self):
        self.frame.rebuild()
    
    def destroy(self) -> None:
        self._combo_changed_sub = None
        return super().destroy()