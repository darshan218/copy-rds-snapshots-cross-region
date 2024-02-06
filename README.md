# RDS and Aurora Snapshot Copy Script

## Overview

This repository contains Python scripts to copy Amazon RDS and Aurora snapshots across different regions. The scripts utilize the AWS SDK for Python (Boto3) to interact with the AWS services.

## Prerequisites

Before using the scripts, ensure that you have:

- Python 3.x installed
- Boto3 library installed (`pip install boto3`)
- AWS credentials configured with the necessary permissions

## Scripts

### 1. RDS Snapshot Copy

The `rds_snapshot_copy.py` script copies RDS snapshots from one AWS region to another.

### 2. Aurora Snapshot Copy

The `rds_snapshot_copy.py` script copies Aurora snapshots from one AWS region to another.

Note: Replace placeholder values such as `'your-account-id'`, `"your-database-name"`, and KMS key ARNs with your actual values in the script and configuration section.
