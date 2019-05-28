# Needs to be run from same directory that has models directory (openpose)
import boto3
import os
import subprocess
import pandas as pd
import shutil
import json

def df2csv_s3(df, s3_path, bucket_name='alignedstorage'):
	"""
	Convert Pandas dataframe to csv and upload to s3.
	"""
	s3 = boto3.resource('s3')
	bucket = s3.Bucket(bucket_name)
	csv_buffer = StringIO()
	df.to_csv(csv_buffer)
	bucket.put_object(Key=s3_path, Body=csv_buffer.getvalue(), ACL='public-read')

def upload_and_delete(local_dir, s3_path):
    """
    Convert pose keypoints from individual json to single df and
    upload to s3.
    """
    df = pd.DataFrame(columns=list(range(75)))
    for subdir, dirs, files in os.walk(local_dir):
        for i, file in enumerate(files):
            full_path = os.path.join(subdir, file)
			try:
                with open(full_path, 'rb') as f:
                    json_file = json.load(f)
                data = json_file['people'][0]['pose_keypoints_2d']
                df.loc[i] = data
            except:
                continue
		df2csv_s3(df=df, s3_path=s3_path)
	shutil.rmtree(subdir)   # delete directory and contents

bucket_name = 'alignedstorage'
prefix = "training_input/"
bucket = boto3.resource('s3').Bucket(bucket_name)

# loops through all files in the bucket beginning with prefix
for obj in bucket.objects.filter(Prefix=prefix):
	path, file = os.path.split(obj.key)

	# 1. grab name of the file
	file_name = str(file)
	print("file name:", file_name)
	if len(file_name) == 0:
		continue
	name, _ = os.path.splitext(file_name)
	# 2. save file in tmp
   	file_path = "/tmp/" + file_name
	bucket.download_file("training_input/"+file_name, file_path)
	# 3. create folder for json
   	output_dir = "/tmp/json_data"  # without extension
	if os.path.isdir(output_dir) == False:
		os.mkdir(output_dir)
	s3_path = "training_data/" + name + ".csv"
	processed_path = "/tmp/" + name + "_processed.avi"
	openpose_path = "/home/ubuntu/openpose/build/examples/openpose/openpose.bin"

	# 4. Run openpose
	openpose_cmd = [
		openpose_path,
		"--video",
		file_path,
		"--write_video",
		processed_path,
		"--write_json",
		output_dir,
		"--display",
		"0"]

	# process = sh.swfdump(_ for _ in openpose_cmd)
	process = subprocess.Popen(openpose_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	print(stderr)  # Print potential error

	# 5. save output to s3 and delete locally
   	upload_and_delete(local_dir=output_dir, s3_path=s3_path)
	os.remove(file_path)
	os.remove(processed_path)
