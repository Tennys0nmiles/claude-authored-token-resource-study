
### Qwen2.5-1.5B_W256 — natural: % of local→full loss gap recovered (gap = 0.312 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     12.3 |      22.3 |      39.8 |      54.6 |       14.9 |        26.6 |        45.7 |        60.6 |
| familiarity head (7 scalars)        |     17.1 |      28.3 |      45   |      58.4 |       20.4 |        33.1 |        50.5 |        63.8 |
| familiarity rule (no training)      |     14.3 |      21.4 |      34.6 |      47   |       17.2 |        24.7 |        38.4 |        50.7 |
| learned head (hidden + familiarity) |     24.1 |      36.8 |      55.2 |      67.1 |       26.5 |        40.7 |        59.7 |        71.6 |
| oracle KL (needs full pass)         |     42.3 |      57.7 |      73.3 |      81.8 |       48.2 |        65.2 |        81   |        88.4 |
| random                              |      4   |       8.2 |      17.7 |      27   |        4.8 |         9.7 |        20.3 |        30.4 |

### Qwen2.5-1.5B_W256 — prose: % of local→full loss gap recovered (gap = 0.380 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      9.4 |      17.5 |      33.3 |      47.8 |       11.7 |        21.3 |        38.7 |        53   |
| familiarity head (7 scalars)        |     13.4 |      23.3 |      39.5 |      54.2 |       16.4 |        27.5 |        44.9 |        59.5 |
| familiarity rule (no training)      |     11.9 |      19.2 |      32.3 |      44.6 |       14.2 |        22.1 |        35.7 |        47.9 |
| learned head (hidden + familiarity) |     19.9 |      31.2 |      49.1 |      62   |       21.9 |        34.5 |        53.6 |        66.4 |
| oracle KL (needs full pass)         |     36.1 |      51.4 |      68.6 |      78.4 |       40.9 |        57.6 |        75.5 |        84.4 |
| random                              |      4   |       8   |      17.5 |      26.8 |        4.8 |         9.5 |        20   |        29.8 |

### Qwen2.5-1.5B_W256 — code: % of local→full loss gap recovered (gap = 0.239 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     17.3 |      30.6 |      50.8 |      66.4 |       20.4 |        35.7 |        57.7 |        73.6 |
| familiarity head (7 scalars)        |     23.4 |      37   |      54.4 |      65.7 |       27.4 |        42.6 |        60.3 |        71.3 |
| familiarity rule (no training)      |     18.5 |      25.2 |      38.4 |      51.1 |       22.4 |        29.3 |        43.1 |        55.5 |
| learned head (hidden + familiarity) |     31.2 |      46.5 |      65.5 |      75.9 |       34.6 |        51.3 |        70.4 |        80.6 |
| oracle KL (needs full pass)         |     53   |      68.7 |      81.3 |      87.8 |       60.6 |        78.3 |        90.5 |        95.4 |
| random                              |      4   |       8.5 |      17.9 |      27.4 |        4.7 |        10   |        20.8 |        31.5 |

### Qwen2.5-1.5B_W256 — prose_ids: % of local→full loss gap recovered (gap = 0.383 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      9.3 |      17.4 |      33.3 |      47.6 |       11.9 |        21.4 |        39   |        53.2 |
| familiarity head (7 scalars)        |     14   |      23.9 |      40.3 |      54.8 |       17.1 |        28.5 |        46   |        60.6 |
| familiarity rule (no training)      |     12.7 |      20   |      32.9 |      45.2 |       15.2 |        22.9 |        36.6 |        48.8 |
| learned head (hidden + familiarity) |     20.1 |      31.6 |      49.7 |      62.6 |       22.3 |        35   |        54.3 |        67.1 |
| oracle KL (needs full pass)         |     36.4 |      51.7 |      69.1 |      78.9 |       41.3 |        57.8 |        75.8 |        84.8 |
| random                              |      4.2 |       8.8 |      17.7 |      27.4 |        4.9 |        10.4 |        20.4 |        30.8 |
