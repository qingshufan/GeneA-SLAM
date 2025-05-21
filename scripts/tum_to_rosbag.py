#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import os
import cv2
import rosbag
import numpy as np
import argparse

def parse_tum_timestamp(timestamp_str):
    """Parse TUM format timestamp string to ROS Time"""
    try:
        parts = timestamp_str.split('.')
        secs = int(parts[0])
        
        if len(parts) > 1:
            nsecs_str = parts[1].ljust(9, '0')[:9]
            nsecs = int(nsecs_str)
        else:
            nsecs = 0
            
        return rospy.Time(secs, nsecs)
    
    except Exception as e:
        print("Error parsing timestamp %s: %s" % (timestamp_str, e))
        return rospy.Time(0, 0)

def tum_to_rosbag(rgb_folder, depth_folder, associations_file, output_bag):
    bridge = CvBridge()
    
    associations = []
    with open(associations_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 4:
                rgb_ts = parts[0]    
                rgb_path = parts[1]  
                depth_ts = parts[2]  
                depth_path = parts[3] 
                associations.append((rgb_ts, rgb_path, depth_ts, depth_path))
    
    if not associations:
        print("Error: No associations found in the file.")
        return
    
    total_frames = len(associations)
    print("Found %d frame associations." % total_frames)
    
    with rosbag.Bag(output_bag, 'w', compression=rosbag.Compression.LZ4) as bag:
        prev_timestamp = rospy.Time(0, 0) 
        for i, (rgb_ts, rgb_rel_path, depth_ts, depth_rel_path) in enumerate(associations):
            try:
                
                # Convert timestamps
                timestamp = parse_tum_timestamp(rgb_ts)
                
                if timestamp <= prev_timestamp:
                    print("Warning: Non-increasing timestamp at frame %d: %s (previous: %s)" % (i, timestamp, prev_timestamp))
                    continue
                
                prev_timestamp = timestamp
                
                 # Build paths
                rgb_abs_path = os.path.join(os.path.dirname(associations_file), rgb_rel_path)
                depth_abs_path = os.path.join(os.path.dirname(associations_file), depth_rel_path)
                
                if not os.path.exists(rgb_abs_path):
                    print("Warning: RGB file %s does not exist. Skipping." % rgb_abs_path)
                    continue
                if not os.path.exists(depth_abs_path):
                    print("Warning: Depth file %s does not exist. Skipping." % depth_abs_path)
                    continue
                
                # Read images
                rgb_img = cv2.imread(rgb_abs_path)
                rgb_msg = bridge.cv2_to_imgmsg(rgb_img, encoding="bgr8")
                rgb_msg.header.stamp = timestamp
                rgb_msg.header.frame_id = "camera_rgb_optical_frame"
                
                depth_img = cv2.imread(depth_abs_path, -1)
                depth_meters = depth_img.astype(np.float32) / 1000.0
                depth_msg = bridge.cv2_to_imgmsg(depth_meters, encoding="32FC1")
                depth_msg.header.stamp = timestamp
                depth_msg.header.frame_id = "camera_depth_optical_frame"
                
                bag.write("/camera/rgb/image_color", rgb_msg, timestamp)
                bag.write("/camera/depth/image", depth_msg, timestamp)
                
                if i % 100 == 0:
                    print("Processed %d/%d frames" % (i, total_frames))
            
            except Exception as e:
                print("Error processing frame %d: %s" % (i, str(e)))
                continue
        
        print("Completed! %d frames saved to %s" % (total_frames, output_bag))

if __name__ == "__main__":
    rospy.init_node('tum_to_rosbag_node')
    parser = argparse.ArgumentParser(description='Convert TUM dataset to ROS bag')
    parser.add_argument('dataset', help='Path to TUM dataset folder')
    parser.add_argument('output', help='Path to output ROS bag file')
    args = parser.parse_args()

    dataset_folder = args.dataset 
    rgb_folder = os.path.join(dataset_folder, "rgb")
    depth_folder = os.path.join(dataset_folder, "depth")
    associations_file = os.path.join(dataset_folder, "associations.txt")
    output_bag = args.output
    
    tum_to_rosbag(rgb_folder, depth_folder, associations_file, output_bag)