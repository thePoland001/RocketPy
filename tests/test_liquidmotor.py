from rocketpy import Fluid
from rocketpy.motors.LiquidMotor import Tank, LiquidMotor, MassBasedTank, UllageBasedTank, MassFlowRateBasedTank
from rocketpy.motors.Fluid import Fluid
from rocketpy.Function import Function
from math import isclose
from scipy.optimize import fmin
import numpy as np


# @PBales1
def test_mass_based_motor():
    lox = Fluid(name = "LOx", density = 1141.7, quality = 1.0) #Placeholder quality value
    propane = Fluid(name = "Propane", density = 493, quality = 1.0) #Placeholder quality value
    n2 = Fluid(name = "Nitrogen Gas", density = 51.75, quality = 1.0) #Placeholder quality value; density value may be estimate
    
    example_motor = MassBasedTank("Example Tank", 0.1540, 0.66, 0.7, "Placeholder", "Placeholder", lox, n2) 


# @curtisjhu
def test_ullage_based_motor():
    lox = Fluid(name = "LOx", density = 2, quality = 1.0)
    n2 = Fluid(name = "Nitrogen Gas", density = 1, quality = 1.0)

    ullageData = [(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1)] # constant flow rate
    tank_geometry = {(0, 6): lambda y: 1}
    ullageTank = UllageBasedTank("Ullage Tank", tank_geometry, gas=n2, liquid=lox, ullage=ullageData)


    center_of_mass_data = [[1, 3], [2, 2.5], [3, 2], [4, 1.5], [5, 1], [6, 0.5]]
    assert ullageTank.centerOfMass() == Function(center_of_mass_data)

    mass_data = [[1, 12], [2, 11], [3, 10], [4, 9], [5, 8], [6, 7]]
    assert ullageTank.mass() == Function(mass_data)

    mass_flow_rate_data = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
    assert ullageTank.netMassFlowRate() == Function(mass_flow_rate_data)

# @gautamsaiy
def test_mfr_tank_basic():
    def test(t, a):
        for i in np.arange(0, 10, .2):
            assert isclose(t.getValue(i), a(i), abs_tol=1e-5)
            # print(t.getValue(i), a(i))
            # print(t(i))

    def test_nmfr():
        nmfr = lambda x: liquid_mass_flow_rate_in + gas_mass_flow_rate_in - liquid_mass_flow_rate_out - gas_mass_flow_rate_out
        test(t.netMassFlowRate(), nmfr)

    def test_mass():
        m = lambda x: (initial_liquid_mass + (liquid_mass_flow_rate_in - liquid_mass_flow_rate_out) * x) + \
            (initial_gas_mass + (gas_mass_flow_rate_in - gas_mass_flow_rate_out) * x)
        lm = t.mass()
        test(lm, m)

    def test_liquid_height():
        alv = lambda x: (initial_liquid_mass + (liquid_mass_flow_rate_in - liquid_mass_flow_rate_out) * x) / lox.density
        alh = lambda x: alv(x) / (np.pi)
        tlh = t.liquidHeight()
        test(tlh, alh)

    def test_com():
        alv = lambda x: (initial_liquid_mass + (liquid_mass_flow_rate_in - liquid_mass_flow_rate_out) * x) / lox.density
        alh = lambda x: alv(x) / (np.pi)
        alm = lambda x: (initial_liquid_mass + (liquid_mass_flow_rate_in - liquid_mass_flow_rate_out) * x)
        agm = lambda x: (initial_gas_mass + (gas_mass_flow_rate_in - gas_mass_flow_rate_out) * x)

        alcom = lambda x: alh(x) / 2
        agcom = lambda x: (5 - alh(x)) / 2 + alh(x)
        acom = lambda x: (alm(x) * alcom(x) + agm(x) * agcom(x)) / (alm(x) + agm(x))

        tcom = t.centerOfMass
        test(tcom, acom)

    def test_inertia():
        i = t.inertiaTensor()
        test(i, 0)
        


    tank_radius_function = {(0, 5): 1}
    lox = Fluid(name = "LOx", density = 1141, quality = 1.0) #Placeholder quality value
    n2 = Fluid(name = "Nitrogen Gas", density = 51.75, quality = 1.0) #Placeholder quality value; density value may be estimate
    initial_liquid_mass = 5
    initial_gas_mass = .1
    liquid_mass_flow_rate_in = .1
    gas_mass_flow_rate_in = .01
    liquid_mass_flow_rate_out = .2
    gas_mass_flow_rate_out = .02

    t = MassFlowRateBasedTank("Test Tank", tank_radius_function,
            initial_liquid_mass, initial_gas_mass, liquid_mass_flow_rate_in,
            gas_mass_flow_rate_in, liquid_mass_flow_rate_out, 
            gas_mass_flow_rate_out, lox, n2)

    test_nmfr()
    test_mass()
    test_liquid_height()
    test_com()
    # test_inertia()


def test_mfr_tank():
    def test(t, a):
        for i in np.arange(0, 10, .2):
            assert isclose(t.getValue(i), a(i), abs_tol=1e-5)

    def test_nmfr():
        anmfr = Function("../data/e1/nmfr.csv")
        nmfr = t.netMassFlowRate()
        test(nmfr, anmfr)

    def test_mass():
        am = Function("../data/e1/mass.csv")
        m = t.mass()
        test(m, am)
    
    def test_liquid_height():
        alh = Function("../data/e1/ullage_height.csv")
        lh = t.liquidHeight()
        test(lh, alh)

    initial_liquid_mass = Function("../data/e1/liquid_mass.csv")(0)
    initial_gas_mass = Function("../data/e1/gas_mass.csv")(0)
    liquid_mass_flow_rate_in = Function(0)
    gas_mass_flow_rate_in = Function("../data/e1/gas_mfri.csv")
    liquid_mass_flow_rate_out = Function("../data/e1/liquid_mfr.csv")
    gas_mass_flow_rate_out = Function("../data/e1/gas_mfro.csv")

    lox = Fluid(name = "LOx", density = 1141, quality = 1.0) #Placeholder quality value
    n2 = Fluid(name = "Nitrogen Gas", density = 51.75, quality = 1.0) #Placeholder quality value; density value may be estimate

    top_endcap = lambda y: np.sqrt(0.0775 ** 2 - (y - 0.692300000000001) ** 2)
    bottom_endcap = lambda y: np.sqrt(0.0775 ** 2 - (0.0775 - y) **2)
    tank_geometry = {(0, 0.0559): bottom_endcap, (.0559, 0.7139): lambda y: 0.0744, (0.7139, 0.7698): top_endcap}
    
    t = MassFlowRateBasedTank("Test Tank", tank_geometry,
            initial_liquid_mass, initial_gas_mass, liquid_mass_flow_rate_in,
            gas_mass_flow_rate_in, liquid_mass_flow_rate_out,
            gas_mass_flow_rate_out, lox, n2)

    test_nmfr()
    test_mass()
    test_liquid_height()
