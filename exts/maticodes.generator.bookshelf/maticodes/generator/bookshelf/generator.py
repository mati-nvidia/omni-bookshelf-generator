# SPDX-License-Identifier: Apache-2.0

import random
import typing
import weakref
from pathlib import Path

import carb
import omni.kit.app
import omni.kit.commands
import omni.usd
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from pxr import Gf, Sdf, Usd, UsdGeom

from .utils import stage_up_adjust

BOOK_A_USD = Path(__file__).parent.parent.parent.parent / "data" / "book_A.usd"
CUBE_POINTS_TEMPLATE = [(-1, -1, -1), (1, -1, -1), (-1, -1, 1), (1, -1, 1), (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)]

class BookshelfGenerator:
    def __init__(self, asset_root_path: typing.Union[str, Sdf.Path]=None) -> None:
        self._stage:Usd.Stage = omni.usd.get_context().get_stage()
        if asset_root_path is None:
            self.create_new()
        else:
            if isinstance(asset_root_path, str):
                self._asset_root_path = Sdf.Path(asset_root_path)
            else:
                self._asset_root_path = asset_root_path
                self.from_usd()
        self._stage_subscription = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
                self._on_usd_context_event, name="Bookshelf Generator USD Stage Open Listening"
            )
    
    def _on_usd_context_event(self, event: carb.events.IEvent):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self._stage = omni.usd.get_context().get_stage()

    def from_usd(self):
        prim = self._stage.GetPrimAtPath(self._asset_root_path)
        self.width = prim.GetAttribute("bookshelf_gen:width").Get()
        self.height = prim.GetAttribute("bookshelf_gen:height").Get()
        self.depth = prim.GetAttribute("bookshelf_gen:depth").Get()
        self.thickness = prim.GetAttribute("bookshelf_gen:thickness").Get()
        self.num_shelves = prim.GetAttribute("bookshelf_gen:numShelves").Get()
        self.geom_scope_path = self._asset_root_path.AppendPath("Geometry")
        self.looks_scope_path = self._asset_root_path.AppendPath("Looks")
        instancer_path = self.geom_scope_path.AppendPath("BooksInstancer")
        self.instancer = UsdGeom.PointInstancer(self._stage.GetPrimAtPath(instancer_path))
        look_prim = self._stage.GetPrimAtPath(self.looks_scope_path)
        self.shelf_mtl_path = look_prim.GetChildren()[0].GetPath()
    
    def create_shelf_material(self, looks_scope_path):
        self.shelf_mtl_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, looks_scope_path.AppendPath("Cherry"), False))
        result = omni.kit.commands.execute('CreateMdlMaterialPrimCommand',
            mtl_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Wood/Cherry.mdl',
            mtl_name='Cherry',
            mtl_path=str(self.shelf_mtl_path))

        omni.kit.commands.execute('SelectPrims',
            old_selected_paths=[],
            new_selected_paths=[str(self.shelf_mtl_path)],
            expand_in_stage=True)

    @property
    def books_instancer_path(self):
        return self.instancer.GetPath()
    
    @property
    def asset_root_path(self):
        return self._asset_root_path

    def create_new(self):
        self._asset_root_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, "/World/Bookshelf", False))
        self.geom_scope_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, self._asset_root_path.AppendPath("Geometry"), False))
        self.looks_scope_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, self._asset_root_path.AppendPath("Looks"), False))
        omni.kit.commands.execute('CreatePrim', prim_type='Xform', prim_path=str(self._asset_root_path))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(self.geom_scope_path))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(self.looks_scope_path))
        self.create_shelf_material(self.looks_scope_path)
        prototypes_container_path = self.geom_scope_path.AppendPath("Prototypes")

        self.width = 150
        self.height = 200
        self.depth = 25
        self.thickness = 2
        self.num_shelves = 3
        self.randomize_scale = True
        self.set_bookshelf_attrs()

        instancer_path = Sdf.Path(omni.usd.get_stage_next_free_path(
            self._stage, 
            self.geom_scope_path.AppendPath("BooksInstancer"), 
            False)
        )
        self.instancer = UsdGeom.PointInstancer.Define(self._stage, instancer_path)

        omni.kit.commands.execute('AddXformOp',
            payload=PrimSelectionPayload(weakref.ref(self._stage), [instancer_path]),
            precision=UsdGeom.XformOp.PrecisionDouble,
            rotation_order='XYZ',
            add_translate_op=True,
            add_rotateXYZ_op=True,
            add_orient_op=False,
            add_scale_op=True,
            add_transform_op=False,
            add_pivot_op=False)

        self.instancer.CreatePositionsAttr().Set([])
        self.instancer.CreateScalesAttr().Set([])
        self.instancer.CreateProtoIndicesAttr().Set([])

    def set_bookshelf_attrs(self):
        asset_root_prim:Usd.Prim = self._stage.GetPrimAtPath(self._asset_root_path)
        asset_root_prim.CreateAttribute("bookshelf_gen:width", Sdf.ValueTypeNames.Float, custom=True).Set(self.width)
        asset_root_prim.CreateAttribute("bookshelf_gen:height", Sdf.ValueTypeNames.Float, custom=True).Set(self.height)
        asset_root_prim.CreateAttribute("bookshelf_gen:depth", Sdf.ValueTypeNames.Float, custom=True).Set(self.depth)
        asset_root_prim.CreateAttribute("bookshelf_gen:thickness", Sdf.ValueTypeNames.Float, custom=True).Set(self.thickness)
        asset_root_prim.CreateAttribute("bookshelf_gen:numShelves", Sdf.ValueTypeNames.Float, custom=True).Set(self.num_shelves)

    def create_default_prototypes(self):
        asset_root_prim:Usd.Prim = self._stage.GetPrimAtPath(self._asset_root_path)
        geom_scope_path = self._asset_root_path.AppendPath("Geometry")
        prototypes:Usd.Prim = self._stage.OverridePrim(geom_scope_path.AppendPath("Prototypes"))
        book_stage:Usd.Stage = Usd.Stage.Open(str(BOOK_A_USD))
        default_prim = book_stage.GetDefaultPrim()
        variants = default_prim.GetVariantSet("color").GetVariantNames() 
        paths = []
        for variant in variants:
            book_path = omni.usd.get_stage_next_free_path(self._stage,
                prototypes.GetPath().AppendPath("book_A"), 
                False
            )
            omni.kit.commands.execute('CreateReference',
                path_to=book_path,
                asset_path=str(BOOK_A_USD),
                usd_context=omni.usd.get_context()
            )
            prim = self._stage.GetPrimAtPath(book_path)
            prim.GetVariantSet("color").SetVariantSelection(variant)
            asset_xform = UsdGeom.Xform(prim)
            if UsdGeom.GetStageUpAxis(self._stage) == UsdGeom.Tokens.z:
                rotate_attr = prim.GetAttribute("xformOp:rotateXYZ")
                rotation = rotate_attr.Get()
                rotation[2] = 0
                rotate_attr.Set(rotation)
            # asset_xform.SetResetXformStack(True)
            paths.append(book_path)

        
        prototypes.SetSpecifier(Sdf.SpecifierOver)
        self.instancer.CreatePrototypesRel().SetTargets(paths)

    def get_prototype_attrs(self):
        self.prototype_widths = []
        self.prototype_paths = []
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        self.prototype_paths = self.instancer.GetPrototypesRel().GetForwardedTargets()
        if len(self.prototype_paths) < 1:
            raise ValueError("You must provide at least one prototype.")

        proto_container = self.prototype_paths[0].GetParentPath()
        container_prim = self._stage.GetPrimAtPath(proto_container)
        container_prim.SetSpecifier(Sdf.SpecifierDef)

        for prototype_path in self.prototype_paths:
            proto_prim = self._stage.GetPrimAtPath(prototype_path)
            bbox = bbox_cache.ComputeWorldBound(proto_prim)
            bbox_range = bbox.GetRange()
            bbox_min = bbox_range.GetMin()
            bbox_max = bbox_range.GetMax()
            self.prototype_widths.append(bbox_max[0] - bbox_min[0])

        container_prim.SetSpecifier(Sdf.SpecifierOver)

    def generate(self, width=100, height=250, depth=20, thickness=2, num_shelves=3, randomize_scale=True):
        self.width = width
        self.height = height
        self.depth = depth
        self.thickness = thickness
        self.num_shelves = num_shelves
        self.randomize_scale = randomize_scale
        self.set_bookshelf_attrs()
        self.positions = []
        self.scales = []
        self.proto_ids = []
        self.get_prototype_attrs()
        self.clear_boards()
        self.create_frame()
        self.create_shelves(self.num_shelves)
        omni.usd.get_context().get_selection().clear_selected_prim_paths()
        self.clearInstanceableOnBookInstancer()

    def clear_boards(self):
        geom_scope_prim: Usd.Prim = self._stage.GetPrimAtPath(self.geom_scope_path)
        boards = []
        for child in geom_scope_prim.GetAllChildren():
            if child.GetName().startswith("Board"):
                boards.append(child.GetPath())

        omni.kit.commands.execute('DeletePrims',
            paths=boards,
            destructive=False
        )

    def create_books(self, shelf_height):
        x = 0
        def get_random_id():
            return random.randint(0, len(self.prototype_paths)-1)
        id = get_random_id()
        
        while True:
            if self.randomize_scale:
                width_scalar = random.random() * 1 + 1 
                height_scalar = random.random() * 0.5 + 1
            else:
                width_scalar = 1
                height_scalar = 1
            if x + self.prototype_widths[id] * width_scalar > self.width:
                break
            pos = stage_up_adjust(self._stage, 
                [x + self.prototype_widths[id] * width_scalar / 2, shelf_height, 0], 
                Gf.Vec3f
            )
            self.positions.append(pos)
            scale = stage_up_adjust(self._stage, 
                [width_scalar, height_scalar, 1], 
                Gf.Vec3d
            )
            self.scales.append(scale)
            self.proto_ids.append(id)
            # Update for next loop for next loop
            x += self.prototype_widths[id] * width_scalar
            id = get_random_id()

        self.instancer.GetPositionsAttr().Set(self.positions)
        self.instancer.GetScalesAttr().Set(self.scales)
        self.instancer.GetProtoIndicesAttr().Set(self.proto_ids)
        

    def create_shelves(self, num_shelves):
        translate_attr = self.instancer.GetPrim().GetAttribute("xformOp:translate")
        translate_attr.Set(stage_up_adjust(self._stage, [-self.width/2, self.thickness/2, 0], Gf.Vec3d))

        # Put books on the bottom of the frame
        self.create_books(self.thickness/2)
        # Generate the other shelves
        if num_shelves > 0:
            offset = self.height / (num_shelves + 1)
            for num in range(1, num_shelves + 1):
                board = self.create_board(self.width)
                shelf_y_pos = num * offset + self.thickness/2
                translate = stage_up_adjust(self._stage, [0, shelf_y_pos, 0], Gf.Vec3d)
                board.GetAttribute("xformOp:translate").Set(translate)
                self.create_books(shelf_y_pos)

    def create_frame(self):
        # bottom
        board = self.create_board(self.width)
        translate = stage_up_adjust(self._stage, [0, self.thickness/2, 0], Gf.Vec3d)
        board.GetAttribute("xformOp:translate").Set(translate)
        # top
        board = self.create_board(self.width)
        translate = stage_up_adjust(self._stage, [0, self.height - self.thickness/2, 0], Gf.Vec3d)
        board.GetAttribute("xformOp:translate").Set(translate)
        # left
        board = self.create_board(self.height)
        translate = stage_up_adjust(self._stage, [-self.width/2 - self.thickness/2, self.height/2, 0], Gf.Vec3d)
        board.GetAttribute("xformOp:translate").Set(translate)
        rotate = stage_up_adjust(self._stage, [0, 0, 90], Gf.Vec3d)
        board.GetAttribute("xformOp:rotateXYZ").Set(rotate)
        # right
        board = self.create_board(self.height)
        translate = stage_up_adjust(self._stage, [self.width/2 + self.thickness/2, self.height/2, 0], Gf.Vec3d)
        board.GetAttribute("xformOp:translate").Set(translate)
        rotate = stage_up_adjust(self._stage, [0, 0, 90], Gf.Vec3d)
        board.GetAttribute("xformOp:rotateXYZ").Set(rotate)

    
    def create_board(self, width):
        cube_prim_path = omni.usd.get_stage_next_free_path(self._stage, self.geom_scope_path.AppendPath("Board"), False)
        success, result = omni.kit.commands.execute('CreateMeshPrimWithDefaultXform', prim_type='Cube')
        omni.kit.commands.execute('MovePrim',
            path_from=result,
            path_to=cube_prim_path)
        result = omni.kit.commands.execute('BindMaterialCommand',
            prim_path=cube_prim_path,
            material_path=str(self.shelf_mtl_path),
            strength='strongerThanDescendants')
        
        tx_scale_y = self.depth / width
        # shader_prim = self._stage.GetPrimAtPath(mtl_path.AppendPath("Shader"))
        # tx_scale_attr = shader_prim.CreateAttribute("inputs:texture_scale", Sdf.ValueTypeNames.Float2)
        # tx_scale_attr.Set((1.0, tx_scale_y))
        cube_prim = self._stage.GetPrimAtPath(cube_prim_path)
        uv_attr = cube_prim.GetAttribute("primvars:st")
        uvs = uv_attr.Get()
        for x in range(len(uvs)):
            uvs[x] = (uvs[x][0], uvs[x][1] * tx_scale_y)
        uv_attr.Set(uvs)
        points_attr = cube_prim.GetAttribute("points")
        scaled_points = []
        for point in CUBE_POINTS_TEMPLATE:
            x = width / 2 * point[0]
            y = self.thickness / 2 * point[1]
            z = self.depth / 2 * point[2]
            scale = stage_up_adjust(self._stage, [x, y, z], Gf.Vec3d)
            scaled_points.append(scale)
        points_attr.Set(scaled_points)

        return cube_prim

    def clearInstanceableOnBookInstancer(self):
        instancer_path = self.geom_scope_path.AppendPath("BooksInstancer")
        omni.kit.commands.execute('ToggleInstanceableCommand', prim_path=[Sdf.Path(instancer_path)])

