![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

# AetherSign Studio 🛠️🖨️

**AetherSign Studio** is a parametric Python desktop application built with Tkinter and Pillow to generate multi-color 3D printable Guest Wi-Fi plaques (`.3mf`) and angled desk stands (`.3mf`) optimized for Bambu Lab multi-color printers (AMS / AMS Lite).

---

## 🌟 Key Features

* **Live 2D Top-Down Scan Test:** Instantly test-scan your Wi-Fi credentials with your smartphone camera directly off your monitor before wasting filament.
* **Interactive 3D Orbit Viewport:** Inspect sign thickness, curved corners, sign tilt angles, and custom widths from all 360° angles right inside the app.
* **3-Tier Multi-Color 3MF Export:** Automatically configures Bambu Studio paint colors and material color groups (`.3mf`) for a clean dual-color print (e.g., Black body, White center pad and text, Black QR code) requiring only 2 filament swaps total.
* **Parametric Customization Engine:**
  * **Sign Sizes:** Compact (65mm), Standard (80mm), or Display (100mm).
  * **Corner Radius Slider:** Adjust corner roundness smoothly from sharp square corners ($0\text{ mm}$) to fully curved ($12\text{ mm}$).
  * **Plaque Thickness:** Choose between Lightweight ($1.4\text{ mm}$), Standard ($2.0\text{ mm}$), or Rigid ($2.8\text{ mm}$).
  * **Stand Styles:** Minimalist (with aesthetic side wings) or Full Width (flush block finish).
  * **Stand Tilt Angles:** Switch between 55° (low tables), 65° (standard countertops), or 75° (high shelves/bars).
  * **Header Glyphs:** Choose between Wi-Fi broadcast waves, a Home icon, a Coffee cup, or none.
  * **Print Styles:** Traditional Raised Relief or Flush PEI Bed Inlay.
* **Zero Bloat & In-Memory State:** Runs locally with zero unnecessary configuration files left on your PC.

---

## 📦 Requirements

Make sure you have Python installed along with the required libraries:

```bash
pip install segno Pillow
