"""Science-fair neuron animations. Run with --help for examples and options.

Regular, rebound, and threshold modes integrate the Izhikevich equations.
DAP numerically reproduces the author's Figure 1Q update scheme (dt=0.1 ms).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.widgets import Button

from neuroscience_notes import explanation

PRESETS = {
    "regular": (0.02, 0.2, -65, 8),
    "bursting": (0.02, 0.2, -55, 4),
    "chattering": (0.02, 0.2, -50, 2),
    "fast": (0.1, 0.2, -65, 2),
}
TITLES = {
    "izhikevich": "Izhikevich neuron",
    "rebound": "Rebound spike",
    "threshold": "Threshold variability",
    "dap": "Depolarizing after-potential (simulation)",
}


# Representative literature values; these do not identify or fit a recorded cell.
CAPACITANCE_PF = {"izhikevich": 31.0, "rebound": 147.0, "threshold": 155.0, "dap": 155.0}


def current_amperes(model_input, capacitance_pf):
    """Equivalent physical input under the mV/ms interpretation of model I.

    mV/ms = V/s, so I(A) = C(pF)*1e-12 * model_input.
    Multiplying the ENTIRE voltage equation by C gives the corresponding
    current balance. This is dimensional scaling, not a biophysical fit.
    """
    if not np.isfinite(capacitance_pf) or capacitance_pf <= 0:
        raise ValueError("Capacitance must be positive and finite")
    return np.asarray(model_input) * capacitance_pf * 1e-12


def input_current(time, mode, current=10.0):
    """Applied current in model units; supports scalar or array times."""
    t = np.asarray(time)
    if mode == "izhikevich":
        return np.where(t >= 50, current, 0.0)
    if mode == "rebound":
        return np.where((t >= 40) & (t < 60), -5.0, 0.0)
    if mode == "threshold":
        positive = ((t >= 10) & (t < 15)) | ((t >= 90) & (t < 95))
        return np.where(positive, 1.0, np.where((t >= 80) & (t < 85), -6.0, 0.0))
    return np.where(np.abs(t - 10.0) < 1.0, 20.0, 0.0)


def simulate_dap(capacitance_pf=155.0):
    """Reproduce the numerical scheme in Izhikevich (2004), Figure 1Q.

    Source: https://www.izhikevich.org/publications/figure1.m
    Parameters: a=1, b=0.2, c=-60, d=-21; v=-70, u=b*v initially.
    This example is step-sensitive: retain dt=0.1 ms AND update u using
    the newly updated v, before testing the spike cutoff and resetting.
    It is a reproduction of the published discrete simulation, not a
    claim that these parameters give the same trace as dt tends to zero.
    """
    a, b, c, d = 1.0, 0.2, -60.0, -21.0
    dt = 0.1
    v, u = -70.0, -14.0
    samples, spikes = [(0.0, v)], []
    for i in range(501):
        time = i * dt
        model_drive = 20.0 if abs(time - 10.0) < 1.0 else 0.0
        physical_drive = float(current_amperes(model_drive, capacitance_pf))
        drive = physical_drive / (capacitance_pf * 1e-12)
        v += dt * (0.04 * v * v + 5 * v + 140 - u + drive)
        u += dt * a * (b * v - u)
        if v > 30.0:
            samples.append((time, 30.0))
            spikes.append(time)
            v = c
            u += d
            samples.append((time, v))
        else:
            samples.append((time, v))
    t, voltage = np.array(samples).T
    return t, voltage, input_current(t, "dap"), np.array(spikes)


def simulate(mode="izhikevich", pattern="regular", current=10.0, capacitance_pf=None):
    """Return time, voltage, current and spike times.

    Non-DAP modes: forward Euler, dt=0.01 ms, cutoff 30 mV; v=c, u+=d.
    DAP: author's sequential update at dt=0.1 ms (see simulate_dap).
    Each reset has two samples at the same time to draw a vertical reset.
    """
    capacitance_pf = CAPACITANCE_PF[mode] if capacitance_pf is None else capacitance_pf
    current_amperes(0, capacitance_pf)  # validate before integration
    if mode == "dap":
        return simulate_dap(capacitance_pf)

    duration = {"izhikevich": 500, "rebound": 200, "threshold": 120}[mode]
    a, b, c, d = PRESETS[pattern] if mode == "izhikevich" else (0.03, 0.25, -60, 4)
    v = -65.0 if mode == "izhikevich" else -64.0
    u = b * v
    dt = 0.01
    times = np.arange(round(duration / dt) + 1) * dt
    physical_drive = current_amperes(input_current(times, mode, current), capacitance_pf)
    drive = physical_drive / (capacitance_pf * 1e-12)
    samples, spikes = [(0.0, v)], []
    for i in range(1, len(times)):
        dv = 0.04 * v * v + 5 * v + 140 - u + drive[i]
        du = a * (b * v - u)
        v += dt * dv
        u += dt * du
        if v >= 30:
            samples.append((times[i], 30.0))
            spikes.append(times[i])
            v, u = c, u + d
            samples.append((times[i], v))
        elif i % 5 == 0:
            samples.append((times[i], v))
    t, voltage = np.array(samples).T
    return t, voltage, input_current(t, mode, current), np.array(spikes)


def phase(mode, time, spikes):
    if mode == "rebound":
        if time < 40:
            return "Resting"
        if time < 60:
            return "Inhibitory input on"
        if len(spikes) and time < spikes[0]:
            return "Input off: voltage rebounds"
        return "Rebound spike and recovery"
    if mode == "threshold":
        if time < 10:
            return "Resting"
        if time < 25:
            return "First positive pulse: no spike"
        if time < 80:
            return "Resting"
        if time < 85:
            return "Inhibitory pulse"
        if time < 90:
            return "Inhibition ends"
        return "Same positive pulse: spike and recovery"
    if mode == "dap":
        if time <= 9:
            return "Resting"
        if time < 11:
            return "Brief excitatory input"
        if len(spikes) and time <= spikes[0] + 0.2:
            return "Main spike and reset"
        if time < 20:
            return "Depolarizing after-potential (DAP)"
        return "Returning to rest"
    return "Current off" if time < 50 else "Current on"


class NeuronAnimation:
    def __init__(self, mode="izhikevich", pattern="regular", current=10.0, capacitance_pf=None):
        self.mode = mode
        self.capacitance_pf = CAPACITANCE_PF[mode] if capacitance_pf is None else capacitance_pf
        self.t, self.v, model_drive, self.spikes = simulate(mode, pattern, current, self.capacitance_pf)
        self.drive = current_amperes(model_drive, self.capacitance_pf) * 1e9
        self.duration = float(self.t[-1])
        self.frames = 241
        self.index = 0
        self.playing = False
        self.fig, (self.ax_v, self.ax_i) = plt.subplots(
            2, 1, sharex=True, figsize=(9, 6), gridspec_kw={"height_ratios": [3, 1]}
        )
        self.fig.subplots_adjust(bottom=0.21, top=0.87, hspace=0.15)
        self.fig.suptitle(TITLES[mode] + f" · C = {self.capacitance_pf:g} pF")
        self.fig.text(0.5, 0.015, "Representative capacitance; equivalent current scale, not fitted cell recordings.", ha="center", fontsize=9)
        self.ax_v.set_ylabel("Voltage (mV)")
        self.ax_i.set_ylabel("Input current\n(nA)")
        self.ax_i.set_xlabel("Time (ms)")
        self.ax_v.set_xlim(0, self.duration)
        self.ax_v.set_ylim(float(self.v.min()) - 6, float(self.v.max()) + 6)
        lo, hi = float(self.drive.min()), float(self.drive.max())
        pad = max(0.3, (hi - lo) * 0.2)
        self.ax_i.set_ylim(lo - pad, hi + pad)
        for ax in (self.ax_v, self.ax_i):
            ax.grid(alpha=0.2)
        self.voltage_line, = self.ax_v.plot([], [], color="tab:blue", lw=1.8)
        self.current_line, = self.ax_i.plot([], [], color="tab:orange", lw=1.8, drawstyle="steps-post")
        self.guides = [ax.axvline(0, color="gray", ls="--", lw=0.8) for ax in (self.ax_v, self.ax_i)]
        self.status = self.fig.text(0.12, 0.91, "", fontsize=10)
        self.play_button = Button(self.fig.add_axes([0.12, 0.06, 0.14, 0.06]), "Play")
        self.replay_button = Button(self.fig.add_axes([0.29, 0.06, 0.14, 0.06]), "Replay")
        self.play_button.on_clicked(self.toggle)
        self.replay_button.on_clicked(self.replay)
        self.timer = self.fig.canvas.new_timer(interval=33)
        self.timer.add_callback(self.advance)
        self.render(0)

    def render(self, frame):
        self.index = max(0, min(self.frames - 1, int(frame)))
        now = self.duration * self.index / (self.frames - 1)
        end = max(1, int(np.searchsorted(self.t, now, side="right")))
        self.voltage_line.set_data(self.t[:end], self.v[:end])
        self.current_line.set_data(self.t[:end], self.drive[:end])
        for line in self.guides:
            line.set_xdata([now, now])
        self.status.set_text(phase(self.mode, now, self.spikes))
        return self.voltage_line, self.current_line, *self.guides, self.status

    def toggle(self, _event=None):
        if self.playing:
            self.timer.stop()
            self.playing = False
            self.play_button.label.set_text("Play")
        else:
            if self.index == self.frames - 1:
                self.render(0)
            self.playing = True
            self.play_button.label.set_text("Pause")
            self.timer.start()
        self.fig.canvas.draw_idle()

    def replay(self, _event=None):
        self.render(0)
        if not self.playing:
            self.toggle()
        self.fig.canvas.draw_idle()

    def advance(self):
        self.render(self.index + 1)
        if self.index == self.frames - 1:
            self.timer.stop()
            self.playing = False
            self.play_button.label.set_text("Play")
        self.fig.canvas.draw_idle()

    def save(self, path):
        self.timer.stop()
        self.playing = False
        self.play_button.label.set_text("Play")
        self.play_button.ax.set_visible(False)
        self.replay_button.ax.set_visible(False)
        movie = FuncAnimation(self.fig, self.render, frames=self.frames, interval=33, repeat=False)
        try:
            movie.save(str(path), writer=PillowWriter(fps=30))
        finally:
            self.play_button.ax.set_visible(True)
            self.replay_button.ax.set_visible(True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--explain", action="store_true", help="Print biological context, sources and default protocol for the selected mode")
    parser.add_argument("--explain-all", action="store_true", help="Print the notes and default protocols for all four modes")
    parser.add_argument("--mode", choices=TITLES, default="izhikevich")
    parser.add_argument("--pattern", choices=PRESETS, default="regular", help="Izhikevich mode only")
    parser.add_argument("--current", type=float, default=10, help="Izhikevich input current (0–30 model units)")
    parser.add_argument("--capacitance-pf", type=float, help="Override the representative capacitance (pF)")
    parser.add_argument("--current-na", type=float, help="Izhikevich current in nA; overrides --current")
    parser.add_argument("--plot", type=Path, metavar="OUTPUT.png", help="Save the completed plot instead of opening a window")
    parser.add_argument("--save", type=Path, metavar="OUTPUT.gif", help="Export a GIF instead of opening a window")
    args = parser.parse_args()
    if args.explain or args.explain_all:
        for mode in (TITLES if args.explain_all else [args.mode]):
            print(explanation(mode), end="\n\n")
        return
    if not 0 <= args.current <= 30:
        parser.error("--current must be between 0 and 30")
    if args.save and args.save.suffix.lower() != ".gif":
        parser.error("--save requires a .gif filename")
    cap = CAPACITANCE_PF[args.mode] if args.capacitance_pf is None else args.capacitance_pf
    if not np.isfinite(cap) or cap <= 0:
        parser.error("--capacitance-pf must be positive and finite")
    current = args.current
    if args.current_na is not None:
        if args.mode != "izhikevich":
            parser.error("--current-na applies only to --mode izhikevich")
        current = args.current_na * 1000 / cap
        if not np.isfinite(current) or not 0 <= current <= 30:
            parser.error("Equivalent model current must be in the range 0–30")
    if args.plot and args.save:
        parser.error("Choose either --plot or --save")
    demo = NeuronAnimation(args.mode, args.pattern, current, cap)
    if args.plot:
        demo.render(demo.frames - 1)
        demo.play_button.ax.set_visible(False)
        demo.replay_button.ax.set_visible(False)
        demo.fig.savefig(args.plot, dpi=180)
        plt.close(demo.fig)
        return
    if args.save:
        demo.save(args.save)
        plt.close(demo.fig)
    else:
        demo.toggle()
        plt.show()


if __name__ == "__main__":
    main()

