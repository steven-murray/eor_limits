#! /usr/bin/env python
# Copyright (c) 2019 Nichole Barry, Bryna Hazelton
# Licensed under the 2-clause BSD License
"""Code for plotting EoR Limits."""

import json
from pathlib import Path
from typing import Literal

from cyclopts import App

from .plots.plot_vs_k_z import default_theory_params, make_plot

app = App()


@app.command
def plot(
    papers=None,
    theory: bool = True,
    theory_legend: bool = True,
    theories: list[str] = None,
    theory_model: str = None,
    theory_nf: list[float] = None,
    theory_redshift: list[float] = None,
    theory_linewidth: list[float] = None,
    aspoints: list[str] = ("patil_2017", "mertens_2020"),
    dsq_range: tuple[float, float] = None,
    z_range: tuple[float, float] = None,
    k_range: tuple[float, float] = None,
    shade_limits: Literal["generational", "alpha", "none"] = "generational",
    shade_theory: Literal["flat", "alpha", "none"] = "flat",
    colormap: str = "Spectral_r",
    bold_papers: list[str] = None,
    fontsize: int = 15,
    sensitivities: list[tuple[str, str]] = None,
    sensitivity_style: list[tuple[str, str]] = None,
    height_ratio: float = None,
    markersize: int = 150,
    out: Path = Path("eor_limits.pdf"),
):
    """
    Plot the current EoR Limits as a function of k or redshift.

    Parameters
    ----------
    papers
        Papers to include on plot (must be in data directory). Defaults to all papers
        in the data directory.
    theory
        Whether to include theory lines on the plot.
    theory_legend
        Whether to exclude theory lines from the legend. Used by some users who
        prefer to add the annotations on the lines by hand to improve readability.
    theories
        Theories to plot. Theory-specific options can be set to control which lines are
        drawn.
    theory_model
        Model type to select from theories (e.g. 'bright' or 'faint' for Mesinger et
        al. 2016).
    theory_nf
        Neutral fractions to select from theories.
    theory_redshift
        Redshifts to select from theories.
    theory_linewidth
        Linewidths for theory lines.
    aspoints
        Papers to plot as points rather than lines to help simplify the plot.
    dsq_range
        Range of Delta Squared to include on plot (yaxis range).
    z_range
        Range of redshifts to include on plot.
    k_range
        Range of k values to include on plot (xaxis range).
    shade_limits
        Type of shading above limits to apply.
    shade_theory
        Type of shading below theories to apply.
    colormap
        Matplotlib colormap to use.
    bold_papers
        List of papers to bold in caption.
    fontsize
        Font size to use in the legend.
    out
        Output file name.
    sensitivities
        List of tuples of (name, file) for which to include sensitivities.
        Files must be 21cmSense v2+ outputs, which can be generated with
        ``sense calc-sense --fname out.h5`` (see 21cmSense docs for more info).
    sensitivity_style
        List of style parameters for plotting sensitivities. Each entry
        should be a name and a dictionary. Each 'name' (if given) should correspond
        to a label in the sensitivities argument, and the values should be a JSON
        string with style parameters for plotting, e.g. {'color': 'k', 'ls': '--',
        'lw': 3}. An additional key 'sensitivity_kind' can be used to specify which
        kind of sensitivity to plot, e.g. 'sample+thermal', 'sample' or 'thermal'.
        If no name is given, the style will be applied to all sensitivities. If no
        style is given, the default style will be used.
    height_ratio
        Height to width ratio of the figure.
    markersize
        Size of the markers for points.
    """
    if shade_limits == "none":
        shade_limits = False
    if shade_theory == "none":
        shade_theory = False

    if theories is not None:
        theories, theory_model, theory_nf, theory_redshift = parse_theories(
            theories, theory_model, theory_nf, theory_redshift, theory_linewidth
        )
    else:
        if theory_nf or theory_redshift or theory_model:
            raise ValueError(
                "You passed a theory nf/redshift/model but no theory itself!"
            )

        theory_params = default_theory_params

    # Process sensitivity arguments.
    if sensitivities:
        sensitivities = dict(sensitivities)

    if sensitivity_style:
        sensitivity_style = {k: json.loads(v) for k, v in sensitivity_style}

    fig = make_plot(
        papers=papers,
        include_theory=theories is not None and theories != [],
        theory_legend=theory_legend,
        theory_params=theory_params,
        plot_as_points=aspoints,
        delta_squared_range=dsq_range,
        redshift_range=z_range,
        k_range=k_range,
        shade_limits=shade_limits,
        shade_theory=shade_theory,
        colormap=colormap,
        bold_papers=bold_papers,
        fontsize=fontsize,
        sensitivities=sensitivities,
        sensitivity_style=sensitivity_style,
        markersize=markersize,
        fig_ratio=height_ratio,
    )
    fig.savefig(out)


def parse_theories(
    theories, theory_model, theory_nf, theory_redshift, theory_linewidth
):
    """Parse theory arguments for plotting."""
    if theory_nf is None:
        theory_nf = [None]
    else:
        theory_nf = [float(val) if val != "None" else None for val in theory_nf]
    if theory_redshift is None:
        theory_redshift = [None]
    if theory_model is None:
        theory_model = [None]

    theory_params = {}
    num_theories = len(theories)
    num_models = len(theory_model)
    num_nf = len(theory_nf)
    num_redshift = len(theory_redshift)
    num_theory_lines = max([num_theories, num_models, num_nf, num_redshift])
    if num_theory_lines > 1:
        if num_theories == 1:
            theories = theories * num_theory_lines
        elif num_theories != num_theory_lines:
            raise ValueError(
                "Number of theories must be one or match the max length of "
                "theory_model, theory_nf or theory_redshift."
            )
        if num_models == 1:
            theory_model = theory_model * num_theory_lines
        elif num_models != num_theory_lines:
            raise ValueError(
                "Number of theory_models must be one or match the max length of "
                "theories, theory_nf or theory_redshift."
            )
        if num_nf == 1:
            theory_nf = theory_nf * num_theory_lines
        elif num_nf != num_theory_lines:
            raise ValueError(
                "Number of theory_nfs must be one or match the max length of "
                "theories, theory_model or theory_redshift."
            )
        if num_redshift == 1:
            theory_redshift = theory_redshift * num_theory_lines
        elif num_redshift != num_theory_lines:
            raise ValueError(
                "Number of theory_redshifts must be one or match the max length of "
                "theories, theory_model or theory_nf."
            )

        if theory_linewidth is not None:
            if len(theory_linewidth) == 1:
                theory_linewidth = theory_linewidth * num_theory_lines
            elif len(theory_linewidth) != num_theory_lines:
                raise ValueError(
                    "Number of theory lines must be one or match the max length of "
                    "theories, theory_model, theory_nf or theory_redshift."
                )
    for index, (theory, model, nf, redshift) in enumerate(
        zip(theories, theory_model, theory_nf, theory_redshift, strict=True)
    ):
        name = f"{theory}_{model}_nf_{nf}_z_{redshift}"

        theory_params[name] = {
            "paper": theory,
            "model": model,
            "nf": float(nf) if nf is not None else None,
            "redshift": float(redshift) if redshift is not None else None,
        }
        if theory_linewidth is not None:
            theory_params[name]["linewidth"] = theory_linewidth[index]
    return theories, theory_model, theory_nf, theory_redshift
