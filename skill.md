# Skill: 51Talk Thailand Performance Rank Analyzer
## Basic Information
- Skill Name: 51Talk Thailand Performance Ranking Query
- Language: English Only
- Workflow: Auto login CRM → extract table data → filter excluded staff → filter USD threshold → convert currency → sort ranking → structured output

## Login Information
Login Page:
https://crm.51talk.com/admin/admin_login.php?login_employee_type=sideline&redirect_uri=

Username: THCC-Panawat
Password: b@2A5qt7

Target Performance Page:
https://crm.51talk.com/Performance/getSsPreformanceList?type=2

## Permanent Exclusion List
Automatically hide all below names in all results:
fsth-test, thcc-Som, thcc-Wave, THCC-panawat, thcc-Kin, THCCSM-KIN, THCC-chareena, THCC-tawanwad, THCC-intuon, THCC-chootamas

## Data Filter Rule
Only keep records with Payment Amount (USD) > 200

## Exchange Rate
Fixed rate: 1 USD = 34 THB
Calculation: THB Performance = USD Amount × 34
Only display THB value. Do NOT show USD amount, exchange rate or conversion description in output.

## Function 1: Full Overall Ranking
Trigger command: Full Rank
Output requirements:
- Pure English only
- Complete continuous global ranking sorted descending by performance
- Show all qualified personnel, no truncation
- Markdown table with only 3 columns: Rank, Name, Performance (THB)

Output template:
# Overall Performance Ranking (THB)
| Rank | Name | Performance (THB) |
|:----:|:-----|:-----------------:|

## Function 2: Single Person Inquiry
Trigger format: Query [Name]
Example: Query THCC-XXX
Output requirements:
- Pure English only
- Return global rank, full name, converted THB performance
- No redundant content

Output template:
# Individual Performance Query Result
Rank:
Name:
Performance (THB):

## Absolute Fixed Rules
1. All output is in English, no Chinese content.
2. Ranking numbers are continuous, no missing numbers, no duplicates.
3. Excluded staff will never appear in any result.
4. Only data over 200 USD is calculated.
5. Exchange rate remains 1:34 permanently.
6. No USD value, rate explanation or extra notes in final display.
7. Full ranking includes every valid employee completely.
