import math
import numpy as np


def travel_linaccel(vi: float, vf: float, a: float):
    return (vf**2 - vi**2) / (2 * a)


def _trapz_intercept_v_c_maxima_roots(
    c: float,  # max speed (abs)
    a_in: float,  # in acceleration
    a_out: float,  # out acceleration
    p_i: float,  # initial position
    v_i: float,  # initial velocity
    v_f: float,  # final velocity
    q_i: float,  # target initial position
    u: float,  # target velocity
):
    if abs(u) >= c:
        raise ValueError("max speed (c) smaller than target velocity")

    root_interior = (
        (a_in**2 - 2 * a_in * a_out + a_out**2) * u**2
        - 2 * (a_in**2 - a_in * a_out) * u * v_f
        + (a_in**2 - a_in * a_out) * v_f**2
        + 2 * (a_in * a_out - a_out**2) * u * v_i
        - (a_in * a_out - a_out**2) * v_i**2
        + 2 * (a_in**2 * a_out - a_in * a_out**2) * p_i
        - 2 * (a_in**2 * a_out - a_in * a_out**2) * q_i
    )

    # TODO: Check negative, reject

    root_part = math.sqrt(root_interior)

    root1 = ((a_in - a_out) * u - root_part) / (a_in - a_out)
    if abs(root1) > c:
        root1 = math.copysign(c, root1)

    root2 = ((a_in - a_out) * u + root_part) / (a_in - a_out)
    if abs(root2) > c:
        root2 = math.copysign(c, root2)
    return root1, root2


def _trapz_intercept_time(
    a_in: float,  # in acceleration
    a_out: float,  # out acceleration
    p_i: float,  # initial position
    v_i: float,  # initial velocity
    v_f: float,  # final velocity
    q_i: float,  # target initial position
    u: float,  # target velocity
    v_c: float,  # cruise velocity
):
    return (
        1
        / 2
        * (
            2 * a_in * a_out * p_i
            - 2 * a_in * a_out * q_i
            + (a_in - a_out) * v_c**2
            - 2 * a_in * v_c * v_f
            + a_in * v_f**2
            + 2 * a_out * v_c * v_i
            - a_out * v_i**2
        )
        / (a_in * a_out * u - a_in * a_out * v_c)
    )


def trapz_v_c_to_intercept_at_t(
    a_in: float,  # in acceleration
    a_out: float,  # out acceleration
    p_i: float,  # initial position
    v_i: float,  # initial velocity
    v_f: float,  # final velocity
    q_i: float,  # target initial position
    u: float,  # target velocity
    t: float,  # time
):
    root = math.sqrt(
        a_in**2 * a_out**2 * t**2
        - 2 * a_in**2 * a_out * t * v_f
        + a_in * a_out * v_f**2
        + a_in * a_out * v_i**2
        + 2 * (a_in**2 * a_out - a_in * a_out**2) * t * u
        - 2 * (a_in**2 * a_out - a_in * a_out**2) * p_i
        + 2 * (a_in**2 * a_out - a_in * a_out**2) * q_i
        + 2 * (a_in * a_out**2 * t - a_in * a_out * v_f) * v_i
    )

    a = a_in * a_out * t - a_in * v_f + a_out * v_i
    b = a_in - a_out

    p_f = q_i + u * t
    s = p_f - p_i

    # Assume the first solution.
    v_c = -(a + root) / b
    # Calculate s_c (cruise distance) using the first solution.
    s_c = s - travel_linaccel(v_i, v_c, a_in) + travel_linaccel(v_c, v_f, a_out)
    # If the s and s_c have opposite signs, the second solution is correct.
    if math.copysign(s_c, s) != s_c:
        v_c = -(a - root) / b
    return v_c


def trapz_opt_v_c_and_t_to_intercept(
    c: float,  # max speed (abs)
    a_in: float,  # in acceleration
    a_out: float,  # out acceleration
    p_i: float,  # initial position
    v_i: float,  # initial velocity
    v_f: float,  # final velocity
    q_i: float,  # target initial position
    u: float,  # target velocity
):
    v_c_1, v_c_2 = _trapz_intercept_v_c_maxima_roots(
        c, a_in, a_out, p_i, v_i, v_f, q_i, u
    )
    t = _trapz_intercept_time(a_in, a_out, p_i, v_i, v_f, q_i, u, v_c_2)
    v_c = v_c_2
    if t < 0:
        t_alt = _trapz_intercept_time(a_in, a_out, p_i, v_i, v_f, q_i, u, v_c_1)
        raise Exception(
            f"maybe it's the other root sometimes, after all: {t} - {t_alt}"
        )

    return v_c, t


def pulse_times_linaccel(
    steps: int,  # signed step count
    u: float,  # initial velocity
    a: float,  # accelration
):
    if steps == 0:
        return np.array([])

    s = np.linspace(math.copysign(1, steps), steps, abs(steps))
    # TODO: I'm not wild about this np.clip, but I'm getting nan for the final
    # value (but only sometimes, especially in Stepper _plan_abort).
    common = np.sqrt(np.clip(2 * a * s + u**2, 0, None))

    # print(f"{num:10}{round(u, 2):10}{a:10}{round(common[0], 2):10}")
    # TODO: Prove that this is the right way to choose which root is correct.
    if math.copysign(steps, common[0]) == steps:
        return -(u - common) / a
    else:
        return -(u + common) / a


def pulse_times_constant(
    steps: int,  # signed step count
    v: float,  # velocity
):
    s = np.linspace(math.copysign(1, steps), steps, abs(steps))
    return s / v


def _discretize_trapz_accel(s_in: float, s_out: float, steps: int):
    steps_in = int(np.trunc(s_in))
    steps_out = int(np.trunc(s_out))

    assert abs(steps_in + steps_out) <= abs(steps)
    steps_cruise = steps - (steps_in + steps_out)
    return steps_in, steps_cruise, steps_out


def pulse_times_trapz(
    v_i: float,  # initial velocity
    v_f: float,  # final velocity
    v_c: float,  # cruise velocity
    a_in: float,  # in acceleration
    a_out: float,  # out acceleration
    steps: int,  # signed step count
):
    s_in = travel_linaccel(v_i, v_c, a_in)
    s_out = travel_linaccel(v_c, v_f, a_out)

    # OPT: Could preallocate an array of `steps` floats, and then fill it,
    # instead of using `np.concatenate`.

    steps_in, steps_c, steps_out = _discretize_trapz_accel(s_in, s_out, steps)

    t_max = 0
    t_in = pulse_times_linaccel(steps_in, v_i, a_in)

    if steps_in != 0:
        t_max = t_in[-1]

    t_cruise = t_max + pulse_times_constant(steps_c, v_c)
    if steps_c != 0:
        t_max = t_cruise[-1]

    t_out = t_max + pulse_times_linaccel(steps_out, v_c, a_out)

    return np.concatenate([t_in, t_cruise, t_out])
