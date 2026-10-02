"""Render a small scientific figure and export it to multiple formats."""

import argparse

import matplotlib.pyplot as plt

import atopos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="example-output")
    args = parser.parse_args()
    with atopos.theme(font="DejaVu Sans", fontsize=9):
        fig, ax = plt.subplots(layout="constrained")
        x = [0, 1, 2, 3, 4]
        ax.plot(x, [1.2, 1.8, 2.5, 2.7, 3.5], marker="o", label="Series A")
        ax.plot(x, [0.8, 1.4, 1.7, 2.3, 2.5], marker="s", label="Series B")
        ax.set(xlabel="Time (hours)", ylabel="Measurement (a.u.)", title="Scientific figure export")
        ax.legend(loc="upper left")
        paths = atopos.imagesave(
            fig,
            "measurement",
            outdir=args.outdir,
            preset="single_column",
            formats=("pdf", "svg", "png", "tiff"),
            dpi=300,
        )
    plt.close(fig)
    for fmt, path in paths.items():
        print(f"{fmt}: {path}")


if __name__ == "__main__":
    main()
