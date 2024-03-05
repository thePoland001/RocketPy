from unittest.mock import patch

import numpy as np
import pytest

from rocketpy import Function, utilities


@pytest.mark.parametrize(
    "terminal_velocity, rocket_mass, air_density, result",
    [
        (25, 15, 1.04, 0.4526146),
        (25, 18, 0.96, 0.5883990),
        (25, 21, 1.04, 0.6336605),
        (30, 15, 1.04, 0.3143157),
        (30, 18, 0.96, 0.4086104),
        (30, 21, 1.04, 0.4400420),
        (40, 15, 1.04, 0.1768026),
        (40, 18, 0.96, 0.2298434),
        (40, 21, 1.04, 0.2475236),
    ],
)
def test_compute_CdS_from_drop_test(
    terminal_velocity, rocket_mass, air_density, result
):
    """Test if the function `compute_cd_s_from_drop_test` returns the correct
    value. It compares the returned value with the expected result in different
    scenarios.

    Parameters
    ----------
    terminal_velocity : float
        The terminal velocity of the body (rocket) in m/s.
    rocket_mass : float
        The mass of the body (rocket) in kg.
    air_density : float
        The air density in kg/m^3.
    result : float
        The expected result of the function.
    """
    cds = utilities.compute_cd_s_from_drop_test(
        terminal_velocity, rocket_mass, air_density, g=9.80665
    )
    assert abs(cds - result) < 1e-6


def test_create_dispersion_dictionary():
    """Test if the function returns a dictionary with the correct keys.
    It reads the keys from the dictionary generated by the utilities function
    and compares them to the expected.
    Be careful if you change the "fixtures/monte_carlo/Valetudo_inputs.csv" file.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    returned_dict = utilities.create_dispersion_dictionary(
        "tests/fixtures/monte_carlo/Valetudo_inputs.csv"
    )

    test_array = np.genfromtxt(
        "tests/fixtures/monte_carlo/Valetudo_inputs.csv",
        usecols=(1, 2, 3),
        skip_header=1,
        delimiter=";",
        dtype=str,
    )
    test_dict = dict()
    for row in test_array:
        if row[0] != "":
            if row[2] == "":
                try:
                    test_dict[row[0].strip()] = float(row[1])
                except:
                    test_dict[row[0].strip()] = eval(row[1])
            else:
                try:
                    test_dict[row[0].strip()] = (float(row[1]), float(row[2]))
                except:
                    test_dict[row[0].strip()] = ""
    assert returned_dict == test_dict


# Tests not passing in the CI, but passing locally due to
# different values in the ubuntu and windows machines


@pytest.mark.skip(reason="legacy tests")
@patch("matplotlib.pyplot.show")
def test_apogee_by_mass(mock_show, flight):
    """Tests the apogee_by_mass function.

    Parameters
    ----------
    mock_show : mock
        Mock of the matplotlib.pyplot.show function.
    flight : rocketpy.Flight
        The flight object to be used in the tests.
    """
    f = utilities.apogee_by_mass(flight=flight, min_mass=5, max_mass=20, points=5)
    assert abs(f(5) - 3528.2072598) < 1e-6
    assert abs(f(10) - 3697.1896424) < 1e-6
    assert abs(f(15) - 3331.6521059) < 1e-6
    assert abs(f(20) - 2538.4542953) < 1e-6
    assert f.plot() == None


@pytest.mark.skip(reason="legacy tests")
@patch("matplotlib.pyplot.show")
def test_liftoff_by_mass(mock_show, flight):
    """Tests the liftoff_by_mass function.

    Parameters
    ----------
    mock_show : mock
        Mock of the matplotlib.pyplot.show function.
    flight : rocketpy.Flight
        The flight object to be used in the tests.
    """
    f = utilities.liftoff_speed_by_mass(
        flight=flight, min_mass=5, max_mass=20, points=5
    )
    assert abs(f(5) - 40.70236234988934) < 1e-6
    assert abs(f(10) - 31.07885818306235) < 1e-6
    assert abs(f(15) - 26.054819726081266) < 1e-6
    assert abs(f(20) - 22.703279913437058) < 1e-6
    assert f.plot() == None


def test_fin_flutter_analysis(flight_calisto_custom_wind):
    """Tests the fin_flutter_analysis function. It tests the both options of
    the see_graphs parameter.
    Parameters
    ----------
    flight_calisto_custom_wind : Flight
        A Flight object with a rocket with fins. This flight object was created
        in the conftest.py file.
    """
    flutter_mach, safety_factor = utilities.fin_flutter_analysis(
        fin_thickness=2 / 1000,
        shear_modulus=10e9,
        flight=flight_calisto_custom_wind,
        see_prints=False,
        see_graphs=False,
    )
    assert np.isclose(flutter_mach(0), 1.00482, atol=5e-3)
    assert np.isclose(flutter_mach(10), 1.1413572089696549, atol=5e-3)
    assert np.isclose(flutter_mach(np.inf), 1.0048188594647927, atol=5e-3)
    assert np.isclose(safety_factor(0), 64.78797, atol=5e-3)
    assert np.isclose(safety_factor(10), 2.1948620401502072, atol=5e-3)
    assert np.isclose(safety_factor(np.inf), 65.40588722032527, atol=5e-3)


def test_flutter_prints(flight_calisto_custom_wind):
    """Tests the _flutter_prints function.

    Parameters
    ----------
    flight_calisto_custom_wind : Flight
        A Flight object with a rocket with fins. This flight object was created
        in the conftest.py file.
    """
    flutter_mach = Function("tests/fixtures/utilities/flutter_mach.txt")
    safety_factor = Function("tests/fixtures/utilities/flutter_safety_factor.txt")
    assert (
        utilities._flutter_prints(  # pylint: disable=protected-access
            fin_thickness=2 / 1000,
            shear_modulus=10e9,
            s=0.009899999999999999,
            ar=1.2222222222222223,
            la=0.5,
            flutter_mach=flutter_mach,
            safety_factor=safety_factor,
            flight=flight_calisto_custom_wind,
        )
        is None
    ), "An error occurred while running the utilities._flutter_prints function."


@patch("matplotlib.pyplot.show")
def test_flutter_plots(mock_show, flight_calisto_custom_wind):
    """Tests the _flutter_plots function.

    Parameters
    ----------
    mock_show : mock
        Mock of the matplotlib.pyplot.show function. This is here so the plots
        are not shown during the tests.
    flight_calisto_custom_wind : Flight
        A Flight object with a rocket with fins. This flight object was created
        in the conftest.py file.
    """
    flutter_mach = Function("tests/fixtures/utilities/flutter_mach.txt")
    safety_factor = Function("tests/fixtures/utilities/flutter_safety_factor.txt")
    assert (
        utilities._flutter_plots(  # pylint: disable=protected-access
            flight_calisto_custom_wind, flutter_mach, safety_factor
        )
        is None
    ), "An error occurred while running the utilities._flutter_plots function."


def test_get_instance_attributes(flight_calisto_robust):
    """Tests if get_instance_attributes returns the expected results for a
    robust flight object."""

    attributes = utilities.get_instance_attributes(flight_calisto_robust)
    for key, value in attributes.items():
        attr = getattr(flight_calisto_robust, key)
        if isinstance(attr, np.ndarray):
            assert np.allclose(attr, value)
        else:
            assert attr == value
