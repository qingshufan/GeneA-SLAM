import cv2
import numpy as np
import os
import argparse
from openni import openni2
from openni import _openni2 as c_api

def oni_to_png(oni_file_path, output_folder):
    if not os.path.isfile(oni_file_path):
        print(f"Error: The ONI file {oni_file_path} does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    rgb_folder = os.path.join(output_folder, 'rgb')
    depth_folder = os.path.join(output_folder, 'depth')
    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(depth_folder, exist_ok=True)
    
    associations_file = os.path.join(output_folder, 'associations.txt')
    rgb_times_file = os.path.join(output_folder, 'rgb.txt')
    depth_times_file = os.path.join(output_folder, 'depth.txt')
    
    folder_name = os.path.basename(os.path.normpath(output_folder))

    with open(rgb_times_file, 'w') as f:
        f.write("# color images\n")
        f.write(f"# file: '{folder_name}'\n")
        f.write("# timestamp filename\n")
        
    with open(depth_times_file, 'w') as f:
        f.write("# depth maps\n")
        f.write(f"# file: '{folder_name}'\n")
        f.write("# timestamp filename\n")

    openni2.initialize()

    try:
        dev = openni2.Device.open_file(oni_file_path.encode('utf-8'))

        depth_stream = dev.create_depth_stream()
        color_stream = dev.create_color_stream()

        if hasattr(dev, 'playback'):
            playback = dev.playback
            total_frames = playback.get_number_of_frames(depth_stream)
            print(f"Total frames in the ONI file: {total_frames}")
        else:
            print("The Device object does not have a 'playback' attribute.")
            return

        depth_stream.start()
        color_stream.start()

        prev_rgb_ts = None
        prev_depth_ts = None

        for frame_id in range(total_frames):
            try:
                depth_frame = depth_stream.read_frame()
                depth_timestamp = depth_frame.timestamp 
                depth_data = depth_frame.get_buffer_as_uint16()
                depth_array = np.frombuffer(depth_data, dtype=np.uint16)
                depth_image = depth_array.reshape((depth_frame.height, depth_frame.width))

                color_frame = color_stream.read_frame()
                rgb_timestamp = color_frame.timestamp 
                
                if prev_rgb_ts is not None and rgb_timestamp <= prev_rgb_ts:
                    print(f"Warning: RGB timestamp {rgb_timestamp} is not increasing. Skipping frame {frame_id}.")
                    continue
                if prev_depth_ts is not None and depth_timestamp <= prev_depth_ts:
                    print(f"Warning: Depth timestamp {depth_timestamp} is not increasing. Skipping frame {frame_id}.")
                    continue
                
                prev_rgb_ts = rgb_timestamp
                prev_depth_ts = depth_timestamp

                rgb_ts_str = f"{rgb_timestamp/1000000:.9f}" 
                depth_ts_str = f"{depth_timestamp/1000000:.9f}" 
                
                color_data = color_frame.get_buffer_as_uint8()
                color_array = np.frombuffer(color_data, dtype=np.uint8)
                color_image = color_array.reshape((color_frame.height, color_frame.width, 3))
                
                rgb_filename = f"{rgb_ts_str}.png"
                rgb_file_path = os.path.join(rgb_folder, rgb_filename)
                cv2.imwrite(rgb_file_path, cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR))

                depth_filename = f"{depth_ts_str}.png"
                depth_file_path = os.path.join(depth_folder, depth_filename)
                cv2.imwrite(depth_file_path, depth_image)

                with open(associations_file, 'a') as f:
                    f.write(f"{rgb_ts_str} rgb/{rgb_filename} {depth_ts_str} depth/{depth_filename}\n")
                with open(rgb_times_file, 'a') as f:
                    f.write(f"{rgb_ts_str} rgb/{rgb_filename}\n")
                with open(depth_times_file, 'a') as f:
                    f.write(f"{depth_ts_str} depth/{depth_filename}\n")

                if frame_id % 100 == 0:
                    print(f"Processed frame {frame_id}/{total_frames}")

            except Exception as e:
                print(f"Error processing frame {frame_id}: {e}")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'depth_stream' in locals():
            depth_stream.stop()
        if 'color_stream' in locals():
            color_stream.stop()
        openni2.unload()

    print(f"Conversion completed. TUM format files saved to {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert ONI file to TUM dataset format.')
    parser.add_argument('oni_file', type=str, help='Path to the ONI file')
    parser.add_argument('output_folder', type=str, help='Path to the output folder')
    args = parser.parse_args()

    oni_to_png(args.oni_file, args.output_folder)