import asyncio

from pathlib import Path

import omni.kit.app
import omni.kit.commands
import omni.usd

from pxr import Usd, UsdGeom, Gf, Sdf

BOOK_A_USD = Path(__file__).parent.parent.parent.parent / "data" / "book_A.usd"
CUBE_POINTS_TEMPLATE = [(-1, -1, -1), (1, -1, -1), (-1, -1, 1), (1, -1, 1), (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)]

class BookshelfGenerator:
    def __init__(self, width=150, height=200, depth=20, thickness=2, num_shelves=5) -> None:
        self._stage:Usd.Stage = omni.usd.get_context().get_stage()
        self.width = width
        self.height = height
        self.depth = depth
        self.thickness = thickness
        omni.kit.commands.execute('DeletePrims', paths=["/World/Looks", "/World/Geometry"])

        self.geom_scope_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, "/World/Geometry", False))
        self.looks_scope_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, "/World/Looks", False))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(self.geom_scope_path))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(self.looks_scope_path))
        prototypes:Usd.Prim = self._stage.OverridePrim(self.geom_scope_path.AppendPath("Prototypes"))
        omni.kit.commands.execute('CreateReference',
            path_to=prototypes.GetPath().AppendPath("book_A"),
            asset_path=str(BOOK_A_USD),
            usd_context=omni.usd.get_context()
        )
        prototypes.SetSpecifier(Sdf.SpecifierOver)
        
        #self.create_frame()
        #self.create_shelves(num_shelves)
        self.create_books()

    def create_books(self):
        instancer_path = Sdf.Path(omni.usd.get_stage_next_free_path(
            self._stage, 
            self.geom_scope_path.AppendPath("BooksInstancer"), 
            False)
        )
        instancer = UsdGeom.PointInstancer.Define(self._stage, instancer_path)



    def create_shelves(self, num_shelves):
        if num_shelves > 0:
            offset = self.height / (num_shelves + 1)
            for num in range(1, num_shelves + 1):
                board = self.create_board(self.width)
                board.GetAttribute("xformOp:translate").Set(Gf.Vec3d(0, num * offset + self.thickness/2, 0))

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
        mtl_path = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, self.looks_scope_path.AppendPath("Cherry"), False))
        result = omni.kit.commands.execute('CreateMdlMaterialPrimCommand',
            mtl_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Wood/Cherry.mdl',
            mtl_name='Cherry',
            mtl_path=str(mtl_path))
        result = omni.kit.commands.execute('BindMaterialCommand',
            prim_path=cube_prim_path,
            material_path=str(mtl_path),
            strength='strongerThanDescendants')
        
        tx_scale_y = self.depth / width
        shader_prim = self._stage.GetPrimAtPath(mtl_path.AppendPath("Shader"))
        tx_scale_attr = shader_prim.CreateAttribute("inputs:texture_scale", Sdf.ValueTypeNames.Float2)
        tx_scale_attr.Set((1.0, tx_scale_y))
        cube_prim = self._stage.GetPrimAtPath(cube_prim_path)
        points_attr = cube_prim.GetAttribute("points")
        scaled_points = []
        for point in CUBE_POINTS_TEMPLATE:
            x = width / 2 * point[0]
            y = self.thickness / 2 * point[1]
            z = self.depth / 2 * point[2]
            scaled_points.append((x, y, z))
        points_attr.Set(scaled_points)

        return cube_prim




        



        

