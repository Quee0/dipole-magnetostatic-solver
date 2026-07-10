# Dipole Magnetostatic Solver

<p align="left">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/numpy-2.4.6-013243?logo=numpy&logoColor=white" alt="Numpy">
  <img src="https://img.shields.io/badge/-Matplotlib-000000?style=flat&logo=python" alt="Matplotlib">
  <img src="https://img.shields.io/badge/customtkinter-6.0.0-2CC985" alt="Customtkinter">
</p>

<p align="center">
  <img src="img\Readme_plot_1.png" width="350" alt="Alt text">
  <img src="img\Readme_plot_2.png" width="350" alt="Alt text">
</p>
<p align="center">
  <img src="img\Readme_plot_3.png" width="350" alt="Alt text">
  <img src="img\Readme_plot_4.png" width="350" alt="Alt text">
</p>
 
---

## 1. Project overview
### 1.1 General Description

An interactive tool for **visualizing and building intuition about magnetic fields in space**, it was mainly designed for me to be an assistance for building an electric motor (or anyone who wants to see how permanent-magnet arrangements shape a magnetic field before committing to a real design). Also this project let further polish an intuition for electromagnetism.
 
It works based on superpositon rule. Computes and plots the field produced by an array of magnetic dipoles in free space, and lets you interactively tweak geometry, magnetization (remanecense), and probe the field with your mouse.
 
> This is a **support for personal project and serves as an educational aid**, not a production electromagnetic design tool.


## 1.2 Features

This tool lets you:
* **Two magnet generation modes**: a magnetized volume and a single independent dipole 
* Optional **polar layout** with evenly spaced magnets around a ring, with an option to alternate polarity
* Live **3D vector field plot (quiver)** plus a **2D streamplot** slice at an adjustable Z-level
* Click anywhere on the 2D plot to **probe the field magnitude** at that point
* Get a rough estimate of **magnetic flux** through a chosen rectangular surface
* All physical and visual parameters adjustable through sliders/entries, no code editing required

# 2. Solver

Whole solver is build around the idea of superposition principle. It sums influences on magnetic field from every dipole. Every magnet (or magnetized volume element) is treated as an ideal **point magnetic dipole**. 

## 2.1 Field of dipole
The field of a single dipole with moment $\vec{m}$ at a field point displaced by $\vec{r}$ from the dipole is:

$$\vec{B}(\vec{r}) = \frac{\mu_0}{4\pi r^3}\left(\frac{3(\vec{m}\cdot\vec{r})\,\vec{r}}{r^2} - \vec{m}\right)$$

Using versor notation we can change initial equation:

$$\vec{B}(\vec{r}) = \frac{\mu_0}{4\pi}\,\frac{1}{r^3}\left[3(\vec{m}\cdot\hat{r})\,\hat{r} - \vec{m}\right]$$

$$\hat{r} = \frac{\vec{r}}{r} =\left(\frac{r_x}{\sqrt{r_x^2+r_y^2+r_z^2}},\;\frac{r_y}{\sqrt{r_x^2+r_y^2+r_z^2}},\;\frac{r_z}{\sqrt{r_x^2+r_y^2+r_z^2}}\right)$$

<br>Using principles of vector algebra we can derive components $B_x$, $B_y$, $B_z$. We substitute $\hat r$ and write out $\vec m\cdot\hat r$:

$$\vec{B}(\vec{r}) = \frac{\mu_0}{4\pi}\,\frac{1}{(r_x^2+r_y^2+r_z^2)^{3/2}}\Bigg[3\left(\frac{m_x r_x}{r}+\frac{m_y r_y}{r}+\frac{m_z r_z}{r}\right)$$

$$\cdot\left(\frac{r_x}{r}\hat{\imath}+\frac{r_y}{r}\hat{\jmath}+\frac{r_z}{r}\hat{k}\right)$$

$$- \left(m_x\hat{\imath}+m_y\hat{\jmath}+m_z\hat{k}\right)\Bigg]$$

$$\vec{B}(\vec{r}) = \frac{\mu_0}{4\pi}\,\frac{1}{r^3}\Bigg[\frac{3m_x r_x}{r}\cdot\frac{r_x}{r}\hat{\imath}+ \frac{3m_x r_x}{r}\cdot\frac{r_y}{r}\hat{\jmath}+ \frac{3m_x r_x}{r}\cdot\frac{r_z}{r}\hat{k}$$

$$+ \frac{3m_y r_y}{r}\cdot\frac{r_x}{r}\hat{\imath}+ \frac{3m_y r_y}{r}\cdot\frac{r_y}{r}\hat{\jmath}+ \frac{3m_y r_y}{r}\cdot\frac{r_z}{r}\hat{k}$$

$$+ \frac{3m_z r_z}{r}\cdot\frac{r_x}{r}\hat{\imath}+ \frac{3m_z r_z}{r}\cdot\frac{r_y}{r}\hat{\jmath}+ \frac{3m_z r_z}{r}\cdot\frac{r_z}{r}\hat{k}\Bigg]$$

$$- \, m_x\hat{\imath} - m_y\hat{\jmath} - m_z\hat{k}$$

And after grouping values with versors:

$$B_x = \frac{\mu_0}{4\pi}\,\frac{1}{r^3}\left(\frac{3m_x r_x^2}{r^2} + \frac{3m_y r_x r_y}{r^2} + \frac{3m_z r_z r_x}{r^2} - m_x\right)$$

$$B_y = \frac{\mu_0}{4\pi}\,\frac{1}{r^3}\left(\frac{3m_x r_x r_y}{r^2} + \frac{3m_y r_y^2}{r^2} + \frac{3m_z r_z r_y}{r^2} - m_y\right)$$

$$B_z = \frac{\mu_0}{4\pi}\,\frac{1}{r^3}\left(\frac{3m_x r_x r_z}{r^2} + \frac{3m_y r_y r_z}{r^2} + \frac{3m_z r_z^2}{r^2} - m_z\right)$$

where ( $\vec{r_1}$ is point in space, $\vec{r_2}$ is position of dipole):

$$\vec{r} = \begin{bmatrix} r_x \cr r_y \cr r_z \end{bmatrix} = \vec{r}_1 - \vec{r}_2 = \begin{bmatrix} r_{1x} - r_{2x} \cr r_{1y} - r_{2y} \cr r_{1z} - r_{2z} \end{bmatrix}, \qquad r = \sqrt{r_x^2+r_y^2+r_z^2}$$

The total field at any point is the **vector sum (superposition)** of the contributions from every dipole in `m_arr`.

## 2.2 Magnetized matter

For the **Magnetized Volume** mode, a solid magnetized block is approximated by discretization it into a grid of small volume elements, each becomes one dipole with moment

$$m = M \cdot dV, \qquad M = \frac{B_r}{\mu_0}$$

Where $B_r$ is the remanence of certain magnet and $dV$ is the volume of one subdivided cell. Increasing the "Volumetric m's resolution" slider subdivides the block more finely, trading accuracy for computation time.

## 3. User guide

### 3.1 Installation

If you want to use source code, beside cloning the repository, you need to download used packages. Use the third command and `requirements.txt` file. Run the script with `main.py`.
 
```
git clone https://github.com/Quee0/dipole-magnetostatic-solver.git
cd dipole-magnetostatic-solver
pip install -r requirements.txt
```

### 3.2 Graphical interface

#### Magnetized Volume mode
  
| Parameter | Meaning |
|---|---|
| Remanence [T] | Remanent flux density $B_r$ of the magnet material |
| Size x/y/z [m] | Dimensions of the magnetized block |
| Volumetric m's resolution | How many dipoles per axis to subdivide the block into (higher = more accurate, slower) |
| Magnetization axis | Which axis (x/y/z) the block is magnetized along |
 
Enable **"Use polar coordinate system"** to instead arrange copies of this magnetized block evenly around a circle of a given radius and count. It was useful for quickly sketching a ring of rotor/stator magnets. **"Swap polarity mid sweep"** flips the magnetization direction for the second half of the ring, which is handy for alternating-pole layouts.
 
#### Independent Dipole mode
 
Places a single ideal dipole at the origin with a magnetic moment you specify directly (in $A\cdot m^2$ ), along a chosen axis. Useful for exploring the base field pattern in isolation. There is also a built-in polar preset that reproduces a small ring of alternating dipoles, it is a residue of earlier development stages.
 
#### Probing the field
 
Click anywhere inside the 2D streamplot to read `|B|` at that point (in Tesla) along with its coordinates. It handy for quickly comparing field strength.
 
#### Flux calculation
 
Set the size and position (along the y-axis) of a flat rectangular window, and the sidebar will report the estimated magnetic flux $\Phi$ (in Weber) through it, computed by summing $B_y$ over the nearest grid points inside that window. This is a coarse, grid based estimate. Refine the field density and flux resolution sliders for a more accurate number.

### 3.3 Limitations

This is a simplified model, and the author is aware of its main limitation:
 
* **No ferromagnetic materials** - The solver only handles ideal point dipoles superposed in free space (vacuum permeability everywhere). It does **not** model soft-magnetic material such as a steel rotor/stator core.  Motor designs rely heavily on ferromagnetic cores to shape and strengthen flux. At this point this script will give unrealistic calculations.
* **Flux and probe readings are limited** by the chosen grid resolution (nearest-neighbor lookup, not true interpolation/integration).

## 4. License
