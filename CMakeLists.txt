cmake_minimum_required(VERSION 2.8)
project(GeneA-SLAM)


set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")
set(CMAKE_CXX_STANDARD 14)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

find_package(OpenCV 3.0 QUIET)

include_directories(
${PROJECT_SOURCE_DIR}
${PROJECT_SOURCE_DIR}/sdk/include 
)

target_link_libraries(${PROJECT_NAME}
${OpenCV_LIBS}
)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR})
add_executable(load load.cpp)
target_link_libraries(load 
${PROJECT_NAME} 
${OpenCV_LIBS}
${PROJECT_SOURCE_DIR}/sdk/libs/libOpenNI2.so
${PROJECT_SOURCE_DIR}/sdk/libs/OpenNI2/Drivers/libOniFile.so 
${PROJECT_SOURCE_DIR}/sdk/libs/OpenNI2/Drivers/liborbbec.so
)

