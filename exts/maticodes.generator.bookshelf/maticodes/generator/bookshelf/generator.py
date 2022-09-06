import asyncio
import random
from pathlib import Path

import carb
import omni.kit.app
import omni.kit.commands
import omni.usd

from pxr import Usd, UsdGeom, Gf, Sdf

BOOK_A_USD = Path(__file__).parent.parent.parent.parent / "data" / "book_A.usd"
CUBE_POINTS_TEMPLATE = [(-1, -1, -1), (1, -1, -1), (-1, -1, 1), (1, -1, 1), (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)]

class BookshelfGenerator:
    def __init__(self, ) -> None:
        self._stage:Usd.Stage = omni.usd.get_context().get_stage()
        # if self._stage.GetPrimAtPath("/World/Bookshelf").IsValid():
        #     omni.kit.commands.execute('DeletePrims', paths=["/World/Bookshelf"])

    def create_shelf_material(self, looks_scope_path):
        shelf_mtl_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, looks_scope_path.AppendPath("Cherry"), False))
        result = omni.kit.commands.execute('CreateMdlMaterialPrimCommand',
            mtl_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Wood/Cherry.mdl',
            mtl_name='Cherry',
            mtl_path=str(shelf_mtl_path))

        omni.kit.commands.execute('SelectPrims',
            old_selected_paths=[],
            new_selected_paths=[str(shelf_mtl_path)],
            expand_in_stage=True)
        
        return shelf_mtl_path

    def create_new(self):
        asset_root_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, "/World/Bookshelf", False))
        geom_scope_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, asset_root_path.AppendPath("Geometry"), False))
        looks_scope_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, asset_root_path.AppendPath("Looks"), False))
        omni.kit.commands.execute('CreatePrim', prim_type='Xform', prim_path=str(asset_root_path))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(geom_scope_path))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(looks_scope_path))
        self.create_shelf_material(looks_scope_path)
        prototypes_container_path = geom_scope_path.AppendPath("Prototypes")

        asset_root_prim:Usd.Prim = self._stage.GetPrimAtPath(asset_root_path)
        asset_root_prim.CreateAttribute("bookshelf_gen:width", Sdf.ValueTypeNames.Float, custom=True).Set(150)
        asset_root_prim.CreateAttribute("bookshelf_gen:height", Sdf.ValueTypeNames.Float, custom=True).Set(200)
        asset_root_prim.CreateAttribute("bookshelf_gen:depth", Sdf.ValueTypeNames.Float, custom=True).Set(25)
        asset_root_prim.CreateAttribute("bookshelf_gen:thickness", Sdf.ValueTypeNames.Float, custom=True).Set(2)
        asset_root_prim.CreateAttribute("bookshelf_gen:numShelves", Sdf.ValueTypeNames.Float, custom=True).Set(3)
        asset_root_prim.CreateAttribute("bookshelf_gen:prototypesContainer", Sdf.ValueTypeNames.String, custom=True).Set(str(prototypes_container_path))

    def create_prototypes(self, asset_root_path):
        if isinstance(asset_root_path, str):
            asset_root_path = Sdf.Path(asset_root_path)
        asset_root_prim:Usd.Prim = self._stage.GetPrimAtPath(asset_root_path)
        geom_scope_path = asset_root_path.AppendPath("Geometry")
        prototypes:Usd.Prim = self._stage.OverridePrim(geom_scope_path.AppendPath("Prototypes"))
        book_stage:Usd.Stage = Usd.Stage.Open(str(BOOK_A_USD))
        default_prim = book_stage.GetDefaultPrim()
        variants = default_prim.GetVariantSet("color").GetVariantNames()
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
            asset_xform.SetResetXformStack(True)

        
        prototypes.SetSpecifier(Sdf.SpecifierOver)
        return prototypes.GetPath()

    def get_prototype_attrs(self, prototypes_container_path):
        # TODO: loop through children and get their widths and paths
        self.prototype_widths = []
        self.prototype_paths = []
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        book_stage:Usd.Stage = Usd.Stage.Open(str(BOOK_A_USD))
        default_prim = book_stage.GetDefaultPrim()
        variants = default_prim.GetVariantSet("color").GetVariantNames()
        for variant in variants:
            book_path = omni.usd.get_stage_next_free_path(self._stage,
                self.prototypes.GetPath().AppendPath("book_A"), 
                False
            )
            self.prototype_paths.append(book_path)
            omni.kit.commands.execute('CreateReference',
                path_to=book_path,
                asset_path=str(BOOK_A_USD),
                usd_context=omni.usd.get_context()
            )
            prim = self._stage.GetPrimAtPath(book_path)
            prim.GetVariantSet("color").SetVariantSelection(variant)
            bbox = bbox_cache.ComputeWorldBound(prim)
            bbox_range = bbox.GetRange()
            bbox_min = bbox_range.GetMin()
            bbox_max = bbox_range.GetMax()
            self.prototype_widths.append(bbox_max[0] - bbox_min[0])
            asset_xform = UsdGeom.Xform(prim)
            asset_xform.SetResetXformStack(True)

    def generate(self, width=100, height=250, depth=20, thickness=2, num_shelves=3, proto_container_path=""):
        self.width = width
        self.height = height
        self.depth = depth
        self.thickness = thickness
        widths, paths = self.get_prototype_attrs()
        self.create_frame()
        self.create_shelves(num_shelves)

    def create_books(self, shelf_height):
        next_x = 0
        def get_random_id():
            return random.randint(0, len(self.prototype_paths)-1)
        next_id = get_random_id()
        next_width = self.prototype_widths[next_id] 
        
        while next_x + next_width < self.width:
            width_scalar = random.random() * 1 + 1 
            height_scalar = random.random() * 0.5 + 1
            self.positions.append(Gf.Vec3f(next_x, shelf_height, 0))
            self.scales.append(Gf.Vec3d(width_scalar, height_scalar, 1))
            self.proto_ids.append(next_id)
            next_x += self.prototype_widths[next_id] * width_scalar
            next_id = get_random_id()
            next_width = self.prototype_widths[next_id] 
            carb.log_info(f"Width Scalar: {width_scalar}")
            carb.log_info(f"Next Width: {next_width}")

        self.instancer.CreatePositionsAttr().Set(self.positions)
        self.instancer.CreateScalesAttr().Set(self.scales)
        self.instancer.CreateProtoIndicesAttr().Set(self.proto_ids)
        self.instancer.CreatePrototypesRel().SetTargets(self.prototype_paths)

    def create_shelves(self, num_shelves):
        instancer_path = Sdf.Path(omni.usd.get_stage_next_free_path(
            self._stage, 
            self.geom_scope_path.AppendPath("BooksInstancer"), 
            False)
        )
        self.instancer = UsdGeom.PointInstancer.Define(self._stage, instancer_path)
        xform = UsdGeom.Xformable(self.instancer)
        xform.AddTranslateOp().Set(Gf.Vec3d(-self.width/2, self.thickness/2, self.depth/3))

        # Put books on the bottom of the frame
        self.create_books(self.thickness/2)
        # Generate the other shelves
        if num_shelves > 0:
            offset = self.height / (num_shelves + 1)
            for num in range(1, num_shelves + 1):
                board = self.create_board(self.width)
                shelf_y_pos = num * offset + self.thickness/2
                board.GetAttribute("xformOp:translate").Set(Gf.Vec3d(0, shelf_y_pos, 0))
                self.create_books(shelf_y_pos)

    def create_frame(self):
        # bottom
        board = self.create_board(self.width)
        board.GetAttribute("xformOp:translate").Set(Gf.Vec3d(0, self.thickness/2, 0))
        # top
        board = self.create_board(self.width)
        board.GetAttribute("xformOp:translate").Set(Gf.Vec3d(0, self.height - self.thickness/2, 0))
        # left
        board = self.create_board(self.height)
        board.GetAttribute("xformOp:translate").Set(Gf.Vec3d(-self.width/2 - self.thickness/2, self.height/2, 0))
        board.GetAttribute("xformOp:rotateXYZ").Set(Gf.Vec3d(0, 0, 90))
        # right
        board = self.create_board(self.height)
        board.GetAttribute("xformOp:translate").Set(Gf.Vec3d(self.width/2 + self.thickness/2, self.height/2, 0))
        board.GetAttribute("xformOp:rotateXYZ").Set(Gf.Vec3d(0, 0, 90))

    
    def create_board(self, width):
        cube_prim_path = omni.usd.get_stage_next_free_path(self._stage, self.geom_scope_path.AppendPath("Cube"), False)
        omni.kit.commands.execute('CreateMeshPrimWithDefaultXform', prim_type='Cube')
        omni.kit.commands.execute('MovePrim',
            path_from='/World/Cube',
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
            scaled_points.append((x, y, z))
        points_attr.Set(scaled_points)

        return cube_prim




        



        

