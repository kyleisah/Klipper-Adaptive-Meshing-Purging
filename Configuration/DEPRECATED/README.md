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

<!-- Moonraker Setup  -->

### I prefer using Moonraker's update manager:


<details>
    <summary>
        <b>
        Expand this section:
        </b>
    </summary>
<p>
</p>

# Moonraker Update Manager Setup

The purpose of this setup is to enable updating KAMP by using Moonraker's plugin manager.
This comes at cost of higher complexity of setup, **and** the need to edit an already existing `PRINT_START` Macro.

To begin, `ssh` into your device running klipper and use the following commands:

```bash
cd
git clone https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git
ln -s ~/Klipper-Adaptive-Meshing-Purging/Configuration printer_data/config/KAMP
```

Then, add the following snippet into your `printer.cfg` file: [^1]
```jinja
[include KAMP/*cfg]
```
Alternatively, you can choose which files you wish to include (useful for those who **only** want adaptive purging) by using the following: [^1]
```jinja
[include KAMP/Adaptive_Mesh.cfg]
[include KAMP/Voron_Purge.cfg]
[include KAMP/Line_Purge.cfg]
```

Lastly, add the following snippet to your `moonraker.conf` file: [^1]

```jinja
[update_manager Klipper-Adaptive-Meshing-Purging]
type: git_repo
channel: dev
path: ~/Klipper-Adaptive-Meshing-Purging
origin: https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git
managed_services: klipper
primary_branch: main
```

This should be all that needs to be done for enabling updates via Moonraker's Update Manager! Be sure to restart your firmware and moonraker instance, or reboot your Pi for all changes to take effect. [^1]

⚠️ Please pay special attention to the following, as this is a critical step:

Before using any macros from KAMP when using the moonraker managed method, you have to **SET** the parameters for the macros before they are called, or they will only use the default parameters. You should only have to change your `PRINT_START` once or twice until you have the parameters set how you like them, then you can leave them alone. There is an example provided at the bottom of this section to show you how you can do this.

> For setting up adaptive meshing, you need to call the macro:
>> ```jinja
>> SETUP_KAMP_MESHING [parameters]
>> ```
> For adaptive purging (Voron-logo):
>> ```jinja
>> SETUP_VORON_PURGE [parameters]
>> ```
> For an adaptive purging in a form of a simple line:
>> ```jinja
>> SETUP_LINE_PURGE [parameters]
>> ```

Be sure the calls for `BED_MESH_CALIBRATE` and/or `VORON_PURGE`/`LINE_PURGE` are also included in your `PRINT_START` and are called **AFTER** calling these setup macros.

As for the parameters, you can inspect the individual config files and the macros. You can also add the parameter `DISPLAY_PARAMETERS=1` to either of the SETUP calls and it will print current values (useful for debugging) when calling the actual macros.
After modifying the `PRINT_START` macro, do not forget to restart klipper again. [^1]

Example `PRINT_START`:
```
[gcode_macro PRINT_START]
gcode:
    .
    .
    SETUP_KAMP_MESHING DISPLAY_PARAMETERS=1 LED_ENABLE=1 FUZZ_ENABLE=1
    SETUP_VORON_PURGE DISPLAY_PARAMETERS=1 ADAPTIVE_ENABLE=1
    .
    .
    BED_MESH_CLEAR
    BED_MESH_CALIBRATE
    .
    .
    VORON_PURGE
```

As you can see, `SETUP_KAMP_MESHING` is setting `LED_ENABLE` and `FUZZ_ENABLE` *before* `BED_MESH_CALIBRATE` is called. The same has also been done using `SETUP_VORON_PURGE`. 

<br>

**It is important that the `SETUP` macros are being called *before* the actual macro, otherwise default values are used.**

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

- This error is caused by klipper not seeing any object definitions, or `EXCLUDE_OBJECT_DEFINE` is happening *after* `PRINT_START` or `BED_MESH_CALIBRATE` is being called. This is something you slicer may be doing. Currently, `exclude_object` injects the object definition code after the first line of gcode it sees. This is being worked on and will be fixed as soon as the PR is merged into Moonraker.

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

## Introduction
Adaptive Purging takes the same secret sauce of Adaptive Meshing, and uses it for a pre-print prime line or purge. So instead of the purge line always being in the same spot of your print bed, the purge will actually be near your print! Some folks find this useful as they can lower the count of lines in their print skirt, or remove it altogether!
<br>

## Setup - Adaptive Purging
<br>

All you need to do is `[include]` the config file for the purge you want in your `printer.cfg`, and adjust a few variables for your needs, and that's it!

<br>

<details>
    <summary>
        <b>
        Voron Logo Purge:
        </b>
    </summary>
<p>

- The values you can adjust are fairly straightforward. If the voron logo's first line is half-extruded, you will need to adjust the `variable_tip_distance` value. Here is a visual aid of what `variable_tip_distance` is related to:

</p>

<p align=center>
    <img src="./Photos/KAMP-Assets/Purging-Assets/tip-distance.png" width="50%">
</p>
    <p align=center>
        Tip distance is the distance from the tip of the filament to the opening of the nozzle. This value will need some adjusting to get the logo to come out clean and perfect. 
    </p>
<br>

- Any other variables in `Voron_Purge.cfg` will relate to flow rate, position, size, or amount of filament purged. These settings are easily tweaked to get it just right. Ideally, the purged lines should be touching so the purge can be removed easily when the print is finished. Here's an example of a proper Voron Purge:
  
</p>

<p align=center>
    <img src="./Photos/KAMP-Assets/Purging-Assets/voron-purge-example.png" width="50%">
</p>
    <p align=center>
        As you can see, the purge lines are touching eachother for easy removal, a small amount was purged to prime the nozzle, and the logo came out nicely.
    </p>

</details> 
<br>

<details>
    <summary>
        <b>
        Line Purge:
        </b>
    </summary>
<p>

- Just like the voron logo purge, the variables to adjust to get this right are pretty straight forward. The default values should work for most folks, but adjusting `flow_rate`, `line_length`, and `purge_amount` will help you get it just right.

</p>
</details> 
<br>

<!-- Special Thanks -->

# Special Thanks
- [MapleLeafMakers](https://github.com/MapleLeafMakers) - for assisting in the inception of the project.
- [Julian Schill](https://github.com/julianschill) - A true code warrior and jinja ninja.
- [KageUrufu](https://github.com/kageurufu) - For spearheading object cancellation in Klipper, and helping make this possible.
- [Le0n](https://github.com/leanghoun) - For the awesome logo work and continuous support for the project.
- [Yenda](https://github.com/jtrmal) - For bringing KAMP into the realm of Moonraker's Update Manager.
- The Voron Helpers and Voron Contributors team, a group I feel are my close friends.
<br>

[^1]: After making any changes to critical Klipper or Moonraker functions, be sure to use `FIRMWARE_RESTART`, as well as restart your Moonraker instance so those changes take effect.

[^2]: Mesh point fuzzing allows the user to fuzz mesh points to spread out possible polishing marks and wear from nozzle-based probes, like load cells or Voron Tap.
