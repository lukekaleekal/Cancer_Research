# Python neuron simulations

Requires Python 3.10+ and a desktop Matplotlib backend for interactive windows.

```sh
python -m pip install -r requirements.txt
python neuron_animations.py --mode izhikevich
python neuron_animations.py --mode rebound
python neuron_animations.py --mode threshold
python neuron_animations.py --mode dap
```

Use Play/Pause and Replay. All four modes calculate voltage numerically. Input current is displayed in nA (1 nA = 1e-9 A), using representative literature capacitances. See [equations, stimulation protocols and sources](../STIMULATION.md) for assumptions and exact pulse times.

The general mode defaults to regular spiking, C=31 pF and a +0.310 nA step starting at 50 ms. Set its applied current explicitly with:

```sh
python neuron_animations.py --mode izhikevich --current-na 0.310
python neuron_animations.py --mode izhikevich --pattern bursting --current-na 0.372
```

The optional `--capacitance-pf` overrides the representative capacitance. Without `--current-na`, this changes the physical current scale while keeping the normalized protocol unchanged. When switching firing presets, the reference capacitance is not a measurement for that new phenotype. The legacy `--current` option accepts a normalized 0–30 input for the general mode; `--current-na` overrides it.

Export a plot or GIF (also works headlessly):

```sh
MPLBACKEND=Agg python neuron_animations.py --mode dap --plot dap.png
MPLBACKEND=Agg python neuron_animations.py --mode dap --save dap.gif
```

Regular/rebound/threshold use 0.01 ms forward Euler; DAP uses the author's 0.1 ms sequential update, which is step-sensitive. These are illustrative dimensional scalings, not fitted recordings or experimental stimulus recommendations.

## Biology, stimulation and threshold explanations

```sh
python neuron_animations.py --mode rebound --explain
python neuron_animations.py --explain-all
```

[neuroscience_notes.py](neuroscience_notes.py) contains channel names and roles, human-relevant locations, proposed functions, evidence limits, source links, all four default protocols and time steps. These are explanatory annotations, not explicit ion-channel equations. `--explain` prints the default protocol; capacitance/current overrides do not modify these reference notes.

All modes use a **+30 mV peak cutoff** for spike/reset detection. This is not a fixed initiation threshold. Spike initiation depends on state and input. See [the biology notes](../NEUROSCIENCE.md).
