"""
pyrad.io.read_data_sensor
=========================

Functions for reading data from other sensors

.. autosummary::
    :toctree: generated/

    read_trt_scores
    read_trt_cell_lightning
    read_trt_data
    read_trt_traj_data
    read_lightning
    read_meteorage
    read_lightning_traj
    read_lightning_all
    get_sensor_data
    read_smn
    read_smn2
    read_disdro_scattering
    read_disdro

"""

import os
import datetime
import csv
from warnings import warn
from copy import deepcopy
import re

import numpy as np

from pyart.config import get_fillvalue


def read_trt_scores(fname):
    """
    Reads the TRT scores contained in a text file. The file has the following
    fields:
        traj ID
        max flash density time
        max flash density rank
        max flash density
        max rank time
        max rank

    Parameters
    ----------
    fname : str
        path of the TRT data file

    Returns
    -------
    A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                delimiter=',')
            nrows = sum(1 for row in reader)

            if nrows == 0:
                warn('No data in file '+fname)
                return None, None, None, None, None, None, None, None

            traj_ID = np.empty(nrows, dtype=int)
            time_flash_density_max = np.empty(nrows, dtype=datetime.datetime)
            flash_density_max_rank = np.empty(nrows, dtype=float)
            flash_density_max_nflashes = np.empty(nrows, dtype=int)
            flash_density_max_area = np.empty(nrows, dtype=float)
            flash_density_max = np.empty(nrows, dtype=float)
            time_rank_max = np.empty(nrows, dtype=datetime.datetime)
            rank_max = np.empty(nrows, dtype=float)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                delimiter=',')
            for i, row in enumerate(reader):
                traj_ID[i] = int(row['traj ID'])
                time_flash_density_max[i] = datetime.datetime.strptime(
                    row['max flash density time'], '%Y-%m-%d %H:%M:%S')
                flash_density_max_rank[i] = float(
                    row['max flash density rank'])
                flash_density_max_nflashes[i] = int(
                    row['max flash density flashes'])
                flash_density_max_area[i] = float(
                    row['max flash density area'])
                flash_density_max[i] = float(
                    row['max flash density'])
                time_rank_max[i] = datetime.datetime.strptime(
                    row['max rank time'], '%Y-%m-%d %H:%M:%S')
                rank_max[i] = row['max rank']

            csvfile.close()

            return (
                traj_ID, time_flash_density_max, flash_density_max_rank,
                flash_density_max_nflashes, flash_density_max_area,
                flash_density_max, time_rank_max, rank_max)

    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None, None, None, None, None, None


def read_trt_cell_lightning(fname):
    """
    Reads the lightning data of a TRT cell. The file has the following
    fields:
        traj_ID
        yyyymmddHHMM
        lon
        lat
        area
        RANKr
        nflashes
        flash_dens

    Parameters
    ----------
    fname : str
        path of the TRT data file

    Returns
    -------
    A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                delimiter=',')
            nrows = sum(1 for row in reader)

            if nrows == 0:
                warn('No data in file '+fname)
                return None, None, None, None, None, None, None, None

            traj_ID = np.empty(nrows, dtype=int)
            time_cell = np.empty(nrows, dtype=datetime.datetime)
            lon_cell = np.empty(nrows, dtype=float)
            lat_cell = np.empty(nrows, dtype=float)
            area_cell = np.empty(nrows, dtype=float)
            rank_cell = np.empty(nrows, dtype=float)
            nflashes_cell = np.ma.empty(nrows, dtype=float)
            flash_dens_cell = np.ma.empty(nrows, dtype=float)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                delimiter=',')
            for i, row in enumerate(reader):
                traj_ID[i] = int(row['traj_ID'])
                time_cell[i] = datetime.datetime.strptime(
                    row['yyyymmddHHMM'], '%Y%m%d%H%M')
                lon_cell[i] = float(row['lon'])
                lat_cell[i] = float(row['lat'])
                area_cell[i] = float(row['area'])
                rank_cell[i] = float(row['RANKr'])
                nflashes_cell[i] = float(row['nflashes'])
                flash_dens_cell[i] = float(row['flash_dens'])

            csvfile.close()

            nflashes_cell = np.ma.masked_values(nflashes_cell, get_fillvalue())
            flash_dens_cell = np.ma.masked_values(flash_dens_cell, get_fillvalue())

            return (
                traj_ID, time_cell, lon_cell, lat_cell, area_cell, rank_cell,
                nflashes_cell, flash_dens_cell)

    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None, None, None, None, None, None


def read_trt_data(fname):
    """
    Reads the TRT data contained in a text file. The file has the following
    fields:
        traj_ID
        yyyymmddHHMM

        Description of ellipsis:
        lon [deg]
        lat [deg]
        ell_L [km] long
        ell_S [km] short
        ell_or [deg] orientation
        area [km2]

        Cell speed:
        vel_x [km/h]
        vel_y [km/h]
        det [dBZ]: detection threshold
        RANKr from 0 to 40 (int)

        Lightning information:
        CG- number (int)
        CG+ number (int)
        CG number (int)
        %CG+ [%]

        Echo top information:
        ET45  [km] echotop 45 max
        ET45m [km] echotop 45 median
        ET15 [km] echotop 15 max
        ET15m [km] echotop 15 median

        VIL and max echo:
        VIL [kg/m2] vertical integrated liquid content
        maxH [km] height of maximum reflectivity (maximum on the cell)
        maxHm [km] height of maximum reflectivity (median per cell)

        POH [%]
        RANK (deprecated)

        standard deviation of the current time step cell velocity respect to
        the previous time:
        Dvel_x [km/h]
        Dvel_y [km/h]

        cell_contour_lon-lat

    Parameters
    ----------
    fname : str
        path of the TRT data file

    Returns
    -------
    A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                (row for row in csvfile if (
                    not row.startswith('#') and
                    not row.startswith('@') and not row.startswith(" ")
                    and row)),
                fieldnames=[
                    'traj_ID', 'yyyymmddHHMM', 'lon', 'lat', 'ell_L', 'ell_S',
                    'ell_or', 'area', 'vel_x', 'vel_y', 'det', 'RANKr', 'CG-',
                    'CG+', 'CG', '%CG+', 'ET45', 'ET45m', 'ET15', 'ET15m',
                    'VIL', 'maxH', 'maxHm', 'POH', 'RANK', 'Dvel_x',
                    'Dvel_y'],
                restkey='cell_contour_lon-lat',
                delimiter=';')
            nrows = sum(1 for row in reader)

            if nrows == 0:
                warn('No data in file '+fname)
                return (
                    None, None, None, None, None, None, None, None, None,
                    None, None, None, None, None, None, None, None, None,
                    None, None, None, None, None, None, None, None, None,
                    None)

            traj_ID = np.empty(nrows, dtype=int)
            yyyymmddHHMM = np.empty(nrows, dtype=datetime.datetime)
            lon = np.empty(nrows, dtype=float)
            lat = np.empty(nrows, dtype=float)
            ell_L = np.empty(nrows, dtype=float)
            ell_S = np.empty(nrows, dtype=float)
            ell_or = np.empty(nrows, dtype=float)
            area = np.empty(nrows, dtype=float)
            vel_x = np.ma.empty(nrows, dtype=float)
            vel_y = np.ma.empty(nrows, dtype=float)
            det = np.ma.empty(nrows, dtype=float)
            RANKr = np.empty(nrows, dtype=int)
            CG_n = np.empty(nrows, dtype=int)
            CG_p = np.empty(nrows, dtype=int)
            CG = np.empty(nrows, dtype=int)
            CG_percent_p = np.ma.empty(nrows, dtype=float)
            ET45 = np.ma.empty(nrows, dtype=float)
            ET45m = np.ma.empty(nrows, dtype=float)
            ET15 = np.ma.empty(nrows, dtype=float)
            ET15m = np.ma.empty(nrows, dtype=float)
            VIL = np.ma.empty(nrows, dtype=float)
            maxH = np.ma.empty(nrows, dtype=float)
            maxHm = np.ma.empty(nrows, dtype=float)
            POH = np.ma.empty(nrows, dtype=float)
            RANK = np.ma.empty(nrows, dtype=float)
            Dvel_x = np.ma.empty(nrows, dtype=float)
            Dvel_y = np.ma.empty(nrows, dtype=float)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                (row for row in csvfile if (
                    not row.startswith('#') and
                    not row.startswith('@') and not row.startswith(" ")
                    and row)),
                fieldnames=[
                    'traj_ID', 'yyyymmddHHMM', 'lon', 'lat', 'ell_L', 'ell_S',
                    'ell_or', 'area', 'vel_x', 'vel_y', 'det', 'RANKr', 'CG-',
                    'CG+', 'CG', '%CG+', 'ET45', 'ET45m', 'ET15', 'ET15m',
                    'VIL', 'maxH', 'maxHm', 'POH', 'RANK', 'Dvel_x',
                    'Dvel_y'],
                restkey='cell_contour_lon-lat',
                delimiter=';')
            cell_contour = []
            for i, row in enumerate(reader):
                traj_ID[i] = int(row['traj_ID'])
                yyyymmddHHMM[i] = datetime.datetime.strptime(
                    row['yyyymmddHHMM'].strip(), '%Y%m%d%H%M')
                lon[i] = float(row['lon'].strip())
                lat[i] = float(row['lat'].strip())
                ell_L[i] = float(row['ell_L'].strip())
                ell_S[i] = float(row['ell_S'].strip())
                ell_or[i] = float(row['ell_or'].strip())
                area[i] = float(row['area'].strip())
                vel_x[i] = float(row['vel_x'].strip())
                vel_y[i] = float(row['vel_y'].strip())
                det[i] = float(row['det'].strip())
                RANKr[i] = int(row['RANKr'].strip())
                CG_n[i] = int(row['CG-'].strip())
                CG_p[i] = int(row['CG+'].strip())
                CG[i] = int(row['CG'].strip())
                CG_percent_p[i] = float(row['%CG+'].strip())
                ET45[i] = float(row['ET45'].strip())
                ET45m[i] = float(row['ET45m'].strip())
                ET15[i] = float(row['ET15'].strip())
                ET15m[i] = float(row['ET15m'].strip())
                VIL[i] = float(row['VIL'].strip())
                maxH[i] = float(row['maxH'].strip())
                maxHm[i] = float(row['maxHm'].strip())
                POH[i] = float(row['POH'].strip())
                RANK[i] = float(row['RANK'].strip())
                Dvel_x[i] = float(row['Dvel_x'].strip())
                Dvel_y[i] = float(row['Dvel_y'].strip())

                cell_contour_list_aux = row['cell_contour_lon-lat']
                nele = len(cell_contour_list_aux)-1
                cell_contour_list = []
                for j in range(nele):
                    cell_contour_list.append(
                        float(cell_contour_list_aux[j].strip()))
                cell_contour_dict = {
                    'lon': cell_contour_list[0::2],
                    'lat': cell_contour_list[1::2]
                }
                cell_contour.append(cell_contour_dict)

            csvfile.close()

            lon = np.ma.masked_invalid(lon)
            lat = np.ma.masked_invalid(lat)
            ell_L = np.ma.masked_invalid(ell_L)
            ell_S = np.ma.masked_invalid(ell_S)
            ell_or = np.ma.masked_invalid(ell_or)
            area = np.ma.masked_invalid(area)
            vel_x = np.ma.masked_invalid(vel_x)
            vel_y = np.ma.masked_invalid(vel_y)
            det = np.ma.masked_invalid(det)
            CG_percent_p = np.ma.masked_invalid(CG_percent_p)
            ET45 = np.ma.masked_invalid(ET45)
            ET45m = np.ma.masked_invalid(ET45m)
            ET15 = np.ma.masked_invalid(ET15)
            ET15m = np.ma.masked_invalid(ET15m)
            VIL = np.ma.masked_invalid(VIL)
            maxH = np.ma.masked_invalid(maxH)
            maxHm = np.ma.masked_invalid(maxHm)
            POH = np.ma.masked_invalid(POH)
            RANK = np.ma.masked_invalid(RANK)
            Dvel_x = np.ma.masked_invalid(Dvel_x)
            Dvel_y = np.ma.masked_invalid(Dvel_y)

            return (
                traj_ID, yyyymmddHHMM, lon, lat, ell_L, ell_S, ell_or, area,
                vel_x, vel_y, det, RANKr, CG_n, CG_p, CG, CG_percent_p, ET45,
                ET45m, ET15, ET15m, VIL, maxH, maxHm, POH, RANK, Dvel_x,
                Dvel_y, cell_contour)

    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return (
            None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None)


def read_trt_traj_data(fname):
    """
    Reads the TRT cell data contained in a text file. The file has the following
    fields:
        traj_ID
        yyyymmddHHMM

        lon [deg]
        lat [deg]
        ell_L [km] long
        ell_S [km] short
        ell_or [deg] orientation
        area [km2]

        vel_x [km/h] cell speed
        vel_y [km/h]
        det [dBZ] detection threshold
        RANKr from 0 to 40 (int)

        CG- number (int)
        CG+ number (int)
        CG number (int)
        %CG+ [%]

        ET45  [km] echotop 45 max
        ET45m [km] echotop 45 median
        ET15 [km] echotop 15 max
        ET15m [km] echotop 15 median
        VIL [kg/m2] vertical integrated liquid content
        maxH [km] height of maximum reflectivity (maximum on the cell)
        maxHm [km] height of maximum reflectivity (median per cell)
        POH [%]
        RANK (deprecated)

        Standard deviation of the current time step cell velocity respect to
        the previous time:
        Dvel_x [km/h]
        Dvel_y [km/h]

        cell_contour_lon-lat

    Parameters
    ----------
    fname : str
        path of the TRT data file

    Returns
    -------
    A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                (row for row in csvfile if (
                    not row.startswith('#') and
                    not row.startswith('@') and row)),
                delimiter=',')
            nrows = sum(1 for row in reader)

            traj_ID = np.empty(nrows, dtype=int)
            yyyymmddHHMM = np.empty(nrows, dtype=datetime.datetime)
            lon = np.empty(nrows, dtype=float)
            lat = np.empty(nrows, dtype=float)
            ell_L = np.empty(nrows, dtype=float)
            ell_S = np.empty(nrows, dtype=float)
            ell_or = np.empty(nrows, dtype=float)
            area = np.empty(nrows, dtype=float)
            vel_x = np.ma.empty(nrows, dtype=float)
            vel_y = np.ma.empty(nrows, dtype=float)
            det = np.ma.empty(nrows, dtype=float)
            RANKr = np.empty(nrows, dtype=int)
            CG_n = np.empty(nrows, dtype=int)
            CG_p = np.empty(nrows, dtype=int)
            CG = np.empty(nrows, dtype=int)
            CG_percent_p = np.ma.empty(nrows, dtype=float)
            ET45 = np.ma.empty(nrows, dtype=float)
            ET45m = np.ma.empty(nrows, dtype=float)
            ET15 = np.ma.empty(nrows, dtype=float)
            ET15m = np.ma.empty(nrows, dtype=float)
            VIL = np.ma.empty(nrows, dtype=float)
            maxH = np.ma.empty(nrows, dtype=float)
            maxHm = np.ma.empty(nrows, dtype=float)
            POH = np.ma.empty(nrows, dtype=float)
            RANK = np.ma.empty(nrows, dtype=float)
            Dvel_x = np.ma.empty(nrows, dtype=float)
            Dvel_y = np.ma.empty(nrows, dtype=float)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                (row for row in csvfile if (
                    not row.startswith('#') and
                    not row.startswith('@') and row)),
                delimiter=',')

            cell_contour = []
            for i, row in enumerate(reader):
                traj_ID[i] = int(row['traj_ID'])
                yyyymmddHHMM[i] = datetime.datetime.strptime(
                    row['yyyymmddHHMM'].strip(), '%Y%m%d%H%M')
                lon[i] = float(row['lon'].strip())
                lat[i] = float(row['lat'].strip())
                ell_L[i] = float(row['ell_L'].strip())
                ell_S[i] = float(row['ell_S'].strip())
                ell_or[i] = float(row['ell_or'].strip())
                area[i] = float(row['area'].strip())
                vel_x[i] = float(row['vel_x'].strip())
                vel_y[i] = float(row['vel_y'].strip())
                det[i] = float(row['det'].strip())
                RANKr[i] = int(row['RANKr'].strip())
                CG_n[i] = int(row['CG-'].strip())
                CG_p[i] = int(row['CG+'].strip())
                CG[i] = int(row['CG'].strip())
                CG_percent_p[i] = float(row['%CG+'].strip())
                ET45[i] = float(row['ET45'].strip())
                ET45m[i] = float(row['ET45m'].strip())
                ET15[i] = float(row['ET15'].strip())
                ET15m[i] = float(row['ET15m'].strip())
                VIL[i] = float(row['VIL'].strip())
                maxH[i] = float(row['maxH'].strip())
                maxHm[i] = float(row['maxHm'].strip())
                POH[i] = float(row['POH'].strip())
                RANK[i] = float(row['RANK'].strip())
                Dvel_x[i] = float(row['Dvel_x'].strip())
                Dvel_y[i] = float(row['Dvel_y'].strip())

                cell_contour_str_arr = row['cell_contour_lon-lat'].split()
                cell_contour_arr = np.empty(
                    len(cell_contour_str_arr), dtype=float)
                for j, cell_contour_el in enumerate(cell_contour_str_arr):
                    cell_contour_arr[j] = float(cell_contour_el)

                cell_contour_dict = {
                    'lon': cell_contour_arr[0::2],
                    'lat': cell_contour_arr[1::2]
                }
                cell_contour.append(cell_contour_dict)

            csvfile.close()

            lon = np.ma.masked_invalid(lon)
            lat = np.ma.masked_invalid(lat)
            ell_L = np.ma.masked_invalid(ell_L)
            ell_S = np.ma.masked_invalid(ell_S)
            ell_or = np.ma.masked_invalid(ell_or)
            area = np.ma.masked_invalid(area)
            vel_x = np.ma.masked_invalid(vel_x)
            vel_y = np.ma.masked_invalid(vel_y)
            det = np.ma.masked_invalid(det)
            CG_percent_p = np.ma.masked_invalid(CG_percent_p)
            ET45 = np.ma.masked_invalid(ET45)
            ET45m = np.ma.masked_invalid(ET45m)
            ET15 = np.ma.masked_invalid(ET15)
            ET15m = np.ma.masked_invalid(ET15m)
            VIL = np.ma.masked_invalid(VIL)
            maxH = np.ma.masked_invalid(maxH)
            maxHm = np.ma.masked_invalid(maxHm)
            POH = np.ma.masked_invalid(POH)
            RANK = np.ma.masked_invalid(RANK)
            Dvel_x = np.ma.masked_invalid(Dvel_x)
            Dvel_y = np.ma.masked_invalid(Dvel_y)

            return (
                traj_ID, yyyymmddHHMM, lon, lat, ell_L, ell_S, ell_or, area,
                vel_x, vel_y, det, RANKr, CG_n, CG_p, CG, CG_percent_p, ET45,
                ET45m, ET15, ET15m, VIL, maxH, maxHm, POH, RANK, Dvel_x,
                Dvel_y, cell_contour)

    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return (
            None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None)


def read_lightning(fname, filter_data=True):
    """
    Reads lightning data contained in a text file. The file has the following
    fields:
        flashnr: (0 is for noise)
        UTC seconds of the day
        Time within flash (in seconds)
        Latitude (decimal degrees)
        Longitude (decimal degrees)
        Altitude (m MSL)
        Power (dBm)

    Parameters
    ----------
    fname : str
        path of time series file
    filter_data : Boolean
        if True filter noise (flashnr = 0)

    Returns
    -------
    flashnr, time_data, time_in_flash, lat, lon, alt, dBm : tupple
        A tupple containing the read values. None otherwise

    """
    try:
        # get date from file name
        bfile = os.path.basename(fname)
        datetimestr = bfile[0:6]
        fdatetime = datetime.datetime.strptime(datetimestr, '%y%m%d')

        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                csvfile, fieldnames=['flashnr', 'time', 'time_in_flash',
                                     'lat', 'lon', 'alt', 'dBm'],
                delimiter=' ')
            nrows = sum(1 for row in reader)

            flashnr = np.ma.empty(nrows, dtype=int)
            time_in_flash = np.ma.empty(nrows, dtype=float)
            lat = np.ma.empty(nrows, dtype=float)
            lon = np.ma.empty(nrows, dtype=float)
            alt = np.ma.empty(nrows, dtype=float)
            dBm = np.ma.empty(nrows, dtype=float)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                csvfile, fieldnames=['flashnr', 'time', 'time_in_flash',
                                     'lat', 'lon', 'alt', 'dBm'],
                delimiter=' ')

            time_data = list()
            for i, row in enumerate(reader):
                flashnr[i] = int(row['flashnr'])
                time_data.append(fdatetime+datetime.timedelta(
                    seconds=float(row['time'])))
                time_in_flash[i] = float(row['time_in_flash'])
                lat[i] = float(row['lat'])
                lon[i] = float(row['lon'])
                alt[i] = float(row['alt'])
                dBm[i] = float(row['dBm'])

            time_data = np.array(time_data)

            if filter_data:
                flashnr_aux = deepcopy(flashnr)
                flashnr = flashnr[flashnr_aux > 0]
                time_data = time_data[flashnr_aux > 0]
                time_in_flash = time_in_flash[flashnr_aux > 0]
                lat = lat[flashnr_aux > 0]
                lon = lon[flashnr_aux > 0]
                alt = alt[flashnr_aux > 0]
                dBm = dBm[flashnr_aux > 0]

            csvfile.close()

            return flashnr, time_data, time_in_flash, lat, lon, alt, dBm
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None, None, None, None, None


def read_meteorage(fname):
    """
    Reads METEORAGE lightning data contained in a text file. The file has the
    following fields:
        date: date + time + time zone
        lon: longitude [degree]
        lat: latitude [degree]
        intens: amplitude [kilo amperes]
        ns: number of strokes of the flash
        mode: kind of localization [0,15]
        intra: 1 = intra-cloud , 0 = cloud-to-ground
        ax: length of the semi-major axis of the ellipse [km]
        ki2: standard deviation on the localization computation (Ki^2)
        ecc: eccentricity (major-axis / minor-axis)
        incl: ellipse inclination (angle with respect to the North, +90° is
            East) [degrees]
        sind: stroke index within the flash

    Parameters
    ----------
    fname : str
        path of time series file

    Returns
    -------
    stroke_time, lon, lat, intens, ns, mode, intra, ax, ki2, ecc, incl,
    sind : tupple
        A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                csvfile, fieldnames=['date', 'lon', 'lat', 'intens', 'ns',
                                     'mode', 'intra', 'ax', 'ki2', 'ecc',
                                     'incl', 'sind', 'par1', 'par2', 'par3',
                                     'par4'],
                delimiter='|')
            nrows = sum(1 for row in reader)

            stroke_time = np.empty(nrows, dtype=datetime.datetime)
            lon = np.empty(nrows, dtype=float)
            lat = np.empty(nrows, dtype=float)
            intens = np.empty(nrows, dtype=float)
            ns = np.empty(nrows, dtype=int)
            mode = np.empty(nrows, dtype=int)
            intra = np.empty(nrows, dtype=int)
            ax = np.empty(nrows, dtype=float)
            ki2 = np.empty(nrows, dtype=float)
            ecc = np.empty(nrows, dtype=float)
            incl = np.empty(nrows, dtype=float)
            sind = np.empty(nrows, dtype=int)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                csvfile, fieldnames=['date', 'lon', 'lat', 'intens', 'ns',
                                     'mode', 'intra', 'ax', 'ki2', 'ecc',
                                     'incl', 'sind', 'par1', 'par2', 'par3',
                                     'par4'],
                delimiter='|')

            for i, row in enumerate(reader):
                stroke_time[i] = datetime.datetime.strptime(
                    row['date'], '%d.%m.%Y %H:%M:%S.%f UTC')
                lon[i] = float(row['lon'])
                lat[i] = float(row['lat'])
                intens[i] = float(row['intens'])
                ns[i] = int(row['ns'])
                mode[i] = int(row['mode'])
                intra[i] = int(row['intra'])
                ax[i] = float(row['ax'])
                ki2[i] = float(row['ki2'])
                ecc[i] = float(row['ecc'])
                incl[i] = float(row['incl'])
                sind[i] = int(float(row['sind']))-1

            csvfile.close()

            return (
                stroke_time, lon, lat, intens, ns, mode, intra, ax, ki2, ecc,
                incl, sind)
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return (
            None, None, None, None, None, None, None, None, None, None, None,
            None)


def read_lightning_traj(fname):
    """
    Reads lightning trajectory data contained in a csv file. The file has the following
    fields:
        Date
        UTC [seconds since midnight]
        # Flash
        Flash Power (dBm)
        Value at flash
        Mean value in a 3x3x3 polar box
        Min value in a 3x3x3 polar box
        Max value in a 3x3x3 polar box
        # valid values in the polar box

    Parameters
    ----------
    fname : str
        path of time series file

    Returns
    -------
    time_flash, flashnr, dBm, val_at_flash, val_mean, val_min, val_max,
    nval : tupple
        A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                fieldnames=['Date', 'UTC', 'flashnr', 'dBm', 'at_flash',
                            'mean', 'min', 'max', 'nvalid'],
                delimiter=',')
            nrows = sum(1 for row in reader)

            time_flash = np.empty(nrows, dtype=datetime.datetime)
            flashnr = np.empty(nrows, dtype=int)
            dBm = np.empty(nrows, dtype=float)
            val_at_flash = np.ma.empty(nrows, dtype=float)
            val_mean = np.ma.empty(nrows, dtype=float)
            val_min = np.ma.empty(nrows, dtype=float)
            val_max = np.ma.empty(nrows, dtype=float)
            nval = np.empty(nrows, dtype=int)

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                fieldnames=['Date', 'UTC', 'flashnr', 'dBm', 'at_flash',
                            'mean', 'min', 'max', 'nvalid'],
                delimiter=',')

            for i, row in enumerate(reader):
                date_flash_aux = datetime.datetime.strptime(
                    row['Date'], '%d-%b-%Y')
                time_flash_aux = float(row['UTC'])
                time_flash[i] = date_flash_aux+datetime.timedelta(
                    seconds=time_flash_aux)

                flashnr[i] = int(float(row['flashnr']))
                dBm[i] = float(row['dBm'])
                val_at_flash[i] = float(row['at_flash'])
                val_mean[i] = float(row['mean'])
                val_min[i] = float(row['min'])
                val_max[i] = float(row['max'])
                nval[i] = int(float(row['nvalid']))

            csvfile.close()

            val_at_flash = np.ma.masked_invalid(val_at_flash)
            val_mean = np.ma.masked_invalid(val_mean)
            val_min = np.ma.masked_invalid(val_min)
            val_max = np.ma.masked_invalid(val_max)

            return (time_flash, flashnr, dBm, val_at_flash, val_mean, val_min,
                    val_max, nval)

    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None, None, None, None, None, None


def read_lightning_all(fname,
                       labels=['hydro [-]', 'KDPc [deg/Km]', 'dBZc [dBZ]',
                               'RhoHVc [-]', 'TEMP [deg C]', 'ZDRc [dB]']):
    """
    Reads a file containing lightning data and co-located polarimetric data.
    fields:
        flashnr
        time data
        Time within flash (in seconds)
        Latitude (decimal degrees)
        Longitude (decimal degrees)
        Altitude (m MSL)
        Power (dBm)
        Polarimetric values at flash position

    Parameters
    ----------
    fname : str
        path of time series file
    labels : list of str
        The polarimetric variables labels

    Returns
    -------
    flashnr, time_data, time_in_flash, lat, lon, alt, dBm,
    pol_vals_dict : tupple
        A tupple containing the read values. None otherwise

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                row for row in csvfile if not row.startswith('#'))
            nrows = sum(1 for row in reader)

            flashnr = np.ma.empty(nrows, dtype=int)
            time_data = np.ma.empty(nrows, dtype=datetime.datetime)
            time_in_flash = np.ma.empty(nrows, dtype=float)
            lat = np.ma.empty(nrows, dtype=float)
            lon = np.ma.empty(nrows, dtype=float)
            alt = np.ma.empty(nrows, dtype=float)
            dBm = np.ma.empty(nrows, dtype=float)
            pol_vals_dict = dict()
            for label in labels:
                pol_vals_dict.update({label: np.ma.empty(nrows, dtype=float)})

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                row for row in csvfile if not row.startswith('#'))

            for i, row in enumerate(reader):
                flashnr[i] = int(row['flashnr'])
                time_data[i] = datetime.datetime.strptime(row['time_data'], '%Y-%m-%d %H:%M:%S.%f')
                time_in_flash[i] = float(row['time_in_flash'])
                lat[i] = float(row['lat'])
                lon[i] = float(row['lon'])
                alt[i] = float(row['alt'])
                dBm[i] = float(row['dBm'])

                for label in labels:
                    pol_vals_dict[label][i] = float(row[label])

            csvfile.close()

            for label in labels:
                pol_vals_dict[label] = np.ma.masked_values(pol_vals_dict[label], get_fillvalue())

            return flashnr, time_data, time_in_flash, lat, lon, alt, dBm, pol_vals_dict
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None, None, None, None, None, None


def get_sensor_data(date, datatype, cfg):
    """
    Gets data from a point measurement sensor (rain gauge or disdrometer)

    Parameters
    ----------
    date : datetime object
        measurement date

    datatype : str
        name of the data type to read

    cfg : dictionary
        dictionary containing sensor information

    Returns
    -------
    sensordate , sensorvalue, label, period : tupple
        date, value, type of sensor and measurement period

    """
    if cfg['sensor'] == 'rgage':
        datapath = cfg['smnpath']+date.strftime('%Y%m')+'/'
        datafile = date.strftime('%Y%m%d')+'_' + cfg['sensorid']+'.csv'
        _, sensordate, _, _, _, sensorvalue, _, _ = read_smn(
            datapath+datafile)
        if sensordate is None:
            return None, None, None, None
        label = 'RG'
        period = (sensordate[1]-sensordate[0]).total_seconds()
    elif cfg['sensor'] == 'disdro':
        if (datatype == 'dBZ') or (datatype == 'dBZc'):
            sensor_datatype = 'dBZ'
        else:
            sensor_datatype = datatype

        datapath = (
            cfg['disdropath']+cfg['sensorid']+'/scattering/' +
            date.strftime('%Y')+'/'+date.strftime('%Y%m')+'/')
        datafile = (
            date.strftime('%Y%m%d')+'_'+cfg['sensorid']+'_'+cfg['location'] +
            '_'+str(cfg['freq'])+'GHz_'+sensor_datatype+'_el'+str(cfg['ele']) +
            '.csv')

        sensordate, _, sensorvalue, _ = read_disdro(datapath+datafile)
        if sensordate is None:
            return None, None, None, None
        label = 'Disdro'
        period = (sensordate[1]-sensordate[0]).total_seconds()

    else:
        warn('Unknown sensor: '+cfg['sensor'])
        return None, None, None, None

    return sensordate, sensorvalue, label, period


def read_smn(fname):
    """
    Reads SwissMetNet data contained in a csv file

    Parameters
    ----------
    fname : str
        path of time series file

    Returns
    -------
    smn_id, date , pressure, temp, rh, precip, wspeed, wdir : tupple
        The read values

    """
    fill_value = 10000000.0
    try:
        with open(fname, 'r', newline='') as csvfile:
            # first count the lines
            reader = csv.DictReader(csvfile)
            nrows = sum(1 for row in reader)
            smn_id = np.ma.empty(nrows, dtype='float32')
            pressure = np.ma.empty(nrows, dtype='float32')
            temp = np.ma.empty(nrows, dtype='float32')
            rh = np.ma.empty(nrows, dtype='float32')
            precip = np.ma.empty(nrows, dtype='float32')
            wspeed = np.ma.empty(nrows, dtype='float32')
            wdir = np.ma.empty(nrows, dtype='float32')

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(csvfile)
            date = list()
            for i, row in enumerate(reader):
                smn_id[i] = float(row['StationID'])
                date.append(datetime.datetime.strptime(
                    row['DateTime'], '%Y%m%d%H%M%S'))
                pressure[i] = float(row['AirPressure'])
                temp[i] = float(row['2mTemperature'])
                rh[i] = float(row['RH'])
                precip[i] = float(row['Precipitation'])
                wspeed[i] = float(row['Windspeed'])
                wdir[i] = float(row['Winddirection'])

            pressure = np.ma.masked_values(pressure, fill_value)
            temp = np.ma.masked_values(temp, fill_value)
            rh = np.ma.masked_values(rh, fill_value)
            precip = np.ma.masked_values(precip, fill_value)
            wspeed = np.ma.masked_values(wspeed, fill_value)
            wdir = np.ma.masked_values(wdir, fill_value)

            # convert precip from mm/10min to mm/h
            precip *= 6.

            csvfile.close()

            return smn_id, date, pressure, temp, rh, precip, wspeed, wdir
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None, None, None, None, None, None


def read_smn2(fname):
    """
    Reads SwissMetNet data contained in a csv file with format
    station,time,value

    Parameters
    ----------
    fname : str
        path of time series file

    Returns
    -------
    smn_id, date , value : tupple
        The read values

    """
    try:
        with open(fname, 'r', newline='') as csvfile:
            # skip the first 2 lines
            next(csvfile)
            next(csvfile)

            # first count the lines
            reader = csv.DictReader(
                csvfile, fieldnames=['StationID', 'DateTime', 'Value'])
            nrows = sum(1 for row in reader)

            if nrows == 0:
                warn('Empty file '+fname)
                return None, None, None
            smn_id = np.ma.empty(nrows, dtype=int)
            value = np.ma.empty(nrows, dtype=float)

            # now read the data
            csvfile.seek(0)

            # skip the first 2 lines
            next(csvfile)
            next(csvfile)

            reader = csv.DictReader(
                csvfile, fieldnames=['StationID', 'DateTime', 'Value'])
            date = list()
            for i, row in enumerate(reader):
                smn_id[i] = float(row['StationID'])
                date.append(datetime.datetime.strptime(
                    row['DateTime'], '%Y%m%d%H%M%S'))
                value[i] = float(row['Value'])

            csvfile.close()

            return smn_id, date, value
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return None, None, None


def read_disdro_scattering(fname):
    """
    Reads scattering parameters computed from disdrometer data contained in a
    text file

    Parameters
    ----------
    fname : str
        path of time series file

    Returns
    -------
    date, preciptype, lwc, rr, zh, zv, zdr, ldr, ah, av, adiff, kdp, deltaco,
    rhohv : tupple
        The read values

    """
    try:
        with open(fname, 'r', newline='', encoding='utf-8', errors='ignore') as csvfile:
            # skip the first line
            next(csvfile)

            # first count the lines
            reader = csv.DictReader(
                csvfile, fieldnames=['date', 'preciptype', 'lwc', 'rr', 'zh',
                                     'zv', 'zdr', 'ldr', 'ah', 'av', 'adiff',
                                     'kdp', 'deltaco', 'rhohv'],
                dialect='excel-tab')
            nrows = sum(1 for row in reader)

            preciptype = np.ma.empty(nrows, dtype='float32')
            lwc = np.ma.empty(nrows, dtype='float32')
            rr = np.ma.empty(nrows, dtype='float32')
            zh = np.ma.empty(nrows, dtype='float32')
            zv = np.ma.empty(nrows, dtype='float32')
            zdr = np.ma.empty(nrows, dtype='float32')
            ldr = np.ma.empty(nrows, dtype='float32')
            ah = np.ma.empty(nrows, dtype='float32')
            av = np.ma.empty(nrows, dtype='float32')
            adiff = np.ma.empty(nrows, dtype='float32')
            kdp = np.ma.empty(nrows, dtype='float32')
            deltaco = np.ma.empty(nrows, dtype='float32')
            rhohv = np.ma.empty(nrows, dtype='float32')

            # now read the data
            csvfile.seek(0)
            # skip the first line
            next(csvfile)

            reader = csv.DictReader(
                csvfile, fieldnames=['date', 'preciptype', 'lwc', 'rr', 'zh',
                                     'zv', 'zdr', 'ldr', 'ah', 'av', 'adiff',
                                     'kdp', 'deltaco', 'rhohv'],
                dialect='excel-tab')
            date = list()
            for i, row in enumerate(reader):
                date.append(datetime.datetime.strptime(
                    row['date'], '%Y-%m-%d %H:%M:%S'))
                preciptype[i] = float(row['preciptype'])
                lwc[i] = float(row['lwc'])
                rr[i] = float(row['rr'])
                zh[i] = float(row['zh'])
                zv[i] = float(row['zv'])
                zdr[i] = float(row['zdr'])
                ldr[i] = float(row['ldr'])
                ah[i] = float(row['ah'])
                av[i] = float(row['av'])
                adiff[i] = float(row['adiff'])
                kdp[i] = float(row['kdp'])
                deltaco[i] = float(row['deltaco'])
                rhohv[i] = float(row['rhohv'])

            csvfile.close()

            return (date, preciptype, lwc, rr, zh, zv, zdr, ldr, ah, av,
                    adiff, kdp, deltaco, rhohv)
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return (None, None, None, None, None, None, None, None, None, None,
                None, None, None)


def read_disdro(fname):
    """
    Reads scattering parameters computed from disdrometer data contained in a
    text file

    Parameters
    ----------
    fname : str
        path of time series file

    Returns
    -------
    date, preciptype, variable, scattering temperature: tuple
        The read values

    """
    try:
        var = re.search('GHz_(.{,7})_el', fname).group(1)
    except AttributeError:
        # AAA, ZZZ not found in the original string
        var = '' # apply your error handling
    try:
        with open(fname, 'r', newline='', encoding='utf-8', errors='ignore') as csvfile:
            # first count the lines
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                delimiter=',')
            nrows = sum(1 for row in reader)

            variable = np.ma.empty(nrows, dtype='float32')
            scatt_temp = np.ma.empty(nrows, dtype='float32')

            # now read the data
            csvfile.seek(0)
            reader = csv.DictReader(
                (row for row in csvfile if not row.startswith('#')),
                delimiter=',')
            i = 0
            date = list()
            preciptype = list()
            for row in reader:
                date.append(datetime.datetime.strptime(
                    row['date'], '%Y-%m-%d %H:%M:%S'))
                preciptype.append(row['Precip Code'])
                variable[i] = float(row[var])
                scatt_temp[i] = float(row['Scattering Temp [deg C]'])
                i += 1
            variable = np.ma.masked_values(variable, get_fillvalue())
            np.ma.set_fill_value(variable, get_fillvalue())
            csvfile.close()

            return (date, preciptype, variable, scatt_temp)
    except EnvironmentError as ee:
        warn(str(ee))
        warn('Unable to read file '+fname)
        return (None, None, None, None)
