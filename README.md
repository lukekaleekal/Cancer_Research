# Cancer Research — Neuron Animations

Four educational neuron simulations for a science fair project, provided as standalone HTML and Python code.

## Browser animations

Download an HTML file from [animations](animations) and open it in a modern browser:

- [Izhikevich neuron and firing presets](animations/izhikevich-neuron.html)
- [Rebound spike](animations/rebound-spike.html)
- [Threshold variability](animations/threshold-variability.html)
- [Depolarizing after-potential (DAP)](animations/depolarizing-after-potential.html)

All four calculate voltage numerically. The browser DAP now uses the published numerical example instead of a schematic.

## Python

See [Python instructions](python/README.md) for installation, animation controls, physical current input, capacitance overrides, plots and GIF export.

## Stimulation and interpretation

[STIMULATION.md](STIMULATION.md) contains the equations, parameters, time steps, pulse amplitudes and intervals, current conversion, and primary sources.

Current is displayed in nanoamperes using representative literature capacitances: 31 pF for the general regular-spiking example, 147 pF for rebound, and 155 pF for threshold variability and DAP. These are illustrative equivalent current scales; the generic model parameters are not fitted to the recorded cells. Other firing presets retain a reference scale, not a measured capacitance for each phenotype. DAP reproduces a step-sensitive 0.1 ms numerical method.

These are educational demonstrations, not experimental cancer treatment results.

[Biological explanations](NEUROSCIENCE.md) cover the main channels, human-relevant locations, functions, evidence limits, time steps and spike cutoff. The same notes are available in Python through `--explain-all`.
