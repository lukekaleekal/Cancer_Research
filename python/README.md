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

All four modes now compute their voltage traces from the Izhikevich equations. DAP no longer uses drawn anchor points.

## DAP numerical method

Run `python neuron_animations.py --mode dap`.

DAP reproduces the author’s Figure 1Q numerical method: `a=1`, `b=0.2`, `c=-60`, `d=-21`, initial `v=-70`, initial `u=-14`, and a current pulse of 20 model units for `abs(t-10)<1` ms. The run lasts 50 ms. Its time step is **0.1 ms**. Voltage is updated first, then recovery uses that updated voltage, then the spike cutoff/reset is applied. The other three modes retain their **0.01 ms** forward Euler step.

This DAP example is sensitive to the integration step and update order. It reproduces the published discrete calculation; reducing the step with these same parameters can change the firing pattern. Do not describe it as a step-independent reproduction of the continuous equations or a measured biological trace.

The simulation yields one spike near 11.3 ms, a post-reset DAP peak near -51.1 mV at 14.4 ms, and a return toward -70 mV.

Sources:
- Author’s original numerical example, section Q: https://www.izhikevich.org/publications/figure1.m
- Izhikevich (2004), Which Model to Use for Cortical Spiking Neurons?: https://www.izhikevich.org/publications/whichmod.htm
- Original model: https://www.izhikevich.org/publications/spikes.pdf
