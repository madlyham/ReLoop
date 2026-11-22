# ReLoop — Serverless E-Waste Marketplace on AWS

Companion code, Lambda deployment packages, sanitized frontend bundle, and modular Terraform Infrastructure as Code for the **ReLoop AWS Serverless Workshop**.

- **Workshop Guide (Modules 5.1 – 5.12):** https://madlyham.github.io/FCAJ-Workshop-Report/5-workshop/
- **Project Proposal:** https://madlyham.github.io/FCAJ-Workshop-Report/2-proposal/
- **Direct Lambda `.zip` Downloads:** [Latest Release (`v1.0.0`)](https://github.com/madlyham/ReLoop/releases/tag/v1.0.0)

## Repository Layout

| Path | Purpose | Used In |
|---|---|---|
| `zips/reloop2-api.zip` | Ready-to-upload Node.js 22 (`arm64`) backend API Lambda package | Module 5.5 / Terraform |
| `zips/reloop2-post-confirmation.zip` | Ready-to-upload Python 3.12 Cognito Post-Confirmation trigger package | Module 5.4 / Terraform |
| `backend/api/` | Unpacked API Lambda bundle (`index.js` + `index.js.map`) | Reference |
| `backend/post-confirmation/` | Readable Python source (`lambda_function.py`) | Module 5.4 |
| `cloudfront-functions/` | `spa-rewrite.js` (Arrow 2) and `api-prefix.js` (Arrow 4) | Module 5.3 / Terraform |
| `frontend/dist/` | Prebuilt React SPA with placeholder Cognito tokens (no Node build needed) | Module 5.4 |
| `frontend/configure.py` | Stamps your Cognito Pool ID, Client ID, and Domain into `frontend/build/` | Module 5.4 |
| `terraform/` | Modular IaC modeling the exact 12-service architecture (Arrows 1 → 10) | Module 5.12 |

## Option 1 — Follow the AWS Console Workshop (Modules 5.2 – 5.12)

Clone this repository before starting Module 5.3:

```bash
git clone https://github.com/madlyham/ReLoop.git
cd ReLoop
```

1. **Module 5.3 (Global Edge):** Paste `cloudfront-functions/spa-rewrite.js` and `cloudfront-functions/api-prefix.js` into CloudFront Functions.
2. **Module 5.4 (Sign-up & Sign-in):**
   - Upload `zips/reloop2-post-confirmation.zip` (or paste `backend/post-confirmation/lambda_function.py`) into `reloop2-post-confirmation`.
   - Stamp your Cognito outputs into the frontend and sync to your private S3 website bucket:
     ```bash
     python frontend/configure.py \
       --pool-id "ap-southeast-1_<id>" \
       --client-id "<client-id>" \
       --domain "https://<your-cognito-domain>.auth.ap-southeast-1.amazoncognito.com"

     aws s3 sync frontend/build/ s3://reloop2-web-<suffix>/ --region ap-southeast-1 --delete
     aws cloudfront create-invalidation --distribution-id <dist-id> --paths "/*"
     ```
3. **Module 5.5 (API Backend):** Upload `zips/reloop2-api.zip` (handler `index.handler`, Node.js 22 `arm64`) into `reloop2-api`.
4. **Module 5.12 (Cleanup):** Follow the reverse-order teardown checklist right after verification so AWS WAF does not keep billing.

## Option 2 — Deploy with Terraform (Reproducible IaC)

Requirements: Terraform `>= 1.10`, AWS CLI v2 configured for **`ap-southeast-1` (Singapore)**, and Python 3.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Generate a random 64-character hex secret for `origin_verify_secret` (never commit `terraform.tfvars`):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `terraform.tfvars` with your unique `bucket_suffix`, `alert_email`, and `origin_verify_secret`, then deploy:

```bash
terraform init
terraform plan
terraform apply
```

Once `terraform apply` prints your outputs, stamp and upload the frontend bundle:

```bash
cd ..
python frontend/configure.py \
  --pool-id "<cognito_user_pool_id>" \
  --client-id "<cognito_client_id>" \
  --domain "<cognito_domain>"

aws s3 sync frontend/build/ s3://<web_bucket_name>/ --region ap-southeast-1 --delete
aws cloudfront create-invalidation --distribution-id <cloudfront_distribution_id> --paths "/*"
```

Confirm the SNS subscription email sent to `alert_email`, then open `cloudfront_url` in your browser.

### Clean Up (Important — Avoid Ongoing WAF Charges)

Empty the two S3 buckets and disable Cognito deletion protection (or set `cognito_deletion_protection = "INACTIVE"` and apply first), then run:

```bash
cd terraform
terraform destroy
```

> **Cost note:** An AWS WAFv2 Web ACL bills **$5/month + $1/month per rule** ($10/month for 5 rules) continuously even with zero traffic. Always tear down after testing.
