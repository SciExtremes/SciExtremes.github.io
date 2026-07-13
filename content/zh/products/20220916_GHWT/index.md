---
title: 'GHWT：全球热浪工具箱'
summary: '全球热浪工具箱（GHWT）用于生成1971年至2100年的热浪矩阵。'
date: 2022-09-16

links:
- name: URL
  url: https://doi.org/10.6084/m9.figshare.17075660.v6


# Featured image
# Place an image named `featured.jpg/png` in this page's folder and customize its options here.
image:
  caption: '工具界面'

authors:
  - Cong-Yin

tags:
  - 热浪
  - 数据
  - 工具
---

本研究利用三套历史再分析数据和多情景CMIP6模式数据，开发了全球热浪工具箱（GHWT），用于生成1971年至2100年的热浪矩阵。

我们采用CRU-JRA、ERA5和GLDAS三套历史逐小时气候数据，以及GFDL-ESM4在三种共享社会经济路径（SSPs）下的未来逐日气候数据，构建了一套长时序全球热浪记录数据集。这些数据集基于35 °C以上的恒定阈值、90%以上的百分位阈值以及3天以上的持续时间阈值。其中的Python文件为全球热浪工具箱的源代码，可用于根据自定义阈值生成热浪记录。