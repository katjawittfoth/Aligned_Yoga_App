# Needs to be run from same directory that has models directory (openpose)
import boto3
import os
import subprocess
import shutil

def upload_and_delete(path, s3_dir):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=s3_dir + full_path[len(path)+1:], Body=data)
#    shutil.rmtree(subdir)   # delete directory and contents

bucket_name = 'alignedstorage'
#bucket_name = 'aligned2'
bucket = boto3.resource('s3').Bucket(bucket_name)

# loops through all files in the bucket
for obj in bucket.objects.filter(Prefix="training_input/"):
    path, file = os.path.split(obj.key)

    # 1. grab name of the file
    file_name = str(file)
    print("file name:", file_name)
    if len(file_name) > 0:
   	 name, _ = os.path.splitext(file_name)
   	 # 2. save file in tmp
   	 file_path = "/tmp/" + file_name
   	 bucket.download_file("training_input/"+file_name, file_path)
   	 # 3. create folder for json
   	 output_dir = "/tmp/json_data"  # without extension
   	 if os.path.isdir(output_dir) == False:
        	os.mkdir(output_dir)
   	 s3_dir = "training_data/" + name + "/"
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
   	 upload_and_delete(output_dir, s3_dir)
    	 #os.remove(file_path)
    	 #os.remove(processed_path)
