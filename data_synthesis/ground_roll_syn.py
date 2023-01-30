##################################################
# Info: Ground roll (surface wave) simulation
# Author: jia zhuang (jzsherlock@163.com)
# Date: 2023-01-30
##################################################

import os
import numpy as np
import matplotlib.pyplot as plt

def ground_roll_syn(num_traces=100,
                    num_time_samples=1000,
                    time_shift=50,
                    freq_low=5,
                    freq_high=20,
                    dx=5,
                    dt=0.002,
                    velocity=200,
                    distance_degradation=0.92,
                    win_scale=4,
                    duration_ratio=0.04,
                    save_path='./syn_data/sample_groundroll.npy'
                    ):
    """
    args:
        num_traces: number of seismic traces (single side w.r.t source point)
        num_time_samples: number of samples in time axis
        time_shift: offset to the top
        freq_low: the lower frequency of the chirp signal to simulate dispersity
        freq_high: the higher frequency of the chirp signal to simulate dispersity
        dx: space sample interval (unit: m)
        dy: time sample interval (unit: s)
        velocity: ground-roll velocity (unit: m/s)
        distance_degradation: amplitude degradation ratio w.r.t distance
        win_scale: controls the smooth edge of window, should be larger than (or equal to) 2, the larger the shearer
        duration_ratio: controls the sampling of chirp of ground-roll in each trace
        save_path: synthetic data save path, if parent folder not exist, it will be created
    """
    dp = dx / (velocity * dt)  # reciprocal of radial velocity
    gr_data = np.zeros((num_time_samples, num_traces))

    for trace_idx in range(num_traces):

        # step 1. generate chirp signal
        T = 1 + trace_idx * duration_ratio
        bandwidth = freq_high - freq_low
        t = np.arange(0, T, dt) / (2 * T)
        Ft = (freq_low + bandwidth * t)
        chirp_signal = np.sin(2 * np.pi * Ft * t)

        # step 2. generate window
        window = np.ones(len(t))
        n_edge = int(np.round(np.pi / (2 * dt * win_scale)))
        # make sure the window is sin-edge + plateau + sin-edge (symm) format
        assert n_edge < len(t) / 2
        t1 = np.arange(0, n_edge * dt, dt)
        edge = np.sin(t1 * win_scale)
        window[:n_edge] = edge
        window[-n_edge:] = edge[::-1]

        # step 3. gen simulated ground-roll
        gr_w = window * chirp_signal
        t_offset = int(np.round(trace_idx * dp) + time_shift)
        cur_deg = distance_degradation ** trace_idx

        if t_offset > num_time_samples:
            break
        elif t_offset + len(t) > num_time_samples:
            cutoff_N = num_time_samples - t_offset
            gr_data[t_offset:, trace_idx] = gr_w[:cutoff_N] * cur_deg
        else:
            gr_data[t_offset: t_offset + len(t), trace_idx] = gr_w[:len(t)] * cur_deg

    VERBOSE = True
    if VERBOSE:
        plt.imshow(gr_data, aspect='auto')
        plt.show()
    
    # save result
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    np.save(save_path, gr_data)


if __name__ == "__main__":
    ground_roll_syn()