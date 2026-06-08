# KAMP per-object mesh support for Klipper
#
# Copyright (C) 2026 KAMP contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math
import random

from . import bed_mesh, probe


class KampObjectMeshError(Exception):
    pass


def _clamp(value, min_value, max_value):
    return min(max_value, max(min_value, value))


def _distance_to_bounds(x, y, bounds):
    min_x, min_y, max_x, max_y = bounds
    dx = max(min_x - x, 0.0, x - max_x)
    dy = max(min_y - y, 0.0, y - max_y)
    return math.sqrt(dx * dx + dy * dy)


def _inside_bounds(x, y, bounds):
    min_x, min_y, max_x, max_y = bounds
    return min_x <= x <= max_x and min_y <= y <= max_y


class KampCompositeMesh:
    def __init__(self, regions, zero_offset=0.0, name="kamp-object"):
        self.regions = regions
        self.zero_offset = zero_offset
        self.profile_name = name
        self.mesh_offsets = [0.0, 0.0]
        min_x = min(r["bounds"][0] for r in regions)
        min_y = min(r["bounds"][1] for r in regions)
        max_x = max(r["bounds"][2] for r in regions)
        max_y = max(r["bounds"][3] for r in regions)
        self.mesh_params = {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "x_count": max(r["x_count"] for r in regions),
            "y_count": max(r["y_count"] for r in regions),
            "mesh_x_pps": regions[0]["params"]["mesh_x_pps"],
            "mesh_y_pps": regions[0]["params"]["mesh_y_pps"],
            "algo": "object_composite",
            "tension": regions[0]["params"]["tension"],
        }

    def get_profile_name(self):
        return self.profile_name

    def get_mesh_params(self):
        return self.mesh_params

    def get_probed_matrix(self):
        rows = []
        for region in self.regions:
            rows.extend(region["mesh"].get_probed_matrix())
        return rows or [[]]

    def get_mesh_matrix(self):
        rows = []
        for region in self.regions:
            rows.extend(region["mesh"].get_mesh_matrix())
        return rows or [[]]

    def set_mesh_offsets(self, offsets):
        for i, offset in enumerate(offsets):
            if offset is not None:
                self.mesh_offsets[i] = offset

    def _select_region(self, x, y):
        matches = [
            region for region in self.regions
            if _inside_bounds(x, y, region["bounds"])
        ]
        if matches:
            return min(matches, key=lambda r: r["area"])
        return min(
            self.regions,
            key=lambda r: _distance_to_bounds(x, y, r["bounds"])
        )

    def _calc_raw_z(self, x, y):
        region = self._select_region(x, y)
        return region["mesh"].calc_z(x, y)

    def calc_z(self, x, y):
        lookup_x = x + self.mesh_offsets[0]
        lookup_y = y + self.mesh_offsets[1]
        return self._calc_raw_z(lookup_x, lookup_y) - self.zero_offset

    def get_z_range(self):
        values = []
        for region in self.regions:
            mesh_min, mesh_max = region["mesh"].get_z_range()
            values.extend([mesh_min - self.zero_offset,
                           mesh_max - self.zero_offset])
        return min(values), max(values)

    def get_z_average(self):
        total = 0.0
        count = 0
        for region in self.regions:
            matrix = region["mesh"].mesh_matrix
            if matrix is None:
                continue
            for row in matrix:
                total += sum(row)
                count += len(row)
        if not count:
            return 0.0
        return round((total / count) - self.zero_offset, 2)

    def print_probed_matrix(self, print_func):
        msg = "KAMP object mesh probed Z positions:\n"
        for region in self.regions:
            msg += "Object/region %s bounds %.2f,%.2f -> %.2f,%.2f\n" % (
                region["name"],
                region["bounds"][0],
                region["bounds"][1],
                region["bounds"][2],
                region["bounds"][3],
            )
            for row in region["mesh"].get_probed_matrix():
                msg += " " + " ".join(["%.6f" % z for z in row]) + "\n"
        print_func(msg)

    def print_mesh(self, print_func, move_z=None):
        msg = "KAMP object composite mesh: %d regions\n" % len(self.regions)
        msg += "Mesh Offsets: X=%.4f, Y=%.4f\n" % (
            self.mesh_offsets[0],
            self.mesh_offsets[1],
        )
        msg += "Zero offset: %.6f\n" % self.zero_offset
        msg += "Mesh Average: %.2f\n" % self.get_z_average()
        mesh_min, mesh_max = self.get_z_range()
        msg += "Mesh Range: min=%.4f max=%.4f\n" % (mesh_min, mesh_max)
        for region in self.regions:
            msg += "Region %s probe_count=%d,%d algorithm=%s\n" % (
                region["name"],
                region["x_count"],
                region["y_count"],
                region["params"]["algo"],
            )
        print_func(msg)


class KampObjectMesh:
    cmd_KAMP_OBJECT_MESH_CALIBRATE_help = (
        "Probe one adaptive bed mesh region per exclude_object polygon"
    )

    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object("gcode")
        self.min_region_size = config.getfloat(
            "min_region_size", 2.0, minval=0.0
        )
        self.fallback_gcode = config.get(
            "fallback_gcode", "_BED_MESH_CALIBRATE"
        )
        self.last_status = {
            "active": False,
            "mode": "idle",
            "regions": [],
            "fallback_reason": None,
        }
        self.pending_regions = []
        self.pending_point_map = []
        self.pending_zero_ref = None
        self.probe_helper = probe.ProbePointsHelper(
            config, self._probe_finalize, []
        )
        self.probe_helper.use_xy_offsets(True)
        self.gcode.register_command(
            "KAMP_OBJECT_MESH_CALIBRATE",
            self.cmd_KAMP_OBJECT_MESH_CALIBRATE,
            desc=self.cmd_KAMP_OBJECT_MESH_CALIBRATE_help,
        )

    def get_status(self, eventtime=None):
        return self.last_status

    def cmd_KAMP_OBJECT_MESH_CALIBRATE(self, gcmd):
        try:
            points = self._prepare_object_regions(gcmd)
        except Exception as exc:
            self._run_stock_fallback(gcmd, str(exc))
            return
        try:
            self.probe_helper.update_probe_points(points, 3)
            self.last_status = {
                "active": True,
                "mode": "object",
                "regions": self._region_status(self.pending_regions),
                "fallback_reason": None,
            }
            self.probe_helper.start_probe(gcmd)
        except Exception as exc:
            self._run_stock_fallback(gcmd, str(exc))

    def _lookup_bed_mesh(self):
        bedmesh = self.printer.lookup_object("bed_mesh", None)
        if bedmesh is None:
            raise KampObjectMeshError("[bed_mesh] is not loaded")
        return bedmesh

    def _get_objects(self):
        exclude_object = self.printer.lookup_object("exclude_object", None)
        if exclude_object is None:
            raise KampObjectMeshError("[exclude_object] is not loaded")
        objects = exclude_object.get_status().get("objects", [])
        objects = [obj for obj in objects if obj.get("polygon")]
        if not objects:
            raise KampObjectMeshError("no exclude_object polygons are defined")
        return objects

    def _prepare_object_regions(self, gcmd):
        method = gcmd.get("METHOD", "automatic").lower()
        if method == "rapid_scan":
            raise KampObjectMeshError(
                "rapid_scan is not supported by KAMP object meshing yet"
            )
        bedmesh = self._lookup_bed_mesh()
        bmc = bedmesh.bmc
        if bmc.orig_config["radius"] is not None:
            raise KampObjectMeshError(
                "round bed meshes are not supported by KAMP object meshing yet"
            )
        if bmc.probe_mgr.faulty_regions:
            raise KampObjectMeshError(
                "faulty_region substitution is not supported by KAMP object "
                "meshing yet"
            )

        objects = self._get_objects()
        margin = gcmd.get_float("MESH_MARGIN", 0.0, minval=0.0)
        fuzz_amount = gcmd.get_float("FUZZ_AMOUNT", 0.0, minval=0.0)
        bed_min = bmc.orig_config["mesh_min"]
        bed_max = bmc.orig_config["mesh_max"]
        full_counts = (
            bmc.orig_config["x_count"],
            bmc.orig_config["y_count"],
        )
        max_x_distance = (bed_max[0] - bed_min[0]) / (full_counts[0] - 1)
        max_y_distance = (bed_max[1] - bed_min[1]) / (full_counts[1] - 1)

        regions = []
        points = []
        point_map = []
        for obj in objects:
            region = self._object_to_region(
                obj, margin, fuzz_amount, bed_min, bed_max,
                max_x_distance, max_y_distance, bmc.mesh_config
            )
            region_index = len(regions)
            regions.append(region)
            region_points, region_map = self._generate_region_points(
                region, region_index
            )
            points.extend(region_points)
            point_map.extend(region_map)

        zero_ref = bmc.probe_mgr.get_zero_ref_pos()
        if zero_ref is not None and not any(
            _inside_bounds(zero_ref[0], zero_ref[1], r["bounds"])
            for r in regions
        ):
            points.append((zero_ref[0], zero_ref[1]))
            point_map.append(("zero_ref", None, None))
            self.pending_zero_ref = zero_ref
        else:
            self.pending_zero_ref = None

        self.pending_regions = regions
        self.pending_point_map = point_map
        logging.info(
            "KAMP object mesh prepared %d regions and %d probe points",
            len(regions), len(points)
        )
        return points

    def _object_to_region(
        self, obj, margin, fuzz_amount, bed_min, bed_max,
        max_x_distance, max_y_distance, mesh_config
    ):
        try:
            polygon = [
                (float(point[0]), float(point[1]))
                for point in obj["polygon"]
            ]
        except Exception:
            raise KampObjectMeshError(
                "object %s has an invalid polygon" % obj.get("name", "?")
            )
        if not polygon:
            raise KampObjectMeshError(
                "object %s has an empty polygon" % obj.get("name", "?")
            )
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        fuzz = random.uniform(0.0, fuzz_amount) if fuzz_amount else 0.0
        min_x = _clamp(min(xs) - margin - fuzz, bed_min[0], bed_max[0])
        min_y = _clamp(min(ys) - margin - fuzz, bed_min[1], bed_max[1])
        max_x = _clamp(max(xs) + margin + fuzz, bed_min[0], bed_max[0])
        max_y = _clamp(max(ys) + margin + fuzz, bed_min[1], bed_max[1])
        min_x, max_x = self._expand_span(min_x, max_x, bed_min[0], bed_max[0])
        min_y, max_y = self._expand_span(min_y, max_y, bed_min[1], bed_max[1])
        x_count, y_count, algorithm = self._probe_counts_for_region(
            min_x, min_y, max_x, max_y,
            max_x_distance, max_y_distance,
            mesh_config["x_count"], mesh_config["y_count"]
        )
        params = dict(mesh_config)
        params.update({
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "x_count": x_count,
            "y_count": y_count,
            "algo": algorithm,
        })
        return {
            "name": obj.get("name", "OBJECT"),
            "polygon": polygon,
            "bounds": (min_x, min_y, max_x, max_y),
            "area": (max_x - min_x) * (max_y - min_y),
            "x_count": x_count,
            "y_count": y_count,
            "params": params,
            "matrix": [[None for _ in range(x_count)]
                       for _ in range(y_count)],
        }

    def _expand_span(self, lower, upper, bed_lower, bed_upper):
        span = upper - lower
        target = max(self.min_region_size, 2.0)
        if span >= target:
            return lower, upper
        center = (lower + upper) / 2.0
        half = target / 2.0
        lower = center - half
        upper = center + half
        if lower < bed_lower:
            upper += bed_lower - lower
            lower = bed_lower
        if upper > bed_upper:
            lower -= upper - bed_upper
            upper = bed_upper
        lower = _clamp(lower, bed_lower, bed_upper)
        upper = _clamp(upper, bed_lower, bed_upper)
        if upper - lower < target:
            raise KampObjectMeshError("region is too small to probe safely")
        return lower, upper

    def _probe_counts_for_region(
        self, min_x, min_y, max_x, max_y,
        max_x_distance, max_y_distance, cfg_x_count, cfg_y_count
    ):
        width = max_x - min_x
        depth = max_y - min_y
        x_count = int(math.ceil(width / max_x_distance)) + 1
        y_count = int(math.ceil(depth / max_y_distance)) + 1
        x_count = _clamp(x_count, 3, cfg_x_count)
        y_count = _clamp(y_count, 3, cfg_y_count)
        if max(x_count, y_count) > 6:
            if min(x_count, y_count) >= 4:
                algorithm = "bicubic"
            else:
                x_count = min(x_count, 6)
                y_count = min(y_count, 6)
                algorithm = "lagrange"
        else:
            algorithm = "lagrange"
        return int(x_count), int(y_count), algorithm

    def _generate_region_points(self, region, region_index):
        min_x, min_y, max_x, max_y = region["bounds"]
        x_count = region["x_count"]
        y_count = region["y_count"]
        x_step = (max_x - min_x) / (x_count - 1)
        y_step = (max_y - min_y) / (y_count - 1)
        points = []
        point_map = []
        for y_index in range(y_count):
            y = min_y + y_step * y_index
            x_indexes = range(x_count)
            if y_index % 2:
                x_indexes = range(x_count - 1, -1, -1)
            for x_index in x_indexes:
                x = min_x + x_step * x_index
                points.append((x, y))
                point_map.append((region_index, y_index, x_index))
        return points, point_map

    def _probe_finalize(self, *args):
        probe_z_offset = 0.0
        if len(args) == 1:
            positions = args[0]
        elif len(args) == 2:
            probe_offsets, positions = args
            if len(probe_offsets) >= 3:
                probe_z_offset = probe_offsets[2]
        else:
            raise self.gcode.error(
                "KAMP object mesh: invalid finalize callback argument count"
            )
        if len(positions) != len(self.pending_point_map):
            raise self.gcode.error(
                "KAMP object mesh: invalid probe result count, expected %d "
                "got %d" % (len(self.pending_point_map), len(positions))
            )
        zero_probe_z = None
        for probed, mapping in zip(positions, self.pending_point_map):
            probed_z = self._get_probed_z(probed, probe_z_offset)
            region_index, y_index, x_index = mapping
            if region_index == "zero_ref":
                zero_probe_z = probed_z
                continue
            region = self.pending_regions[region_index]
            region["matrix"][y_index][x_index] = probed_z

        for region in self.pending_regions:
            for row in region["matrix"]:
                if any(value is None for value in row):
                    raise self.gcode.error(
                        "KAMP object mesh: incomplete matrix for %s"
                        % region["name"]
                    )
            zmesh = bed_mesh.ZMesh(region["params"], region["name"])
            try:
                zmesh.build_mesh(region["matrix"])
            except bed_mesh.BedMeshError as exc:
                raise self.gcode.error(str(exc))
            region["mesh"] = zmesh

        composite = KampCompositeMesh(self.pending_regions)
        if zero_probe_z is not None:
            composite.zero_offset = zero_probe_z
        else:
            zero_ref = self._lookup_bed_mesh().bmc.probe_mgr.get_zero_ref_pos()
            if zero_ref is not None:
                composite.zero_offset = composite._calc_raw_z(
                    zero_ref[0], zero_ref[1]
                )
        self._lookup_bed_mesh().set_mesh(composite)
        self.last_status = {
            "active": False,
            "mode": "object",
            "regions": self._region_status(self.pending_regions),
            "fallback_reason": None,
        }
        self.gcode.respond_info(
            "KAMP object mesh complete: %d object regions, %d probed points"
            % (len(self.pending_regions), len(self.pending_point_map))
        )

    def _get_probed_z(self, probed, probe_z_offset):
        if hasattr(probed, "bed_z"):
            return probed.bed_z
        return probed[2] - probe_z_offset

    def _region_status(self, regions):
        return [
            {
                "name": region["name"],
                "bounds": region["bounds"],
                "probe_count": (region["x_count"], region["y_count"]),
                "algorithm": region["params"]["algo"],
            }
            for region in regions
        ]

    def _run_stock_fallback(self, gcmd, reason):
        if not gcmd.get_int("FALLBACK", 1):
            raise gcmd.error("KAMP object mesh failed: %s" % reason)
        if not self.fallback_gcode:
            raise gcmd.error(
                "KAMP object mesh failed and no fallback_gcode is configured: "
                "%s" % reason
            )
        fallback_parts = [self.fallback_gcode]
        mapping = [
            ("FALLBACK_MESH_MIN", "MESH_MIN"),
            ("FALLBACK_MESH_MAX", "MESH_MAX"),
            ("FALLBACK_ALGORITHM", "ALGORITHM"),
            ("FALLBACK_PROBE_COUNT", "PROBE_COUNT"),
        ]
        for source, target in mapping:
            value = gcmd.get(source, None)
            if value is not None:
                fallback_parts.append("%s=%s" % (target, value))
        method = gcmd.get("METHOD", None)
        if method is not None:
            fallback_parts.append("METHOD=%s" % method)
        self.last_status = {
            "active": False,
            "mode": "fallback",
            "regions": [],
            "fallback_reason": reason,
        }
        fallback = " ".join(fallback_parts)
        gcmd.respond_info(
            "KAMP object mesh unavailable: %s. Falling back with: %s"
            % (reason, fallback)
        )
        self.gcode.run_script_from_command(fallback)


def load_config(config):
    return KampObjectMesh(config)
