# Science fair questions 1–4

These answers cover the four simulated behaviors. The ion-channel explanations describe representative biological mechanisms; the Izhikevich model represents their combined effects without explicitly simulating individual channels.

## 1. Which ion channels make these behaviors possible?

| Behavior | Main channels and their roles |
|---|---|
| Regular spiking | NaV sodium channels produce the spike’s rising phase. Kv potassium channels bring voltage back down. Kv7/KCNQ potassium channels can slow repeated firing through adaptation. |
| Rebound spike | T-type calcium channels, especially CaV3.1 in thalamic relay cells, recover from inactivation during hyperpolarization and can open when voltage rises afterward. HCN channels can help voltage recover. NaV and Kv channels produce the fast spike. |
| Threshold variability | NaV channel availability changes with recent activity, affecting how easily a spike starts. Voltage-gated potassium channels also influence excitability. |
| Depolarizing after-potential (DAP) | Persistent sodium current and, in some neurons, R-type or L-type calcium currents sustain depolarization after a spike. Kv7/KCNQ potassium channels oppose this depolarization. |

Channel contributions vary between neuron types, age and experimental conditions. Not every neuron requires every channel listed, and a firing trace alone cannot identify its channel composition.

Sources: [human NaV/Kv physiology](https://pubmed.ncbi.nlm.nih.gov/37824607/), [thalamic T-type channels](https://pubmed.ncbi.nlm.nih.gov/22933804/), [threshold mechanisms](https://pmc.ncbi.nlm.nih.gov/articles/PMC2900290/), [persistent sodium and DAP](https://pubmed.ncbi.nlm.nih.gov/16237175/), [R-type calcium and DAP](https://pubmed.ncbi.nlm.nih.gov/15958743/), [KCNQ and DAP](https://pubmed.ncbi.nlm.nih.gov/15140933/), [L-type involvement in developing rat CA1 cells](https://pubmed.ncbi.nlm.nih.gov/15919718/).

## 2. Where are these behaviors found, and what do they contribute?

| Behavior | Brain location and contribution |
|---|---|
| Regular spiking | Common in cerebral cortical pyramidal neurons, including human neurons. Repeated firing communicates sustained inputs. |
| Rebound spike | Found in thalamic circuits. Rebound firing contributes to sleep rhythms and state-dependent sensory transmission; related burst patterns have been recorded in humans. |
| Threshold variability | Studied in cortical and hippocampal pyramidal neurons. It makes responses depend on recent activity and can favor rapidly rising inputs. |
| DAP | Well studied in hippocampal CA1 pyramidal neurons. It temporarily increases excitability and can promote bursts, potentially influencing information coding and synaptic plasticity. |

The detailed threshold-variability and DAP mechanisms cited here mainly come from animal studies and models. The human cortex, thalamus and hippocampus contain the relevant anatomical cell classes, but that does not establish identical mechanisms or the exact modeled responses in human cells. These functions describe contributions to circuit processing, not proof of why the behaviors evolved.

Sources: [human cortical neurons](https://pubmed.ncbi.nlm.nih.gov/37824607/), [human thalamic sleep/wake recordings](https://pubmed.ncbi.nlm.nih.gov/9063713/), [thalamic sensory transmission](https://pubmed.ncbi.nlm.nih.gov/22933804/), [rat hippocampal threshold variability](https://pubmed.ncbi.nlm.nih.gov/11483306/), [sodium-inactivation threshold model](https://pubmed.ncbi.nlm.nih.gov/21573200/), [CA1 afterdepolarization](https://pubmed.ncbi.nlm.nih.gov/15958743/).

## 3. What time step did we use?

| Simulation | Integration time step |
|---|---:|
| Regular spiking | 0.01 ms |
| Rebound spike | 0.01 ms |
| Threshold variability | 0.01 ms |
| DAP | 0.1 ms |

The first three use forward Euler with both derivatives evaluated from the previous state. DAP matches the author’s original Figure 1Q sequential update: update voltage, update recovery using that new voltage, then detect and reset the spike. DAP is sensitive to this time step and update order; reproducing that discrete example is not a claim of convergence as the step approaches zero. Integration time step is separate from the animation playback interval.

Source: [Izhikevich’s original Figure 1 code, section Q](https://www.izhikevich.org/publications/figure1.m). Implementation: [Python simulation](python/neuron_animations.py).

## 4. What threshold did we use?

Our code uses **+30 mV as the spike-detection cutoff near the peak of a spike**. When voltage crosses this cutoff, the code records the spike, resets voltage to parameter `c`, and increases the recovery variable by `d`.

**We did not set a fixed voltage threshold for starting an action potential.** That initiation threshold depends on the model’s voltage, recovery variable and stimulation history. Therefore, **−55 mV was not a threshold programmed into these simulations**.

The exact comparisons in the code are `v >= 30` for regular spiking, rebound and threshold variability, and `v > 30` for DAP, following its original example. The cutoff is a membrane voltage relative to the reference potential, not a requirement to increase voltage by 30 mV from rest.

Sources: [original model](https://www.izhikevich.org/publications/spikes.pdf), [Figure 1 numerical examples](https://www.izhikevich.org/publications/figure1.m).

For current amplitudes, capacitance assumptions, pulse timing and model parameters, see [STIMULATION.md](STIMULATION.md). For more detailed biological notes, see [NEUROSCIENCE.md](NEUROSCIENCE.md).
