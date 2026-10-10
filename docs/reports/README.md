# Milestone 2 Technical Reports Directory — IT5006 Group 11

This directory houses the authoritative technical reports, documentation, and graphical figures for **IT5006 Milestone 2 (AY 2026/27 Semester 1)**.

---

## 📄 Authoritative Deliverables

| Deliverable | File Path | Format & Scope |
| :--- | :--- | :--- |
| **Final Technical Report (Markdown Source)** | [`Team11_Phase2_IT5006_AY2627Sem1_final.md`](Team11_Phase2_IT5006_AY2627Sem1_final.md) | Authoritative, fully elaborated Markdown document containing all 17 tables, CRISP-DM methodology, leakage analyses, and links to all 15 figures. |
| **Final Technical Report (Word Document)** | [`Team11_Phase2_IT5006_AY2627Sem1_final.docx`](Team11_Phase2_IT5006_AY2627Sem1_final.docx) | Exact 1:1 publication Word document compiled via `src/models/export_final_docx.py` with all 17 native tables and 15 figures directly embedded. |
| **High-Resolution Figures** | [`figures/`](figures/) | Directory of 15 diagnostic charts, correlation matrices, residual distributions, and threshold optimization curves. |

---

## 🧭 Modeling Evolution & Report Content

The final report documents the three-generation modeling journey:

1. **Generation 1 (Historical Baseline, Milestone 1)**:
   - 27 raw predictors with severe multicollinearity ($\kappa = \infty$, rank deficiency 9).
   - Random grouped 80/20 train/test splitting resulting in fatal **temporal inversion leakage** (future orders training models to predict past orders).
2. **Generation 2 (Refinement Cycle 1, `refinement-selected-v3`)**:
   - Fixed temporal leakage using **5-fold chronological forward-chaining cross-validation** with customer purges and label maturity gating.
   - Initial 13/14 pruned feature baseline with Decision Trees ($d=5$) and Logistic Regression ($C=0.01$).
3. **Generation 3 (Refinement Cycle 2 / Experiment 3, `refinement-selected-v4`, Champion)**:
   - **Option 1 Implementation**: Pruned `has_items` and `freight_ratio_missing` because legitimate checkout carts inherently contain items, and zero-item records represent post-checkout cancellations.
   - **Pre-Checkout Gating**: Filtered 604 zero-item cancellation records from classification pipelines, ensuring strict pre-checkout integrity.
   - **Full-Rank 9-Feature Core**: Verified full numerical rank ($71/71$) and low condition number ($\kappa = 70.77$).
   - **Task-Specific Expansions**:
     - **Regression (11 features)**: 9 core + `distance_km_max` + `distance_missing_fraction`.
     - **Classification (12 features)**: 9 core + `n_sellers` + `primary_seller_state` + `interstate_share`.
   - **Winning Architectures**:
     - *Regression Champion*: Tuned Random Forest ($N=50, d=14, L=20$) with Target Log1p and 60-day winsorization (Holdout MAE = **3.719 days**, $R^2 = \mathbf{+0.1871}$).
     - *Classification Champion*: Tuned Random Forest with Cost-Calibrated Optimal Threshold $\tau^* = \mathbf{0.17}$ at $1:5$ business cost ratio (Recall = **$38.2\%$**, lowest business cost = **8,205 units**).

---

## 🛠️ Re-generating Deliverables

To recompile the Word document directly from the Markdown source and figures:

```bash
python -m src.models.export_final_docx
```
