# Sigrid API Client

This script provides a set of functionalities using the Sigrid API that center around export / import of Sigrid data to spreadsheet format. At this time, not all API functionality has been implemented into this client. 

## Prerequisites

You will need the following to use this script:
- This script has been tested with Python 3.14. Other versions may still work but have not been validated.
- You will need a valid [API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html) to access the [Sigrid REST API](https://docs.sigrid-says.com/integrations/sigrid-api-documentation.html).


## Setup

The following instructions have been tested on MacOS, and will likely work on Linux-based systems.  

Instructions for use of virtual environments on Windows can be found in the [Python documentation](https://docs.python.org/3/library/venv.html)

It is recommended to create a virtual environment to install the necessary dependencies. This can be done as follows:
- Navigate to the Sigrid API Client repository
- Run the command `python -m venv .venv`
- Activate the virtual environment using `source .venv/bin/activate`
- Install dependencies using `pip install -r requirements.txt`

Alternatively, some IDEs will automatically detect `requirements.txt` files and handle the creation and use of a virtual environment.

## Usage

After setup, the API client can be used with the command `python cli.py`.  If no arguments are provided, or only `--help`, a list of commands will be displayed.  Available options per-command can be shown using `python cli.py [command] --help`

---

## Available Commands

### Common Arguments

The following arguments are used across multiple commands:

- **`-c, --customer`** (required): Your Sigrid customer name (the organization identifier in Sigrid)
- **`-t, --token`** (required): Your Sigrid API authentication token. Can also be supplied via the `SIGRID_CI_TOKEN` environment variable, in which case the `-t` argument may be omitted.
- **`-o, --out_file`**: Path where the output file will be written. Note that some commands will output to CSV and some to XLSX.
- **`-d, --dry_run`**: When specified, simulates the operation without making actual changes (prints what would be done)
- **`-u, --url`**: Base Sigrid URL to target - not needed for most use cases. Defaults to `https://sigrid-says.com`.

---

### `export-portfolio-metadata`

Exports metadata for all systems in a portfolio to an Excel file. This is typically the first step when you want to update system metadata in bulk.

**Workflow:** Use this command to export current metadata, edit the Excel file with your changes, then use `import-portfolio-metadata` to apply the updates back to Sigrid.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-o, --out_file` (required): Output Excel (.xlsx) file path where metadata will be written
- `-t, --token` (required): Sigrid API token

**Example:**
```bash
python cli.py export-portfolio-metadata -c <your-customer> -o <metadata.xlsx> -t <your-sigrid-token>
```

After running this command, open the Excel file, make your desired changes to system metadata, and proceed to `import-portfolio-metadata`.

---

### `import-portfolio-metadata`

Updates system metadata in Sigrid by importing from an Excel file. This command applies metadata changes back to Sigrid.

**Workflow for updating portfolio metadata:**
1. **Export:** First, run `export-portfolio-metadata` to get the current metadata in an Excel file
2. **Edit:** Open the Excel file and update the metadata fields you want to change
3. **Preview:** Run this command with `--dry_run` to see what will be changed
4. **Import:** Run this command without `--dry_run` to apply the changes to Sigrid

**Arguments:**
- `-c, --customer` (required): Customer name
- `-i, --input_file` (required): Input Excel (.xlsx) file containing metadata to import
- `-t, --token` (required): Sigrid API token
- `-d, --dry_run` (optional): If specified, shows what would be changed without making actual updates

**Example:**
```bash
# Step 1: Export current metadata
python cli.py export-portfolio-metadata -c <your-customer> -o <metadata.xlsx> -t <your-sigrid-token>

# Step 2: Edit metadata.xlsx in Excel

# Step 3: Preview changes
python cli.py import-portfolio-metadata -c <your-customer> -i <metadata.xlsx> -t <your-sigrid-token> -d

# Step 4: Apply changes
python cli.py import-portfolio-metadata -c <your-customer> -i <metadata.xlsx> -t <your-sigrid-token>
```

---

### `onboard-mendix-systems`

Onboards Mendix systems to Sigrid from an Excel file containing system information.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-i, --input_file` (required): Input Excel (.xlsx) file with Mendix system details
- `-t, --token` (required): Sigrid API token
- `-p, --pat` (optional): Mendix Personal Access Token (PAT) to use if not specified in the Excel file
- `-e, --email` (optional): Email address to associate with systems if not specified in the Excel file
- `-d, --dry_run` (optional): If specified, simulates onboarding without making actual changes
- `-o, --output_file` (optional): Path to write an Excel file containing the results (e.g., assigned system names)

**Example:**
```bash
# Preview onboarding
python cli.py onboard-mendix-systems -c <your-customer> -i <mendix-systems.xlsx> -t <your-sigrid-token> -d

# Onboard systems with output file
python cli.py onboard-mendix-systems -c <your-customer> -i <mendix-systems.xlsx> -t <your-sigrid-token> -o <output-results.xlsx>
```

---

### `export-security-results`

Exports Open Source Health (security) findings for systems in a portfolio to an Excel file.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-o, --out_file` (required): Output Excel (.xlsx) file path
- `-t, --token` (required): Sigrid API token
- `-s, --system` (optional): Export security results for a single specific system
- `-f, --system_file` (optional): Path to a text file containing a list of system names (one per line)

**Usage Modes:**

**All Systems:**
```bash
python cli.py export-security-results -c <your-customer> -o <security.xlsx> -t <your-sigrid-token>
```

**Single System:**
```bash
python cli.py export-security-results -c <your-customer> -s <your-system> -o <security.xlsx> -t <your-sigrid-token>
```

**Specific Systems from File:**
```bash
python cli.py export-security-results -c <your-customer> -f <system-list.txt> -o <security.xlsx> -t <your-sigrid-token>
```

---

### `export-portfolio-users`

Exports all user accounts and their permissions for a portfolio to an Excel file.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-o, --out_file` (required): Output Excel (.xlsx) file path
- `-t, --token` (required): Sigrid API token

**Example:**
```bash
python cli.py export-portfolio-users -c <your-customer> -o <users.xlsx> -t <your-sigrid-token>
```

---

### `update-portfolio-users`

Updates user accounts and permissions in Sigrid from an Excel file.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-i, --input_file` (required): Input Excel (.xlsx) file containing user information
- `-t, --token` (required): Sigrid API token
- `-d, --dry_run` (optional): If specified, shows what would be changed without making actual updates

**Example:**
```bash
# Preview changes
python cli.py update-portfolio-users -c <your-customer> -i <users.xlsx> -t <your-sigrid-token> -d

# Apply changes
python cli.py update-portfolio-users -c <your-customer> -i <users.xlsx> -t <your-sigrid-token>
```

---

### `download-objectives`

Downloads quality objectives for all systems in a portfolio to a CSV file.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-o, --out_file` (required): Output CSV file path where objectives will be written
- `-t, --token` (required): Sigrid API token

**Example:**
```bash
python cli.py download-objectives -c <your-customer> -o <objectives.csv> -t <your-sigrid-token>
```

---

### `download-maintainability-json`

Downloads the Maintainability analysis JSON for a specific system and snapshot date.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-s, --system` (required): Name of the Sigrid system to download
- `-d, --date` (optional): Snapshot date in the format used by Sigrid (e.g., `2026-03-09`). If omitted, the most recent snapshot is used.
- `-o, --out_file` (required): Output JSON file path
- `-t, --token` (required): Sigrid API token

**Example:**
```bash
python cli.py download-maintainability-json -c <your-customer> -s <your-system> -d <snapshot-date> -o <output.json> -t <your-sigrid-token>
```

---

### `export-architecture-jsons`

Exports architecture JSON files for either a single system or all systems in a portfolio.

**Arguments:**
- `-c, --customer` (required): Customer name
- `-t, --token` (required): Sigrid API token
- `-s, --system` (optional): Specific system name to export (for single system export)
- `-f, --out_file` (optional): Output JSON file path (required when using `-s`)
- `-o, --out_directory` (optional): Output directory for portfolio export (required when not using `-s`)

**Usage Modes:**

**Single System Export:**
```bash
python cli.py export-architecture-jsons -c <your-customer> -s <your-system> -f <output.json> -t <your-sigrid-token>
```

**Portfolio Export:**
```bash
python cli.py export-architecture-jsons -c <your-customer> -o <output-directory> -t <your-sigrid-token>
```

---

## Tips

- Always use `--dry_run` first when updating data to preview changes before applying them
- Keep your API token secure and never commit it to version control.
- For commands that accept system lists via file (`-f, --system_file`), create a plain text file with one system name per line
- Excel files should maintain the format from exported files when being used for import operations