echo "Building ROS nodes"

cd Examples/ROS/GeneA_SLAM
mkdir build
cd build
cmake .. -DROS_BUILD_TYPE=Release
make -j4
