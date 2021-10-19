import os
import subprocess
import tempfile

os.chdir('/opt/nvidia/deepstream/deepstream-5.1/samples/configs/deepstream-app')


proc = subprocess.Popen(['sudo', '-S', 'nano', 'test.txt'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=b'a\n') #get root
command = 'sudo deepstream-app -c  source8_1080p_dec_infer-resnet_tracker_tiled_display_fp16_nano.txt'
#p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#outinfo = p.stdout.readlines() #或者outinfo = p.stdout.read()
#print(outinfo)


with tempfile.TemporaryFile() as tempf:
    proc = subprocess.Popen(command, shell=True,  stdout=tempf)
    proc.wait()
    tempf.seek(0)
    print(tempf.read())