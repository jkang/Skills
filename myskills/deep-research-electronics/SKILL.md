---
name: deep-research-electronics
description: Perform deep research on consumer electronics companies (Apple, Samsung, Xiaomi, OPPO, Honor) regarding their AI initiatives and generate a minimalistic one-page PPT report. Use this skill when the user asks for a quarterly AI trend analysis, competitor research on mobile/AI PC features, or a summary of AI applications in the electronics industry.
---

# Deep Research Electronics Skill

This skill automates the process of gathering and synthesizing AI-related business intelligence for major consumer electronics players and formatting it into a professional, minimalist PPT report.

## Objective
To provide a consolidated view of how Apple, Samsung, Xiaomi, OPPO, and Honor are leveraging AI across their organizations, products, and value chains within a specific time range (default: the last quarter).

## Workflow

### 1. Information Gathering
For each company (Apple, Samsung, Xiaomi, OPPO, Honor), research the following dimensions for the target period:
- **Organization**: New AI departments, leadership changes, or corporate restructuring focused on AI.
- **Edge-side Models & AI Platforms**: Developments in on-device LLMs (e.g., Apple Intelligence, Samsung Gauss), AI chips, or developer platforms.
- **AI Applications by Domain**:
    - **R&D**: AI-assisted design, coding, or testing.
    - **Production**: AI in manufacturing, quality control, or robotics.
    - **Supply Chain**: AI for demand forecasting, inventory management, or logistics.
    - **Sales**: AI in marketing, retail experience, or pricing.
    - **Service**: AI chatbots, automated repair diagnostics, or customer support.

### 2. Synthesis
- Summarize the most significant 3-5 movements for each company.
- Focus on concrete actions and product launches rather than vague marketing hype.
- Keep descriptions concise for a multi-column PPT layout.

### 3. Report Generation
Generate a one-page PPT report with the following requirements:
- **Template**: Business minimalist, white background, no decorative elements.
- **Layout**: 5 columns (one per company).
- **Font**: Use a clean sans-serif font (e.g., Arial or Calibri).
- **Notes**: Each slide must include URLs of the information sources in the "Notes" section.

## Implementation Details
The skill uses a helper script `scripts/generate_ppt.py` to ensure strict adherence to the visual layout requirements.

### Helper Script Usage
When the research is complete, format the data into a JSON structure and pass it to the `generate_ppt.py` script.

#### JSON Data Structure:
```json
{
  "companies": [
    {
      "name": "Apple",
      "movements": ["Point 1", "Point 2"],
      "sources": ["URL1", "URL2"]
    },
    ...
  ]
}
```

## Troubleshooting
- If no information is found for a specific dimension (e.g., AI in Supply Chain for Honor), it can be ignored.
- Ensure the time range is strictly followed to avoid stale data.
