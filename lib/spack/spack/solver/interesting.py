#!/usr/bin/env python3
import subprocess
import sys
import os

# Define the error strings we expect to find on a single line.
# The order in the output line is arbitrary, so we check for the presence of each string independently.
expected_errors = [
    'error(100,"Package \'{0}\' needs to provide both \'{1}\' and \'{2}\' together, but provides only \'{1}\'","msvc","cxx","fortran")',
    'error(100,"Package \'{0}\' needs to provide both \'{1}\' and \'{2}\' together, but provides only \'{1}\'","msvc","c","fortran")',
    # Add the 3rd error string here if needed, e.g.:
    # 'error(100,"Package \'{0}\' needs to provide both \'{1}\' and \'{2}\' together, but provides only \'{1}\'","msvc","fortran","c")'
]

solver_path = "/Users/harmenstoppels/spack/lib/spack/spack/solver"
lp_files = [
    os.path.join(solver_path, "concretize.lp"),
    os.path.join(solver_path, "heuristic.lp"),
    os.path.join(solver_path, "display.lp"),
    os.path.join(solver_path, "direct_dependency.lp"),
    os.path.join(solver_path, "os_compatibility.lp"),
    "vtk.lp" # Assuming vtk.lp is in the current working directory
]

cmd = [
    "clingo",
    "--verbose=3",
    "--stats=2",
    "--configuration=tweety",
    "--opt-strategy=usc",
    "--heuristic=Domain",
    "--quiet=1,0,0"
] + lp_files

print(f"Running: {' '.join(cmd)}")

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

found = False
for line in process.stdout:
    line = line.strip()
    # Split the line by "] space" assuming the clingo output format for atoms
    # Or more simply, split by " error(" if that is reliable, but usually clingo outputs atoms separated by spaces.
    # However, since error() terms match balanced parens, splitting by space might break arguments containing spaces.
    # A safer approach is to check if the count of "error(" matches the expected count 
    # and all expected errors are present.

    # Count how many errors are on this line
    error_count = line.count("error(")
    
    if error_count == len(expected_errors) and all(err in line for err in expected_errors):
        print(f"MATCH FOUND:\n{line}")
        found = True
        break 

process.wait()

if not found:
    print("No line matched all expected errors.")
    sys.exit(1)
