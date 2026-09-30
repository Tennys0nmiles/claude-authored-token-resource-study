
### pythia-410m-deduped_W256 — natural: % of local→full loss gap recovered (gap = 0.194 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     11.2 |      20.4 |      37.2 |      50.8 |       14.2 |        25.8 |        45   |        59.1 |
| familiarity head (7 scalars)        |     20.9 |      33.3 |      48.5 |      61.5 |       23.4 |        36.5 |        53.3 |        66.6 |
| familiarity rule (no training)      |     19.3 |      31.7 |      47.5 |      59.5 |       21.9 |        34.4 |        51.2 |        64.3 |
| learned head (hidden + familiarity) |     26.9 |      41.9 |      59.4 |      71   |       29.7 |        45.4 |        63.6 |        74.2 |
| oracle KL (needs full pass)         |     48.2 |      65   |      79.3 |      86.4 |       54.6 |        71.9 |        85.2 |        91.6 |
| random                              |      4.1 |       7.8 |      17.1 |      27.6 |        4.4 |         8.7 |        19.2 |        29.7 |

### pythia-410m-deduped_W256 — prose: % of local→full loss gap recovered (gap = 0.253 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      7   |      14.6 |      29.8 |      43.7 |       10   |        19.9 |        38.5 |        52.8 |
| familiarity head (7 scalars)        |     19.5 |      33.1 |      48   |      59.1 |       22.1 |        36.7 |        53.7 |        65.2 |
| familiarity rule (no training)      |     18.5 |      31.3 |      47.1 |      58.3 |       21.1 |        34.2 |        51.2 |        64.4 |
| learned head (hidden + familiarity) |     23.4 |      37.3 |      54.7 |      66.6 |       25.8 |        40.3 |        58.7 |        69.3 |
| oracle KL (needs full pass)         |     42.1 |      59.6 |      75.8 |      84.1 |       47.4 |        66   |        81.6 |        89.2 |
| random                              |      3.5 |       6.8 |      15.7 |      26.2 |        3.8 |         8   |        17.9 |        28.2 |

### pythia-410m-deduped_W256 — code: % of local→full loss gap recovered (gap = 0.140 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     18   |      29.9 |      49.2 |      62.3 |       21   |        35.3 |        55.4 |        69.5 |
| familiarity head (7 scalars)        |     23.2 |      33.8 |      49.2 |      65.4 |       25.6 |        36.2 |        52.6 |        68.9 |
| familiarity rule (no training)      |     20.6 |      32.4 |      48.1 |      61.5 |       23.2 |        34.9 |        51.2 |        64.2 |
| learned head (hidden + familiarity) |     32.6 |      49.3 |      67.2 |      78.1 |       35.8 |        53.6 |        71.7 |        82.2 |
| oracle KL (needs full pass)         |     58.1 |      73.8 |      85   |      90.2 |       66.3 |        81.4 |        91.2 |        95.4 |
| random                              |      5   |       9.5 |      19.3 |      29.9 |        5.4 |         9.9 |        21.2 |        32.1 |

### pythia-410m-deduped_W256 — prose_ids: % of local→full loss gap recovered (gap = 0.265 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      5.7 |      13.8 |      29.1 |      44.5 |        8.2 |        18.4 |        36.1 |        51.7 |
| familiarity head (7 scalars)        |     23.8 |      38.2 |      52.2 |      61.9 |       27.1 |        41.1 |        56.6 |        66.8 |
| familiarity rule (no training)      |     23.1 |      37.2 |      51.4 |      61.1 |       25.8 |        39.7 |        54.8 |        65.1 |
| learned head (hidden + familiarity) |     23.6 |      37.5 |      55.9 |      65.7 |       25.9 |        40.9 |        59.4 |        68.9 |
| oracle KL (needs full pass)         |     44.7 |      60.3 |      76.2 |      83.8 |       50.1 |        65.7 |        80.7 |        87.5 |
| random                              |      4.3 |       8   |      15.9 |      26.6 |        5.1 |         9.5 |        18.7 |        29.3 |
