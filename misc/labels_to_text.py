import numpy as np
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

#labels = [1, 1, 1, 1, 0, 0 ,0 , 0, 0]

class ProsessPose:

    @classmethod
    def to_text(cls, labels:list):
        trans_fd = {
    0: 'straighten your arms, keep palms facing down',
    1: 'make sure your front shin is perpendicular to the floor. So that your \
    knee and shin are forming a right angle between the right thigh and the \
     right calf',
    2: 'make sure your knee is not extended beyond your ankle, but is in line \
     with the heel',
    3: 'turn your head and look over your front fingers. Fix your gaze to \
    increase the focus',
    4: 'square your hips and shoulders sideways towards the camera. Engage your\
     core! Tailbone down, belly in',
    5: 'make a wider step, your feet are too close together' ,
    6: 'drop your shoulders away from your ears and actively reach towards both\
     ends of the room',
    7: "stack your shoulders directly over your hips so that rib cage isn't\
     floating forward",
    8: "stack your shoulders directly over your hips so that rib cage isn't\
     floating backward",
    9: 'make a shorter stance, seems like your feet are be too wide apart.\
     Back leg straight and strong'
    }
        if labels.count(1) == 0:
            print(f'Excellent job! Keep it up, yogi! Wanna try different pose?')

        if labels.count(1) == 1:
            index = np.where(np.array(labels) == 1)[0]
            output = trans_fd[index[0]]
            print(f'Very very nice! One little thing: try to {output}!')

        if labels.count(1) >= 2 and labels.count(1) < 7:
            index = np.where(np.array(labels) == 1)[0] #list
            print('Well done! Couple of things to keep in mind for you:')
            for i in index:
                print(f'- {trans_fd[i][0].capitalize() +trans_fd[i][1:]}.')

        if labels.count(1) >= 7:
            print("Are you sure you were following my instructions?\
             Let's try again!")