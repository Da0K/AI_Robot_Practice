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
        ROBOT_MODE_AUTONOMOUS,
    )

    set_robot_mode(ROBOT_MODE_AUTONOMOUS)

    robot = Robot(node)
    print("Setting Success")

    # make pick and place

    # set picking point
    gear_pick_1 = [362.24, -157.13, 17.48, 163.83, 179.45, 164.01]
    gear_pick_2 = [450.93, -100.07, 17.97, 177.70, 178.96, 177.98]
    gear_pick_3 = [456.42, -205.46, 18.47, 169.93, 179.72, 170.40]

    # gear_pick_up_1 = gear_pick_1.copy()
    # gear_pick_up_2 = gear_pick_2.copy()
    # gear_pick_up_3 = gear_pick_3.copy()

    # gear_pick_up_1[2] += 100.00
    # gear_pick_up_2[2] += 100.00
    # gear_pick_up_3[2] += 100.00

    # set release point
    gear_place_1 = [365.83, 141.51, 16.94, 39.18, -179.80, 39.24]
    gear_place_2 = [454.16, 199.29, 17.92, 38.62, -179.12, 38.66]
    gear_place_3 = [459.84, 93.57, 17.69, 29.79, -178.26, 29.99]

    # gear_place_up_1 = gear_place_1.copy()
    # gear_place_up_2 = gear_place_2.copy()
    # gear_place_up_3 = gear_place_3.copy()

    # gear_place_up_1[2] += 100.00
    # gear_place_up_2[2] += 100.00
    # gear_place_up_3[2] += 100.00

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

    # Pick and Place Start
    print("Start pick and place")
    robot.release()
    robot.home_position()

    # Make Gear Pick and place
    for i in range(3):
        robot.move_l(gear_pick[i][1])
        robot.move_l(gear_pick[i][1])
        robot.move_l(gear_pick[i][0])
        robot.grasp()
        robot.move_l(gear_pick[i][1])

        robot.move_l(gear_place[i][1])
        robot.move_l(gear_place[i][1])
        robot.move_l(gear_place[i][0])
        robot.release()
        robot.move_l(gear_place[i][1])

    robot.home_position()

    for i in range(3):
        robot.move_l(gear_place[i][1])
        robot.move_l(gear_place[i][1])
        robot.move_l(gear_place[i][0])
        robot.grasp()
        robot.move_l(gear_place[i][1])

        robot.move_l(gear_pick[i][1])
        robot.move_l(gear_pick[i][1])
        robot.move_l(gear_pick[i][0])
        robot.release()
        robot.move_l(gear_pick[i][1])


    # # Gear 1 pick
    # robot.move_l(gear_pick_up_1)
    # robot.move_l(gear_pick_up_1)
    # robot.move_l(gear_pick_1)
    # robot.grasp()
    # robot.move_l(gear_pick_up_1)

    # # Gear 2 place
    # robot.move_l(gear_place_up_1)
    # robot.move_l(gear_place_1)
    # robot.release()
    # robot.move_l(gear_place_up_1)

    # # Gear 2 pick
    # robot.move_l(gear_pick_up_2)
    # robot.move_l(gear_pick_2)
    # robot.grasp()
    # robot.move_l(gear_pick_up_2)


    # # Gear 2 place
    # robot.move_l(gear_place_up_2)
    # robot.move_l(gear_place_2)
    # robot.release()
    # robot.move_l(gear_place_up_2)

    # # Gear 3 pick
    # robot.move_l(gear_pick_up_3)
    # robot.move_l(gear_pick_3)
    # robot.grasp()
    # robot.move_l(gear_pick_up_3)

    # # Gear 3 place
    # robot.move_l(gear_place_up_3)
    # robot.move_l(gear_place_3)
    # robot.release()
    # robot.move_l(gear_place_up_3)

    # Go to the home position
    robot.home_position()


    # end of process

    print("Example complete")
    rclpy.shutdown()

if __name__ == '__main__':
    main()