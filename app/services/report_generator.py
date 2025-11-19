def generate_markdown(sector: str, analysis: dict):
    # Safely handle missing opportunities/risks
    opps = analysis.get("opportunities", [])
    risks = analysis.get("risks", [])

    # Pad lists to avoid IndexError
    while len(opps) < 2:
        opps.append("-")
    while len(risks) < 2:
        risks.append("-")

    markdown = f"""
# {sector.capitalize()} Sector Market Report - India

## Summary
{analysis['summary']}

---

### Opportunities
- {opps[0]}
- {opps[1]}

### Risks
- {risks[0]}
- {risks[1]}

Generated automatically.
"""
    return markdown
