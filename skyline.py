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
from tqdm.auto import tqdm


def get_commits_per_day_for_year(year, author=None):
    author_string = f"--author={author}" if author else ""
    git_cmd = f"git log {author_string} --date=short --pretty=format:%ad"
    proc = subprocess.run(
        [x for x in git_cmd.split(" ") if x != ""], capture_output=True
    )
    assert proc.returncode == 0, "Something went wrong with git!"

    commit_dates = []
    for date in tqdm(
        proc.stdout.decode("utf-8").split("\n"), desc="Parsing git history"
    ):
        git_year, git_month, git_day = date.split("-")
        date = datetime.datetime(int(git_year), int(git_month), int(git_day))
        match date.isoweekday():
            case 6:
                date =- datetime.timedelta(days=1)
            # Add Sunday commits to Monday
            case 7:
                date =+ datetime.timedelta(days=1)
            # Week days are treated normally
        commit_dates.append(date)

    dates = []
    for month in tqdm(range(1, 13), desc="Creating calendar"):
        for day in range(1, calendar.monthrange(int(year), month)[1] + 1):
            date = datetime.datetime(int(year), month, day)
            if date.isoweekday() not in [6, 7]:
                dates.append(date)

    commits_per_day = [commit_dates.count(x) for x in dates]

    return commits_per_day


def generate_skyline(year, author, name, repo=None):
    year_contribution_list = get_commits_per_day_for_year(year, author)
    max_contributions_by_day = max(year_contribution_list)

    base_top_width = 17
    base_width = 27.5
    base_height = 10
    max_length_contributionbar = 20
    bar_base_dimension = 2.5
    base_length = (len(year_contribution_list) + 1) * bar_base_dimension / 5 + 17.5
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
        [base_top_offset, base_width - base_top_offset, base_height],
    ]

    base_faces = [
        [0, 1, 2, 3],  # bottom
        [4, 5, 1, 0],  # front
        [7, 6, 5, 4],  # top
        [5, 6, 2, 1],  # right
        [6, 7, 3, 2],  # back
        [7, 4, 0, 3],  # left
    ]

    base_scad = polyhedron(points=base_points, faces=base_faces)

    year_scad = rotate([face_angle, 0, 0])(
        translate(
            [
                base_length - base_length / 5 + 3.5,
                base_height / 2 - base_top_offset / 2 - 1,
                -1.5,
            ]
        )(linear_extrude(height=3)(text(str(year), 6)))
    )

    nick = name if name else author
    user_scad = rotate([face_angle, 0, 0])(
        translate([6, base_height / 2 - base_top_offset / 2, -1.5])(
            linear_extrude(height=3)(text(nick, 6))
        )
    )

    repo_name = repo if repo else ""
    repo_scad = rotate([face_angle, 0, 0])(
        translate(
            [
                (base_length - base_length / 2) - len(repo_name) * 2.5,
                base_height / 2 - base_top_offset / 2 - 1,
                -1.5,
            ]
        )(linear_extrude(height=3)(text(repo_name, 6)))
    )

    bars = None

    week_number = 1
    for i in tqdm(range(len(year_contribution_list)), desc="Generating SCAD skyline"):
        day_number = i % 5
        if day_number == 0:
            week_number += 1
        if year_contribution_list[i] == 0:
            continue

        bar = translate(
            [
                base_top_offset + 2.5 + (week_number - 2) * bar_base_dimension,
                base_top_offset + 2.5 + day_number * bar_base_dimension,
                base_height,
            ]
        )(
            cube(
                [
                    bar_base_dimension,
                    bar_base_dimension,
                    year_contribution_list[i]
                    * max_length_contributionbar
                    / max_contributions_by_day,
                ]
            )
        )

        if bars is None:
            bars = bar
        else:
            bars += bar

    nick = f"{nick}_" if nick else ""
    scad_contributions_filename = f"git_{nick}{year}"
    scad_skyline_object = base_scad + user_scad + repo_scad + year_scad

    if bars is not None:
        scad_skyline_object += bars

    scad_file = f"{scad_contributions_filename}.scad"
    scad_render_to_file(scad_skyline_object, scad_file)

    print("SCAD generated converting to STL")

    stl_file = f"{scad_contributions_filename}.stl"
    try:
        subprocess.run(["openscad", "-o", stl_file, scad_file], capture_output=True)
        os.remove(scad_file)
    except FileNotFoundError as err:
        os.remove(scad_file)
        raise err


def parse_args():
    parser = argparse.ArgumentParser(description="Create git skyline of current repo")
    parser.add_argument("year", help="Which year are we interested int?")
    parser.add_argument("--author", help="Who are we making skyline for?")
    parser.add_argument("--name", help="Nick name instead of author name?")
    parser.add_argument("--repo", help="Name of the repository?")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    generate_skyline(args.year, args.author, args.name, args.repo)
