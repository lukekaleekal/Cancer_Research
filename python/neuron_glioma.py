#!/usr/bin/env python3
"""Neuron–glioma animation: 50 neurons and 10 passive glioma cells.

Keep neuron_network.py (in this repository) beside this file.
Install: python -m pip install numpy matplotlib pillow
Run: python neuron_glioma.py
Check: MPLBACKEND=Agg python neuron_glioma.py --check
Export: python neuron_glioma.py --save glioma.gif --speed 100

GABA reversals -25 and -57.2 mV reflect DMG measurements, not all gliomas.
https://www.nature.com/articles/s41586-024-08579-3
Glioma: C=40 pF, leak=1 nS, E_leak=initial voltage=-70 mV.
GABA increment=.3 nS per incoming spike, decay=20 ms (illustrative).
I→glioma connection probability=.35; a disconnected glioma cell gets one
fallback connection. No glioma spikes, proliferation or feedback to neurons.
Positive I_GABA=g*(E_GABA-V)/1000 nA is inward/depolarizing.
C*dV/dt=g_leak*(E_leak-V)+g_GABA*(E_GABA-V), using pF, nS, mV, ms.
Pulse: -1.8 nA (assumed model conversion) on I neurons at 400–600 ms.
Regular/burst replays impose 20 spikes per I neuron; imposed bursts are not
proof of intrinsic rebound. Both reversals remain depolarizing from -70 mV.
"""
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection
from matplotlib.widgets import Button, Slider, RadioButtons
from neuron_network import simulate

EG = np.array([-25., -57.2])
AMPS = np.array([.05, .1, .2, .3, .5, .75, 1., 1.5, 2.])
COLORS = ['#397bd5', '#bc8700', '#9864c4', '#289b87']
PROTOCOLS = ['Network control', 'Network + pulse', 'Regular replay', 'Burst replay']


def network(seed):
    def random():
        nonlocal seed
        seed = (1664525 * seed + 1013904223) & 0xffffffff
        return seed / 4294967296
    edges = np.array([(i, j) for i in range(50) for j in range(50)
                      if i != j and random() < .18])
    drive = np.array([5 + 2 * random() for _ in range(50)])
    initial = np.array([-65 + 4 * random() for _ in range(50)])
    ge = np.array([(i, g) for i in range(40, 50) for g in range(10) if random() < .35])
    for g in range(10):
        if not np.any(ge[:, 1] == g):
            ge = np.vstack([ge, [40 + g, g]])
    return edges, drive, initial, ge


def glioma(spikes, ge):
    dt, steps = .25, 4000
    events = np.zeros((steps, 10))
    for i, g in ge:
        np.add.at(events[:, g], np.rint(spikes[i] / dt).astype(int), .3)
    conductance = np.zeros((steps + 1, 10))
    fraction = np.zeros((steps + 1, 10))
    peak = np.zeros((len(AMPS), 10))
    x = peak.copy()
    for k in range(steps):
        g = conductance[k] * np.exp(-dt / 20) + events[k]
        conductance[k + 1] = g
        gg = (AMPS / .3)[:, None] * g
        total = 1 + gg
        eq = gg / total
        # Exact passive update with conductance frozen during each .25 ms step.
        x = eq + (x - eq) * np.exp(-total * dt / 40)
        fraction[k + 1] = x[3]
        peak = np.maximum(peak, x)
    voltage = -70 + (EG[:, None, None] + 70) * fraction[None, :, :]
    current = conductance[None, :, :] * (EG[:, None, None] - voltage) / 1000
    delta = voltage + 70
    metrics = np.stack([delta.max(axis=1), ((delta[:, 1:] + delta[:, :-1]) * .5).sum(axis=1) * dt / 1000,
                        (voltage[:, 1:] > -50).sum(axis=1) * dt], axis=1)
    assert np.isfinite(voltage).all()
    assert voltage.min() >= -70 - 1e-10
    assert np.all(voltage <= EG[:, None, None] + 1e-10)
    return dict(v=voltage[:, ::20], g=conductance[::20], current=current[:, ::20],
                metrics=metrics, heat=peak.mean(axis=1))


def compute(seeds=8):
    results = []
    for seed in range(1937, 1937 + seeds):
        edges, drive, initial, ge = network(seed)
        runs = []
        for pulse in [False, True]:
            spikes = simulate(edges, drive, initial, pulse)['spikes']
            runs.append(dict(spikes=spikes, **glioma(spikes, ge)))
        regular = np.arange(100, 900, 40.)
        burst = np.array([start + 3 * k for start in [100, 340, 580, 820] for k in range(5)])
        for timing in [regular, burst]:
            spikes = [s.copy() for s in runs[0]['spikes']]
            for i in range(40, 50):
                spikes[i] = timing.copy()
            runs.append(dict(spikes=spikes, **glioma(spikes, ge)))
        assert all(len(runs[2]['spikes'][i]) == len(runs[3]['spikes'][i]) == 20 for i in range(40, 50))
        results.append(dict(seed=seed, edges=edges, ge=ge, runs=runs))
        print(f'Computed seed {seed}', flush=True)
    return results


def create_animation(data, speed=40):
    state = dict(seed=0, protocol=1, cell=0, t=0., playing=False)
    fig = plt.figure(figsize=(16, 14), layout=None)
    grid = fig.add_gridspec(4, 2, left=.07, right=.96, bottom=.13, top=.93,
                            hspace=.7, wspace=.3)
    axes = [fig.add_subplot(grid[0, :])]
    axes += [fig.add_subplot(grid[r, c]) for r, c in [(1, 0), (1, 1), (2, 0), (2, 1)]]
    # Analysis figure is static with respect to time; updates for seed/protocol.
    analysis = plt.figure(figsize=(15, 9), layout='constrained')
    ag = analysis.add_gridspec(2, 3)
    metric_axes = [analysis.add_subplot(ag[0, k]) for k in range(3)]
    heat_ax = analysis.add_subplot(ag[1, :])
    title_names = ['2. Neuronal spike raster', '3. Glioma voltage',
                   '4. GABA conductance', '5. GABA current (inward positive)']
    pos = np.array([(i % 8, -(i // 8)) if i < 40 else
                    (9 + (i - 40) % 2, -((i - 40) // 2)) if i < 50 else
                    (12 + (i - 50) % 2, -((i - 50) // 2)) for i in range(60)])
    node_colors = [COLORS[0] if i < 40 else COLORS[1] if i < 50 else COLORS[2] for i in range(60)]
    ts = np.arange(0, 1001, 5)
    ylimits = [None, None, (-72, -24), (0, max(r['g'].max() for n in data for r in n['runs']) * 1.05),
               (0, max(r['current'].max() for n in data for r in n['runs']) * 1.05)]
    def draw(t):
        state['t'] = float(t)
        net = data[state['seed']]
        run = net['runs'][state['protocol']]
        cell = state['cell']
        visible = ts <= t
        phase = ('pulse ON' if 400 <= t < 600 else 'post-pulse' if t >= 600 else 'baseline') if state['protocol'] == 1 else PROTOCOLS[state['protocol']]
        fig.suptitle(f'50 neurons + 10 passive glioma cells | {t:.0f} ms | {phase} | seed {net["seed"]}')
        ax = axes[0]
        ax.clear()
        all_edges = np.vstack([net['edges'], np.column_stack([net['ge'][:, 0], 50 + net['ge'][:, 1]])])
        ax.add_collection(LineCollection(pos[all_edges], colors='gray', alpha=.12, linewidths=.5))
        latest = np.array([s[s <= t][-1] if np.any(s <= t) else -1e6 for s in run['spikes']])
        age = t - latest
        for ids, marker in [(np.arange(40), 'o'), (np.arange(40, 50), 'D')]:
            sizes = np.where(age[ids] < 8, 90, 25)
            if state['protocol'] >= 2 and ids[0] == 0:
                sizes[:] = 25
            ax.scatter(*pos[ids].T, c=np.array(node_colors)[ids], s=sizes, marker=marker)
        source = all_edges[:, 0]
        mask = (age[source] >= 0) & (age[source] < 15)
        if state['protocol'] >= 2:
            mask &= source >= 40
        f = age[source[mask], None] / 15
        dots = pos[all_edges[mask, 0]] * (1 - f) + pos[all_edges[mask, 1]] * f
        ax.scatter(*dots.T, c=np.array(node_colors)[source[mask]], s=9)
        k = min(200, int(t // 5))
        dep = run['v'][0, k] + 70
        ax.scatter(*pos[50:].T, c=COLORS[2], s=35 + 5 * dep, marker='s')
        ax.scatter(*pos[50 + cell], s=240, facecolors='none', edgecolors='black')
        for i, (x, y) in enumerate(pos):
            name = f'E{i + 1}' if i < 40 else f'I{i - 39}' if i < 50 else f'G{i - 49}'
            ax.text(x, y - .25, name, ha='center', fontsize=8)
        ax.set(xlim=(-.5, 13.5), ylim=(-4.6, .6), title='1. Network: E circles, I diamonds, G squares; square size = baseline depolarization')
        ax.axis('off')
        for j, ax in enumerate(axes[1:]):
            ax.clear()
            ax.set(title=title_names[j], xlim=(0, 1000), xlabel='Time (ms)')
            if state['protocol'] == 1:
                ax.axvspan(400, 600, color='gray', alpha=.12)
            ax.axvline(t, color='gray', linewidth=.7)
        raster, voltage, conductance, current = axes[1:]
        for i, spikes in enumerate(run['spikes']):
            if state['protocol'] >= 2 and i < 40:
                continue
            raster.vlines(spikes[spikes <= t], i + .7, i + 1.3, color=node_colors[i], linewidth=.7)
        raster.set(ylim=(50.5, .5), ylabel='Neuron index')
        for z, name in enumerate(['Baseline DMG (−25 mV)', 'NKCC1 inhibition (−57.2 mV)']):
            voltage.plot(ts[visible], run['v'][z, visible, cell], label=name, color=COLORS[z + 2], linestyle='-' if z == 0 else '--')
            current.plot(ts[visible], run['current'][z, visible, cell], label=name, color=COLORS[z + 2], linestyle='-' if z == 0 else '--')
        conductance.plot(ts[visible], run['g'][visible, cell], color=COLORS[1])
        voltage.set(ylabel=f'G{cell + 1} voltage (mV)', ylim=ylimits[2])
        conductance.set(ylabel=f'G{cell + 1} conductance (nS)', ylim=ylimits[3])
        current.set(ylabel=f'G{cell + 1} current (nA)', ylim=ylimits[4])
        voltage.legend(fontsize=8)
        current.legend(fontsize=8)
        fig.canvas.draw_idle()

    def draw_analysis():
        groups = [(2, 0, 'R −25'), (3, 0, 'B −25'), (2, 1, 'R −57'), (3, 1, 'B −57')]
        for m, (ax, title, unit) in enumerate(zip(metric_axes,
                ['Peak depolarization', 'Positive depolarization integral', 'Time above −50 mV'], ['mV', 'mV·s', 'ms'])):
            ax.clear()
            for k, (p, e, label) in enumerate(groups):
                values = [n['runs'][p]['metrics'][e, m].mean() for n in data]
                ax.bar(k, np.mean(values), color=COLORS[e + 2], alpha=.35)
                ax.scatter(k + np.linspace(-.1, .1, len(data)), values, color=COLORS[e + 2], s=20)
            ax.set(title='6. ' + title, ylabel=unit, xticks=range(4),
                   xticklabels=[g[2] for g in groups], xlabel='R: regular; B: imposed burst; 20 spikes/I')
        heat_ax.clear()
        run = data[state['seed']]['runs'][state['protocol']]
        reversals = np.arange(-65, -14, 5)
        heat = (reversals[:, None] + 70) * run['heat'][None, :]
        # Colorbar is updated rather than accumulating on redraw.
        image = heat_ax.imshow(heat, origin='lower', aspect='auto', extent=(-.5, 8.5, -67.5, -12.5), cmap='viridis')
        heat_ax.set(title=f'7. Mean peak depolarization: {PROTOCOLS[state["protocol"]]} | seed {data[state["seed"]]["seed"]}',
                    xticks=range(9), xticklabels=AMPS, xlabel='Conductance increment per spike (nS)', ylabel='GABA reversal (mV)')
        if not hasattr(heat_ax, '_colorbar'):
            heat_ax._colorbar = analysis.colorbar(image, ax=heat_ax, label='Mean peak ΔV (mV)')
        else:
            heat_ax._colorbar.update_normal(image)
        analysis.suptitle(f'Full 1 s run | {len(data)} networks | dots = means across 10 glioma cells | threshold is illustrative, not a firing threshold')
        analysis.canvas.draw_idle()

    time_slider = Slider(fig.add_axes([.12, .075, .73, .018]), 'Time (ms)', 0, 1000, valinit=0)
    seed_slider = Slider(fig.add_axes([.12, .045, .3, .018]), 'Seed index', 0, len(data) - 1, valinit=0, valstep=1)
    cell_slider = Slider(fig.add_axes([.56, .045, .3, .018]), 'Glioma G', 1, 10, valinit=1, valstep=1)
    play_button = Button(fig.add_axes([.12, .005, .16, .03]), 'Play / Pause')
    replay_button = Button(fig.add_axes([.31, .005, .16, .03]), 'Replay')
    protocol_buttons = [Button(fig.add_axes([.08 + k * .225, .23, .21, .035]), name) for k, name in enumerate(PROTOCOLS)]
    time_slider.on_changed(draw)
    def change_seed(value):
        state['seed'] = int(value)
        draw(state['t'])
        draw_analysis()
    def change_cell(value):
        state['cell'] = int(value) - 1
        draw(state['t'])
    def change_protocol(name):
        state['protocol'] = PROTOCOLS.index(name)
        draw(state['t'])
        draw_analysis()
    seed_slider.on_changed(change_seed)
    cell_slider.on_changed(change_cell)
    for name, button in zip(PROTOCOLS, protocol_buttons):
        button.on_clicked(lambda _, name=name: change_protocol(name))
    play_button.on_clicked(lambda _: state.update(playing=not state['playing']))
    def replay(_):
        state['playing'] = True
        time_slider.set_val(0)
    replay_button.on_clicked(replay)
    def update(_):
        if state['playing']:
            t = min(1000, state['t'] + speed / 20)
            time_slider.set_val(t)
            if t == 1000:
                state['playing'] = False
    animation = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    fig._glioma_widgets = (time_slider, seed_slider, cell_slider, protocol_buttons, play_button, replay_button)
    draw(0)
    draw_analysis()
    return fig, animation, draw, draw_analysis, state


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--speed', type=float, default=40)
    parser.add_argument('--save', type=Path, help='Save main animation to GIF; full-run analysis saved as sibling PNG')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not np.isfinite(args.speed) or args.speed <= 0:
        parser.error('--speed must be finite and positive')
    if args.save and args.save.suffix.lower() != '.gif':
        parser.error('--save must end in .gif')
    data = compute()
    fig, animation, draw, draw_analysis, state = create_animation(data, args.speed)
    if args.check:
        animation._draw_was_started = True
        for seed, protocol, cell, t in [(0, 1, 0, 0), (1, 1, 9, 450), (7, 1, 4, 650), (0, 2, 0, 1000), (7, 3, 9, 1000)]:
            state.update(seed=seed, protocol=protocol, cell=cell)
            draw(t)
            draw_analysis()
            for num in plt.get_fignums():
                plt.figure(num).canvas.draw()
        plt.close('all')
        print('Validated 8 networks, 4 protocols, equal spike counts, physical bounds, and 5 rendering states.')
    elif args.save:
        animation.event_source.stop()
        animation._draw_was_started = True
        frames = np.unique(np.r_[np.arange(0, 1000, args.speed / 20), 1000])
        export = FuncAnimation(fig, draw, frames=frames, interval=50, repeat=False)
        export.save(args.save, writer=PillowWriter(fps=20), dpi=80)
        plt.figure(2).savefig(args.save.with_name(args.save.stem + '_analysis.png'), dpi=150)
        plt.close('all')
    else:
        plt.show()


if __name__ == '__main__':
    main()
