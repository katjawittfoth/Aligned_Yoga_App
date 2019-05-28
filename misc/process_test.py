
import boto3
import os
import subprocess
import pandas as pd
import shutil
import json
import sys
from io import StringIO

#training_input/testing_hw.avi



path_video = sys.argv[1]
#path_s3_csv = sys.argv[2]

# Get paths
dir, file_name = os.path.split(path_video)
name, _ = os.path.splitext(file_name)

path_s3_csv = 'output/' + name + '.csv'

path_local = "/tmp/" + file_name
output_dir = "/tmp/json_data"  # without extension
processed_path = "/tmp/" + name + "_processed.avi"
openpose_path = "/home/ubuntu/openpose/build/examples/openpose/openpose.bin"

# Download file from bucket
bucket_name = 'alignedstorage'
#bucket_name = 'aligned2'
bucket = boto3.resource('s3').Bucket(bucket_name)
bucket.download_file(path_video, path_local)