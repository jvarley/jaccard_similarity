import numpy as np

import subprocess
import argparse
import binvox_rw
import os
import shutil
import plyfile

def jaccard_similarity(mesh_filepath0, mesh_filepath1):
    
    temp_mesh0_filepath = "/tmp/mesh0.ply"
    temp_mesh1_filepath = "/tmp/mesh1.ply"
    
    binvox0_filepath = temp_mesh0_filepath.replace(".ply", ".binvox")
    binvox1_filepath = temp_mesh1_filepath.replace(".ply", ".binvox")
    
    if os.path.exists(temp_mesh0_filepath):
        os.remove(temp_mesh0_filepath)

    if os.path.exists(temp_mesh1_filepath):
        os.remove(temp_mesh1_filepath)

    if os.path.exists(binvox0_filepath):
        os.remove(temp_mesh0_filepath)

    if os.path.exists(binvox1_filepath):
        os.remove(temp_mesh1_filepath)
    
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
    cmd_base = "binvox -e -d 40 -bb " + str(minx) + " " + str(miny) + " " + str(minz) + " " + str(maxx) + " " + str(maxy) + " " + str(maxz)
    
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
    
    #print intersection_count 
    #print union_count
    return float(intersection_count) / float(union_count)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute Jaccard between two meshes')
    parser.add_argument('mesh_filepaths', metavar='N', type=str, nargs='+',
                    help='meshes to compare')
    args = parser.parse_args()


    mesh_files = args.mesh_filepaths
    if len(mesh_files) != 2:
        print "wrong number of mesh files: wanted 2, got: " + str(len(mesh_files)) 
        
    print compute_jaccard(*mesh_files)
