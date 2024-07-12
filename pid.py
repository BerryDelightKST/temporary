
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, output_limits=(None, None)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_limits = output_limits

        self._integral = 0
        self._previous_error = None

    def update(self, current_value, dt):
        error = self.setpoint - current_value
        self._integral += error * dt
        derivative = 0 if self._previous_error is None else (error - self._previous_error) / dt
        self._previous_error = error

        output = self.Kp * error + self.Ki * self._integral + self.Kd * derivative
        output = max(self.output_limits[0], min(output, self.output_limits[1])) if self.output_limits[0] is not None else output # constrain

        return output