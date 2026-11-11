#!/usr/bin/env python3
"""50-neuron Izhikevich network, matched control/pulse simulation and animation.

Install: python -m pip install numpy matplotlib pillow
Run: python neuron_network.py
Export: python neuron_network.py --save network.gif
Compare control: python neuron_network.py --condition control
Representative currents: python neuron_network.py --neuron E1

Model assumptions: dt=.25 ms, 1 model current unit=.1 nA (100 pF scaling).
Background 5..7 units; E synapses +1.2 units, tau=5 ms; I synapses -2.5,
tau=10 ms. Pulse -18 units (-1.8 nA) on I neurons during 400<=t<600 ms.
Seed 1937 reproduces the original JavaScript connectivity and initial states.
Traveling dots are illustrative, not measured conduction delays. Correlations
use 20 ms bins over the full run. Post-pulse spikes do not prove intrinsic rebound.
Reference: https://www.izhikevich.org/publications/spikes.pdf
"""
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection
from matplotlib.widgets import Button, RadioButtons, Slider

N, T, DT = 50, 1000, .25
REP = [0, 1, 2, 40, 41, 42]
E_COLOR, I_COLOR = '#3576d2', '#c38c00'


def make_network():
    """Use the original animation's unsigned 32-bit random generator."""
    seed = 1937
    def random():
        nonlocal seed
        seed = (1664525 * seed + 1013904223) & 0xffffffff
        return seed / 4294967296
    edges = [(i, j) for i in range(N) for j in range(N)
             if i != j and random() < .18]
    drive = np.array([5 + 2 * random() for _ in range(N)])
    initial = np.array([-65 + 4 * random() for _ in range(N)])
    return np.array(edges), drive, initial


def simulate(edges, drive, initial, pulse):
    v = initial.copy()
    inhibitory = np.arange(N) >= 40
    a = np.where(inhibitory, .03, .02)
    b = np.where(inhibitory, .25, .20)
    c = np.where(inhibitory, -60., -65.)
    d = np.where(inhibitory, 4., 8.)
    u = b * v
    exc, inh = np.zeros(N), np.zeros(N)
    voltage = np.zeros((T, 6))
    current = np.zeros((T, 6, 3))
    spikes = [[] for _ in range(N)]
    source, target = edges.T
    for step in range(int(T / DT)):
        t = step * DT
        exc *= np.exp(-DT / 5)
        inh *= np.exp(-DT / 10)
        applied = np.where(inhibitory, -18., 0.) if pulse and 400 <= t < 600 else 0.
        v += DT * (.04 * v * v + 5 * v + 140 - u + drive + exc + inh + applied)
        u += DT * a * (b * v - u)
        fired = v >= 30
        for i in np.flatnonzero(fired):
            spikes[i].append(t)
        v[fired] = c[fired]
        u[fired] += d[fired]
        if step % 4 == 0:
            k = step // 4
            voltage[k] = np.where(fired[REP], 30., v[REP])
            current[k, :, 0] = exc[REP] * .1
            current[k, :, 1] = inh[REP] * .1
            current[k, :, 2] = (exc[REP] + inh[REP]) * .1
        active = fired[source]
        np.add.at(exc, target[active & (source < 40)], 1.2)
        np.add.at(inh, target[active & (source >= 40)], -2.5)
    spikes = [np.asarray(s) for s in spikes]
    counts = np.array([np.histogram(s, bins=np.arange(0, T + 20, 20))[0] for s in spikes])
    centered = counts - counts.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(centered, axis=1)
    denom = np.outer(norm, norm)
    correlation = np.divide(centered @ centered.T, denom,
                            out=np.full((N, N), np.nan), where=denom > 0)
    rate = np.zeros((T, 2))
    for t in range(1, T):
        start = max(0, t - 50)
        for group, indices in enumerate((range(40), range(40, 50))):
            count = sum(np.count_nonzero((spikes[i] >= start) & (spikes[i] < t)) for i in indices)
            rate[t, group] = count * 1000 / ((t - start) * len(indices))
    return dict(spikes=spikes, voltage=voltage, current=current,
                rate=rate, correlation=correlation)


def label(i):
    return f'E{i + 1}' if i < 40 else f'I{i - 39}'


def build_animation(runs, edges, condition=1, representative=3, speed=40):
    fig = plt.figure(figsize=(16, 14))
    grid = fig.add_gridspec(4, 2, left=.07, right=.95, bottom=.13,
                            top=.93, hspace=.8, wspace=.28)
    network = fig.add_subplot(grid[0, :])
    raster = fig.add_subplot(grid[1, 0])
    voltage_grid = grid[1:3, 1].subgridspec(6, 1, hspace=.5)
    volt_axes = [fig.add_subplot(voltage_grid[k]) for k in range(6)]
    rates = fig.add_subplot(grid[2, 0])
    heats = [fig.add_subplot(grid[3, k]) for k in range(2)]
    # Separate current figure keeps six voltage traces comfortably spaced.
    cfig, currents = plt.subplots(figsize=(10, 4))
    cfig.subplots_adjust(bottom=.25)
    selector = RadioButtons(cfig.add_axes([.01, .02, .97, .12]),
                            [label(i) for i in REP], active=representative,
                            activecolor=E_COLOR)
    pos = np.array([(i % 8, -(i // 8)) if i < 40
                    else (9 + (i - 40) % 2, -((i - 40) // 2)) for i in range(N)])
    segments = pos[edges]
    source = edges[:, 0]
    colors = np.array([E_COLOR if i < 40 else I_COLOR for i in range(N)])
    state = dict(condition=condition, representative=representative, time=0, playing=True)
    all_v = np.concatenate([r['voltage'].ravel() for r in runs])
    vlim = (all_v.min() - 5, all_v.max() + 5)
    heat_cmap = plt.get_cmap('coolwarm').copy()
    heat_cmap.set_bad('lightgray')
    for ax, run, name in zip(heats, runs, ('control', 'pulse')):
        image = ax.imshow(run['correlation'], vmin=-1, vmax=1, cmap=heat_cmap,
                          extent=(.5, 50.5, 50.5, .5), aspect='auto')
        ax.set(title=f'6. Correlation heatmap: {name} (full run)',
               xlabel='Neuron index', ylabel='Neuron index')
        fig.colorbar(image, ax=ax, label='Correlation r', fraction=.025)

    def time_axis(ax, title, ylabel):
        ax.clear()
        ax.set(xlim=(0, T), title=title, ylabel=ylabel, xlabel='Time (ms)')
        if state['condition']:
            ax.axvspan(400, 600, color='gray', alpha=.12)
        ax.axvline(state['time'], color='gray', linewidth=.7)

    def draw(t):
        t = int(t)
        state['time'] = t
        run = runs[state['condition']]
        phase = ('pulse ON' if state['condition'] and 400 <= t < 600
                 else 'after pulse removal' if state['condition'] and t >= 600
                 else 'control' if not state['condition'] else 'baseline')
        fig.suptitle(f'50-neuron network | {t} ms | {phase}', fontsize=16)
        network.clear()
        network.set_title('1. Moving network: circles E, diamonds I; ring = current selection')
        network.add_collection(LineCollection(segments, colors='gray', alpha=.10, linewidths=.5))
        latest = np.array([s[s <= t][-1] if np.any(s <= t) else -1e6 for s in run['spikes']])
        age = t - latest
        for ids, marker in ((np.arange(40), 'o'), (np.arange(40, 50), 'D')):
            network.scatter(*pos[ids].T, c=colors[ids], marker=marker,
                            s=np.where(age[ids] < 8, 95, 30), alpha=.8)
        traveling = (age[source] >= 0) & (age[source] < 12)
        if traveling.any():
            frac = age[source[traveling], None] / 12
            dots = segments[traveling, 0] * (1 - frac) + segments[traveling, 1] * frac
            network.scatter(*dots.T, c=colors[source[traveling]], s=8)
        for i, (x, y) in enumerate(pos):
            network.text(x, y - .24, label(i), ha='center', fontsize=8)
        selected = REP[state['representative']]
        network.scatter(*pos[selected], s=190, facecolors='none', edgecolors='black')
        network.set(xlim=(-.5, 10.5), ylim=(-4.6, .5))
        network.axis('off')
        time_axis(raster, '2. Spike raster', 'Neuron index')
        for i, s in enumerate(run['spikes']):
            visible = s[s <= t]
            raster.vlines(visible, i + .7, i + 1.3, color=colors[i], linewidth=.6)
        raster.set_ylim(50.5, .5)
        ts = np.arange(t + 1)
        for k, ax in enumerate(volt_axes):
            time_axis(ax, f'3. {label(REP[k])}', 'mV')
            ax.plot(ts, run['voltage'][:t + 1, k], color=colors[REP[k]], linewidth=.8)
            ax.set_ylim(vlim)
            if k < 5:
                ax.set_xlabel('')
                ax.tick_params(labelbottom=False)
        time_axis(rates, '4. Population firing rates (trailing 50 ms)', 'Rate (Hz)')
        for g, name, color in ((0, 'Excitatory', E_COLOR), (1, 'Inhibitory', I_COLOR)):
            rates.plot(ts, run['rate'][:t + 1, g], label=name, color=color)
        rates.set_ylim(0, max(r['rate'].max() for r in runs) * 1.05)
        rates.legend(fontsize=8)
        time_axis(currents, f'5. Synaptic currents received by {label(selected)}', 'Current (nA)')
        for k, (name, color) in enumerate(zip(('Excitatory', 'Inhibitory', 'Net'),
                                             (E_COLOR, I_COLOR, '#cc5599'))):
            currents.plot(ts, run['current'][:t + 1, state['representative'], k],
                          label=name, color=color)
        current_values = np.concatenate([r['current'][:, state['representative']].ravel() for r in runs])
        currents.set_ylim(current_values.min() - .05, current_values.max() + .05)
        currents.legend()
        fig.canvas.draw_idle()
        cfig.canvas.draw_idle()

    slider = Slider(fig.add_axes([.12, .07, .72, .02]), 'Time (ms)', 0, 999, valinit=0, valstep=1)
    pause = Button(fig.add_axes([.12, .02, .15, .03]), 'Pause / Play')
    switch = Button(fig.add_axes([.32, .02, .2, .03]), 'Control / Pulse')
    pause.on_clicked(lambda _: state.update(playing=not state['playing']))
    def toggle(_):
        state['condition'] = 1 - state['condition']
        draw(state['time'])
    switch.on_clicked(toggle)
    selector.on_clicked(lambda name: (state.update(representative=[label(i) for i in REP].index(name)), draw(state['time'])))
    slider.on_changed(draw)
    def update(_):
        if state['playing']:
            next_time = min(999, state['time'] + speed / 20)
            slider.set_val(next_time)
            if next_time >= 999:
                state['playing'] = False
    animation = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    # Keep widget references alive for interactive callbacks.
    fig._network_widgets = (slider, pause, switch, selector)
    draw(0)
    return fig, animation, draw


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--condition', choices=['control', 'pulse'], default='pulse')
    parser.add_argument('--neuron', choices=[label(i) for i in REP], default='I1')
    parser.add_argument('--speed', type=float, default=40, help='Simulation ms per playback second')
    parser.add_argument('--save', type=Path, help='Export main figure to .gif (current plot remains interactive only)')
    parser.add_argument('--check', action='store_true', help='Validate simulation and rendering without a GUI')
    args = parser.parse_args()
    if args.speed <= 0:
        parser.error('--speed must be positive')
    edges, drive, initial = make_network()
    runs = [simulate(edges, drive, initial, pulse) for pulse in (False, True)]
    for name, run in zip(('Control', 'Pulse'), runs):
        assert np.isfinite(run['voltage']).all()
        counts = [len(s) for s in run['spikes']]
        post = sum(np.count_nonzero((s >= 600) & (s < 650)) for s in run['spikes'][40:])
        upper = run['correlation'][np.triu_indices(N, 1)]
        print(f'{name}: E={np.mean(counts[:40]):.2f} Hz; I={np.mean(counts[40:]):.2f} Hz; '
              f'I spikes 600–650 ms={post}; mean pair r={np.nanmean(upper):.3f}')
    fig, animation, draw = build_animation(runs, edges, int(args.condition == 'pulse'),
                                           [label(i) for i in REP].index(args.neuron), args.speed)
    if args.check:
        animation._draw_was_started = True
        for t in (0, 450, 650, 999):
            draw(t)
            for number in plt.get_fignums():
                plt.figure(number).canvas.draw()
        plt.close('all')
        print(f'Validated {len(edges)} directed edges and four animation times.')
    elif args.save:
        if args.save.suffix.lower() != '.gif':
            parser.error('--save requires a .gif path')
        animation.event_source.stop()
        export = FuncAnimation(fig, draw, frames=np.unique(np.r_[np.arange(0, 1000, args.speed / 20), 999]).astype(int),
                               interval=50, repeat=False)
        export.save(args.save, writer=PillowWriter(fps=20), dpi=80)
        animation._draw_was_started = True
        plt.close('all')
    else:
        plt.show()


if __name__ == '__main__':
    main()
