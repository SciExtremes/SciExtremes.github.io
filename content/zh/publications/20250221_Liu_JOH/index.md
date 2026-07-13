---
title: 一种基于Transformer的多尺度土壤湿度模拟方法
authors:
- Yangxiaoyue Liu
- Ying Xin
- Cong-Yin
date: '2025-07-01'
publishDate: '2025-08-07T06:33:17.655730Z'
publication_types:
- article-journal
publication: '*Journal of Hydrology*'
doi: 10.1016/j.jhydrol.2025.132900
abstract: 'Transformer模型作为一种新兴的深度学习方法，在时空序列相关的模拟任务中展现出巨大潜力。然而，人们对其在土壤湿度（SM）模拟中的表现了解十分有限。本研究提出了一种基于Transformer的土壤湿度模拟网络（SMSNet），通过对像元进行重构和降尺度，提升广泛使用的主被动土壤湿度（SMAP）土壤湿度产品的质量，并获得分辨率为9公里和1公里的逐日土壤湿度产品。该模型在相互独立的Transformer结构中采用时空注意力机制，提取10个动态变量（MODIS第1—7波段、土地覆盖、地表温度和降水）和8个静态变量（土壤容重、黏粒含量、砾石含量、砂粒含量、粉粒含量、数字高程模型、纬度和经度）的模式，建立变量模式与SMAP土壤湿度分布之间的关系。在美国本土，SMSNet重构的土壤湿度产品与实地观测吻合良好（SCAN观测网：R = 0.639，RMSE = 0.086 m³/m³；UCSRN观测网：R = 0.665，RMSE = 0.097 m³/m³）。此外，它能够有效缓解SMAP土壤湿度的高估程度，并提升森林中的精度。利用重构的土壤湿度填补空缺，实现了SMAP土壤湿度的无缝制图，且填补后的土壤湿度呈现出合理的时空格局。降尺度后的1公里土壤湿度精度与重构结果相当，证明了将9公里尺度建立的SMSNet迁移至1公里尺度土壤湿度模拟的可行性。降尺度数据集能够提供详细的土壤湿度特征，进一步增强了SMAP土壤湿度在区域分析中的价值。此外，与三次样条插值、随机森林和卷积神经网络的相应结果相比，重构和降尺度的土壤湿度均表现出精度优势。总体而言，本研究凸显了SMSNet在多样化、大范围区域生成高精度土壤湿度产品方面的优势与潜力。'
tags:
- 降尺度
- 重构
- 模拟
- 土壤湿度
- Transformer
links:
- name: URL
  url: https://www.sciencedirect.com/science/article/pii/S0022169425002380
---