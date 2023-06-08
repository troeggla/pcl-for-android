#!/bin/bash

set -e

ARCH=${1}

if [ $# -ne 1 ]; then
  echo "USAGE: $0 arch"
  exit 1
fi

echo -e "\n\n\033[1;35m###########################################"
echo -e "### FLANN cross-compiling start...      ###"
echo -e "###########################################\033[m\n\n"

conan create conanfiles/lz4 --profile android -s arch=$ARCH --build=missing
conan create conanfiles/flann --profile android -s arch=$ARCH --build=missing

echo "FLANN cross-compiling finished!"

echo -e "\n\n\033[1;35m###########################################"
echo -e "### BOOST cross-compiling start...      ###"
echo -e "###########################################\033[m\n\n"

conan create conanfiles/boost --profile android -s arch=$ARCH --build=missing

echo "BOOST cross-compiling finished!"

echo -e "\n\n\033[1;35mm###########################################"
echo -e "### PCL cross-compiling start...        ###"
echo -e "###########################################\033[m\n\n"

conan create conanfiles/pcl --profile android -s arch=$ARCH --build=missing

echo "PCL cross-compiling finished!"
