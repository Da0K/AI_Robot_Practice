import rclpy
import DR_init
import sys

def main(args=None):
    rclpy.init(args=args)

    ROBOT_ID = "dsr17"
    ROBOT_MODEL = "m0609"
    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL

    node = rclpy.create_node('example_py', namespace=ROBOT_ID)

    DR_init.__dsr__node = node

    from DSR_ROBOT2 import movej, posj, set_robot_mode, ROBOT_MODE_AUTONOMOUS

    set_robot_mode(ROBOT_MODE_AUTONOMOUS)

    target_pos = posj(0, 0, 90.0, 0, 90.0, 0)

    movej(target_pos, vel=100, acc=100)

    print("Example complete")
    rclpy.shutdown()

if __name__ == '__main__':
    main()