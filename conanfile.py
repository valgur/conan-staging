from conan.tools.microsoft import is_msvc
from conans import ConanFile, CMake, tools
import functools

required_conan_version = ">=1.45.0"


class MapnikConan(ConanFile):
    name = "mapnik"
    description = "Mapnik is an open source toolkit for developing mapping applications."
    license = "LGPL-2.1-or-later"
    topics = ("mapnik", "mapping", "gis", "cartography")
    homepage = "https://mapnik.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_libxml2": [True, False],
        "with_cairo": [True, False],
        "with_proj": [True, False],
        "grid_renderer": [True, False],
        "svg_renderer": [True, False],
        "bigint": [True, False],
        "memory_mapped_file": [True, False],
        "threadsafe": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": True,
        "with_png": True,
        "with_tiff": True,
        "with_webp": True,
        "with_libxml2": True,
        "with_cairo": True,
        "with_proj": True,
        "grid_renderer": True,
        "svg_renderer": True,
        "bigint": True,
        "memory_mapped_file": True,
        "threadsafe": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("freetype/2.11.1")
        self.requires("harfbuzz/4.2.1")
        self.requires("icu/71.1")
        self.requires("mapbox-geometry/2.0.3")
        self.requires("mapbox-variant/1.2.0")
        self.requires("polylabel/1.1.0")
        self.requires("protozero/1.7.1")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.13")
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        if self.options.with_proj:
            self.requires("proj/9.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["INSTALL_DEPENDENCIES"] = False

        cmake.definitions["USE_EXTERNAL_MAPBOX_GEOMETRY"] = True
        cmake.definitions["USE_EXTERNAL_MAPBOX_POLYLABEL"] = True
        cmake.definitions["USE_EXTERNAL_MAPBOX_PROTOZERO"] = True
        cmake.definitions["USE_EXTERNAL_MAPBOX_VARIANT"] = True
        cmake.definitions["USE_JPEG"] = self.options.with_jpeg
        cmake.definitions["USE_PNG"] = self.options.with_png
        cmake.definitions["USE_TIFF"] = self.options.with_tiff
        cmake.definitions["USE_WEBP"] = self.options.with_webp
        cmake.definitions["USE_LIBXML2"] = self.options.with_libxml2
        cmake.definitions["USE_CAIRO"] = self.options.with_cairo
        cmake.definitions["USE_PROJ"] = self.options.with_proj
        cmake.definitions["USE_GRID_RENDERER"] = self.options.grid_renderer
        cmake.definitions["USE_SVG_RENDERER"] = self.options.svg_renderer
        cmake.definitions["USE_BIGINT"] = self.options.bigint
        cmake.definitions["USE_MEMORY_MAPPED_FILE"] = self.options.memory_mapped_file
        cmake.definitions["USE_MULTITHREADED"] = self.options.threadsafe
        cmake.definitions["USE_NO_ATEXIT"] = False
        cmake.definitions["USE_NO_DLCLOSE"] = False
        cmake.definitions["USE_DEBUG_OUTPUT"] = False
        cmake.definitions["USE_LOG"] = False
        cmake.definitions["USE_STATS"] = False

        # TODO: add options
        cmake.definitions["USE_PLUGIN_INPUT_CSV"] = False
        cmake.definitions["USE_PLUGIN_INPUT_GDAL"] = False
        cmake.definitions["USE_PLUGIN_INPUT_GEOBUF"] = False
        cmake.definitions["USE_PLUGIN_INPUT_GEOJSON"] = False
        cmake.definitions["USE_PLUGIN_INPUT_OGR"] = False
        cmake.definitions["USE_PLUGIN_INPUT_PGRASTER"] = False
        cmake.definitions["USE_PLUGIN_INPUT_POSTGIS"] = False
        cmake.definitions["USE_PLUGIN_INPUT_RASTER"] = False
        cmake.definitions["USE_PLUGIN_INPUT_SHAPE"] = False
        cmake.definitions["USE_PLUGIN_INPUT_SQLITE"] = False
        cmake.definitions["USE_PLUGIN_INPUT_TOPOJSON"] = False

        cmake.definitions["BUILD_DEMO_VIEWER"] = False
        cmake.definitions["BUILD_DEMO_CPP"] = False

        cmake.definitions["BUILD_BENCHMARK"] = False

        # TODO: add options
        cmake.definitions["BUILD_UTILITY_GEOMETRY_TO_WKB"] = False
        cmake.definitions["BUILD_UTILITY_MAPNIK_INDEX"] = False
        cmake.definitions["BUILD_UTILITY_MAPNIK_RENDER"] = False
        cmake.definitions["BUILD_UTILITY_OGRINDEX"] = False
        cmake.definitions["BUILD_UTILITY_PGSQL2SQLITE"] = False
        cmake.definitions["BUILD_UTILITY_SHAPEINDEX"] = False
        cmake.definitions["BUILD_UTILITY_SVG2PNG"] = False

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mapnik")
        self.cpp_info.set_property("cmake_target_name", "mapnik::mapnik")

        prefix = "lib" if is_msvc(self) else ""
        suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.components["_mapnik"].set_property("cmake_target_name", "mapnik::mapnik")
        self.cpp_info.components["_mapnik"].libs = [f"{prefix}mapnik{suffix}"]
        self.cpp_info.components["_mapnik"].requires = ["mapnik_core", "mapnik_agg"]

        self.cpp_info.components["mapnik_core"].set_property("cmake_target_name", "mapnik::core")
        self.cpp_info.components["mapnik_core"].libdirs = []
        self.cpp_info.components["mapnik_core"].frameworkdirs = []

        self.cpp_info.components["mapnik_agg"].set_property("cmake_target_name", "mapnik::agg")
        self.cpp_info.components["mapnik_agg"].libdirs = []
        self.cpp_info.components["mapnik_agg"].frameworkdirs = []
        self.cpp_info.components["mapnik_agg"].requires = ["mapnik_core"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_mapnik"].names["cmake_find_package"] = "mapnik"
        self.cpp_info.components["_mapnik"].names["cmake_find_package_multi"] = "mapnik"
        self.cpp_info.components["mapnik_core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["mapnik_core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["mapnik_agg"].names["cmake_find_package"] = "agg"
        self.cpp_info.components["mapnik_agg"].names["cmake_find_package_multi"] = "agg"
