# HIV D:A:D cardiovascular-risk input checker

This repository provides a local and browser-based **input-readiness checker** for the reduced D:A:D cardiovascular-risk model used in people living with HIV.

> **Clinical status:** This project does **not** calculate the published five-year D:A:D CVD risk, assign risk categories, or recommend interventions. The original arbitrary weighted-sum score has been withdrawn. For actual estimates use the [CHIP D:A:D Risk Assessment Tool](https://chip.dk/resources/tools-standards/risk-assessment-tool/) and independent clinical judgment.

## Features

- **Browser form:** The standalone **web/index.html** reviews all nine reduced-model predictors and downloads a CSV header template.
- **Python checker:** **dad_hiv_risk.py** validates one input set or local CSV batches without generating a risk percentage.
- **Demonstration-only agent framework:** **agents/** and **cli.py** implement mock status/rule processing, HMAC-chained in-memory audits, FastAPI endpoints, and batch simulation. They are not clinical decision-support tools.
- Tests cover predictor validation, CSV edge cases, audit-signature tampering, and prior demonstration functionality.

## Browser usage

Open **web/index.html** in a modern browser. Alternatively run:

~~~bash
python -m http.server 8080 --directory web
~~~

Then visit http://localhost:8080/. The browser form has no server dependencies or external script/font requests. Values are checked locally and are not saved or uploaded. The link to the official CHIP tool opens an independent website.

## Python usage

Requires Python 3.10+.

~~~bash
python dad_hiv_risk.py single --age 48 --sex male --systolic-bp 130 \
  --smoking-status former --family-history-cvd no --diabetes no \
  --total-cholesterol 5.2 --hdl-cholesterol 1.3 --cd4-count 650

python dad_hiv_risk.py batch -i sample.csv -o results.csv
~~~

Results report **INPUTS_COMPLETE** or **INPUTS_INCOMPLETE**, missing/invalid fields and a null or blank five-year risk. No clinical risk is calculated.

CSV predictor columns are: age (years), sex (male/female as coded by the published model), systolic_bp (mmHg), smoking_status (never/former/current), family_history_cvd (yes/no), diabetes (yes/no), total_cholesterol (mmol/L), hdl_cholesterol (mmol/L), and cd4_count (cells/µL). Extra local identifier columns are retained. Do not send patient-identifiable data to third-party calculators.

Age limits are based on the reported calculator applicability; other input ranges are broad plausibility checks, not clinical thresholds.

## Optional demonstration CLI/API

~~~bash
python -m pip install -e ".[dev]"
python -m pytest -q
hiv-dadr-risk serve --host 127.0.0.1 --port 8000
hiv-dadr-risk audit --task-id TEST-001 --target KEY-001 --primary 15
hiv-dadr-risk verify-audit
~~~

API endpoints are **/health**, **/metrics**, **/api/audit**, **/api/chat**, and **/api/audit/logs**. Their logic is demonstration-only; the mock chat adapter does not query external models or verify clinical statements. Do not expose the unauthenticated API publicly.

For Docker Compose, provide an audit key at runtime:

~~~bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
~~~

The audit ledger is process-local, not persistent. HMAC verification detects alterations to stored signed entries but is not a substitute for a durable audit system. The regex-based identifier filter does not guarantee full PHI de-identification or regulatory compliance.

## Limitations and validation

The 2016 updated D:A:D model has both reduced and full formulations. The full formulation additionally uses antiretroviral exposure. Correct calculation requires published model coefficients and baseline survival; neither is implemented here. Clinical validity, browser compatibility, and deployment status should not be inferred from input completeness.

The static browser form is intended for current Chromium, Firefox and Safari; it requires JavaScript. The source code is authoritative if deployment information becomes outdated.

## Reference

Friis-Møller N, Ryom L, Smith C, et al. An updated prediction model of the global risk of cardiovascular disease in HIV-positive persons: the D:A:D study. *European Journal of Preventive Cardiology*. 2016;23(2):214–223. [PMID 25882821](https://pubmed.ncbi.nlm.nih.gov/25882821/).

## License

MIT — see [LICENSE](LICENSE).
