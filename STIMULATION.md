# Equations, stimulation and current scaling

All four HTML and Python animations numerically calculate voltage. DAP uses the original Figure 1Q discrete update; it no longer uses a drawn curve.

## Equations and conversion

The normalized model is

```
dv/dt = 0.04*v*v + 5*v + 140 - u + J
du/dt = a*(b*v - u)
if v reaches 30 mV: v = c; u = u + d
```

With voltage interpreted in mV and time in ms, interpret `J` as a voltage-rate input. Choose an effective whole-cell capacitance `C`. The equivalent applied current is:

```
I_amperes = C_pF * 1e-12 * J
I_nanoamperes = C_pF * J / 1000
J = I_amperes / (C_pF * 1e-12)
```

This works because 1 mV/ms equals 1 V/s. Multiplying the **entire** voltage equation by C gives the corresponding current-balance equation. Thus the intrinsic terms are scaled along with the input; this is not changing only the input in an otherwise fitted cell model.

The chosen capacitances are representative literature values. No curve here has been fitted to a recorded neuron. They do not establish actual experimental stimulation thresholds, currents, or a unique neuron identity. In particular, the rebound reference reports rebound bursts; our generic example shows a single rebound spike. The CA1 behavior papers and capacitance paper studied different cells and experimental preparations.

## Default stimulation protocols

Outside the intervals below, applied current is zero. Positive current depolarizes; negative current hyperpolarizes.

| Animation | C (pF) | Stimulation | Model J | Parameters (a,b,c,d) | Initial (v,u) | Time step | Run length |
|---|---:|---|---|---|---|---|---|
| Regular spiking | 31 | +0.310 nA from 50 through 500 ms | +10 | 0.02, 0.2, -65, 8 | -65, -13 | 0.01 ms | 500 ms |
| Rebound spike | 147 | -0.735 nA for 40 <= t < 60 ms | -5 | 0.03, 0.25, -60, 4 | -64, -16 | 0.01 ms | 200 ms |
| Threshold variability | 155 | +0.155 nA for 10 <= t < 15 and 90 <= t < 95 ms; -0.930 nA for 80 <= t < 85 ms | +1 and -6 | 0.03, 0.25, -60, 4 | -64, -16 | 0.01 ms | 120 ms |
| DAP | 155 | +3.100 nA when abs(t - 10) < 1 ms (9 < t < 11) | +20 | 1, 0.2, -60, -21 | -70, -14 | 0.1 ms | 50 ms |

Regular, rebound and threshold use forward Euler with both derivatives evaluated from the previous state. DAP reproduces the author's sequential scheme: update v, update u using the new v, test v > 30, and reset. Its trace is sensitive to both step size and update order; it is a reproduction of that discrete calculation, not a claim of step-size convergence.

The general Izhikevich animation also has bursting (0.02,0.2,-55,4), chattering (0.02,0.2,-50,2) and fast-spiking (0.1,0.2,-65,2) presets. The 31 pF value remains an illustrative reference scale when switching presets; it is **not** a measured capacitance for those other phenotypes. Supply a documented capacitance override in Python to use a different scale.

## Literature supporting the representative capacitances

1. Locke and Nerbonne (1997), *Role of Voltage-Gated K+ Currents in Mediating the Regular-Spiking Phenotype of Callosal-Projecting Rat Visual Cortical Neurons*. Whole-cell capacitance 31 ± 10 pF (mean ± SD, n=60). https://doi.org/10.1152/jn.1997.78.5.2321
2. Tissone et al. (2021), *Differential contribution of the subthreshold operating currents IT, Ih, and IKir to the resonance of thalamocortical neurons*. Mouse thalamocortical neurons show rebound bursts. Resonant cells: 0.147 ± 0.0057 nF (147 pF, n=45), from fits to experimental impedance. https://doi.org/10.1152/jn.00147.2021
3. Zemankovics et al. (2010), *Differences in subthreshold resonance of hippocampal pyramidal cells and interneurons*. Rat CA1 pyramidal cells: median 155 pF, interquartile range 121–195 pF, n=19, Table 1. https://doi.org/10.1113/jphysiol.2009.185975
4. Henze and Buzsáki (2001), *Action potential threshold of hippocampal pyramidal cells in vivo is increased by recent spiking activity*. Supports threshold variability in rat hippocampal pyramidal cells, not the exact pulse protocol here. https://pubmed.ncbi.nlm.nih.gov/11483306/
5. Metz et al. (2005), *R-Type Calcium Channels Contribute to Afterdepolarization and Bursting in Hippocampal CA1 Pyramidal Neurons*. Supports CA1 afterdepolarization, not a fit of our DAP parameters to those cells. https://pubmed.ncbi.nlm.nih.gov/15958743/
6. Izhikevich's original model and Figure 1 code: https://www.izhikevich.org/publications/spikes.pdf and https://www.izhikevich.org/publications/figure1.m
