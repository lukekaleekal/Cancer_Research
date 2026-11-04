"""Source-backed biological context and simulation settings.

Channels here explain examples in real neurons. The Izhikevich model does
not explicitly solve ion-channel gating, conductances or ionic concentrations.
Human anatomy is distinguished from direct human physiological evidence.
"""

SCIENCE_NOTES = {'izhikevich': {'behavior': 'Regular spiking: a sustained positive input produces repeated spikes, '
                            'often with adaptation.',
                'channels': ['Voltage-gated sodium (NaV) channels: transient inward Na+ current '
                             'drives the fast spike upstroke.',
                             'Voltage-gated delayed-rectifier potassium (Kv) channels: outward K+ '
                             'current repolarizes the spike.',
                             'Kv7/KCNQ M-type potassium channels (including Kv7.2/KCNQ2 and '
                             'Kv7.3/KCNQ3): slow outward current can promote adaptation and limit '
                             'bursting.',
                             'Small-conductance calcium-activated potassium (SK/KCa2) channels can '
                             'contribute to afterhyperpolarization and adaptation in some '
                             'pyramidal cells; no single channel set defines every regular-spiking '
                             'neuron.'],
                'human_location': 'Excitatory pyramidal neurons throughout the cerebral neocortex, '
                                  'including layers 2/3 and 5. Human cortical recordings directly '
                                  'support repetitive firing and NaV/Kv-dependent fast signaling.',
                'function': 'Repeated spikes encode sustained input. Adaptation can reduce '
                            'responses to persistent input. Exact functions depend on cortical '
                            'region and circuit; this is a contribution, not proof of an '
                            'evolutionary purpose.',
                'evidence': 'Direct human cortical physiology supports Na+/K+ contributions. '
                            'Detailed M-current and other adaptation mechanisms also rely on '
                            'mammalian animal studies. The 31 pF calibration is from rat visual '
                            'cortical cells, not a human capacitance measurement.',
                'sources': ['https://pubmed.ncbi.nlm.nih.gov/37824607/',
                            'https://www.nature.com/articles/s41467-021-22741-9',
                            'https://pubmed.ncbi.nlm.nih.gov/15140933/',
                            'https://doi.org/10.1152/jn.1997.78.5.2321']},
 'rebound': {'behavior': 'A hyperpolarizing pulse is followed by a spike or burst when inhibition '
                         'ends.',
             'channels': ['T-type voltage-gated calcium channels, especially CaV3.1/CACNA1G in '
                          'thalamic relay cells: hyperpolarization removes inactivation; '
                          'subsequent depolarization opens channels and supplies inward Ca2+ '
                          'current.',
                          'HCN (hyperpolarization-activated cyclic nucleotide-gated) channels '
                          'carry a mixed Na+/K+ inward current at negative voltages; this can help '
                          'voltage recover, but is not required for every rebound mechanism.',
                          'Transient NaV channels generate the fast action potentials riding on '
                          'the low-threshold depolarization; Kv channels repolarize them.',
                          'Rebound is not unique to T-type channels: other cell types can use '
                          'persistent Na+ currents and different channel combinations. Injected '
                          'negative current in this simulation does not explicitly activate GABA '
                          'receptors.'],
             'human_location': 'Thalamic relay circuits, including human lateral thalamus. Human '
                               'recordings show sleep-related low-threshold burst patterns. The '
                               'exact cellular channel mechanism is supported primarily by animal '
                               'electrophysiology.',
             'function': 'Helps connect inhibition to later excitation and contributes to '
                         'thalamocortical sleep rhythms and state-dependent sensory transmission. '
                         'A single model rebound spike is a simplified example, not a fitted human '
                         'thalamic burst.',
             'evidence': 'Human extracellular firing patterns: PMID 9063713. T-type causal '
                         'evidence: animal slice/knockout/dynamic-clamp studies. The 147 pF '
                         'reference is from mouse thalamocortical cells.',
             'sources': ['https://pubmed.ncbi.nlm.nih.gov/9063713/',
                         'https://pubmed.ncbi.nlm.nih.gov/22933804/',
                         'https://www.nature.com/articles/s41467-025-58717-2',
                         'https://doi.org/10.1152/jn.00147.2021']},
 'threshold': {'behavior': 'Identical positive pulses can have different outcomes because recent '
                           'voltage history changes excitability; inhibition before the second '
                           'pulse permits a spike.',
               'channels': ['NaV channels: voltage-dependent inactivation changes the number '
                            'available to open. Hyperpolarization can restore availability, making '
                            'subsequent spike initiation easier.',
                            'Voltage-gated K+ channels, including low-threshold/slow currents, '
                            'oppose depolarization and can change the effective threshold.',
                            'Kv1-family D-type or other slowly inactivating K+ currents can '
                            'support history dependence in some neurons, but the generic '
                            'simulation does not identify a particular subtype.',
                            'Axon-to-soma propagation and recording location also affect apparent '
                            'threshold variability; it cannot always be assigned solely to a '
                            'channel.'],
               'human_location': 'Human-relevant regions include neocortical pyramidal neurons and '
                                 'hippocampal pyramidal circuits. The specific '
                                 'threshold-variability studies cited here used ferret cortex, rat '
                                 'hippocampus or models; they do NOT directly verify our exact '
                                 'inhibition-pulse behavior in a human cell.',
               'function': 'A history-dependent threshold changes which inputs trigger spikes, can '
                           'favor rapidly rising inputs, and reduces firing after recent activity. '
                           'These are experimentally supported or model-based mechanisms, not a '
                           'uniquely established human cognitive function.',
               'evidence': 'Direct human NaV/Kv work supports the presence and kinetics of the '
                           'relevant channels, not this exact protocol. Rat hippocampal threshold '
                           'variability and theoretical sodium-inactivation work support the '
                           'explanation. The 155 pF reference comes from a separate rat CA1 study.',
               'sources': ['https://pubmed.ncbi.nlm.nih.gov/11483306/',
                           'https://pubmed.ncbi.nlm.nih.gov/21573200/',
                           'https://pmc.ncbi.nlm.nih.gov/articles/PMC2900290/',
                           'https://pubmed.ncbi.nlm.nih.gov/18632930/',
                           'https://pubmed.ncbi.nlm.nih.gov/37824607/',
                           'https://doi.org/10.1113/jphysiol.2009.185975']},
 'dap': {'behavior': 'After the spike and reset, voltage rises into a smaller depolarizing '
                     'after-potential before returning toward rest.',
         'channels': ['Persistent sodium current (INaP) through NaV channels can maintain inward '
                      'Na+ flow after the fast spike. Persistent and transient Na+ currents need '
                      'not come from separate channel genes.',
                      'R-type calcium channels (CaV2.3/CACNA1E) can contribute inward Ca2+ tail '
                      'current to the afterdepolarization in some CA1 preparations.',
                      'Kv7/KCNQ M-type potassium channels counteract the depolarization and limit '
                      'its duration and escalation to bursts.',
                      'Fast NaV and repolarizing Kv channels generate the preceding spike. '
                      'Relative Na+/Ca2+ contributions vary with age, preparation and recording '
                      'conditions; do not claim every DAP requires all of these channels.'],
         'human_location': 'The hippocampal CA1 region is the human anatomical counterpart of the '
                           'rodent cells used as examples here. The cited channel-mechanism and '
                           'capacitance studies are animal studies; they do not verify a '
                           'particular human CA1 DAP trace.',
         'function': 'The after-potential briefly increases excitability and can promote burst '
                     'output, potentially influencing synaptic plasticity and hippocampal '
                     'information coding. A direct causal explanation of human memory from this '
                     'simulation would be unsupported.',
         'evidence': 'Rodent CA1 experiments support persistent Na+, R-type Ca2+, and opposing '
                     'KCNQ currents under differing conditions. These mechanisms are biological '
                     'context, not channels explicitly simulated by the two-variable Izhikevich '
                     'model.',
         'sources': ['https://pubmed.ncbi.nlm.nih.gov/16237175/',
                     'https://pubmed.ncbi.nlm.nih.gov/15958743/',
                     'https://pubmed.ncbi.nlm.nih.gov/15140933/',
                     'https://doi.org/10.1113/jphysiol.2009.185975',
                     'https://www.izhikevich.org/publications/figure1.m']}}

PROTOCOLS = {'izhikevich': {'capacitance_pf': 31.0,
                'dt_ms': 0.01,
                'duration_ms': 500,
                'parameters': [0.02, 0.2, -65, 8],
                'initial_v_mv': -65,
                'initial_u': -13,
                'stimulation': '0 nA before 50 ms; +0.310 nA from 50 to 500 ms (default regular '
                               'preset).'},
 'rebound': {'capacitance_pf': 147.0,
             'dt_ms': 0.01,
             'duration_ms': 200,
             'parameters': [0.03, 0.25, -60, 4],
             'initial_v_mv': -64,
             'initial_u': -16,
             'stimulation': '-0.735 nA for 40 <= t < 60 ms; zero otherwise.'},
 'threshold': {'capacitance_pf': 155.0,
               'dt_ms': 0.01,
               'duration_ms': 120,
               'parameters': [0.03, 0.25, -60, 4],
               'initial_v_mv': -64,
               'initial_u': -16,
               'stimulation': '+0.155 nA for 10 <= t < 15 and 90 <= t < 95 ms; -0.930 nA for 80 <= '
                              't < 85 ms; zero otherwise.'},
 'dap': {'capacitance_pf': 155.0,
         'dt_ms': 0.1,
         'duration_ms': 50,
         'parameters': [1, 0.2, -60, -21],
         'initial_v_mv': -70,
         'initial_u': -14,
         'stimulation': '+3.100 nA for abs(t - 10) < 1 ms; zero otherwise. Uses sequential '
                        'voltage/recovery update.'}}

THRESHOLD_EXPLANATION = (
    "All modes use a +30 mV spike cutoff/peak marker, followed by reset to c "
    "and u += d. This is NOT the voltage threshold at which a biological "
    "action potential starts. The model's initiation threshold depends on "
    "the current state (v,u) and stimulation; there is no fixed -55 mV "
    "initiation threshold. DAP tests v > 30; the other modes use v >= 30."
)


def explanation(mode):
    note, protocol = SCIENCE_NOTES[mode], PROTOCOLS[mode]
    lines = [mode.upper(), note['behavior'], '', 'Main channel mechanisms:']
    lines.extend('- ' + item for item in note['channels'])
    lines.extend(['', 'Brain location and human evidence:', note['human_location'],
                  '', 'Contribution to brain function:', note['function'],
                  '', 'Evidence limits:', note['evidence'],
                  '', 'Default simulation settings:',
                  f"Time step: {protocol['dt_ms']} ms; run: {protocol['duration_ms']} ms",
                  f"Parameters (a,b,c,d): {protocol['parameters']}",
                  f"Initial v: {protocol['initial_v_mv']} mV; initial u: {protocol['initial_u']}",
                  f"Representative capacitance: {protocol['capacitance_pf']} pF",
                  protocol['stimulation'], '', 'Threshold:', THRESHOLD_EXPLANATION,
                  '', 'Sources:'])
    lines.extend(note['sources'])
    return '\n'.join(lines)
