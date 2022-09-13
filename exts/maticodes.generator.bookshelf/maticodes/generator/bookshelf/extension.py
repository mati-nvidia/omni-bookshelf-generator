"""
TODO:
    - Multiple bookshelves in one scene (BookshelfGenerator per bookshelf)
    - add custom attributes to tag top-level xform as a bookshelf and list parameters used.
    - Subclass omni.kit.property.usd.relationship.RelationshipEditWidget
    - Button to generate prototypes
    - Let users provide their own prototypes
    - Manipulate existing prims instead creating new on every generate
    - Optional backboard
    - Add support for gaps
    - Recheck book overflow math
    - Kit Command and/or undo group
"""

import omni.ext
import omni.ui as ui

from .ui import BookshelfGenWindow


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[maticodes.generator.bookshelf] MyExtension startup")
        self._window = BookshelfGenWindow("Bookshelf Generator", width=300, height=300)
            

    

    def on_shutdown(self):
        print("[maticodes.generator.bookshelf] MyExtension shutdown")
        self._window.destroy()
        self._window = None
