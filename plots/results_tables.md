## Main Results: AIC / F1 / EM by Dataset and Budget

Bold = best value in that row group (dataset x budget).


### 2wikimultihopqa

| Budget | Method | AIC | F1 | EM | Avg Tokens |
|---|---|---|---|---|---|
| 80 | Top-K | 0.405 | 0.127 | 0.065 | 77.0 |
|  | MMR | **0.425** | **0.141** | **0.070** | 77.1 |
|  | Focused | 0.400 | 0.122 | 0.065 | 77.0 |
|  | AnswerSurvival | 0.395 | 0.119 | 0.065 | 76.8 |
| 160 | Top-K | 0.515 | 0.114 | **0.060** | 156.7 |
|  | MMR | 0.500 | **0.117** | **0.060** | 157.0 |
|  | Focused | 0.540 | 0.108 | **0.060** | 156.8 |
|  | AnswerSurvival | **0.560** | 0.109 | **0.060** | 155.9 |
| 256 | Top-K | 0.625 | 0.104 | **0.055** | 250.9 |
|  | MMR | 0.620 | **0.107** | **0.055** | 250.6 |
|  | Focused | 0.630 | 0.102 | **0.055** | 251.0 |
|  | AnswerSurvival | **0.640** | 0.100 | **0.055** | 247.6 |
| 384 | Top-K | 0.710 | **0.095** | **0.055** | 349.2 |
|  | MMR | **0.725** | 0.093 | **0.055** | 349.3 |
|  | Focused | 0.710 | 0.093 | **0.055** | 349.2 |
|  | AnswerSurvival | 0.720 | 0.091 | **0.055** | 346.1 |
| 512 | Top-K | 0.740 | **0.095** | **0.055** | 374.7 |
|  | MMR | **0.745** | 0.092 | **0.055** | 374.9 |
|  | Focused | 0.740 | 0.093 | **0.055** | 374.7 |
|  | AnswerSurvival | 0.740 | 0.091 | **0.055** | 374.3 |

### hotpotqa

| Budget | Method | AIC | F1 | EM | Avg Tokens |
|---|---|---|---|---|---|
| 80 | Top-K | 0.480 | 0.061 | **0.010** | 76.3 |
|  | MMR | **0.520** | 0.057 | 0.005 | 76.1 |
|  | Focused | 0.435 | 0.059 | **0.010** | 76.1 |
|  | AnswerSurvival | 0.475 | **0.062** | **0.010** | 76.1 |
| 160 | Top-K | **0.625** | 0.055 | **0.005** | 155.7 |
|  | MMR | **0.625** | **0.058** | **0.005** | 155.9 |
|  | Focused | 0.620 | 0.050 | **0.005** | 155.6 |
|  | AnswerSurvival | **0.625** | 0.055 | **0.005** | 155.3 |
| 256 | Top-K | **0.720** | 0.052 | **0.005** | 250.4 |
|  | MMR | 0.715 | **0.055** | **0.005** | 251.4 |
|  | Focused | 0.710 | 0.052 | **0.005** | 251.3 |
|  | AnswerSurvival | **0.720** | 0.053 | **0.005** | 249.8 |
| 384 | Top-K | 0.805 | 0.054 | **0.005** | 374.0 |
|  | MMR | 0.785 | **0.055** | **0.005** | 374.4 |
|  | Focused | **0.810** | 0.055 | **0.005** | 374.5 |
|  | AnswerSurvival | 0.800 | 0.053 | **0.005** | 370.3 |
| 512 | Top-K | **0.855** | 0.050 | **0.005** | 444.9 |
|  | MMR | 0.845 | 0.050 | **0.005** | 444.9 |
|  | Focused | **0.855** | **0.051** | **0.005** | 445.1 |
|  | AnswerSurvival | 0.850 | **0.051** | **0.005** | 442.6 |

### squad

| Budget | Method | AIC | F1 | EM | Avg Tokens |
|---|---|---|---|---|---|
| 80 | Top-K | 0.905 | 0.161 | **0.040** | 69.9 |
|  | MMR | **0.930** | **0.162** | **0.040** | 68.9 |
|  | Focused | 0.880 | 0.154 | 0.035 | 70.0 |
|  | AnswerSurvival | 0.905 | 0.159 | **0.040** | 68.1 |
| 160 | Top-K | **0.985** | 0.167 | **0.045** | 116.6 |
|  | MMR | 0.980 | **0.169** | **0.045** | 116.2 |
|  | Focused | **0.985** | 0.167 | **0.045** | 116.6 |
|  | AnswerSurvival | **0.985** | 0.169 | **0.045** | 114.9 |
| 256 | Top-K | **0.985** | 0.168 | **0.045** | 124.3 |
|  | MMR | **0.985** | **0.169** | **0.045** | 124.3 |
|  | Focused | **0.985** | 0.168 | **0.045** | 124.3 |
|  | AnswerSurvival | **0.985** | 0.169 | **0.045** | 124.0 |
| 384 | Top-K | **0.985** | 0.168 | **0.045** | 125.4 |
|  | MMR | **0.985** | **0.168** | **0.045** | 125.4 |
|  | Focused | **0.985** | 0.168 | **0.045** | 125.4 |
|  | AnswerSurvival | **0.985** | 0.168 | **0.045** | 125.4 |
| 512 | Top-K | **0.985** | 0.168 | **0.045** | 125.4 |
|  | MMR | **0.985** | **0.168** | **0.045** | 125.4 |
|  | Focused | **0.985** | 0.168 | **0.045** | 125.4 |
|  | AnswerSurvival | **0.985** | 0.168 | **0.045** | 125.4 |

### triviaqa

| Budget | Method | AIC | F1 | EM | Avg Tokens |
|---|---|---|---|---|---|
| 80 | Top-K | 0.500 | **0.048** | 0.010 | 76.3 |
|  | MMR | 0.465 | 0.040 | **0.015** | 76.3 |
|  | Focused | 0.510 | 0.041 | 0.005 | 76.3 |
|  | AnswerSurvival | **0.525** | 0.046 | 0.005 | 73.9 |
| 160 | Top-K | 0.625 | **0.049** | 0.005 | 154.9 |
|  | MMR | 0.615 | 0.042 | **0.010** | 155.2 |
|  | Focused | 0.650 | 0.042 | 0.005 | 155.3 |
|  | AnswerSurvival | **0.665** | 0.044 | 0.005 | 154.2 |
| 256 | Top-K | 0.700 | 0.041 | 0.000 | 248.6 |
|  | MMR | 0.665 | 0.042 | **0.010** | 249.4 |
|  | Focused | 0.695 | **0.046** | 0.005 | 249.3 |
|  | AnswerSurvival | **0.725** | 0.039 | 0.000 | 247.2 |
| 384 | Top-K | 0.770 | **0.045** | **0.000** | 365.0 |
|  | MMR | 0.745 | 0.036 | **0.000** | 365.8 |
|  | Focused | **0.775** | 0.044 | **0.000** | 365.7 |
|  | AnswerSurvival | 0.770 | 0.040 | **0.000** | 360.1 |
| 512 | Top-K | 0.805 | **0.045** | **0.000** | 448.6 |
|  | MMR | 0.790 | 0.040 | **0.000** | 447.3 |
|  | Focused | **0.810** | 0.044 | **0.000** | 449.0 |
|  | AnswerSurvival | 0.805 | 0.041 | **0.000** | 443.8 |


## Best Method per Dataset/Budget

| Dataset | Budget | Best AIC method | Best AIC | AnswerSurvival AIC | Best F1 method | Best F1 | AnswerSurvival F1 |
|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | 80 | MMR | 0.425 | 0.395 | MMR | 0.141 | 0.119 |
| 2wikimultihopqa | 160 | AnswerSurvival <- AS wins | 0.560 | 0.560 | MMR | 0.117 | 0.109 |
| 2wikimultihopqa | 256 | AnswerSurvival <- AS wins | 0.640 | 0.640 | MMR | 0.107 | 0.100 |
| 2wikimultihopqa | 384 | MMR | 0.725 | 0.720 | Top-K | 0.095 | 0.091 |
| 2wikimultihopqa | 512 | MMR | 0.745 | 0.740 | Top-K | 0.095 | 0.091 |
| hotpotqa | 80 | MMR | 0.520 | 0.475 | AnswerSurvival <- AS wins | 0.062 | 0.062 |
| hotpotqa | 160 | Top-K | 0.625 | 0.625 | MMR | 0.058 | 0.055 |
| hotpotqa | 256 | Top-K | 0.720 | 0.720 | MMR | 0.055 | 0.053 |
| hotpotqa | 384 | Focused | 0.810 | 0.800 | MMR | 0.055 | 0.053 |
| hotpotqa | 512 | Top-K | 0.855 | 0.850 | Focused | 0.051 | 0.051 |
| squad | 80 | MMR | 0.930 | 0.905 | MMR | 0.162 | 0.159 |
| squad | 160 | Top-K | 0.985 | 0.985 | MMR | 0.169 | 0.169 |
| squad | 256 | Top-K | 0.985 | 0.985 | MMR | 0.169 | 0.169 |
| squad | 384 | Top-K | 0.985 | 0.985 | MMR | 0.168 | 0.168 |
| squad | 512 | Top-K | 0.985 | 0.985 | MMR | 0.168 | 0.168 |
| triviaqa | 80 | AnswerSurvival <- AS wins | 0.525 | 0.525 | Top-K | 0.048 | 0.046 |
| triviaqa | 160 | AnswerSurvival <- AS wins | 0.665 | 0.665 | Top-K | 0.049 | 0.044 |
| triviaqa | 256 | AnswerSurvival <- AS wins | 0.725 | 0.725 | Focused | 0.046 | 0.039 |
| triviaqa | 384 | Focused | 0.775 | 0.770 | Top-K | 0.045 | 0.040 |
| triviaqa | 512 | Focused | 0.810 | 0.805 | Top-K | 0.045 | 0.041 |


## Statistical Significance: AnswerSurvival vs Baselines (paired bootstrap, 95% CI)

Only rows with a significant difference (CI excludes 0) shown. Positive mean_diff = AnswerSurvival better.

| Dataset | Budget | Metric | Baseline | Mean diff | 95% CI | p-value | Direction |
|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | 80 | f1 | MMR | -0.022 | [-0.045, -0.002] | 0.0344 | AS worse |
| 2wikimultihopqa | 160 | aic | Top-K | +0.045 | [+0.010, +0.085] | 0.0220 | AS better |
| 2wikimultihopqa | 160 | aic | MMR | +0.060 | [+0.010, +0.110] | 0.0300 | AS better |
| 2wikimultihopqa | 384 | f1 | Top-K | -0.004 | [-0.009, -0.000] | 0.0328 | AS worse |
| 2wikimultihopqa | 512 | f1 | Top-K | -0.004 | [-0.010, -0.000] | 0.0180 | AS worse |
| hotpotqa | 80 | aic | Focused | +0.040 | [+0.010, +0.075] | 0.0060 | AS better |
| hotpotqa | 160 | f1 | Focused | +0.005 | [+0.001, +0.010] | 0.0012 | AS better |
| hotpotqa | 256 | f1 | Focused | +0.002 | [+0.000, +0.003] | 0.0344 | AS better |
| triviaqa | 256 | aic | MMR | +0.060 | [+0.020, +0.105] | 0.0084 | AS better |