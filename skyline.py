#!/usr/bin/env python3
"""
Requires:
    - git
    - openscad

Pip:
    - solidpython
"""
import os
import argparse
import subprocess
import datetime
import calendar
import math
from solid import *
from solid.utils import *

def get_commits_per_day_for_year(author, year):
    git_cmd = "git log --date=short --pretty=format:%ad"
    proc = subprocess.run(git_cmd.split(" "), capture_output=True)
    assert proc.returncode == 0, "Something went wrong with git!"

    commit_dates = []
    for date in proc.stdout.decode("utf-8").split("\n"):
        git_year, git_month, git_day = date.split("-")
        commit_dates.append(datetime.datetime(int(git_year), int(git_month), int(git_day)))

    dates = []
    for month in range(1, 13):
        for day in range(1, calendar.monthrange(int(year), month)[1] + 1):
            dates.append(datetime.datetime(int(year), month, day))
                
    commits_per_day = [commit_dates.count(x) for x in dates]

    return commits_per_day

def generate_skyline(author, year):
    year_contribution_list = get_commits_per_day_for_year(author, year)
    max_contributions_by_day = max(year_contribution_list)

    base_top_width = 23
    base_width = 30
    base_length = 150
    base_height = 10
    max_length_contributionbar = 20
    bar_base_dimension = 2.5
    base_top_offset = (base_width - base_top_width) / 2
    face_angle = math.degrees(math.atan(base_height / base_top_offset))

    base_points = [
        [0, 0, 0],
        [base_length, 0, 0],
        [base_length, base_width, 0],
        [0, base_width, 0],
        [base_top_offset, base_top_offset, base_height],
        [base_length - base_top_offset, base_top_offset, base_height],
        [base_length - base_top_offset, base_width - base_top_offset, base_height],
        [base_top_offset, base_width - base_top_offset, base_height]
    ]

    base_faces = [
        [0, 1, 2, 3],  # bottom
        [4, 5, 1, 0],  # front
        [7, 6, 5, 4],  # top
        [5, 6, 2, 1],  # right
        [6, 7, 3, 2],  # back
        [7, 4, 0, 3]  # left
    ]

    base_scad = polyhedron(points=base_points, faces=base_faces)

    year_scad = rotate([face_angle, 0, 0])(
        translate([base_length - base_length / 5, base_height / 2 - base_top_offset / 2 - 1, -1.5])(
            linear_extrude(height=3)(
                text(str(year), 6)
            )
        )
    )

    user_scad = rotate([face_angle, 0, 0])(
        translate([9, base_height / 2 - base_top_offset / 2, -1.5])(
            linear_extrude(height=3)(
                text(author, 6)
            )
        )
    )

    bars = None

    week_number = 1
    from tqdm.auto import tqdm
    for i in tqdm(range(len(year_contribution_list))):
        day_number = i % 7
        if day_number == 0:
            week_number += 1
        if year_contribution_list[i] == 0:
            continue

        bar = translate(
            [base_top_offset + 2.5 + (week_number - 1) * bar_base_dimension,
             base_top_offset + 2.5 + day_number * bar_base_dimension, base_height])(
                cube([bar_base_dimension, bar_base_dimension,
                year_contribution_list[i] * max_length_contributionbar / max_contributions_by_day])
        )

        if bars is None:
            bars = bar
        else:
            bars += bar

    scad_contributions_filename = f"git_{author}_{year}"
    scad_skyline_object = base_scad + user_scad + year_scad

    if bars is not None:
        scad_skyline_object += bars

    scad_file = f"{scad_contributions_filename}.scad"
    scad_render_to_file(scad_skyline_object, scad_file)

    print("SCAD generated converting to STL")

    stl_file = f"{scad_contributions_filename}.stl"
    subprocess.run(['openscad', '-o', stl_file, scad_file], capture_output=True)
    os.remove(scad_file)


def parse_args():
    parser = argparse.ArgumentParser(description="Create git skyline of current repo")
    parser.add_argument("author", help="Who are we making skyline for?")
    parser.add_argument("year", help="Which year are we interested int?")

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    generate_skyline(args.author, args.year)
