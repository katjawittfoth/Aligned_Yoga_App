import json
import sys
from pprint import pprint
import numpy as np
import math
from pathlib import Path
from os import listdir
from os.path import isfile, join
import pandas as pd


def x_y_points(data):
    """
    from openpose 'pose_keypoints_2d' array,
    finds x and y corridnates and return two lists
    """
    x_warrior = []
    y_warrior = []
    c_warrior = [] # certainity of pose
    keypoints = data['people'][0]['pose_keypoints_2d']
    for n in range(len(keypoints)):
        if (n%3) == 0:
            x_warrior.append(keypoints[n])
        elif (n%3) == 1:
            y_warrior.append(keypoints[n])
        elif (n%3) == 1:
            c_warrior.append(keypoints[n])

    return x_warrior, y_warrior


def straight_arms(x, y, max_slope=0.2):
    """
    input array of 25 x corridnates and array of 25 y corridinates from openpose (x_y_points(data))
    output is slope of the line from one hand to another
    perfectly straight arms would have a slope of zero.
    7:"LWrist" and 4:"RWrist"
    0 - straight
    1 - not straight
    returns slope and label
    """
    slope = (y[4] - y[7])/(x[4]-x[7])
    if -max_slope <= slope <= max_slope:
        return slope, 0
    else:
        return slope, 1


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
        return slope, 0
    else:
        return slope, 1


def torso_forward(x, y, min_slope=0.3):
    """
    1:"Neck" and 8:"MidHip"
    perfect would be a vertial line, so steep/high slope is ideal
    for too far forward we see if the slope if larger than the min slope
    0 - not too far forward
    1 - too far forward
    returns slope and label
    """
    rev_slope = (x[1]-x[8])/(y[1] - y[8])
    if rev_slope >= min_slope:
        return rev_slope, 1
    else:
        return rev_slope, 0


def torso_backward(x, y, min_slope=-0.3):
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
    if rev_slope <= min_slope:
        return rev_slope, 1
    else:
        return rev_slope, 0


def hips_square(x, y, max_slope=0.2):
    """
    9:"RHip" and 12:"LHip"
    straight line (square hips) would have a slope of 0
    0 - stright
    1 - not straight
    """
    slope = (y[9] - y[12])/(x[9]-x[12])
    if -max_slope <= slope <= max_slope:
        return slope, 0
    else:
        return slope, 1


def shoulders_up(x, y, max_slope=0.2):
    """
    1:"Neck",
    2:"RShoulder",
    5:"LShoulder".
    looks at line from left shoulder to neck, and line from right shoulder to neck
    if either are not straight returns 1
    if both are flat (slope of 0 or close to 0) returns 1
    """
    left_slope = (y[1] - y[5])/(x[1]-x[5])
    right_slope = (y[1] - y[2])/(x[1]-x[2])
    if abs(left_slope) >= max_slope or abs(right_slope) >= max_slope:
        return left_slope, right_slope, 1
    else:
        return left_slope, right_slope, 0


def head_front(x, y, max_ratio_diff=0.2):
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
    ear_dist = np.sqrt((x[17]-x[18])**2+(y[17]-y[18])**2)
    eye_dist = np.sqrt((x[15]-x[16])**2+(y[15]-y[16])**2)
    ratio = eye_dist/ear_dist
    if ratio > max_ratio_diff:
        return ratio, 1
    else:
        return ratio, 0


def front_knee_obtuse(x, y, max_angle=95, side='right'):
    """
    10:"RKnee",
    11:"RAnkle",
    13:"LKnee",
    14:"LAnkle"
    """
    if side =='right':
        degrees = math.degrees(math.atan2(y[11]-y[10], x[11]-x[10]))
    else:
        degrees = math.degrees(math.atan2(y[14]-y[13], x[14]-x[13]))
    if degrees > max_angle:
        return degrees, 1
    else:
        return degrees, 0


def front_knee_acute(x, y, min_angle=85, side='right'):
    """
    10:"RKnee",
    11:"RAnkle",
    13:"LKnee",
    14:"LAnkle"
    """
    if side =='right':
        degrees = math.degrees(math.atan2(y[11]-y[10], x[11]-x[10]))
    else:
        degrees = math.degrees(math.atan2(y[14]-y[13], x[14]-x[13]))
    if degrees < min_angle:
        return degrees, 1
    else:
        return degrees, 0


def step_wider(x, y, min_ratio=0.5):
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
        return ratio, 1
    else:
        return ratio, 0

POSE_BODY_25_BODY_PARTS  = {
    0:"Nose",
    1:"Neck",
    2:"RShoulder",
    3:"RElbow",
    4:"RWrist",
    5:"LShoulder",
    6:"LElbow",
    7:"LWrist",
    8:"MidHip",
    9:"RHip",
    10:"RKnee",
    11:"RAnkle",
    12:"LHip",
    13:"LKnee",
    14:"LAnkle",
    15:"REye",
    16:"LEye",
    17:"REar",
    18:"LEar",
    19:"LBigToe",
    20:"LSmallToe",
    21:"LHeel",
    22:"RBigToe",
    23:"RSmallToe",
    24:"RHeel",
    25:"Background"}

def warroir2_label_json_folder(path_to_json, side='right'):
    """
    assumes directory has only the json files for still moment of one pose
    takes averages of all json
    order: head_front, sholders, arms, torso forward, torso backward hips, knee acute, knee obtuse, step wider
    1 - needs to be adjusted
    0 - good
    """
    PATH = Path(path_to_json)
    files = list(PATH.iterdir())
    warrior = []
    for js in files:
        try:
            data = json.load(open(js,"r"))
            keypoints = data['people'][0]['pose_keypoints_2d']
            warrior.append(keypoints)
        except:
            continue
    warrior = np.array(warrior)
    warrior_means = np.mean(warrior, axis=1)  # average for each point accros all jsons
    x, y = x_y_points(data)
    labels = []
    values = []
    ratio, label = head_front(x, y)
    labels.append(label)
    values.append(ratio)
    left_slope, right_slope, label = shoulders_up(x, y)
    labels.append(label)
    values.append((left_slope, right_slope))
    slope, label = straight_arms(x, y)
    labels.append(label)
    values.append(slope)
    slope, label = torso_forward(x, y)
    labels.append(label)
    values.append(slope)
    slope, label = torso_backward(x, y)
    labels.append(label)
    values.append(slope)
    slope, label = hips_square(x, y)
    labels.append(label)
    values.append(slope)
    if side == 'right':
        acute_angle, acute_label = front_knee_acute(x, y, side='right')
        obtuse_angle, obtuse_label = front_knee_obtuse(x, y, side='right')
    else:
        acute_angle, acute_label = front_knee_acute(x, y, side='left')
        obtuse_angle, obtuse_label = front_knee_obtuse(x, y, side='left')
    labels.append(acute_label)
    values.append(acute_angle)
    labels.append(obtuse_label)
    values.append(obtuse_angle)
    distance, label = step_wider(x, y)
    labels.append(label)
    values.append(distance)
    return labels, values

if __name__ == '__main__':
    json_path = sys.argv[1]
    labels, values = warroir2_label_json_folder(json_path)
    print(labels)
    print(values)
