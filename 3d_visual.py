import argparse
import numpy as np
import pyvista as pv
from pathlib import Path
from tqdm import tqdm
import os

parser = argparse.ArgumentParser()
parser.add_argument('ply_folder', help='folder containing colored pointcloud objects in .ply format')
parser.add_argument('--output', '-o', help='path to output folder', required=True)
parser.add_argument('--radius', '-r', type=float, default=10, help='radius of circular camera path in meters')
parser.add_argument('--distance', '-d', type=float, default=-100, help='camera z distance from origin')
parser.add_argument('--fps', type=int, default=10, help='frames per second')
parser.add_argument('--period', type=int, default=4, help='duration in seconds for a full rotation')
parser.add_argument('--resolution', nargs=2, default=[640,512], type=int, help='output image resolution')
parser.add_argument('--psf', type=float, default=1, help='pointcloud scale factor')
parser.add_argument('--endoscope', help='path to endoscope CAD model')
parser.add_argument('--grid', action='store_true', help='display grid')
parser.add_argument('--display', action='store_true', help='keep render open')

def render_camera_axis(pv_plotter, scale=0.015):
    x = pv.Arrow(direction=(1,0,0), scale=scale)
    y = pv.Arrow(direction=(0,1,0), scale=scale)
    z = pv.Arrow(direction=(0,0,1), scale=scale)
    pv_plotter.add_mesh(x, color='red')
    pv_plotter.add_mesh(y, color='green')
    pv_plotter.add_mesh(z, color='blue')

if __name__ == '__main__':
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    ply_files = sorted([f for f in os.listdir(args.ply_folder) if f.endswith('.ply')])

    # configure plotter
    plotter = pv.Plotter(window_size=args.resolution, off_screen=True)
    plotter.set_background('white')
    if args.grid:
        plotter.show_grid()
    plotter.show_axes()
    render_camera_axis(plotter, 0.015)

    current_angle = 0  # Track the current rotation angle
    frames_per_ply = 2  # Number of frames to generate per PLY file

    for idx, ply_file in enumerate(ply_files):
        ply_path = os.path.join(args.ply_folder, ply_file)
        print(f"Processing {ply_path} ...")

        pt_cloud = pv.read(ply_path)
        pt_cloud.points *= args.psf
        plotter.clear()
        plotter.add_mesh(pt_cloud, point_size=2, rgb=True)

        if args.endoscope is not None:
            try:
                endoscope = pv.read(args.endoscope)
                plotter.add_mesh(endoscope, rgb=True)
            except FileNotFoundError:
                raise

        focus = pt_cloud.center

        for f in range(frames_per_ply):
            angle = current_angle + f * (2 * np.pi / (args.fps * args.period))
            x = args.radius * np.cos(angle)
            y = -args.radius * np.sin(angle)
            plotter.camera.SetPosition(x, y, args.distance)
            plotter.camera.SetViewUp(0, -1, 0)
            plotter.camera.SetFocalPoint(focus)
            plotter.reset_camera_clipping_range()

            plotter.show(interactive_update=(args.display), auto_close=False)
            save_path = os.path.join(args.output, f"{idx:04d}_{f:04d}.png")
            plotter.screenshot(save_path)
        
        # Update the current angle for the next PLY file
        current_angle += frames_per_ply * (2 * np.pi / (args.fps * args.period))

    plotter.close()
    print("All frames saved.")
