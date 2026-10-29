# Model API and hosting (dashboard plan revision 2, 6a.2)

The frozen T1 bundles are served by a small FastAPI service (`main.py`), hosted on Render.com. The Streamlit app is
hosted on Streamlit Community Cloud and calls the API when `MODEL_API_URL` is set; without it the app predicts
locally with the same bundles. Both paths give the same predictions (`test_api.py`). Both hosts are free tier.

The accounts, the GitHub connection and the repository access are set up by Henry or Benson (Benson owns the
repository). Claude does not create accounts.

## 1. Render.com: the model API

New → Web Service → connect the GitHub repository, then:

| Setting | Value |
| --- | --- |
| Branch | the branch to serve (`e5/deliverables-henry` now; `milestone-3` after the merge) |
| Root directory | empty (the repository root) |
| Runtime | Python |
| Build command | `pip install -r experiments/experiment_5/pipeline_b/deliverables/dashboard/api/requirements.txt` |
| Start command | `uvicorn experiments.experiment_5.pipeline_b.deliverables.dashboard.api.main:app --host 0.0.0.0 --port $PORT` |
| Environment variable | `PYTHON_VERSION` = `3.12.10` |
| Health check path | `/health` |
| Instance type | Free |

When it is live, `https://<service>.onrender.com/health` returns the thresholds (B 4/15, A 1/6). A free service
sleeps after a period without requests and takes up to about a minute to wake; the app waits up to 90 seconds.

## 2. Streamlit Community Cloud: the app

Create app → GitHub repository, then:

| Setting | Value |
| --- | --- |
| Branch | the same branch as Render |
| Main file path | `experiments/experiment_5/pipeline_b/deliverables/dashboard/app/app.py` |
| Python version (Advanced settings) | 3.12 |
| Secrets (Advanced settings) | `MODEL_API_URL = "https://<service>.onrender.com"` |

Streamlit installs `app/requirements.txt` (next to the main file). The app reads the business data, the stored
outputs and `data/raw/` from the repository; all are in git. Its sidebar shows where predictions come from.

## 3. After both are live

Send the app URL to Henry's Claude: it goes into report §8 and the deck, and the deliverables audit is rerun.

## Local run

From the repository root, with the app's environment:

```
experiments\experiment_5\pipeline_b\deliverables\dashboard\app\.venv\Scripts\python.exe -m uvicorn experiments.experiment_5.pipeline_b.deliverables.dashboard.api.main:app --port 8000
```
