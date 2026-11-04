# Python neuron animations

Install Python 3.10 or newer, then run these commands from this folder:

```sh
python -m pip install -r requirements.txt
python neuron_animations.py
python neuron_animations.py --mode rebound
python neuron_animations.py --mode threshold
python neuron_animations.py --mode dap
```

The window has Play/Pause and Replay buttons. Each animation takes about eight seconds. Use a desktop Python environment with a Matplotlib GUI backend to open the window. On a headless computer, export a GIF instead:

```sh
MPLBACKEND=Agg python neuron_animations.py --mode rebound --save rebound.gif
```

Change the general model's firing pattern or current with:

```sh
python neuron_animations.py --pattern bursting --current 12
```

Available patterns: `regular`, `bursting`, `chattering`, `fast`. Current range: 0–30 model units.

The first three modes integrate the Izhikevich equations with a 0.01 ms Euler step. The DAP mode is explicitly a schematic matching the supplied drawing, not a numerical simulation. Its time axis is illustrative.

Model: https://www.izhikevich.org/publications/spikes.pdf
