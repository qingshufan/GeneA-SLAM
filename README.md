# GeneA-SLAM

## Sculpture Dataset

### Description
The relevant data was collected using the Orbbec Astra depth camera (which has been calibrated) to construct the Sculpture dataset. The frame rate was set to 30, resulting in a total of 6571 image pairs, with both RGB and depth images aligned. Each image has a resolution of ( 640 x 480 ). And the final data is saved in the dataset/sculpture.oni file

### Usage
1. **Concatenate the split files:**:
   If you have the split parts of the sculpture.tar.gz file, you can concatenate them back into a single file using the following command:
   ```bash
   cat ./dataset/sculpture.part.* > ./dataset/sculpture.tar.gz
   ```
1. **Decompress the ONI file**:
   ```bash
   tar -xzf ./dataset/sculpture.tar.gz
   ```
   This command will extract the contents of `sculpture.tar.gz`, which should include the `sculpture.oni` file.

2. **Read the data**:
   Once the file is decompressed, you can use the example code located in `load.cpp` to read the data from the ONI file.

3. **Build the project**:
   Use CMake to configure and generate build files for your project.

Remember to have the OpenNI2 and OpenCV libraries installed on your system before you attempt to build the project. The `load.cpp` file should include the necessary includes and code to interface with these libraries for reading ONI files.
