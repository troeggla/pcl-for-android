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

  echo "Copying compiled artifacts..."
  conan list 'pcl#:*' |sed 's/ //g' > package_info.txt

  package_name=`cat package_info.txt |head -n3 |tail -n1`
  revision_id=`cat package_info.txt |head -n5 |tail -n1 |sed 's/(.*)//'`
  package_id=`cat package_info.txt |head -n7 |tail -n1`

  package_folder=`conan cache path ${package_name}#${revision_id}:${package_id}`

  if [ -d "dist/${ARCH}" ]; then
    echo "Deleting outdated dist directory..."
    rm -r dist/${ARCH}
  fi

  mkdir -p dist/${ARCH}/lib dist/${ARCH}/include
  cp ${package_folder}/lib/*.so dist/${ARCH}/lib
  cp -r ${package_folder}/include/* dist/${ARCH}/include

  rm package_info.txt

  echo "DONE!"
else
  echo "Building static PCL library..."
  conan create conanfiles/pcl --profile android -s arch=$ARCH --build=missing
fi

echo "PCL cross-compiling finished!"
