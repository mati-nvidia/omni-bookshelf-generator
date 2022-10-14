# SPDX-License-Identifier: Apache-2.0

import carb
import omni.ui as ui
import omni.usd
from omni.kit.property.usd.relationship import RelationshipEditWidget

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
        self.current_index = -1
        self.current_bookshelf = None
        self.frame.set_build_fn(self.build_frame)
        self._combo_changed_sub = None
        self._stage_subscription = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_usd_context_event, name="Bookshelf Generator UI USD Stage Open Listening"
        )
        self.randomize_book_model = ui.SimpleBoolModel(True)
    
    def _on_usd_context_event(self, event: carb.events.IEvent):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self._stage = omni.usd.get_context().get_stage()

    def get_bookshelves(self):
        self.bookshelves = []
        bookshelf_paths = []
        for prim in self._stage.Traverse():
            if prim.HasAttribute("bookshelf_gen:width"):
                self.bookshelves.append(BookshelfGenerator(prim.GetPath()))
                bookshelf_paths.append(prim.GetPath())

        if (self.current_bookshelf is not None and self.current_index < len(self.bookshelves)
                and self.current_bookshelf.asset_root_path == self.bookshelves[self.current_index].asset_root_path):
            return
        
        self.current_index = -1
        self.current_bookshelf = None
        
        for i, bookshelf_path in enumerate(bookshelf_paths):
            if (self.current_bookshelf is not None 
                and bookshelf_path == self.current_bookshelf.asset_root_path):
                self.current_index = i
                self.current_bookshelf: BookshelfGenerator = self.bookshelves[self.current_index]
    
    def build_frame(self):
        self.get_bookshelves()
        with ui.VStack():
            with ui.HStack(height=0):
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
                    self.current_index = len(self.bookshelves) - 1
                    value_model = combo_model.get_item_value_model()
                    value_model.set_value(self.current_index)

                ui.Button("Create New", width=0, clicked_fn=lambda: create_new())

                def reload_frame():
                    self.reload_frame()
                ui.Button("Reload", width=0, clicked_fn=lambda: reload_frame())
            
            if self.current_index == -1:
                if len(self.bookshelves) > 0:
                    ui.Label("Create a new bookshelf or select an existing one from the dropdown to get started.",
                        word_wrap=True,
                        alignment=ui.Alignment.CENTER
                    )
                else:
                    ui.Label("Create a new bookshelf or to get started.",
                        word_wrap=True,
                        alignment=ui.Alignment.CENTER
                    )
            else:
                def create_default_prototypes():
                    self.current_bookshelf.create_default_prototypes()
                    self.proto_edit_widget.on_change_cb()
    
                with ui.VStack(height=0):
                    with ui.CollapsableFrame("Prototypes", collapsed=True):
                        with ui.VStack():
                            ui.Button("Create Default Prototypes", height=0, clicked_fn=lambda: create_default_prototypes())
                            with ui.ScrollingFrame(height=200):
                                with ui.VStack():
                                    self.proto_edit_widget = PrototypesRelEditWidget(
                                        self._stage, 
                                        "prototypes", 
                                        [self.current_bookshelf.books_instancer_path]
                                    )
                                    ui.Spacer()
                                    ui.Spacer()     
                                    ui.Spacer() 
                                    ui.Spacer() 

                    with ui.HStack(height=0, style={"margin_height":1}):
                        ui.Label("Width (cm): ")
                        self.width_model = ui.SimpleIntModel(int(self.current_bookshelf.width))
                        ui.IntField(model=self.width_model, width=50)
                    
                    with ui.HStack(height=0, style={"margin_height":1}):
                        ui.Label("Height (cm): ")
                        self.height_model = ui.SimpleIntModel(int(self.current_bookshelf.height))
                        ui.IntField(model=self.height_model, width=50)

                    with ui.HStack(height=0, style={"margin_height":1}):
                        ui.Label("Depth (cm): ")
                        self.depth_model = ui.SimpleIntModel(int(self.current_bookshelf.depth))
                        ui.IntField(model=self.depth_model, width=50)
                    
                    with ui.HStack(height=0, style={"margin_height":1}):
                        ui.Label("Thickness (cm): ")
                        self.thickness_model = ui.SimpleIntModel(int(self.current_bookshelf.thickness))
                        ui.IntField(model=self.thickness_model, width=50)

                    with ui.HStack(height=0, style={"margin_height":1}):
                        ui.Label("Number of Shelves: ")
                        self.num_shelves_model = ui.SimpleIntModel(int(self.current_bookshelf.num_shelves))
                        ui.IntField(model=self.num_shelves_model, width=50)
                    with ui.HStack(height=0, style={"margin_height":1}):
                        ui.Label("Randomize Book Scale:")
                        ui.CheckBox(model=self.randomize_book_model, width=50)

                def on_click():
                    self.current_bookshelf.generate(
                        width=self.width_model.as_int,
                        height=self.height_model.as_int,
                        depth=self.depth_model.as_int,
                        thickness=self.thickness_model.as_int,
                        num_shelves=self.num_shelves_model.as_int,
                        randomize_scale=self.randomize_book_model.as_bool
                    )
                ui.Button("Generate", height=40, clicked_fn=lambda: on_click())

    def reload_frame(self):
        self.frame.rebuild()
    
    def destroy(self) -> None:
        self._combo_changed_sub = None
        self._stage_subscription.unsubscribe()
        return super().destroy()
