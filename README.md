<!-- KAMP Logo/Banner -->

<p align=center>
    <img src="./Photos/KAMP-Assets/Logo/KAMP-for-dark-BG.png" width=500px>
</p>

<p align=center>
    <b>
        Welcome to Klipper Adaptive Meshing and Purging, or KAMP!
    </b>
<br>
</br>
</p>

---

<!-- Table of Contents -->

<br>
</br>
<b>
    Table of Contents:
</b>

- [Adaptive Meshing](#adaptive-meshing)
  - [Introduction](#introduction)
    - [What is it?](#what-is-it)
    - [Why do I want this?](#why-do-i-want-this)
    - [How does it work?](#how-does-it-work)
  - [Setup](#setup)
    - [I have a dockable probe like Klicky or Euclid:](#i-have-a-dockable-probe-like-klicky-or-euclid)
    - [I've configured my probe already, or my probe is integrated:](#ive-configured-my-probe-already-or-my-probe-is-integrated)
    - [I prefer using Moonraker's update manager:](#i-prefer-using-moonrakers-update-manager)
  - [Troubleshooting](#troubleshooting)
- [Adaptive Purging](#adaptive-purging)
  - [Introduction](#introduction-1)
  - [Setup - Adaptive Purging](#setup---adaptive-purging)
  - [Troubleshooting - Adaptive Purging](#troubleshooting---adaptive-purging)
- [Special Thanks](#special-thanks)

<br>

<!-- Adaptive Meshing Section -->

# Adaptive Meshing

<br>

## Introduction

<br>

### What is it?

``KAMP`` is a project that was created to simplify the usage of adaptive meshing on Klipper-based 3D printers. Adaptive meshing is the practice of using values from a gcode file to define a mesh's dimensions. This gives you the benefits of using a bed mesh, but only *specifically* where it is needed, without passing a bunch of variables around. ``KAMP`` was designed with simplicity in mind!

<br>

### Why do I want this?

The use of bed meshes is considered [cheap insurance](https://github.com/AndrewEllis93/Print-Tuning-Guide/blob/main/articles/troubleshooting/first_layer_squish_consistency.md#first-layer-consistency) by the great [Andrew Ellis](https://github.com/AndrewEllis93) in his very popular [Print Tuning Guide](https://github.com/AndrewEllis93/Print-Tuning-Guide). While I completely agree, I also believe in efficiency. Building a bed mesh can take a bit of time, and what's worse, a lot of it will be wasted because the mesh is not the same size as the build area *being used*, until now! Adaptive meshing will not only waste much less time and effort building bed meshes, it will make your meshes more **effective** by building a richer bed mesh tailored to the area you are *actually* using when you print. Imagine the *perfection* your first layer can become because almost no information is wasted in your bed mesh!

<br>

### How does it work?

Thanks to the great work from [kageurufu](https://github.com/kageurufu) on `[exclude_object]` in the Klipper firmware, we are able to easily work out a bed mesh's `min` and `max` values by pulling out a sliced object's size and clamp that size to a bed mesh. Imagine making a bed mesh, but the size of a Benchy! Multiple objects in gcode are parsed the same way, so the mesh density can adapt to any number of objects, as long as they fit on your buildplate. We can also use these values for localized [purge lines](./Configuration/Adaptive_Purge.cfg), purging near the print. No more long romantic walks from the corner of the buildplate to the first extruded line!

<br>

<details>
    <summary>
        <b>
        What does an adaptive mesh look like?   
        </b>
    </summary>
<p>
</p>

Well, for clarity, let's look at a normal 7x7 mesh:
    
<img src="./Photos/KAMP-Assets/Meshing-Assets/7x7-richness.png" width="25%">

This is a normal 7x7 mesh. If I were printing just a couple small objects, or one large object, or a plate full of parts, this is what a machine will **normally** make.

Now, here's what an adaptive mesh looks like:
    
<img src="./Photos/KAMP-Assets/Meshing-Assets/3x3-richness.png" width="25%">

This is an adaptive mesh for a small object near the origin of the bed. Despite the fact that the object is only 20mm^2^, a 3x3 mesh was still created, making this mesh **extremely** dense, which will result in an even better first layer.

<img src="./Photos/KAMP-Assets/Meshing-Assets/7x4-richness.png" width="25%">

This is an adaptive mesh for a skinny and long object at the back of the bed, 200mm x 10mm in size. While the object is rather small, ``KAMP`` made a mesh that is 7x4, almost *exactly* the size of the object, and **packed** with information.

</details>

<br>

<details>
    <summary>
        <b>
        ⚠️ A note on the usage of a Relative Reference Index:   
        </b>
    </summary>
<p>
</p>

Relative Reference Index is a method used in the Klipper firmware to calculate mesh points for printers that have a probe, as well as a physical Z endstop, like the ones commonly found on Voron printers. Normally, when using Relative Reference Index, the mesh point closest to the Z endstop or the center of the bed is defined, and that point becomes `Z0.0` in the mesh, and all other points are scaled in Z from that point. This is normally fine when the mesh can't move around, as that point will remain consistent. We've gotten ``KAMP`` to change that value depending on the size of the mesh that is adaptively generated, but current Klipper limitations do not allow us to use that value and home the Z axis to it, setting that point in the mesh to `Z0.0`. What this means for Relative Reference Index users, typically, is your mesh may *appear* strange, but should work as intended. If you've got a creative solution that works, feel free to submit a Pull Request and contribute to the project!
- If you absolutely must have a perfect implementation of [Relative Reference Index](https://www.klipper3d.org/Bed_Mesh.html?h=relative#the-relative-reference-index), a workaround can be used by combining `KAMP` with [Automatic Z Calibration](https://github.com/protoloft/klipper_z_calibration). Alternatively, you can [home the Z axis with your probe](https://docs.vorondesign.com/community/howto/Takuya/Klicky_Probe_AutoZ_Alternative.html) and remove Relative Reference Index from your config altogether. 

</details>

<br> 

## Setup

<br>

### I have a dockable probe like [Klicky](https://github.com/jlas1/Klicky-Probe) or [Euclid](https://github.com/nionio6915/Euclid_Probe):

<details>
    <summary>
        <b>
        Expand this section:
        </b>
    </summary>
<p>
</p>

- If you are using a `BED_MESH_CALIBRATE` macro override *for probe attachment routines*, you must `#comment` it out or ~~remove it.~~ Don't worry, we thought ahead and made it easy to define macros that attach and remove a probe, like for [Klicky](https://github.com/jlas1/Klicky-Probe), [Euclid](https://github.com/nionio6915/Euclid_Probe), and other dockable probes.

    >
    >klicky-probe.cfg
    >>
    >>Simply add a `#` before the [include ./klicky-bed-mesh-calibrate.cfg] to disable it.
    >>
    >>```jinja
    >>
    >>...
    >>#[include ./klicky-bed-mesh-calibrate.cfg]
    >>...
    >>```

- And update the variables in Adaptive_Mesh.cfg:

    >>```jinja
    >>variable_probe_dock_enable: True       # Normally False, enable with True if you have a dockable probe.
    >>variable_attach_macro: 'Attach_Probe'  # The macro you use to attach the dockable probe.
    >>variable_detach_macro: 'Dock_Probe'    # The macro you use to dock the dockable probe.
    >>...
    >>```

- Once you have these done, move to the [next section](#ive-configured-my-probe-already-or-my-probe-is-integrated).

</details>
<br>


### I've configured my probe already, or my probe is integrated:

<details>
    <summary>
        <b>
        Expand this section:
        </b>
    </summary>
<p>
</p>

- You must have a version of the Klipper firmware that supports [Object Exclusion](https://www.klipper3d.org/Exclude_Object.html?h=exclude#exclude-objects), and have `[exclude_object]` defined in your `printer.cfg` file. [^1]
  
    >Printer.cfg
    >>```jinja
    >>[exclude_object]
    >>...
    >>```

- Once you have `exclude_object` defined in your `printer.cfg` file, make sure you have `enable_object_processing: True` under `[file_manager]` in your `moonraker.conf` file. This will allow Klipper to process incoming gcode files for objects. [^1]
  
    >Moonraker.conf
    >>```jinja
    >>[file_manager]
    >>enable_object_processing: True
    >>...
    >>```


- You must have object labeling enabled in your slicer. (Usually in slicer output options.)

<p align=center>
    <img src="./Photos/KAMP-Assets/Meshing-Assets/slicer-setting.png">
</p>

</details>
<br>

### I prefer using Moonraker's update manager:


<details>
    <summary>
        <b>
        Expand this section:
        </b>
    </summary>
<p>
</p>

1. hello
2. yes
3. this is dog

</details>
<br>

## Troubleshooting

<br>

<details>
    <summary>
        <b>
        0 object points / bed mesh not adapting:
        </b>
    </summary>
<p>
</p>

- This error is caused by `BED_MESH_CALIBRATE` or `PRINT_START` being called in your gcode file **before** `EXCLUDE_OBJECT_DEFINE` is. This is something you slicer may be doing. Currently, `exclude_object` injects the object definition code after the first line of gcode it sees. This is being worked on and will be fixed as soon as the PR is merged into Moonraker.

Solution:

- In the mean time, you can add a gcode command in your slicer's start gcode section before `PRINT_START` is called and that will fix the issue. `M117` is a good one to use, it'll just clear the display's current message. 

<p align=center>
    <img src="./Photos/KAMP-Assets/Meshing-Assets/0-points-fix.png" width="50%">
</p>
    <p align=center>
        Here, M117 has been added to the Slicer's Start gcode. 
    </p>

</details> 

<br>

<!-- Adaptive Purging Section -->

# Adaptive Purging

<br>

## Introduction

<br>

## Setup - Adaptive Purging
<br>

## Troubleshooting - Adaptive Purging

<br>

<!-- Special Thanks -->

# Special Thanks

<br>

[^1]: After making any changes to critical Klipper or Moonraker functions, be sure to use `FIRMWARE_RESTART`, as well as restart your Moonraker instance so those changes take effect.
[^2]: Mesh point fuzzing allows the user to fuzz mesh points to spread out possible polishing marks and wear from nozzle-based probes, like load cells or Voron Tap.
