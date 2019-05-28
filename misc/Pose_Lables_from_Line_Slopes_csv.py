import sys
from pprint import pprint
import numpy as np
import math
from pathlib import Path
from os import listdir
from os.path import isfile, join
import pandas as pd

# procesing csv
def mean_ten_still_frames(pose_csv):
    pose_df = pose_csv
    #pose_df = pd.read_csv(pose_csv)
    pose_diff = pose_df.diff()
    rows_total_diff = pose_diff.sum(axis=1)
    rows_total_diff = [abs(i) for i in rows_total_diff]
    ten_rows_diff = []
    for i in range(len(rows_total_diff)-10):
        ten_rows_diff.append((i, sum(rows_total_diff[i:(i+10)])))
    best_ten = sorted(ten_rows_diff, key=lambda x: x[1], reverse=False)
    still_point = best_ten[0][0]
    stillest_ten = pose_df.iloc[still_point:still_point+10, :]
    mean = np.mean(stillest_ten, axis=0)
    return mean[1:]

def x_y_points(data):
    """
    from array of average of points in a single 'pose_keypoints_2d' array
    finds x and y corridnates and return two lists
    """
    x_warrior = []
    y_warrior = []
    c_warrior = [] # certainity of pose
    for n in range(len(data)):
        if (n%3) == 0:
            x_warrior.append(data[n])
        elif (n%3) == 1:
            y_warrior.append(data[n])
        elif (n%3) == 2:
            c_warrior.append(data[n])

    return x_warrior, y_warrior


# In progress

def straight_arms_slope(x, y, min_slope=-0.07, max_slope=0.0481):
    """
    input array of 25 x corridnates and array of 25 y corridinates from openpose (x_y_points(data))
    output is slope of the line from one hand to another
    perfectly straight arms would have a slope of zero.
    7:"LWrist" and 4:"RWrist"
    0 - straight
    1 - not straight
    returns slope and label
    """
    slope = (y[7]-y[4])/(x[7]-x[4])
    if min_slope <= slope <= max_slope:
        return slope, 0.0
    else:
        return slope, 1.0

def straight_arms_area(x, y, max_area = 40, max_slope = 0.07):
    """
    7:"LWrist"
    5: 'LShoulder'
    4:"RWrist"
    2: 'RShoulder'
    1: 'Neck'
    """
    d1 = (x[2]-x[5], y[2]-y[5])
    d2 = (x[4]-x[7], y[4]-y[7])
    A = .5 *abs((d1[0]*d1[1])-(d2[0]*d2[1]))
    arms_len = np.sqrt((x[7]-x[0])**2+(y[7]-y[0])**2) # 7, 0
    slope_shoulder = (y[5]-y[2])/(x[5]-x[2])

    if abs(A/arms_len) <= max_area and slope_shoulder <= max_slope:
        return (A/arms_len, slope_shoulder), 0.0
    else:
        return (A/arms_len, slope_shoulder), 1.0 # 5 wrong

def straight_arms(x, y, min_slope=-0.25, max_slope=0.25):
    slope_shoulder = (y[5]-y[2])/(x[5]-x[2])
    if min_slope <= slope_shoulder <= max_slope:
        return straight_arms_slope(x, y)
    else:
        return straight_arms_area(x, y)


def shoulders_up(x, y, max_angle=10): # 0.3
    """
    1:"Neck",
    2:"RShoulder",
    5:"LShoulder".
    looks at line from left shoulder to neck, and line from right shoulder to neck
    if either are not straight returns 1
    if both are flat (slope of 0 or close to 0) returns 1
    """
    left_degrees = math.degrees(math.atan2(y[5]-y[1], x[5]-x[1]))
    right_degrees = math.degrees(math.atan2(y[1]-y[2], x[1]-x[2]))
#     left_degrees = math.degrees(math.atan((y[5]-y[1])/(x[5]-x[1])))
#     right_degrees = math.degrees(math.atan((y[1]-y[2])/(x[1]-x[2])))  # no difference
    slope_shoulder = (y[5]-y[2])/(x[5]-x[2])
    if (left_degrees <= max_angle and right_degrees <= max_angle) and slope_shoulder <= 0.25:
        return left_degrees, right_degrees, 0.0
    else:
        return left_degrees, right_degrees, 1.0

def hips_square(x, y, max_slope=0.1):
    """
    9:"RHip" and 12:"LHip"
    straight line (square hips) would have a slope of 0
    0 - stright
    1 - not straight
    """
    slope = (y[9] - y[12])/(x[9]-x[12])
    if -max_slope <= slope <= max_slope:
        return slope, 0.0
    else:
        return slope, 1.0

# Working well

def straight_torso(x, y, min_slope=9):
    """
    1:"Neck" and 8:"MidHip"
    perfect would be a vertial line, so steep/high slope is ideal
    0 - straight
    1 - not straight
    returns slope and label
    """
    slope = (y[1] - y[8])/(x[1]-x[8])
    if abs(slope) >= min_slope:
        return slope, 0.0
    else:
        return slope, 1.0


def torso_forward(x, y, min_slope=-0.2):
    """
    1:"Neck" and 8:"MidHip"
    perfect would be a vertial line, so steep/high slope is ideal
    for too far forward we see if the slope if larger than the min slope
    0 - not too far forward
    1 - too far forward
    returns slope and label
    """
    rev_slope = (x[1]-x[8])/(y[1] - y[8])
    if rev_slope <= min_slope:
        return rev_slope, 1.0
    else:
        return rev_slope, 0.0


def torso_backward(x, y, min_slope=0.02):
    """
    1:"Neck" and 8:"MidHip"
    perfect would be a vertial line, so steep/high slope is ideal
    swtiches x and y for easier computation, want reversed slope to be zero if straight
    for too far forward we see if the slope if larger than the min slope
    0 - not too far forward
    1 - too far forward
    returns slope and label
    """
    rev_slope = (x[1]-x[8])/(y[1] - y[8])
    if rev_slope >= min_slope:
        return rev_slope, 1.0
    else:
        return rev_slope, 0.0

def head_front(x, y, max_ratio_diff=0.5, side='right'):
    """
    0:"Nose"
    15:"REye"
    16:"LEye"
    17:"REar"
    18:"LEar"
    Compares distance from left eye to right eye
    If looking forward eye to eye distance will be larger and closer to ear to ear distance
    If looking if head is front they will be small, and much smaller than ear to ear distance
    Divide by length from ear to ear to normalize and account for different distance
    label 0 - head is front
    label 1 - head is not facing the front (facing the side)
    """
    if side == 'right':
        ear_dist = np.sqrt((x[17]-x[0])**2+(y[17]-y[0])**2)
        eye_dist = np.sqrt((x[15]-x[0])**2+(y[15]-y[0])**2)
    else:
        ear_dist = np.sqrt((x[18]-x[0])**2+(y[18]-y[0])**2)
        eye_dist = np.sqrt((x[16]-x[0])**2+(y[16]-y[0])**2)
    ratio = eye_dist/ear_dist
    if ratio > max_ratio_diff:
        return ratio, 1.0
    else:
        return ratio, 0.0


def front_knee_obtuse(x, y, max_angle=75, side='right'):
    """
    10:"RKnee",
    11:"RAnkle",
    13:"LKnee",
    14:"LAnkle"
    """
    if side =='right':
        degrees = math.degrees(math.atan2(y[14]-y[13], x[14]-x[13]))
    else:
        degrees = math.degrees(math.atan2(y[11]-y[10], x[11]-x[10]))
    if degrees < max_angle:
        return degrees, 1.0
    else:
        return degrees, 0.0


def front_knee_acute(x, y, min_angle=100, side='right'):
    """
    10:"RKnee",
    11:"RAnkle",
    13:"LKnee",
    14:"LAnkle"
    """
    if side =='right':
        degrees = math.degrees(math.atan2(y[14]-y[13], x[14]-x[13]))
    else:
        degrees = math.degrees(math.atan2(y[11]-y[10], x[11]-x[10]))
    if degrees > min_angle:
        return degrees, 1.0
    else:
        return degrees, 0.0


def step_too_narrow(x, y, min_ratio=0.61):
    """
    4:"RWrist",
    7:"LWrist",
    11:"RAnkle",
    14:"LAnkle".
    compares arm span to distance between feet
    if feet are wide enough, the distance between feet will be similar
    to the distance between arms
    label - 0 feet are wide enough
    label - 1 feet are too narrow
    """
    arm_distance = np.sqrt((x[7]-x[4])**2+(y[7]-y[4])**2)
    feet_disatance = np.sqrt((x[11]-x[14])**2+(y[11]-y[14])**2)
    ratio = feet_disatance/arm_distance
    if ratio < min_ratio:
        return ratio, 1.0
    else:
        return ratio, 0.0


def step_too_wide(x, y, max_ratio=0.9):
    """
    4:"RWrist",
    7:"LWrist",
    11:"RAnkle",
    14:"LAnkle".
    compares arm span to distance between feet
    if feet are wide enough, the distance between feet will be similar
    to the distance between arms
    label - 0 feet are wide enough
    label - 1 feet are too narrow
    """
    arm_distance = np.sqrt((x[7]-x[4])**2+(y[7]-y[4])**2)
    feet_disatance = np.sqrt((x[11]-x[14])**2+(y[11]-y[14])**2)
    ratio = feet_disatance/arm_distance
    if ratio > max_ratio:
        return ratio, 1.0
    else:
        return ratio, 0.0

def warroir2_label_csv(pose_csv, side='right'):
    """
    takes averages of all rows (2d_points)
    OLD order: head_front, sholders, arms, torso forward, torso backward hips, knee acute, knee obtuse, step wider
    1 - needs to be adjusted
    0 - good
    Order for 9 digit labeling:
    1. arms
    2. front_knee_obtuse
    3. front_knee_acute
    4. head_sideways
    5. hips_angled
    6. narrow_step
    7. shoulders_up
    8. torso_forward
    9. torso_backward
    10. wide_step
    """

    x, y = x_y_points(np.array(mean_ten_still_frames(pose_csv))) # average for each point accros all ten frames
    labels = []
    values = []
    # 1 arms
    slope, label = straight_arms(x, y)
    labels.append(label)
    values.append(slope)
    # 2 and 3 front_knee_obtuse and front_knee_acute
    if side == 'right':
        obtuse_angle, obtuse_label = front_knee_obtuse(x, y, side='right')
        acute_angle, acute_label = front_knee_acute(x, y, side='right')
    else:
        obtuse_angle, obtuse_label = front_knee_obtuse(x, y, side='left')
        acute_angle, acute_label = front_knee_acute(x, y, side='left')
    labels.append(obtuse_label)
    values.append(obtuse_angle)
    labels.append(acute_label)
    values.append(acute_angle)
    # 4 head_sideways
    ratio, label = head_front(x, y)
    labels.append(label)
    values.append(ratio)
    # 5 hips_angled
    slope, label = hips_square(x, y)
    labels.append(label)
    values.append(slope)
    # 6 narrow_step
    ratio, label = step_too_narrow(x, y)
    labels.append(label)
    values.append(ratio)
    # 7 shoulders_up
    left_slope, right_slope, label = shoulders_up(x, y)
    labels.append(label)
    values.append((left_slope, right_slope))
    # 8 torso_forward
    slope, label = torso_forward(x, y)
    labels.append(label)
    values.append(slope)
    # 9 torso_backward
    slope, label = torso_backward(x, y)
    labels.append(label)
    values.append(slope)
    # 10 too wide step
    ratio, label = step_too_wide(x, y)
    labels.append(label)
    values.append(ratio)
    return labels, values


if __name__ == '__main__':
    csv_path = sys.argv[1]
    labels, values = warroir2_label_csv(csv_path)
    print(labels)
    print(values)
   #  print("""
   # 1. arms
   # 2. front_knee_obtuse
   # 3. front_knee_acute
   # 4. head_sideways
   # 5. hips_angled
   # 6. narrow_step
   # 7. shoulders_up
   # 8. torso_forward
   # 9. torso_backward
   # 10. wide_step
   # """)
