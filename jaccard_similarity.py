import numpy as np

import subprocess
import argparse
import binvox_rw
import os
import shutil
import plyfile
import tempfile

def jaccard_similarity(mesh_filepath0, mesh_filepath1, grid_size=40, exact=True):
    
    t0_handle, temp_mesh0_filepath = tempfile.mkstemp(suffix=".ply")
    t1_handle, temp_mesh1_filepath = tempfile.mkstemp(suffix=".ply")
    
    binvox0_filepath = temp_mesh0_filepath.replace(".ply", ".binvox")
    binvox1_filepath = temp_mesh1_filepath.replace(".ply", ".binvox")
    
    shutil.copyfile(mesh_filepath0, temp_mesh0_filepath)
    shutil.copyfile(mesh_filepath1, temp_mesh1_filepath)

    mesh0 = plyfile.PlyData.read(temp_mesh0_filepath)
    mesh1 = plyfile.PlyData.read(temp_mesh1_filepath)
    
    minx = mesh0['vertex']['x'].min()
    miny = mesh0['vertex']['y'].min()
    minz = mesh0['vertex']['z'].min()

    maxx = mesh0['vertex']['x'].max()
    maxy = mesh0['vertex']['y'].max()
    maxz = mesh0['vertex']['z'].max()
    
    #-d: specify voxel grid size (default 256, max 1024)(no max when using -e)
    #-e: exact voxelization (any voxel with part of a triangle gets set)(does not use graphics card)
    #-bb <minx> <miny> <minz> <maxx> <maxy> <maxz>: force a different input model bounding box
    cmd_base = "binvox -pb " 
    if exact:
        cmd_base += "-e "
    
    cmd_base += "-d " + str(grid_size) + " -bb " + str(minx) + " " + str(miny) + " " + str(minz) + " " + str(maxx) + " " + str(maxy) + " " + str(maxz)
    
    mesh0_cmd = cmd_base + " " + temp_mesh0_filepath
    mesh1_cmd = cmd_base + " " + temp_mesh1_filepath

    subprocess.call(mesh0_cmd.split(" "))
    subprocess.call(mesh1_cmd.split(" "))
    
    mesh0_binvox = binvox_rw.read_as_3d_array(open(binvox0_filepath,'r'))
    mesh1_binvox = binvox_rw.read_as_3d_array(open(binvox1_filepath, 'r'))

    intersection = np.logical_and(mesh0_binvox.data, mesh1_binvox.data)
    intersection_count  = np.count_nonzero(intersection)

    union = np.logical_or(mesh0_binvox.data, mesh1_binvox.data)
    union_count  = np.count_nonzero(union)
    jaccard = float(intersection_count) / float(union_count)

    if os.path.exists(temp_mesh0_filepath):
        os.remove(temp_mesh0_filepath)

    if os.path.exists(temp_mesh1_filepath):
        os.remove(temp_mesh1_filepath)

    if os.path.exists(binvox0_filepath):
        os.remove(binvox0_filepath)

    if os.path.exists(binvox1_filepath):
        os.remove(binvox1_filepath)
    
    return jaccard
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute Jaccard between two meshes')
    parser.add_argument('mesh_filepaths', metavar='N', type=str, nargs='+',
                    help='meshes to compare')

    parser.add_argument('--grid_size', metavar='d', type=int, default=40,
                    help='grid size along single dimention')
    parser.add_argument('--exact', metavar='e', type=bool, default=True,
                    help='exact voxelization is only voxels that intersect surface')

    args = parser.parse_args()

    mesh_files = args.mesh_filepaths
    grid_size = args.grid_size
    exact = args.exact
    if len(mesh_files) != 2:
        print "wrong number of mesh files: wanted 2, got: " + str(len(mesh_files)) 
        
    print jaccard_similarity(mesh_files[0], mesh_files[1], grid_size, exact)
