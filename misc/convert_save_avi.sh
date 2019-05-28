# brew install ffmpeg
# to save files to a subdirectory change to s3://alignedstorage/videos/<dir_name>

for f in *.mov
do
ffmpeg -i $f -acodec copy -vcodec copy ${f%%.MOV}.avi
echo "Converted file $f"
aws s3 cp $f s3://alignedstorage/new_videos/ --acl bucket-owner-full-control --metadata "One=Two"
echo "Saved file $f to s3"
done
