# 🎶 Tonnetz Pattern Generator 🎶

An interactive Python-based musical grid visualizer and synthesizer using **Tkinter** and **sounddevice**.  
Inspired by the **Tonnetz** — a musical space representing harmonic relationships — this app lets you explore musical patterns, generate algorithmic sequences, and play notes live via mouse interaction.

---

## 📸 Preview  

> 🖱️ **Click and drag** over the circles to play notes.  
> 🎛️ Use **"Generate Pattern"** button to hear algorithmic patterns play across the grid.

---

## 🎹 Features  

- **Tonnetz-style grid layout** of musical notes (C, C#, D, ... B).
- Interactive **mouse click and drag** note triggering.
- Multiple **algorithmic pattern generators**:
  - 🎲 **Eulerian random path**
  - 🌿 **Perlin noise pattern**
  - 🔁 **Lissajous figure pattern**
  - 🔢 **Fibonacci sequence path**
  - 📑 **Predefined grid patterns**
- Real-time **sine wave synthesis** using `sounddevice`.
- **Aesthetic color effects** when notes play.
- Clean **Tkinter canvas interface** with dynamic note labels and connecting lines representing harmonic relations.

---

## 🛠️ Requirements  

Install dependencies via pip:

```bash
pip install numpy sounddevice noise
