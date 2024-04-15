import numpy as np

from ..mathutils.vector_matrix import Matrix, Vector
from ..prints.sensors_prints import _GyroscopePrints
from ..sensors.sensors import Sensors


class Gyroscope(Sensors):
    """Class for the gyroscope sensor

    Attributes
    ----------
    type : str
        Type of the sensor, in this case "Gyroscope".
    acceleration_sensitivity : float, list
        Sensitivity of the sensor to linear acceleration in rad/s/g.
    prints : _GyroscopePrints
        Object that contains the print functions for the sensor.
    sampling_rate : float
        Sample rate of the sensor in Hz.
    orientation : tuple, list
        Orientation of the sensor in the rocket.
    measurement_range : float, tuple
        The measurement range of the sensor in the rad/s.
    resolution : float
        The resolution of the sensor in rad/s/LSB.
    noise_density : float, list
        The noise density of the sensor in rad/s/√Hz.
    random_walk : float, list
        The random walk of the sensor in rad/s/√Hz.
    constant_bias : float, list
        The constant bias of the sensor in rad/s.
    operating_temperature : float
        The operating temperature of the sensor in degrees Celsius.
    temperature_bias : float, list
        The temperature bias of the sensor in rad/s/°C.
    temperature_scale_factor : float, list
        The temperature scale factor of the sensor in %/°C.
    cross_axis_sensitivity : float
        The cross axis sensitivity of the sensor in percentage.
    name : str
        The name of the sensor.
    rotation_matrix : Matrix
        The rotation matrix of the sensor from the sensor frame to the rocket
        frame of reference.
    normal_vector : Vector
        The normal vector of the sensor in the rocket frame of reference.
    _random_walk_drift : Vector
        The random walk drift of the sensor in rad/s.
    measurement : float
        The measurement of the sensor after quantization, noise and temperature
        drift.
    measured_data : list
        The stored measured data of the sensor after quantization, noise and
        temperature drift.
    """

    def __init__(
        self,
        sampling_rate,
        orientation=(0, 0, 0),
        measurement_range=np.inf,
        resolution=0,
        noise_density=0,
        random_walk=0,
        constant_bias=0,
        operating_temperature=25,
        temperature_bias=0,
        temperature_scale_factor=0,
        cross_axis_sensitivity=0,
        acceleration_sensitivity=0,
        name="Gyroscope",
    ):
        """
        Initialize the gyroscope sensor

        Parameters
        ----------
        sampling_rate : float
            Sample rate of the sensor in Hz.
        orientation : tuple, list, optional
            Orientation of the sensor in the rocket. The orientation can be
            given as:
            - A list of length 3, where the elements are the Euler angles for
              the rotation roll (φ), pitch (θ) and yaw (ψ) in radians. The
              standard rotation sequence is z-y-x (3-2-1) is used, meaning the
              sensor is first rotated by ψ around the z axis, then by θ around
              the new y axis and finally by φ around the new x axis.
            - A list of lists (matrix) of shape 3x3, representing the rotation
              matrix from the sensor frame to the rocket frame. The sensor frame
              of reference is defined as to have z axis along the sensor's normal
              vector pointing upwards, x and y axes perpendicular to the z axis
              and each other.
            The rocket frame of reference is defined as to have z axis
            along the rocket's axis of symmetry pointing upwards, x and y axes
            perpendicular to the z axis and each other. Default is (0, 0, 0),
            meaning the sensor is aligned with the rocket's axis of symmetry.
        measurement_range : float, tuple, optional
            The measurement range of the sensor in the rad/s. If a float, the
            same range is applied both for positive and negative values. If a
            tuple, the first value is the positive range and the second value is
            the negative range. Default is np.inf.
        resolution : float, optional
            The resolution of the sensor in rad/s/LSB. Default is 0, meaning no
            quantization is applied.
        noise_density : float, list, optional
            The noise density of the sensor in rad/s/√Hz. Sometimes called
            "white noise drift", "angular random walk" for gyroscopes, "velocity
            random walk" for the accelerometers or "(rate) noise density".
            Default is 0, meaning no noise is applied. If a float or int is
            given, the same noise density is applied to all axes. The values of
            each axis can be set individually by passing a list of length 3.
        random_walk : float, list, optional
            The random walk of the sensor in rad/s/√Hz. Sometimes called "bias
            (in)stability" or "bias drift"". Default is 0, meaning no random
            walk is applied. If a float or int is given, the same random walk is
            applied to all axes. The values of each axis can be set individually
            by passing a list of length 3.
        constant_bias : float, list, optional
            The constant bias of the sensor in rad/s. Default is 0, meaning no
            constant bias is applied. If a float or int is given, the same bias
            is applied to all axes. The values of each axis can be set
            individually by passing a list of length 3.
        operating_temperature : float, optional
            The operating temperature of the sensor in degrees Celsius. At 25°C,
            the temperature bias and scale factor are 0. Default is 25.
        temperature_sensitivity : float, list, optional
            The temperature bias of the sensor in rad/s/°C. Default is 0,
            meaning no temperature bias is applied. If a float or int is given,
            the same temperature bias is applied to all axes. The values of each
            axis can be set individually by passing a list of length 3.
        temperature_scale_factor : float, list, optional
            The temperature scale factor of the sensor in %/°C. Default is 0,
            meaning no temperature scale factor is applied. If a float or int is
            given, the same temperature scale factor is applied to all axes. The
            values of each axis can be set individually by passing a list of
            length 3.
        cross_axis_sensitivity : float, optional
            Skewness of the sensor's axes in percentage. Default is 0, meaning
            no cross-axis sensitivity is applied.
            of each axis can be set individually by passing a list of length 3.
        acceleration_sensitivity : float, list, optional
            Sensitivity of the sensor to linear acceleration in rad/s/g. Default
            is 0, meaning no sensitivity to linear acceleration is applied. If a
            float or int is given, the same sensitivity is applied to all axes.
            The values of each axis can be set individually by passing a list of
            length 3.

        Returns
        -------
        None
        """
        super().__init__(
            sampling_rate,
            orientation,
            measurement_range=measurement_range,
            resolution=resolution,
            noise_density=noise_density,
            random_walk=random_walk,
            constant_bias=constant_bias,
            operating_temperature=operating_temperature,
            temperature_bias=temperature_bias,
            temperature_scale_factor=temperature_scale_factor,
            cross_axis_sensitivity=cross_axis_sensitivity,
            name=name,
        )
        self.type = "Gyroscope"
        self.acceleration_sensitivity = self._vectorize_input(
            acceleration_sensitivity, "acceleration_sensitivity"
        )
        self.prints = _GyroscopePrints(self)

    def measure(self, t, u, u_dot, relative_position, *args):
        """Measure the angular velocity of the rocket

        Parameters
        ----------
        t : float
            Time at which the measurement is taken
        u : list
            State vector of the rocket
        u_dot : list
            Time derivative of the state vector of the rocket
        relative_position : Vector
            Vector from the rocket's center of mass to the sensor
        """
        # Angular velocity of the rocket in the rocket frame
        omega = Vector(u[10:13])

        # Transform to sensor frame
        inertial_to_sensor = self._total_rotation_matrix @ Matrix.transformation(
            u[6:10]
        )
        W = inertial_to_sensor @ omega

        # Apply noise + bias
        # Apply noise + bias and quatize
        W = self.apply_noise(W)
        W = self.apply_temperature_drift(W)

        # Apply acceleration sensitivity
        if self.acceleration_sensitivity != Vector.zeros():
            W += self.apply_acceleration_sensitivity(
                omega, u_dot, relative_position, inertial_to_sensor
            )

        W = self.quantize(W)

        self.measurement = tuple([*W])
        self.measured_data.append((t, *W))

    def apply_acceleration_sensitivity(
        self, omega, u_dot, relative_position, rotation_matrix
    ):
        """
        Apply acceleration sensitivity to the sensor measurement

        Parameters
        ----------
        omega : Vector
            The angular velocity to apply acceleration sensitivity to
        u_dot : list
            The time derivative of the state vector
        relative_position : Vector
            The vector from the rocket's center of mass to the sensor
        rotation_matrix : Matrix
            The rotation matrix from the rocket frame to the sensor frame

        Returns
        -------
        Vector
            The angular velocity with the acceleration sensitivity applied
        """
        # Linear acceleration of rocket cdm in inertial frame
        a_I = Vector(u_dot[3:6])

        # Angular velocity and accel of rocket
        omega_dot = Vector(u_dot[10:13])

        # Acceleration felt in sensor
        A = (
            a_I
            + Vector.cross(omega_dot, relative_position)
            + Vector.cross(omega, Vector.cross(omega, relative_position))
        )
        # Transform to sensor frame
        A = rotation_matrix @ A

        return self.acceleration_sensitivity & A

    def export_measured_data(self, filename, format="csv"):
        """
        Export the measured values to a file

        Parameters
        ----------
        filename : str
            Name of the file to export the values to
        format : str
            Format of the file to export the values to. Options are "csv" and
            "json". Default is "csv".

        Returns
        -------
        None
        """
        if format == "csv":
            with open(filename, "w") as f:
                f.write("t,wx,wy,wz\n")
                for t, wx, wy, wz in self.measured_data:
                    f.write(f"{t},{wx},{wy},{wz}\n")
        elif format == "json":
            import json

            data = {"t": [], "wx": [], "wy": [], "wz": []}
            for t, wx, wy, wz in self.measured_data:
                data["t"].append(t)
                data["wx"].append(wx)
                data["wy"].append(wy)
                data["wz"].append(wz)
            with open(filename, "w") as f:
                json.dump(data, f)
        else:
            raise ValueError("Invalid format")
