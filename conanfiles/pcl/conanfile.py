from conan import ConanFile, tools
from os import path


class PclConan(ConanFile):
    name = "pcl"
    version = "1.9.1"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan Package for pcl"
    user = "pcl-android"
    channel = "stable"
    license = "BSD"
    url = "http://www.pointclouds.org/"
    exports_sources = ["no_except.patch", "pcl_binaries.patch"]

    def _to_android_abi(self, arch: str) -> str:
        if arch == "armv7":
            return "armeabi-v7a"
        if arch == "armv8":
            return "arm64-v8a"

        return arch

    def _to_android_platform(self, api_level: str) -> str:
        return "android-{}".format(api_level)

    def _configure_cmake(self):
        cmake = tools.cmake.CMake(self)

        boost_include_dir = self.dependencies["boost"].cpp_info.includedirs[0]
        boost_lib_dir = self.dependencies["boost"].cpp_info.libdirs[0]
        flann_include_dir = self.dependencies["flann"].cpp_info.includedirs[0]
        flann_lib_dir = self.dependencies["flann"].cpp_info.libdirs[0]
        eigen_include_dir = path.join(
            self.dependencies["eigen"].cpp_info.includedirs[0],
            "eigen3"
        )

        cmake.configure({
            "PCL_SHARED_LIBS": "OFF",
            "PCL_BINARIES": "OFF",
            "WITH_CUDA": "OFF",
            "WITH_OPENGL": "OFF",
            "WITH_PCAP": "OFF",
            "WITH_PNG": "OFF",
            "WITH_QHULL": "OFF",
            "WITH_VTK": "OFF",
            "Boost_DATE_TIME_LIBRARY": f"{boost_lib_dir}/libboost_date_time.a",
            "Boost_FILESYSTEM_LIBRARY": f"{boost_lib_dir}/libboost_filesystem.a",
            "Boost_IOSTREAMS_LIBRARY": f"{boost_lib_dir}/libboost_iostreams.a",
            "Boost_SYSTEM_LIBRARY": f"{boost_lib_dir}/libboost_system.a",
            "Boost_THREAD_LIBRARY": f"{boost_lib_dir}/libboost_thread.a",
            "Boost_INCLUDE_DIR": boost_include_dir,
            "Boost_LIBRARY_DIRS": boost_lib_dir,
            "EIGEN_INCLUDE_DIR": eigen_include_dir,
            "FLANN_USE_STATIC": "ON",
            "FLANN_INCLUDE_DIR": flann_include_dir,
            "FLANN_LIBRARY": f"{flann_lib_dir}/libflann_cpp_s.a;{flann_lib_dir}/liblz4.a"
        })

        return cmake

    def generate(self):
        toolchain = tools.cmake.CMakeToolchain(self)

        toolchain.variables["ANDROID_STL"] = "c++_static"
        toolchain.variables["ANDROID_TOOLCHAIN"] = self.settings.compiler
        toolchain.variables["ANDROID_PLATFORM"] = self._to_android_platform(self.settings.os.api_level)
        toolchain.variables["ANDROID_ABI"] = self._to_android_abi(str(self.settings.arch))

        toolchain.generate()

    def requirements(self):
        self.requires("boost/1.70.0@pcl-android/stable")
        self.requires("flann/1.9.1@pcl-android/stable")
        self.requires("eigen/3.3.7")

    def source(self):
        git = tools.scm.Git(self)
        git.fetch_commit(
            "https://github.com/PointCloudLibrary/pcl.git",
            f"{self.name}-{self.version}"
        )

        tools.files.patch(self, patch_file="no_except.patch") # >= boost version 1.70 https://github.com/PointCloudLibrary/pcl/commit/5605910a26f299cb53bd792e923598b3aa5bbc18
        tools.files.patch(self, patch_file="pcl_binaries.patch")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.copy(
            self,
            pattern="*.a",
            dst=path.join(self.package_folder, "lib"),
            src=path.join(self.build_folder, "lib")
        )

        tools.files.copy(
            self,
            pattern="*",
            dst=path.join(self.package_folder, "include"),
            src=path.join(self.build_folder, "include")
        )

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self)
