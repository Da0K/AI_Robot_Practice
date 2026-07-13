import rclpy
import DR_init
import sys

from robot import Robot
import time

def main(args=None):
    rclpy.init(args=args)

    ROBOT_ID = "dsr7"
    ROBOT_MODEL = "m0609"
    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL

    node = rclpy.create_node('example_py', namespace=ROBOT_ID)

    DR_init.__dsr__node = node
    
    from DSR_ROBOT2 import (
        set_robot_mode,
        check_force_condition,
        DR_AXIS_Z,
        DR_BASE,
        DR_TOOL,
        ROBOT_MODE_AUTONOMOUS,
        get_tool_force,
        task_compliance_ctrl,
        set_desired_force,
        set_stiffnessx,
        DR_FC_MOD_REL,
        release_compliance_ctrl,
        release_force,
        set_ref_coord
    )

    set_robot_mode(ROBOT_MODE_AUTONOMOUS)

    robot = Robot(node)
    print("Setting Success")

    # make pick and place

    # set picking point
    gear_pick_1 = [362.24, -157.13, 17.48, 163.83, 179.45, 164.01]
    gear_pick_2 = [450.93, -100.07, 17.97, 177.70, 178.96, 177.98]
    gear_pick_3 = [456.42, -205.46, 18.47, 169.93, 179.72, 170.40]

    # set release point
    gear_place_1 = [365.83, 141.51, 16.94, 39.18, -179.80, 39.24]
    gear_place_2 = [454.16, 199.29, 17.92, 38.62, -179.12, 38.66]
    gear_place_3 = [459.84, 93.57, 17.69, 29.79, -178.26, 29.99]

    # make gear pick positions to one list
    gear_pick = [[gear_pick_1, gear_pick_1.copy()]]
    # print(gear_pick)
    gear_pick.append([gear_pick_2, gear_pick_2.copy()])
    # print(gear_pick)
    gear_pick.append([gear_pick_3, gear_pick_3.copy()])
    for i in range(len(gear_pick)):
        # print(gear_pick[i][1])
        gear_pick[i][1][2] += 100.00
    
    # make gear place positions to one list
    gear_place = [[gear_place_1, gear_place_1.copy()]]
    # print(gear_pick)
    gear_place.append([gear_place_2, gear_place_2.copy()])
    # print(gear_pick)
    gear_place.append([gear_place_3, gear_place_3.copy()])
    for i in range(len(gear_place)):
        # print(gear_pick[i][1])
        gear_place[i][1][2] += 100.00    

    # small gear positions

    gear_pick_small = [423.38, -154.53, 17.94, 7.70, -179.63, 7.83]
    gear_place_small = [426.83, 144.72, 17.45, 46.21, -179.77, 46.09]

    small_gear_pick = [gear_pick_small, gear_pick_small.copy()]
    small_gear_place = [gear_place_small, gear_place_small.copy()]
    small_gear_pick[1][2] += 100.00
    small_gear_place[1][2] += 100.00    
    # print(small_gear_place)


    # Pick and Place Start
    print("Start pick and place")
    robot.release()
    robot.home_position()

    # # Make Gear Pick and place
    # for i in range(3):
    #     robot.move_l(gear_pick[i][1])
    #     robot.move_l(gear_pick[i][1])
    #     robot.move_l(gear_pick[i][0])
    #     robot.grasp()
    #     robot.move_l(gear_pick[i][1])

    #     robot.move_l(gear_place[i][1])
    #     robot.move_l(gear_place[i][1])
    #     robot.move_l(gear_place[i][0])
    #     robot.release()
    #     robot.move_l(gear_place[i][1])

    # Make small gear pick
    robot.release()
    robot.move_l(small_gear_pick[1])
    robot.move_l(small_gear_pick[1])
    robot.move_l(small_gear_pick[0])
    robot.grasp()
    robot.move_l(small_gear_pick[1])

    robot.move_l(small_gear_place[1])
    # Start Force Control

    k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
    task_compliance_ctrl(k_d)
    print("set compliance")

    force_desired = 20.0
    f_d = [0.0, 0.0, -force_desired, 0.0, 0.0, 0.0]
    f_dir = [0, 0, 1, 0, 0, 0]
    set_desired_force(f_d, f_dir)
    print("set force")

    # If detecting external force
    force_check = 10.0
    force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
    while force_condition:
        force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
        if force_check == 0:
            break
    
    release_force()
    time.sleep(0.5)
    release_compliance_ctrl()
    robot.release()

    robot.home_position()

    # for i in range(3):
    #     robot.move_l(gear_place[i][1])
    #     robot.move_l(gear_place[i][1])
    #     robot.move_l(gear_place[i][0])
    #     robot.grasp()
    #     robot.move_l(gear_place[i][1])

    #     robot.move_l(gear_pick[i][1])
    #     robot.move_l(gear_pick[i][1])
    #     robot.move_l(gear_pick[i][0])
    #     robot.release()
    #     robot.move_l(gear_pick[i][1])



    # Go to the home position
    robot.home_position()


    # end of process

    print("Example complete")
    rclpy.shutdown()

if __name__ == '__main__':
    main()