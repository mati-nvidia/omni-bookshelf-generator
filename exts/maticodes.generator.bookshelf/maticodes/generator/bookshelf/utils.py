
from signal import SIG_DFL

# SPDX-License-Identifier: Apache-2.0

from pxr import UsdGeom

def stage_up_adjust(stage, values, vec_type):
    if UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z:
        return vec_type(values[0], values[2], values[1])
    else:
        return vec_type(*values)