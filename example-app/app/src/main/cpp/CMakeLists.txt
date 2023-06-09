cmake_minimum_required(VERSION 3.18.1)
project("myapplication")
add_library(myapplication SHARED native-lib.cpp)

find_library(log-lib log)

find_package(PCL CONFIG)

target_link_libraries(myapplication ${log-lib} PCL::PCL)
