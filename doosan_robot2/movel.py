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

    from DSR_ROBOT2 import movel, set_robot_mode, get_current_pose, DR_TOOL, ROBOT_MODE_AUTONOMOUS

    set_robot_mode(ROBOT_MODE_AUTONOMOUS)

    joint = get_current_pose(0)
    task = get_current_pose(1)

    print("joint: ", joint)
    print("task: ", task)

    point_1 = [368.00, 6.00, 424.00, 10.00, -179.00, 10.00]
    point_2 = [368.00, 6.00, 394.00, 10.00, -179.00, 10.00]

    movel(point_1, vel=50, acc=50)
    movel(point_2, vel=50, acc=50)

    print("Example complete")
    rclpy.shutdown()

if __name__ == '__main__':
    main()