from conan import ConanFile, tools
from os import path

import yaml


class BoostConan(ConanFile):
    name = "boost"
    version = "1.82.0"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan package for boost library"
    url = "https://www.boost.org/"
    license = "Boost Software License"
    folder_name = "boost-{}".format(version[:4].replace(".", "_"))
    user = "pcl-android"
    channel = "stable"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    _cached_dependencies = None

    def export(self):
        tools.files.copy(
            self,
            f"dependencies/{self._dependency_filename}",
            src=self.recipe_folder,
            dst=self.export_folder
        )

    @property
    def _dependency_filename(self):
        return f"dependencies-{self.version}.yml"

    @property
    def _dependencies(self):
        if self._cached_dependencies is None:
            dependencies_filepath = path.join(
                self.recipe_folder, "dependencies", self._dependency_filename
            )

            if not path.isfile(dependencies_filepath):
                raise FileNotFoundError(f"Cannot find {dependencies_filepath}")

            with open(dependencies_filepath, encoding='utf-8') as f:
                self._cached_dependencies = yaml.safe_load(f)

        return self._cached_dependencies

    def _to_android_arch(self, arch: str) -> str:
        if arch == "armv7":
            return "armeabi-v7a"
        if arch == "armv8":
            return "arm64-v8a"

        return arch

    def source(self):
        git = tools.scm.Git(self)
        git.clone(
            url="https://github.com/moritz-wundke/Boost-for-Android",
            target="."
        )

    def build(self):
        ndk_path = self.conf.get("tools.android:ndk_path")
        android_arch = self._to_android_arch(self.settings.arch)

        self.run(f"./build-android.sh {ndk_path} --arch={android_arch} --boost={self.version}")

    def package(self):
        android_arch = self._to_android_arch(self.settings.arch)

        tools.files.copy(
            self,
            pattern="*.a",
            dst=path.join(self.package_folder, "lib"),
            src=f"build/out/{android_arch}/lib"
        )
        tools.files.copy(
            self,
            pattern="*",
            dst=path.join(self.package_folder, "include/boost"),
            src=f"build/out/{android_arch}/include/{self.folder_name}/boost"
        )

    def package_info(self):
        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.set_property("cmake_file_name", "Boost")
        self.cpp_info.filenames["cmake_find_package"] = "Boost"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Boost"
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].set_property("cmake_target_name", "Boost::headers")
        self.cpp_info.components["headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["headers"].names["pkg_config"] = "boost"

        # Boost::boost is an alias of Boost::headers
        self.cpp_info.components["_boost_cmake"].requires = ["headers"]
        self.cpp_info.components["_boost_cmake"].set_property("cmake_target_name", "Boost::boost")
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package"] = "boost"
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package_multi"] = "boost"

        self.cpp_info.components["_libboost"].requires = ["headers"]

        self.cpp_info.components["diagnostic_definitions"].libs = []
        self.cpp_info.components["diagnostic_definitions"].set_property("cmake_target_name", "Boost::diagnostic_definitions")
        self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package"] = "diagnostic_definitions"
        self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package_multi"] = "diagnostic_definitions"
        self.cpp_info.components["diagnostic_definitions"].names["pkg_config"] = "boost_diagnostic_definitions"  # FIXME: disable on pkg_config
        self.cpp_info.components["headers"].requires.append("diagnostic_definitions")

        self.cpp_info.components["disable_autolinking"].libs = []
        self.cpp_info.components["disable_autolinking"].set_property("cmake_target_name", "Boost::disable_autolinking")
        self.cpp_info.components["disable_autolinking"].names["cmake_find_package"] = "disable_autolinking"
        self.cpp_info.components["disable_autolinking"].names["cmake_find_package_multi"] = "disable_autolinking"
        self.cpp_info.components["disable_autolinking"].names["pkg_config"] = "boost_disable_autolinking"  # FIXME: disable on pkg_config

        self.cpp_info.components["headers"].requires.append("disable_autolinking")

        self.cpp_info.components["dynamic_linking"].libs = []
        self.cpp_info.components["dynamic_linking"].set_property("cmake_target_name", "Boost::dynamic_linking")
        self.cpp_info.components["dynamic_linking"].names["cmake_find_package"] = "dynamic_linking"
        self.cpp_info.components["dynamic_linking"].names["cmake_find_package_multi"] = "dynamic_linking"
        self.cpp_info.components["dynamic_linking"].names["pkg_config"] = "boost_dynamic_linking"  # FIXME: disable on pkg_config
        self.cpp_info.components["headers"].requires.append("dynamic_linking")

        for module in self._dependencies["dependencies"]:
            self.cpp_info.components[module].set_property("cmake_target_name", "Boost::" + module)
            self.cpp_info.components[module].names["cmake_find_package"] = module
            self.cpp_info.components[module].names["cmake_find_package_multi"] = module
            self.cpp_info.components[module].names["pkg_config"] = f"boost_{module}"
