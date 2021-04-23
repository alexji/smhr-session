#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import logging
import numpy as np
import os
import re
from collections import OrderedDict
from hashlib import md5

from astropy.io import fits
from astropy.stats import biweight_scale, sigma_clip
from scipy import interpolate, ndimage, polyfit, poly1d, optimize as op, signal
from ..robust_polyfit import polyfit as rpolyfit
from .spectrum import Spectrum1D

logger = logging.getLogger(__name__)

#def find_peaks(flux, cont=None, noise=None, detection_sigma=2.0):
#    # Subtract continuum:
#    if cont is not None: flux = flux - cont
#    
#    # Find threshold for peak finding
#    if noise is None:
#        clipped = sigma_clip(flux)
#        noise = biweight_scale(clipped)
#    thresh = detection_sigma * noise
#    
#    # 1st derivative for peak finding
#    dflux = np.gradient(flux)
#    ii1 = flux > thresh
#    ii2 = dflux >= 0
#    ii3 = np.zeros_like(ii2)
#    ii3[:-1] = dflux[1:] < 0
#    peaklocs = ii1 & ii2 & ii3
#    peaklocs[mask] = False
#    peakindices = np.where(peaklocs)[0]

def find_peaks(flux,
               window = 51,niter = 5,
               clip_iter = 5,clip_sigma_upper = 5.0,clip_sigma_lower = 5.0,
               detection_sigma = 3.0,
               min_peak_dist_sigma = 5.0,
               gaussian_width = 1.0,
               make_fig=False):
    """
    * Subtract median filter (param "window")
    * Iterate: (param "niter")
        * Sigma clip, estimate noise (params clip_iter, clip_sigma_upper clip_sigma_lower)
        * Find peaks (param detection_sigma)
        * Remove peaks too close to previous (param min_peak_dist_sigma)
        * Fit Gaussians to peaks (initialize width at param gaussian_width)
    Returns:
        allpeakx: locations of peaks
        fullmodel: the model of all the gaussians
        If make_fig=True: fig, a plot showing all the peaks found at each iteration.
    """
    # This is the data we will try to fit with a
    # combination of Gaussians
    xarr = np.arange(len(flux))
    flux = flux - signal.medfilt(flux,window)
    continuum = models.Linear1D(slope=0, intercept=0)
    fullmodel = continuum
    
    allpeakx = []
    allpeaksigma = []
    
    fitter = fitting.LevMarLSQFitter()
    if make_fig: fig, axes = plt.subplots(niter)
    for iiter in range(niter):
        # Subtract existing peaks
        tflux = flux - fullmodel(xarr)
        # Estimate noise
        cflux = sigma_clip(tflux, 
                           iters=clip_iter,
                           sigma_upper=clip_sigma_upper,
                           sigma_lower=clip_sigma_lower)
        noise = np.std(cflux)
        # Find peaks in residual using gradient = 0
        # Only keep peaks above detection threshold
        deriv = np.gradient(tflux)
        peaklocs = (deriv[:-1] >= 0) & (deriv[1:] < 0) & \
            (tflux[:-1] > detection_sigma * noise)
        peakx = np.where(peaklocs)[0]
        peaky = flux[:-1][peaklocs]
        # Prune peaks too close to existing peaks
        peaks_to_keep = np.ones_like(peakx, dtype=bool)
        for ix,x in enumerate(peakx):
            z = (x-np.array(allpeakx))/np.array(allpeaksigma)
            if np.any(np.abs(z) < min_peak_dist_sigma):
                peaks_to_keep[ix] = False
        peakx = peakx[peaks_to_keep]
        peaky = peaky[peaks_to_keep]
        
        # Add new peaks to the model
        for x, y in zip(peakx, peaky):
            g = models.Gaussian1D(amplitude=y, mean=x,
                                  stddev=gaussian_width)
            fullmodel = fullmodel + g
        print("iter {}: {} peaks (found {}, added {})".format(
                iiter, fullmodel.n_submodels()-1,
                len(peaks_to_keep), len(peakx)))
        # Fit the full model
        fullmodel = fitter(fullmodel, xarr, flux, maxiter=200*(fullmodel.parameters.size+1))
        print(fitter.fit_info["message"], fitter.fit_info["ierr"])
        # Extract peak x and sigma
        peak_x_indices = np.where(["mean_" in param for param in fullmodel.param_names])[0]
        peak_y_indices = peak_x_indices - 1
        peak_sigma_indices = peak_x_indices + 1
        allpeakx = fullmodel.parameters[peak_x_indices]
        allpeaky = fullmodel.parameters[peak_y_indices]
        allpeaksigma = fullmodel.parameters[peak_sigma_indices]
        # Make a plot
        if make_fig:
            try:
                ax = axes[iiter]
            except:
                ax = axes
            ax.plot(xarr,flux)
            ax.plot(peakx,peaky,'ro')
            ax.plot(xarr,fullmodel(xarr), lw=1)
            ax.axhspan(-noise,+noise,color='k',alpha=.2)
            ax.plot(xarr,flux-fullmodel(xarr))
            ax.vlines(allpeakx, allpeaky*1.1, allpeaky*1.1+300, color='r', lw=1)
    if make_fig: return allpeakx, fullmodel, fig
    return allpeakx, fullmodel
