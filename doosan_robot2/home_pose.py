import rclpy
import DR_init
import sys

def main(args=None):
    rclpy.init(args=args)

    ROBOT_ID = "dsr7"
    ROBOT_MODEL = "m0609"
    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL

    node = rclpy.create_node('example_py', namespace=ROBOT_ID)

    DR_init.__dsr__node = node

    from DSR_ROBOT2 import movej, posj, move_home, set_robot_mode, ROBOT_MODE_AUTONOMOUS

    set_robot_mode(ROBOT_MODE_AUTONOMOUS)

    home_joint = posj(0, 0, 90.0, 0, 90.0, 0)

    # movej(home_joint, vel=25, acc=25)

    move_home(0) # packaging home
    # move_home(1) # customized home

    # task_home_joint = [-180.00, 0.00, 90.00, 0.00, 90.00, 60.00]
    # movej(task_home_joint, vel=25, acc=25)

    print("Example complete")
    rclpy.shutdown()

if __name__ == '__main__':
    main()