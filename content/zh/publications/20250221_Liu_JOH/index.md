---
title: A Transformer-based method to simulate multi-scale soil moisture
authors:
- Yangxiaoyue Liu
- Ying Xin
- me_zh
date: '2025-07-01'
publishDate: '2025-08-07T06:33:17.655730Z'
publication_types:
- article-journal
publication: '*Journal of Hydrology*'
doi: 10.1016/j.jhydrol.2025.132900
abstract: 'The Transformer model, as an emerging deep learning method, shows great
  potential in spatiotemporal sequence-related simulation tasks. However, there is
  very limited understanding of its performance in soil moisture (SM) simulation.
  Here, we present a Transformer-based SM simulation network (SMSNet) to improve the
  quality of the widely used Soil Moisture Active Passive (SMAP) SM product by reconstructing
  and downscaling the pixels, and obtain daily SM products with resolutions of 9 km
  and 1 km. The model employs spatiotemporal attention in separate Transformer structures
  to extract patterns of 10 dynamic (MODIS Bands 1–7, land cover, land surface temperature,
  and precipitation) and 8 static variables (soil bulk density, clay content, gravel
  content, sand content, silt content, digital elevation model, latitude, and longitude)
  to establish the relationship between variable pattern and SMAP SM distribution.
  The SM product reconstructed by SMSNet shows good agreement with in-situ measurements
  (SCAN network: R = 0.639, RMSE = 0.086 m3/m3. UCSRN network: R = 0.665, RMSE = 0.097 m3/m3)
  at the Continental United States. Moreover, it can effectively mitigate the overestimation
  degree of SMAP SM and improve the accuracy in forest. The seamless mapping of SMAP
  SM is achieved using reconstructed SM to fill the gap, and the gap-filling SM exhibits
  reasonable spatiotemporal pattern. The downscaled 1 km SM performs similar accuracy
  degrees to those of the reconstructed ones, proving the applicability of transferring
  9 km scale established SMSNet to 1 km scale SM simulation. The downscaled dataset
  can provide detailed SM characteristics, which further enhances the merit of SMAP
  SM at regional analysis. Moreover, both reconstructed and downscaled SMs exhibit
  accuracy superiority compared to the corresponding results from Cubic Spline Interpolation,
  Random Forest, and Convolutional Neural Network. Overall, our study highlights the
  benefits and potential of SMSNet in generating SM products with favorable accuracy
  over diverse and vast regions.'
tags:
- 降尺度  
- 重建  
- 模拟  
- 土壤湿度  
- Transformer（变换器）模型  
links:
- name: URL
  url: https://www.sciencedirect.com/science/article/pii/S0022169425002380
---
