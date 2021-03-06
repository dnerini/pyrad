"""
==================================
Plotting (:mod:`pyrad.graph`)
==================================

.. currentmodule:: pyrad.graph

Functions to plot graphics.

Plots
=====

.. autosummary::
    :toctree: generated/

    plot_surface
    plot_latitude_slice
    plot_longitude_slice
    plot_latlon_slice
    plot_ppi
    plot_ppi_contour
    plot_ppi_map
    plot_rhi
    plot_rhi_contour
    plot_bscope
    plot_fixed_rng
    plot_fixed_rng_span
    plot_time_range
    plot_rhi_profile
    plot_along_coord
    plot_field_coverage
    plot_density
    plot_cappi
    plot_traj
    plot_pos
    plot_quantiles
    plot_histogram
    plot_histogram2
    plot_antenna_pattern
    plot_timeseries
    plot_timeseries_comp
    plot_monitoring_ts
    plot_scatter_comp
    plot_intercomp_scores_ts
    plot_ml_ts
    plot_sun_hits
    plot_sun_retrieval_ts
    get_colobar_label
    get_field_name
    _plot_time_range

"""

from .plots import plot_histogram, plot_histogram2, plot_density, plot_scatter
from .plots import plot_sun_hits, plot_antenna_pattern
from .plots import plot_scatter_comp, plot_quantiles

from .plots_vol import plot_ppi, plot_ppi_map, plot_rhi, plot_bscope
from .plots_vol import plot_time_range, plot_cappi, plot_rhi_profile
from .plots_vol import plot_along_coord, plot_field_coverage, plot_traj
from .plots_vol import plot_pos, _plot_time_range, plot_rhi_contour
from .plots_vol import plot_ppi_contour, plot_fixed_rng, plot_fixed_rng_span

from .plots_grid import plot_surface, plot_latitude_slice
from .plots_grid import plot_longitude_slice, plot_latlon_slice

from .plots_timeseries import plot_timeseries, plot_timeseries_comp
from .plots_timeseries import plot_monitoring_ts, plot_intercomp_scores_ts
from .plots_timeseries import plot_sun_retrieval_ts, plot_ml_ts

from .plots_aux import get_colobar_label, get_field_name

__all__ = [s for s in dir() if not s.startswith('_')]
