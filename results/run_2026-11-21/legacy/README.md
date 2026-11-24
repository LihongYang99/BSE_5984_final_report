# Shrimp LCA Project

A Python and openLCA workflow for a screening life cycle assessment of shrimp aquaculture. The current implementation compares **Indiana Biofloc** and **Alabama Pond** using literature-derived foreground inputs and an ecoinvent electricity background.

The functional unit is **1 kg of live-weight shrimp at the farm gate**. Current calculated shrimp results cover **electricity only**. Feed inventories and provider searches are prepared, but feed impacts have not yet been integrated into the shrimp results.

## Current Status

Status checked against local scripts and saved CSV files on **2026-11-20**. Existing calculations were not rerun during this documentation update.

- Python environment and JSON-RPC IPC connection verified; the connection test previously returned 25,412 process descriptors.
- US foreground inventory and electricity/feed input figures are available.
- A saved US electricity LCIA result and a contribution audit are available.
- Electricity-only shrimp results and figures are available.
- Feed C composition has been normalized; provider selection remains pending.

The original project handoff focused on Sun et al. (2023) and Chinese RAS/BFT/HPP systems. Scripts 03–11 now implement a separate US case attributed to Al Eissa et al. (2022). Keep these datasets and scenarios distinct.

## Project Layout

```text
final_project/
├── .venv/       # Project Python environment
├── scripts/     # Numbered workflow scripts
├── data/        # Prepared foreground inventories
├── outputs/     # Candidate lists, mappings and calculated results
├── figures/     # Generated PNG/PDF figures
├── results/     # Currently unused by the numbered scripts
└── README.md
```

## Python Virtual Environment (macOS / zsh)

Use the `.venv` directory in the project root for all project work. If the environment already exists, activate it without creating it again. Both the terminal and VS Code should use this environment.

### Initial Setup

Open a terminal, navigate to the project directory, and create the environment using an installed Python 3.12 interpreter:

```bash
cd /Users/lihongyang/Desktop/final_project
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

If `python3.12` is not found, install Python 3.12 or replace the command with the full path to an existing Python 3.12 interpreter.

### Install Dependencies

With the environment activated, run:

```bash
python -m pip install --upgrade pip
python -m pip install olca-ipc olca-schema pandas numpy matplotlib openpyxl scipy
python -m pip check
```

The message `No broken requirements found.` confirms that the installed package dependencies are consistent. It does not confirm a successful connection to openLCA.

### Activate the Environment in a New Terminal

```bash
cd /Users/lihongyang/Desktop/final_project
source .venv/bin/activate
python -c "import sys; print(sys.executable)"
python -m pip --version
```

The interpreter path should be `/Users/lihongyang/Desktop/final_project/.venv/bin/python`. The pip path should also be inside the same `.venv` directory. Run `deactivate` when you want to leave the environment.

### Select the VS Code Interpreter

1. Open the `final_project` folder.
2. Press `Cmd+Shift+P` and run `Python: Select Interpreter`.
3. Select `/Users/lihongyang/Desktop/final_project/.venv/bin/python`. If it is not listed, use `Enter interpreter path` to specify it manually.
4. Open a new terminal and run the activation and path checks above to confirm that the Run button and terminal use the same environment.

### Troubleshooting

- `No module named python`: The command contains an extra `-m python`. Use `python -m pip install --upgrade pip`, not `python -m python -m pip ...`.
- `Operation cancelled by user`: Installation was interrupted with `Ctrl+C`. Run the installation command again.
- `No module named olca_ipc`: Check `sys.executable`, confirm that it points to `.venv`, and install the dependencies in that environment.
- If you are unsure which environment is active, specify the interpreter directly from the project directory:

```bash
.venv/bin/python -m pip check
.venv/bin/python scripts/01_test_connection.py
```

### Verified Environment

Local verification on **2026-11-20** confirmed Python **3.12.13** in the project's `.venv` directory. The `pip check` command passed.

| Package | Installed Version |
| --- | --- |
| pip | 26.3 |
| olca-ipc | 2.7.0 |
| olca-schema | 2.7.0 |
| pandas | 3.1.1 |
| numpy | 2.5.5 |
| matplotlib | 3.11.2 |
| openpyxl | 3.1.5 |
| scipy | 1.18.1 |

These versions record the local installation. The installation commands above do not pin versions and may install different releases in the future. To record all installed dependency versions, activate the environment and run:

```bash
python -m pip freeze > requirements.txt
```

You can then install the recorded dependencies with `python -m pip install -r requirements.txt`.

## openLCA Setup

Open the intended database and start **Tools → Developer tools → IPC Server** on port **8080**. Select the standard **IPC / JSON-RPC** protocol, not gRPC. The Python client uses JSON-RPC over HTTP.

An error containing `Unexpected HTTP/1.x request` indicates a protocol mismatch; stop the gRPC server and start the standard IPC server. Check the active database if no processes are returned.

The project targets ecoinvent 3.11 Cut-off Unit Processes. Check the database name/version in openLCA before calculations; process counts alone do not establish the database version.

## Workflow and Run Order

Run commands from the project root after activating `.venv`:

```bash
cd /Users/lihongyang/Desktop/final_project
source .venv/bin/activate
```

| Step | Script | Purpose | Requires openLCA | Database behavior |
| --- | --- | --- | --- | --- |
| 01 | `scripts/01_test_connection.py` | List process count and sample names | Yes | Read-only |
| 02 | `scripts/02_find_processes.py` | Search background candidates and list LCIA methods | Yes | Read-only |
| 03 | `scripts/03_prepare_us_LCI.py` | Write the two-system US foreground inventory | No | None |
| 04 | `scripts/04_plot_us_LCI.py` | Plot electricity and feed inputs from step 03 | No | None |
| 05 | `scripts/05_validate_background.py` | Inspect a fixed provider shortlist and search baking soda | Yes | Read-only; mappings remain pending |
| 06 | `scripts/06_calculate_electricity_gwp.py` | Create an electricity product system and calculate impacts for amount 1 | Yes | **Creates a product system** |
| 07 | `scripts/07_check_electricity_system.py` | Inspect matching electricity product systems and links | Yes | Read-only |
| 08 | `scripts/08_audit_electricity_gwp.py` | Calculate GWP100 and export direct contributions | Yes | Calculates an existing system; disposes temporary results |
| 09 | `scripts/09_electricity_only_shrimp.py` | Multiply shrimp electricity demand by the stored electricity factor | No | None |
| 10 | `scripts/10_prepare_feed_lci.py` | Normalize Feed C ingredients | No | None |
| 11 | `scripts/11_find_feed_providers.py` | Inspect feed ingredient provider candidates | Yes | Read-only |

Run one step at a time with `python scripts/<filename>.py`. For example, the current feed workflow is:

```bash
python scripts/10_prepare_feed_lci.py
python scripts/11_find_feed_providers.py
```

Step 06 is not an idempotent setup command: rerunning it can create additional product systems. Use a verified working copy or an explicitly isolated modeling database before running it. This README does not establish whether previous runs used a copy.

Step 08 uses a fixed product-system UUID; it does not automatically use the system most recently created by step 06. Inspect step 07 output and reconcile the IDs before recalculating. Step 09 uses a hard-coded factor and foreground values, rather than loading the step 03 and step 06 CSVs. Updating those CSVs alone will not update step 09.

## Foreground Data and Units

Scripts 03 and 09 attribute these values to **Al Eissa et al. (2022), Table 2**:

| System | Electricity (kWh/kg live shrimp) | Feed (kg/kg live shrimp) |
| --- | ---: | ---: |
| Indiana Biofloc | 0.921 | 1.500 |
| Alabama Pond | 8.799 | 1.020 |

These are published inputs reused in this project, not new farm measurements or IoT observations. The `Primary farm data` label in the Indiana CSV describes the source study's data, not measurements collected by this project. The source attribution is recorded in the scripts; the original Al Eissa tables were not independently rechecked during this README update.

Step 10 attributes Feed C to **Al Eissa et al. (2022), Table 1**:

| Ingredient | kg/kg feed | kg/kg live shrimp at feed input 1.5 |
| --- | ---: | ---: |
| Fish meal | 0.30 | 0.450 |
| Poultry by-product meal | 0.05 | 0.075 |
| Soybean meal | 0.20 | 0.300 |
| Wheat flour | 0.30 | 0.450 |
| Rice bran | 0.05 | 0.075 |
| Fish oil | 0.03 | 0.045 |
| Soybean lecithin | 0.03 | 0.045 |
| Supplements | 0.04 | 0.060 |
| **Total** | **1.00** | **1.500** |

In `feed_c_lci.csv`, `mass_kg` refers to ingredients for **1,000 kg live shrimp**, not for one kilogram. The normalized columns provide the two other bases explicitly. Applying this formulation to Alabama would require a documented scenario assumption and rescaling to its feed input; do not reuse Indiana's per-shrimp ingredient amounts unchanged.

## Electricity Calculation and Saved Results

The scripts currently reference these database-specific identifiers:

| Object | UUID |
| --- | --- |
| US electricity process (steps 05–07) | `483cde5f-7ae5-379e-ae10-54bb8fbbe6a2` |
| Impact method, labeled IPCC 2021 in step 06 | `9488e228-f9d7-4921-b616-0cad160d96f7` |
| Product system used by step 08 | `931b7343-5d8e-4f14-ab2e-2fd147a3191d` |

The selected category is **Climate change: total (excl. biogenic CO2) - Global warming potential (GWP100)**. Its saved value in `outputs/electricity_gwp_us.csv` is **0.1353780587964153 kg CO2-eq per modeled kWh**. Do not add the total category to its component categories, or combine different time horizons.

The 17,182 entries in `electricity_gwp_contributions.csv` sum to approximately **0.1353780587964155**, matching the saved total within floating-point precision. This confirms numerical reconciliation of the saved files, not the completeness or geographic representativeness of the underlying model. Confirm reference units, upstream links, provider choices and method metadata before treating the factor as a validated grid benchmark.

Step 09 applies the same US electricity factor to both systems:

```text
Electricity-related GWP = electricity demand × electricity GWP factor
```

| System | Saved electricity-related GWP (kg CO2-eq/kg live shrimp) |
| --- | ---: |
| Indiana Biofloc | 0.124683 |
| Alabama Pond | 1.191192 |

This is a common-background diagnostic, not a state-specific electricity comparison or a full shrimp carbon footprint. Feed, chemicals, infrastructure, transport and direct farm emissions are not included in these shrimp totals.

## Candidate Search and Feed Mapping

A candidate is a dataset whose name matches a keyword. A match is not an approved provider or a calculation result. LCIA methods are sets of impact-assessment rules, not additional foreground processes.

Step 02 exports all name matches and displays up to 12 per group. It prioritizes Chinese location codes for display, inherited from the original Sun workflow; this is not a US provider selection rule. Use `--limit 20` to display more matches. Blank descriptor units must be checked from detailed reference exchanges.

Step 11 inspects only the first 30 matches per ingredient in the returned order. Its `expected_origin` values are search targets encoded in the script, not confirmed provider origins or source-verified selections. The saved file contains 68 candidate reference-product rows:

| Ingredient | Candidate rows |
| --- | ---: |
| Fish meal | 23 |
| Soybean meal | 18 |
| Wheat flour | 7 |
| Fish oil | 20 |

Poultry by-product meal, rice bran, soybean lecithin and supplements have no rows in this saved export. This does not prove they are absent from the database. All saved candidates remain `PENDING_REVIEW`.

The next modeling task is to resolve these gaps and document provider geography, reference product, unit and substitution rationale. Feed manufacturing energy and transport also need explicit treatment before claiming a complete commercial-feed footprint.

## Outputs

| File under `outputs/` | Meaning |
| --- | --- |
| `process_name_matches.csv` | All step 02 keyword matches |
| `lcia_methods.csv` | All available method descriptors, including UUIDs |
| `background_mapping_review.csv` | Step 05 shortlist with reference products and pending review status |
| `electricity_gwp_us.csv` | Step 06 impact-category results |
| `electricity_gwp_contributions.csv` | Step 08 direct GWP contributions |
| `electricity_only_shrimp_gwp.csv` | Step 09 partial shrimp footprints |
| `feed_provider_candidates.csv` | Step 11 candidate reference products |
| `process_candidate_details.csv` | Legacy output; not refreshed by current step 02 |

Step 04 creates `fig01_US_electricity` and `fig02_US_feed` in PNG/PDF formats. Step 08 creates `fig03_electricity_gwp_audit.png`. Step 09 creates `fig04_electricity_only_shrimp_gwp` in PNG/PDF formats.

Scripts overwrite their named local outputs when rerun. Preserve any results that need to remain associated with a particular database, method or provider configuration before rerunning.

## Scope, Reproducibility and Licensing

- Keep literature inputs, assumptions and computed impacts separate. Published GWP scores are comparison benchmarks, not foreground emissions.
- Never interpret keyword matches or pending mapping rows as approved substitutions.
- Record database version, method/category, reference unit, provider UUIDs and system-linking choices with final results. UUIDs may not resolve in a different database.
- Future IoT work requires measured timestamped consumption; the current scripts contain no such data.
- Keep licensed database contents and metadata exports private. The current folder has no `.gitignore`; add exclusions for `.venv/`, licensed sources, database exports and private outputs before publishing a repository.
