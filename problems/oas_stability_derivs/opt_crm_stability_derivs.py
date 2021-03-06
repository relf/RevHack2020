"""
OpenMDAO optimization of eCRM design subject to stability derivative constraints.
"""
import pickle

import numpy as np

import openmdao.api as om
from openaerostruct.utils.constants import grav_constant

from ecrm_comp_with_stability_derivs import ECRM


#Read baseline mesh
with open('baseline_meshes_reduced.pkl', "rb") as f:
    meshes = pickle.load(f)

wing_mesh = meshes['wing_mesh']
horiz_tail_mesh = meshes['horiz_tail_mesh']
vert_tail_mesh = meshes['vert_tail_mesh']

# Define data for surfaces
wing_surface = {
    # Wing definition
    'name' : 'wing',        # name of the surface
    'symmetry' : True,      # if true, model one half of wing
                            # reflected across the plane y = 0
    'S_ref_type' : 'wetted', # how we compute the wing area,
                             # can be 'wetted' or 'projected'
    'fem_model_type': 'tube',
    'twist_cp': np.zeros((1)),
    'mesh': wing_mesh,

    'thickness_cp' : np.array([.1, .2]),

    # Aerodynamic performance of the lifting surface at
    # an angle of attack of 0 (alpha=0).
    # These CL0 and CD0 values are added to the CL and CD
    # obtained from aerodynamic analysis of the surface to get
    # the total CL and CD.
    # These CL0 and CD0 values do not vary wrt alpha.
    'CL0' : 0.0,            # CL of the surface at alpha=0
    'CD0' : 0.015,          # CD of the surface at alpha=0

    # Airfoil properties for viscous drag calculation
    'k_lam' : 0.05,         # percentage of chord with laminar
                            # flow, used for viscous drag
    't_over_c_cp': np.array([0.15]),  # thickness over chord ratio (NACA0015)
    'c_max_t': 0.303,  # chordwise location of maximum (NACA0015)
                            # thickness
    'with_viscous' : True,
    'with_wave' : False,     # if true, compute wave drag

    # Structural values are based on aluminum 7075
    'E' : 70.e9,            # [Pa] Young's modulus of the spar
    'G' : 30.e9,            # [Pa] shear modulus of the spar
    'yield' : 500.e6 / 2.5, # [Pa] yield stress divided by 2.5 for limiting case
    'mrho' : 3.e3,          # [kg/m^3] material density
    'fem_origin' : 0.35,    # normalized chordwise location of the spar
    'wing_weight_ratio' : 2.,
    'struct_weight_relief' : False,    # True to add the weight of the structure to the loads on the structure
    'distributed_fuel_weight' : False,
    # Constraints
    'exact_failure_constraint' : False, # if false, use KS function
}

# TODO - need real data for horiz tail.
horiz_tail_surface = {
    # Wing definition
    'name': 'horiz_tail',  # name of the surface
    'symmetry': True,  # if true, model one half of wing
    # reflected across the plane y = 0
    'S_ref_type': 'wetted',  # how we compute the wing area,
    # can be 'wetted' or 'projected'
    'fem_model_type': 'tube',
    'twist_cp': np.zeros((1)),
    'twist_cp_dv': False,

    'mesh': horiz_tail_mesh,

    'thickness_cp' : np.array([.01, .02]),

    # Aerodynamic performance of the lifting surface at
    # an angle of attack of 0 (alpha=0).
    # These CL0 and CD0 values are added to the CL and CD
    # obtained from aerodynamic analysis of the surface to get
    # the total CL and CD.
    # These CL0 and CD0 values do not vary wrt alpha.
    'CL0': 0.0,  # CL of the surface at alpha=0
    'CD0': 0.0,  # CD of the surface at alpha=0
    # Airfoil properties for viscous drag calculation
    'k_lam': 0.05,  # percentage of chord with laminar
    # flow, used for viscous drag
    't_over_c_cp': np.array([0.15]),  # thickness over chord ratio (NACA0015)
    'c_max_t': 0.303,  # chordwise location of maximum (NACA0015)
    # thickness
    'with_viscous': True,  # if true, compute viscous drag
    'with_wave': False,

    # Structural values are based on aluminum 7075
    'E' : 70.e9,            # [Pa] Young's modulus of the spar
    'G' : 30.e9,            # [Pa] shear modulus of the spar
    'yield' : 500.e6 / 2.5, # [Pa] yield stress divided by 2.5 for limiting case
    'mrho' : 3.e3,          # [kg/m^3] material density
    'fem_origin' : 0.35,    # normalized chordwise location of the spar
    'wing_weight_ratio' : 2.,
    'struct_weight_relief' : False,    # True to add the weight of the structure to the loads on the structure
    'distributed_fuel_weight' : False,
    # Constraints
    'exact_failure_constraint' : False, # if false, use KS function
}

vert_tail_surface = {
    # Wing definition
    'name': 'vert_tail',  # name of the surface
    'symmetry': False,  # if true, model one half of wing
    # reflected across the plane y = 0
    'S_ref_type': 'wetted',  # how we compute the wing area,
    # can be 'wetted' or 'projected'
    'fem_model_type': 'tube',
    'twist_cp': np.zeros((1)),
    'twist_cp_dv': False,

    'mesh': vert_tail_mesh,

    'thickness_cp' : np.array([.01, .02]),

    # Aerodynamic performance of the lifting surface at
    # an angle of attack of 0 (alpha=0).
    # These CL0 and CD0 values are added to the CL and CD
    # obtained from aerodynamic analysis of the surface to get
    # the total CL and CD.
    # These CL0 and CD0 values do not vary wrt alpha.
    'CL0': 0.0,  # CL of the surface at alpha=0
    'CD0': 0.0,  # CD of the surface at alpha=0
    # Airfoil properties for viscous drag calculation
    'k_lam': 0.05,  # percentage of chord with laminar
    # flow, used for viscous drag
    't_over_c_cp': np.array([0.15]),  # thickness over chord ratio (NACA0015)
    'c_max_t': 0.303,  # chordwise location of maximum (NACA0015)
    # thickness
    'with_viscous': True,  # if true, compute viscous drag
    'with_wave': False,

    # Structural values are based on aluminum 7075
    'E' : 70.e9,            # [Pa] Young's modulus of the spar
    'G' : 30.e9,            # [Pa] shear modulus of the spar
    'yield' : 500.e6 / 2.5, # [Pa] yield stress divided by 2.5 for limiting case
    'mrho' : 3.e3,          # [kg/m^3] material density
    'fem_origin' : 0.35,    # normalized chordwise location of the spar
    'wing_weight_ratio' : 2.,
    'struct_weight_relief' : False,    # True to add the weight of the structure to the loads on the structure
    'distributed_fuel_weight' : False,
    # Constraints
    'exact_failure_constraint' : False, # if false, use KS function
}


prob = om.Problem()
model = prob.model

design_inputs = ['wing_cord', 'vert_tail_area', 'horiz_tail_area']
common_settings = ['beta', 're', 'rho', 'CT', 'R', 'W0', 'load_factor', 'speed_of_sound', 'empty_cg']

model.add_subsystem('ecrm_70', ECRM(wing_surface=wing_surface,
                                    horiz_tail_surface=horiz_tail_surface,
                                    vert_tail_surface=vert_tail_surface),
                    promotes_inputs=design_inputs + common_settings)

model.add_subsystem('ecrm_150', ECRM(wing_surface=wing_surface,
                                     horiz_tail_surface=horiz_tail_surface,
                                     vert_tail_surface=vert_tail_surface),
                    promotes_inputs=design_inputs + common_settings)

model.add_subsystem('ecrm_200', ECRM(wing_surface=wing_surface,
                                     horiz_tail_surface=horiz_tail_surface,
                                     vert_tail_surface=vert_tail_surface),
                    promotes_inputs=design_inputs + common_settings)

# Objective: Maximize L/D @ 150 mph
model.add_subsystem('l_over_d', om.ExecComp('val = CL / CD'))
model.connect('ecrm_150.CL', 'l_over_d.CL')
model.connect('ecrm_150.CD', 'l_over_d.CD')
model.add_objective('l_over_d.val')

# Constraint: -CM_α/CL_α > 0.0
model.add_subsystem('con_alpha_70', om.ExecComp('val = -CMa / CLa'))
model.connect('ecrm_70.CM_alpha', 'con_alpha_70.CMa')
model.connect('ecrm_70.CL_alpha', 'con_alpha_70.CLa')
model.add_constraint('con_alpha_70.val', lower=0.0)

model.add_subsystem('con_alpha_150', om.ExecComp('val = -CMa / CLa'))
model.connect('ecrm_150.CM_alpha', 'con_alpha_150.CMa')
model.connect('ecrm_150.CL_alpha', 'con_alpha_150.CLa')
model.add_constraint('con_alpha_150.val', lower=0.0)

model.add_subsystem('con_alpha_200', om.ExecComp('val = -CMa / CLa'))
model.connect('ecrm_200.CM_alpha', 'con_alpha_200.CMa')
model.connect('ecrm_200.CL_alpha', 'con_alpha_200.CLa')
model.add_constraint('con_alpha_200.val', lower=0.0)

# Constraint: CN_β > 0.0
model.add_constraint('ecrm_70.CN_beta', lower=0.0)
model.add_constraint('ecrm_150.CN_beta', lower=0.0)
model.add_constraint('ecrm_200.CN_beta', lower=0.0)

# Constraint: CL < 1.3
model.add_constraint('ecrm_70.CL', upper=1.3)
model.add_constraint('ecrm_150.CL', upper=1.3)
model.add_constraint('ecrm_200.CL', upper=1.3)

# Constraint: CL = W/qS
model.add_subsystem('con_lift_weight_70', om.ExecComp('val = CW - CL'))
model.connect('ecrm_70.C_weight', 'con_lift_weight_70.CW')
model.connect('ecrm_70.CL', 'con_lift_weight_70.CL')
model.add_constraint('con_lift_weight_70.val', equals=0.0)

model.add_subsystem('con_lift_weight_150', om.ExecComp('val = CW - CL'))
model.connect('ecrm_150.C_weight', 'con_lift_weight_150.CW')
model.connect('ecrm_150.CL', 'con_lift_weight_150.CL')
model.add_constraint('con_lift_weight_150.val', equals=0.0)

model.add_subsystem('con_lift_weight_200', om.ExecComp('val = CW - CL'))
model.connect('ecrm_200.C_weight', 'con_lift_weight_200.CW')
model.connect('ecrm_200.CL', 'con_lift_weight_200.CL')
model.add_constraint('con_lift_weight_200.val', equals=0.0)

# Design Variables
model.add_design_var('wing_cord')
model.add_design_var('vert_tail_area')
model.add_design_var('horiz_tail_area')
model.add_design_var('ecrm_70.alpha', lower=0.0, upper=12.0)
model.add_design_var('ecrm_150.alpha', lower=0.0, upper=12.0)
model.add_design_var('ecrm_200.alpha', lower=0.0, upper=12.0)

prob.driver = om.pyOptSparseDriver()
prob.driver.options['optimizer'] = "SNOPT"
prob.driver.opt_settings['Major feasibility tolerance'] = 1e-6

prob.setup()

# Set Initial Conditions
prob.set_val('beta', 0.0, units='deg')
prob.set_val('re', 1.0e6, units='1/m')
prob.set_val('rho', 0.38, units='kg/m**3')
prob.set_val('CT', grav_constant * 17.e-6, units='1/s')
prob.set_val('R', 11.165e6, units='m')
prob.set_val('W0', 0.4 * 3e5,  units='kg')
prob.set_val('load_factor', 1.)
prob.set_val('speed_of_sound', 767.0, units='mi/h')
prob.set_val('empty_cg', np.array([262.614, 0.0, 115.861]), units='m')

# Set Initial Conditions 70 mph model
prob.set_val('ecrm_70.v', 70.0, units='mi/h')
prob.set_val('ecrm_70.Mach_number', 70.0/767)

# Set Initial Conditions 150 mph model
prob.set_val('ecrm_150.v', 150.0, units='mi/h')
prob.set_val('ecrm_150.Mach_number', 150.0/767)

# Set Initial Conditions 200 mph model
prob.set_val('ecrm_200.v', 200.0, units='mi/h')
prob.set_val('ecrm_200.Mach_number', 200.0/767)

prob.run_driver()

print('done')