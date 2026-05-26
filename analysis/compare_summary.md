# Probe Battery — Finetuned vs Baseline

## 之总览

| dim | n | ft_wenyan/100han | bl_wenyan/100han | Δwenyan | ft_modern/100han | bl_modern/100han | Δmodern | ft_latin% | bl_latin% |
|---|---|---|---|---|---|---|---|---|---|
| pre_1424_control | 17 | 11.946 | 1.343 | +10.60 | 0.0 | 0.0 | +0.00 | 1.1% | 0.1% |
| 1424_to_1900 | 17 | 12.256 | 1.691 | +10.56 | 0.0 | 0.223 | -0.22 | 0.8% | 0.0% |
| post_1900 | 17 | 10.938 | 1.824 | +9.11 | 0.728 | 2.199 | -1.47 | 3.1% | 1.1% |
| cosmology | 17 | 15.102 | 2.879 | +12.22 | 0.0 | 0.415 | -0.41 | 0.8% | 0.0% |
| cross_civ | 17 | 8.714 | 1.719 | +7.00 | 0.318 | 0.048 | +0.27 | 0.8% | 0.5% |
| meta | 15 | 12.415 | 1.431 | +10.98 | 0.092 | 1.229 | -1.14 | 2.1% | 0.7% |

## Key signals

- 总 wenyan marker/100han: ft=11.885, bl=1.822, Δ=+10.06
- 总 modern token/100han: ft=0.192, bl=0.675, Δ=-0.48
- post_1900 dim 之 modern token Δ: ft=0.728, bl=2.199
- cross_civ dim 之 modern token Δ: ft=0.318, bl=0.048