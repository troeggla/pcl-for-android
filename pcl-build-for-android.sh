#!/bin/bash

set -e

if [ $# -lt 1 ]; then
  echo "USAGE: $0 arch [shared]"
  exit 1
fi

ARCH=${1}

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

if [ $2 == "shared" ]; then
  echo "Building shared PCL library..."
  conan create conanfiles/pcl --profile android -s arch=$ARCH -o shared=True --build=missing
else
  echo "Building static PCL library..."
  conan create conanfiles/pcl --profile android -s arch=$ARCH --build=missing
fi

echo "PCL cross-compiling finished!"
