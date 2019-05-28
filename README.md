
<div align="left">
    <img src="code/aligned/app/static/images/logo.svg",style="height:50px;">
</div>

# Aligned - Yoga Pose Correction App
Aligned is a yoga pose correction application that processes images and videos of a user’s yoga poses and provides feedback on how to improve the pose.

The app allows yoga enthusiasts to practive yoga safely from the comfort of their own home while still being able to receive personalized feedback on their poses.

The app was built using Flask and runs on an Amazon EC2 instance with GPU.

The overall process is as follows:

* User logs in and selects which pose to evaluate
* App provides instructions on how to execute the pose
Once ready, the user records a video of themselves doing the pose within the app (using webcam)
Video is automatically processed using [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose), an open-source, deep learning-based library for keypoint detection developed at Carnegie Mellon University.
* The app uses the keypoints from OpenPose as features *to classify different pose faults using a rule-based system.
* Feedback is provided to the user on how they can safely improve their pose.


<i> Note that the app's website is not currently available due to the high cost of running AWS EC2 instance.</i>

* [![Watch Demo Video](https://i.imgur.com/vKb2F1B.png)](https://youtu.be/t8HMLYR1-FE)
* [Slide Deck for final presentation to VCs](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/Aligned_VC_Presentation_Deck.pdf)
* [Flask routes](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/code/aligned/app/routes.py)
* [Video processing script](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/code/aligned/process_openpose_user.py)
* [Modeling](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/code/aligned/modeling.py)
