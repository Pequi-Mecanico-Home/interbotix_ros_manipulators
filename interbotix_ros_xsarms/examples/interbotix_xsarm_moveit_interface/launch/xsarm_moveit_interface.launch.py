# Copyright 2022 Trossen Robotics
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from interbotix_xs_modules.xs_common import (
    get_interbotix_xsarm_models,
)
from interbotix_xs_modules.xs_launch import (
    construct_interbotix_xsarm_semantic_robot_description_command,
    declare_interbotix_xsarm_robot_description_launch_arguments,
)
from interbotix_xs_modules.xs_launch.xs_launch import determine_use_sim_time_param
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    TextSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    TextSubstitution,
    FindExecutable,
    Command,
)
# funciona
def launch_setup(context, *args, **kwargs):

    robot_name_launch_arg = LaunchConfiguration('robot_name')
    hardware_type_launch_arg = LaunchConfiguration('hardware_type')
    use_moveit_interface_gui_launch_arg = LaunchConfiguration('use_moveit_interface_gui')

    # sets use_sim_time parameter to 'true' if using gazebo hardware
    use_sim_time_param = determine_use_sim_time_param(
        context=context,
        hardware_type_launch_arg=hardware_type_launch_arg
    )

    robot_description_semantic = Command([
    PathJoinSubstitution([
        FindExecutable(name='xacro')
    ]),
    ' ',
    PathJoinSubstitution([
        FindPackageShare('misskal_moveit'),
        'srdf',
        'vx300s.srdf.xacro'
    ]),
    ' ',
    'robot_name:=', LaunchConfiguration('robot_name'), ' ',
    'base_link_frame:=', 'vx300s_base', ' ',
    'use_gripper:=', LaunchConfiguration('use_gripper'), ' ',
    'show_ar_tag:=', LaunchConfiguration('show_ar_tag'), ' ',
    'show_gripper_bar:=', LaunchConfiguration('show_gripper_bar'), ' ',
    'show_gripper_fingers:=', LaunchConfiguration('show_gripper_fingers'), ' ',
    'use_world_frame:=', 'false', ' ',
    'external_urdf_loc:=', LaunchConfiguration('external_urdf_loc'), ' ',
    'external_srdf_loc:=', LaunchConfiguration('external_srdf_loc'), ' ',
    ])

    remappings = [
        (
            '/planning_scene',
            '/misskal/planning_scene'
        ),
        (
            '/arm_controller/follow_joint_trajectory',
            f'/misskal/arm_controller/follow_joint_trajectory'
        ),
        (
            '/gripper_controller/follow_joint_trajectory',
            f'/misskal/gripper_controller/follow_joint_trajectory'
        ),
        (
            '/joint_states',
            f'/misskal/platform/joint_states'
        ),
        (
            '/move_group/trajectory_execution/goal',
            f'/misskal/move_group/trajectory_execution/goal'
        ),
        (
            '/move_group/get_planning_scene',
            f'/misskal/move_group/get_planning_scene'
        ),
        (
            '/tf',
            f'/misskal/tf'
        ),
        (
            '/tf_static',
            f'/misskal/tf_static'
        ),
        (
            '/move_group/feedback',
            f'/misskal/move_group/feedback'
        ),
        (
            '/move_group/status',
            f'/misskal/move_group/status'
        ),
        (
            '/move_group/result',
            f'/misskal/move_group/result'
        ),
        (
            '/move_action',
            f'/misskal/move_action'
        ),
        (
        '/attached_collision_object',
        '/misskal/attached_collision_object'
        ),
        (
        '/display_planned_path',
        '/misskal/display_planned_path'
        ),
        (
        '/monitored_planning_scene',
        '/misskal/monitored_planning_scene'
        ),
        (
        '/planning_scene_world',
        '/misskal/planning_scene_world'
        ),
        (
        '/trajectory_execution_event',
        '/misskal/trajectory_execution_event'
        ),
        (
            '/rviz_moveit_motion_planning_display/robot_interaction_interactive_marker_topic/feedback',
            f'/misskal/rviz_moveit_motion_planning_display/robot_interaction_interactive_marker_topic/feedback'
        ),
        (
            '/rviz_moveit_motion_planning_display/robot_interaction_interactive_marker_topic/update',
            f'/misskal/rviz_moveit_motion_planning_display/robot_interaction_interactive_marker_topic/update'
        ),
        (
            '/execute_task_solution',
            '/misskal/execute_task_solution'
        ),
        (

            '/robot_description', 
            f'/misskal/robot_description'
        ),
    ]


    moveit_interface_node = Node(
        package='interbotix_moveit_interface',
        executable='moveit_interface',
        # namespace=robot_name_launch_arg,
        condition=LaunchConfigurationEquals(
            'moveit_interface_type',
            expected_value='cpp'
        ),
        parameters=[{
            'planning_scene_monitor_options': {
                    'robot_description':
                        'robot_description',
                    'joint_state_topic':
                         f'/misskal/platform/joint_states' if context.perform_substitution(use_sim_time_param).lower() == 'true' else '/misskal/joint_states_filtered'
                },
            'robot_description_semantic': robot_description_semantic,
            'use_sim_time': use_sim_time_param,
        }],
        remappings=remappings,
    )

    moveit_interface_gui_node = Node(
        package='interbotix_moveit_interface',
        executable='moveit_interface_gui',
        # namespace=robot_name_launch_arg,
        condition=(
            LaunchConfigurationEquals(
                launch_configuration_name='moveit_interface_type',
                expected_value='cpp'
            ) and IfCondition(
                use_moveit_interface_gui_launch_arg
            )
        ),
        parameters=[{
            'planning_scene_monitor_options': {
                    'robot_description':
                        'robot_description',
                    'joint_state_topic':
                         f'/misskal/platform/joint_states' if context.perform_substitution(use_sim_time_param).lower() == 'true' else '/misskal/joint_states_filtered'
                },
            'use_sim_time': use_sim_time_param,
        }],
        remappings=remappings,
    )

    return [
        moveit_interface_node,
        moveit_interface_gui_node,
    ]


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_model',
            choices=get_interbotix_xsarm_models(),
            description="model type of the Interbotix Arm such as 'wx200' or 'rx150'.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_name',
            default_value='misskal', # HARD CODED
            description=(
                'name of the robot (typically equal to `robot_model`, but could be anything).'
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'external_srdf_loc',
            default_value=TextSubstitution(text=''),
            description=(
                'the file path to the custom semantic description file that you would '
                "like to include in the Interbotix robot's semantic description."
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'mode_configs',
            default_value=PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_moveit_interface'),
                'config',
                'modes.yaml',
            ]),
            description="the file path to the 'mode config' YAML file.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_moveit_rviz',
            default_value='true',
            choices=('true', 'false'),
            description="launches RViz with MoveIt's RViz configuration.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'rviz_frame',
            default_value='world',
            description=(
                'defines the fixed frame parameter in RViz. Note that if '
                '`use_world_frame` is `false`, this parameter should be changed to a frame'
                ' that exists.'
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'rviz_config_file',
            default_value=PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_moveit_interface'),
                'rviz',
                'xsarm_moveit_interface.rviz'
            ]),
            description='file path to the config file RViz should load.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'world_filepath',
            default_value=PathJoinSubstitution([
                FindPackageShare('interbotix_common_sim'),
                'worlds',
                'interbotix.world',
            ]),
            description="the file path to the Gazebo 'world' file to load.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'moveit_interface_type',
            default_value='cpp',
            choices=(
                'cpp',
                # 'python',
            ),
            description=(
                "if 'cpp', launches the custom moveit_interface C++ API node; if 'python', launch "
                'the Python Interface tutorial node; only the cpp option is currently supported.'
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_moveit_interface_gui',
            default_value='true',
            choices=('true', 'false'),
            description=(
                'launch a custom GUI to interface with the moveit_interface node so that the user '
                "can command specific end-effector poses (defined by 'ee_gripper_link')."
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            choices=('true', 'false'),
            description=(
                'tells ROS nodes asking for time to get the Gazebo-published simulation time, '
                "published over the ROS topic /clock; this value is automatically set to 'true' if"
                ' using Gazebo hardware.'
            )
        )
    )
    declared_arguments.extend(
        declare_interbotix_xsarm_robot_description_launch_arguments(
            show_gripper_bar='true',
            show_gripper_fingers='true',
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
