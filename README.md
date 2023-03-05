
<h1 align="center">
  <br>
  <img src="./KAMP-Assets/Logo/KAMP-Logo.png" width="260"></a>
  <br>
    Klipper Adaptive Meshing & Purging
  <br>
</h1>

<h4 align="center"> Your 3D printer just got a whole lot smarter!</h4>
    <br>
<p align="center">
<img src="./KAMP-Assets/Badges/built-for-klipper-made-with-love.svg" width="400">
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#installation">Installation</a> •
  <a href="#adaptive-meshing">Adaptive Meshing</a> •
  <a href="#adaptive-purging">Adaptive Purging</a> •
  <a href="#troubleshooting">Troubleshooting</a> •
  <a href="#credits">Credits</a>
</p>

<p align="center">
<img src="./KAMP-Assets/Meshing-Assets/adaptive_benchy_glow.gif" width=300>

## Key Features:

* No wasted probe information
  - KAMP will generate a mesh **only** in the area you actually need it: Where you're printing!
  - Since the mesh area will be smaller, the mesh can be much more dense. Imagine making a 3x3 mesh, but the size of a [3DBenchy](https://www.3dbenchy.com)!

* Compatibility
  - If you've got a 3D printer running Klipper and a probe, KAMP is ready to serve you.
  - We've seen users have success with inductive probes, [Klicky](https://github.com/jlas1/Klicky-Probe), [Euclid](https://github.com/nionio6915/Euclid_Probe), BLTouch, and [Voron Tap](https://github.com/VoronDesign/Voron-Tap)
    >**Note:**
    >KAMP  has the option to fuzz mesh points, which helps to spread out wear from nozzle-based probing.
* Straightforward setup
  - One of the main goals of KAMP was to be as easy to implement as possible. Just `[include]` a few files, and you're ready to go!


* No parameter passing
  - KAMP uses information from [[exclude_object]](https://www.klipper3d.org/Exclude_Object.html#exclude-objects) to define mesh bounds. Complicated slicer parameter passing is finally a thing of the past. Welcome to the future!

* [Adaptive Purging](#adaptive-purging) 
  - Allows you to purge right next to the print area. We don't believe in boring purges, we like to sign our work with purge logos! We also have provisions for [more simplistic]() purges as well.

<p align="center">
<img src="./KAMP-Assets/Purging-Assets/voron-purge-example.png" width="375" >
</p>

<p align="center">
    <b>
        Adaptive Voron Logo Purge
    </b>
</p>

## Requirements:

1. You will need `[exclude_object]` defined in `printer.cfg`.

2. You will also need to make sure the following is defined in `moonraker.conf`:
  
    ```yaml
    [file_manager]
    enable_object_processing: True

    ```
3. Finally, you will need to make sure your slicer is labeling objects:

<p align="center">
<img src="./KAMP-Assets/Meshing-Assets/slicer-setting.png" width="500">
</p>

<p align="center">
If you've got all that, you're ready for KAMP!
</p>

## Installation:

The cleanest and easiest way to get started with KAMP is to use Moonraker's Update Manager utility. This will allow you to easily install and helps to provide future updates when more features are rolled out!

1. `ssh` into your Klipper device and execute the following commands:
   ```bash
    cd
    
    git clone https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git
    
    ln -s ~/Klipper-Adaptive-Meshing-Purging/Configuration printer_data/config/KAMP

    cp ~/Klipper-Adaptive-Meshing-Purging/Configuration/KAMP_Settings.cfg ~/printer_data/config/KAMP_Settings.cfg
    ```
    > **Note:**
    > This will change to the home directory, clone the KAMP repo, create a symbolic link of the repo to your printer's config folder, and create a copy of `KAMP_Settings.cfg` in your config directory, ready to edit.

2. Open your `Moonraker.cfg` and add this configuration:
   ```yaml
   [update_manager Klipper-Adaptive-Meshing-Purging]
    type: git_repo
    channel: dev
    path: ~/Klipper-Adaptive-Meshing-Purging
    origin: https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git
    managed_services: klipper
    primary_branch: main
    ```

    > **Note:**
    > Whenever Moonraker configurations are changed, it must be restarted for changes to take effect.

3. Depending on what features you want from KAMP, you'll need to `[include]` some files in your `printer.cfg`.

    UPDATE THIS TO LINK TO CONFIG FILE THAT NEEDS TO BE COPY/PASTED, ADD INCLUDE LINES TO THAT CONFIG

    ```yaml
    # This file contains everything KAMP needs to work, and must be included.
    [include ./KAMP/Base_KAMP.cfg]

    # This file enables the use of adaptive meshing.
    [include ./KAMP/Adaptive_Meshing.cfg]

    # This file enables the use of adaptive purging.
    [include ./KAMP/Adaptive_Purging.cfg]
    ```

    >**Note:**
    The KAMP configuration files are broken up like this to allow those who do not use bed probes to benefit from adaptive purging.

4. After you `[include]` the features you want, restart your firmware and test KAMP with this macro:
    ```yaml
    
    ```

## Adaptive Meshing:
*

## Adaptive Purging:
*

## Troubleshooting:
* 

## Credits:

KAMP was not a one man effort, it was made possible with help from fine folks such as:
- [MapleLeafMakers](https://github.com/MapleLeafMakers) - for assisting in the inception of this project.
- [Julian Schill](https://github.com/julianschill) - A true code warrior and jinja ninja.
- [KageUrufu](https://github.com/kageurufu) - For spearheading object cancellation in Klipper, and helping make this possible.
- [Le0n](https://github.com/leanghoun) - For the fantastic KAMP artwork.
- [Yenda](https://github.com/jtrmal) - For bringing KAMP into the realm of Moonraker's Update Manager.

- [You](https://en.wikipedia.org/wiki/You) - For the continued support and sharing KAMP with your friends. :smiling_face_with_three_hearts:

## You may also like...

- [Ellis' Print-Tuning Guide](https://ellis3dp.com/Print-Tuning-Guide/) - A guide for tuning your 3D printer to *perfection*.
- [Jontek2's Print_Start Guide](https://github.com/amitmerchant1990/correo) - A fantastic `Print_Start` guide for Voron printers.
- [Takuya's Tools](http://tools.takuya.wtf/index.html) A collection of handy tools for any Klipper user.

---



