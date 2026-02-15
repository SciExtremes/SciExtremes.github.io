---
title: 'GHWT: Global Heat Wave Toolbox'
summary: 'Global Heat Wave Toolbox (GHWT) was developed to generate heat wave matrix from 1971 to 2100.'
date: 2022-09-16

links:
- name: URL
  url: https://doi.org/10.6084/m9.figshare.17075660.v6


# Featured image
# Place an image named `featured.jpg/png` in this page's folder and customize its options here.
image:
  caption: 'Tool interface'

authors:
  - me_en

tags:
  - Heat Waves
  - Data
  - Tool
---

Using three historical reanalysis data and multi scenario CMIP6 modeled data, Global Heat Wave Toolbox (GHWT) was developed to generate heat wave matrix from 1971 to 2100.

A long-term global heat wave record dataset was constructed using three historical hourly climate data of CRU-JRA, ERA5 and GLDAS and future daily climate data of GFDL-ESM4 under three SSPS (Shared Socioeconomic Pathways). These datasets are based on constant thresholds over 35 °C, percentile thresholds over 90%, and duration thresholds over 3 days. The Python file is the source code for the Global Heat Wave Toolbox, which can be used to generate heat wave records based on custom thresholds.