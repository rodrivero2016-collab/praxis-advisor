"""
Praxis Advisor - Project Charter Generator API
A Flask API that uses Claude AI to generate professional project charters
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Initialize Anthropic client
# You'll set ANTHROPIC_API_KEY as an environment variable
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "service": "Praxis Advisor - Project Charter Generator",
        "version": "1.0",
        "endpoint": "/webhook/praxis-charter"
    })

@app.route('/webhook/praxis-charter', methods=['POST'])
def generate_charter():
    """
    Generate a project charter using Claude AI
    
    Expected JSON body:
    {
        "projectName": "string (required)",
        "projectGoal": "string (required)",
        "timeline": "string (optional)",
        "budget": "string (optional)",
        "stakeholders": "string (optional)",
        "constraints": "string (optional)",
        "industry": "string (optional)",
        "teamSize": "string (optional)"
    }
    """
    
    # Validate request
    if not request.is_json:
        return jsonify({
            "error": True,
            "message": "Content-Type must be application/json",
            "statusCode": 400
        }), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['projectName', 'projectGoal']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "error": True,
            "message": f"Missing required fields: {', '.join(missing_fields)}",
            "statusCode": 400
        }), 400
    
    # Extract and set defaults
    project_name = data.get('projectName')
    project_goal = data.get('projectGoal')
    timeline = data.get('timeline', 'Not specified')
    budget = data.get('budget', 'Not specified')
    stakeholders = data.get('stakeholders', 'To be determined')
    constraints = data.get('constraints', 'None specified')
    industry = data.get('industry', 'General')
    team_size = data.get('teamSize', 'To be determined')
    
    # Build the system prompt
    system_prompt = """You are Praxis Advisor, an expert strategic business consultant with over 20 years of experience in Agile/Scrum project management, portfolio coordination, and cross-functional team leadership. You specialize in helping organizations deliver transformative outcomes through proven methodologies.

Your approach is practical, evidence-based, and tailored to each client's context. Your deliverables are structured, professional, and include specific next steps."""
    
    # Build the user prompt
    user_prompt = f"""Generate a comprehensive project charter for the following project:

**CRITICAL FORMATTING REQUIREMENTS:**
- Use HTML tables for all spreadsheet-style data
- Use proper HTML markup (tables, divs with classes)
- For Project Phases: DO NOT use |- before month/day bullets
- Include visual gauges for KPIs
- Use color-coded status indicators

**Project Information:**
Project Name: {projectName}
Project Goal: {projectGoal}
Timeline: {timeline if timeline else 'Not specified'}
Budget: {budget if budget else 'Not specified'}
Key Stakeholders: {stakeholders if stakeholders else 'Not specified'}
Constraints: {constraints if constraints else 'Not specified'}
Industry: {industry if industry else 'Not specified'}
Team Size: {teamSize if teamSize else 'Not specified'}

**Generate the charter with these sections:**

## 1. EXECUTIVE SUMMARY
Provide a comprehensive 2-3 paragraph executive summary.

## 2. PROJECT OBJECTIVES
List specific, measurable objectives with clear success criteria.

## 3. SCOPE
Define what is IN SCOPE and OUT OF SCOPE clearly.

## 4. KEY DELIVERABLES SUMMARY
**Format as HTML TABLE:**
<table>
<thead>
<tr>
<th>Deliverable</th>
<th>Description</th>
<th>Due Date</th>
<th>Owner</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>[Deliverable name]</td>
<td>[Brief description]</td>
<td>[Date]</td>
<td>[Team/Person]</td>
<td><span class="status-green">On Track</span></td>
</tr>
<!-- Add 5-8 deliverables -->
</tbody>
</table>

## 5. STAKEHOLDER MATRIX
**Format as HTML TABLE:**
<table>
<thead>
<tr>
<th>Stakeholder</th>
<th>Role</th>
<th>Responsibility</th>
<th>Influence</th>
<th>Engagement Level</th>
</tr>
</thead>
<tbody>
<tr>
<td>[Name/Title]</td>
<td>[Position]</td>
<td>[Key responsibilities]</td>
<td>[High/Medium/Low]</td>
<td>[Daily/Weekly/Monthly]</td>
</tr>
<!-- Add all stakeholders -->
</tbody>
</table>

## 6. PROJECT PHASES AND MILESTONES
**For each phase, format like this (NO |- symbols):**

**Phase 1: Planning & Design (Months 1-2)**
Month 1:
  - Requirement gathering
  - Stakeholder interviews
  - Initial design concepts

Month 2:
  - Design finalization
  - Resource allocation
  - Kickoff meeting

**Phase 2: Development (Months 3-4)**
Month 3:
  - Core development begins
  - First prototype
  
Month 4:
  - Feature completion
  - Internal testing

## 7. CORE PROJECT TEAM
**Format as HTML TABLE:**
<table>
<thead>
<tr>
<th>Name/Role</th>
<th>Responsibilities</th>
<th>Allocation</th>
<th>Skills</th>
<th>Contact</th>
</tr>
</thead>
<tbody>
<tr>
<td>Project Manager</td>
<td>Overall coordination, timeline management, stakeholder communication</td>
<td>100%</td>
<td>PMP, Agile, Leadership</td>
<td>pm@company.com</td>
</tr>
<!-- Add all team members based on team size -->
</tbody>
</table>

## 8. BUDGET ALLOCATION BY CATEGORY
**Format as HTML TABLE:**
<table>
<thead>
<tr>
<th>Category</th>
<th>Amount</th>
<th>Percentage</th>
<th>Justification</th>
</tr>
</thead>
<tbody>
<tr>
<td>Personnel</td>
<td>$XXX,XXX</td>
<td>XX%</td>
<td>[Explanation]</td>
</tr>
<tr>
<td>Technology/Tools</td>
<td>$XX,XXX</td>
<td>XX%</td>
<td>[Explanation]</td>
</tr>
<tr>
<td>Infrastructure</td>
<td>$XX,XXX</td>
<td>XX%</td>
<td>[Explanation]</td>
</tr>
<tr>
<td>Training</td>
<td>$XX,XXX</td>
<td>XX%</td>
<td>[Explanation]</td>
</tr>
<tr>
<td>Contingency (10-15%)</td>
<td>$XX,XXX</td>
<td>XX%</td>
<td>[Explanation]</td>
</tr>
<tr>
<td><strong>TOTAL</strong></td>
<td><strong>[Total Budget]</strong></td>
<td><strong>100%</strong></td>
<td></td>
</tr>
</tbody>
</table>

## 9. BUDGET PHASING BY MONTH
**Format as HTML TABLE:**
<table>
<thead>
<tr>
<th>Month</th>
<th>Planned Spend</th>
<th>Cumulative</th>
<th>% of Total</th>
<th>Key Activities</th>
</tr>
</thead>
<tbody>
<tr>
<td>Month 1</td>
<td>$XX,XXX</td>
<td>$XX,XXX</td>
<td>X%</td>
<td>[Key spending areas]</td>
</tr>
<!-- Add row for each month of timeline -->
</tbody>
</table>

## 10. RISK ASSESSMENT MATRIX
**Format as HTML TABLE with color-coded risk scores:**
<table>
<thead>
<tr>
<th>Risk Description</th>
<th>Probability</th>
<th>Impact</th>
<th>Risk Score</th>
<th>Mitigation Strategy</th>
<th>Contingency Plan</th>
</tr>
</thead>
<tbody>
<tr>
<td>[Risk description]</td>
<td>High/Medium/Low</td>
<td>High/Medium/Low</td>
<td><span class="risk-high">9</span></td>
<td>[Proactive mitigation steps]</td>
<td>[If risk occurs, do this]</td>
</tr>
<!-- Add 5-10 key risks -->
<!-- Use class="risk-high" for scores 7-9, "risk-medium" for 4-6, "risk-low" for 1-3 -->
</tbody>
</table>

**Risk Scoring:** Probability × Impact (both scored 1-3: Low=1, Medium=2, High=3)

## 11. OKRs AND KPIs ALIGNED WITH STRATEGIC OBJECTIVES

### Strategic Alignment
Explain how this project aligns with the organization's strategic plan and objectives.

### Objectives and Key Results (OKRs)

**Objective 1: [Strategic Objective]**
- **Key Result 1:** [Measurable outcome]
- **Key Result 2:** [Measurable outcome]
- **Key Result 3:** [Measurable outcome]

**Objective 2: [Strategic Objective]**
- **Key Result 1:** [Measurable outcome]
- **Key Result 2:** [Measurable outcome]

### Key Performance Indicators (KPIs) Dashboard

**Format with HTML gauges (use appropriate percentages and colors):**

<div class="kpi-container">
  <div class="kpi-item">
    <div class="kpi-gauge" style="--gauge-percent: 85; --gauge-color: #00ff88;">
      <span class="kpi-gauge-text">85%</span>
    </div>
    <div class="kpi-label">On-Time Delivery</div>
    <div class="kpi-target">Target: 90%</div>
  </div>
  
  <div class="kpi-item">
    <div class="kpi-gauge" style="--gauge-percent: 65; --gauge-color: #ffeb3b;">
      <span class="kpi-gauge-text">65%</span>
    </div>
    <div class="kpi-label">Budget Utilization</div>
    <div class="kpi-target">Target: 100%</div>
  </div>
  
  <div class="kpi-item">
    <div class="kpi-gauge" style="--gauge-percent: 92; --gauge-color: #00ff88;">
      <span class="kpi-gauge-text">92%</span>
    </div>
    <div class="kpi-label">Quality Score</div>
    <div class="kpi-target">Target: 95%</div>
  </div>
  
  <div class="kpi-item">
    <div class="kpi-gauge" style="--gauge-percent: 45; --gauge-color: #ff5722;">
      <span class="kpi-gauge-text">45%</span>
    </div>
    <div class="kpi-label">Stakeholder Satisfaction</div>
    <div class="kpi-target">Target: 85%</div>
  </div>
</div>

**Color Coding:**
- Green (#00ff88): 80-100% (On Track)
- Yellow (#ffeb3b): 60-79% (Needs Attention)
- Red (#ff5722): 0-59% (At Risk)

### KPI Tracking Table
**Format as HTML TABLE:**
<table>
<thead>
<tr>
<th>KPI</th>
<th>Current</th>
<th>Target</th>
<th>Status</th>
<th>Trend</th>
<th>Action Required</th>
</tr>
</thead>
<tbody>
<tr>
<td>On-Time Delivery</td>
<td>85%</td>
<td>90%</td>
<td><span class="status-yellow">Needs Attention</span></td>
<td>↗</td>
<td>Accelerate Phase 2 tasks</td>
</tr>
<tr>
<td>Budget Utilization</td>
<td>65%</td>
<td>100%</td>
<td><span class="status-green">On Track</span></td>
<td>→</td>
<td>Continue monitoring</td>
</tr>
<!-- Add 5-8 KPIs total -->
</tbody>
</table>

## 12. SUCCESS CRITERIA
Define clear, measurable success criteria.

## 13. ASSUMPTIONS AND DEPENDENCIES
List key assumptions and external dependencies.

## 14. COMMUNICATION PLAN
Outline how project updates will be shared.

## 15. APPROVAL AND SIGN-OFF
Standard approval section with stakeholder names.

---

**REMEMBER:** 
- Use proper HTML table syntax
- Use color-coded classes (status-green, status-yellow, status-red, risk-high, risk-medium, risk-low)
- Include KPI gauges with appropriate colors
- NO |- symbols in phase bullets
- Be specific and comprehensive
- All budget numbers should add up correctly
- All percentages should total 100%
"""
```

---

## 🎨 Color Coding Reference for Backend

When generating KPI gauges and status badges, use these guidelines:

### **For KPI Gauges:**
```python
# In your prompt, specify colors based on performance:
- 80-100%: use color #00ff88 (green)
- 60-79%: use color #ffeb3b (yellow)
- 0-59%: use color #ff5722 (red)
```

### **For Status Badges:**
```python
# In your prompt, specify classes:
- On Track / Good: <span class="status-green">On Track</span>
- Needs Attention / Warning: <span class="status-yellow">Needs Attention</span>
- At Risk / Critical: <span class="status-red">At Risk</span>
```

### **For Risk Scores:**
```python
# In your prompt, specify classes:
- Score 1-3 (Low): <span class="risk-low">3</span>
- Score 4-6 (Medium): <span class="risk-medium">6</span>
- Score 7-9 (High): <span class="risk-high">9</span>
```

---

## 📦 Complete Backend Code Example

Here's how your complete backend function should look:

```python
from flask import Flask, request, jsonify
from anthropic import Anthropic
import os
from datetime import datetime

app = Flask(__name__)
anthropic = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

@app.route('/webhook/praxis-charter', methods=['POST'])
def generate_charter():
    try:
        data = request.get_json()
        
        projectName = data.get('projectName', '')
        projectGoal = data.get('projectGoal', '')
        timeline = data.get('timeline', '')
        budget = data.get('budget', '')
        stakeholders = data.get('stakeholders', '')
        constraints = data.get('constraints', '')
        industry = data.get('industry', '')
        teamSize = data.get('teamSize', '')
        
        # Use the comprehensive prompt from above
        prompt = f"""[INSERT THE FULL PROMPT FROM ABOVE HERE]"""
        
        message = anthropic.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=8000,  # Increased for longer output with tables
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        
        charter = message.content[0].text
        
        return jsonify({
            'success': True,
            'projectName': projectName,
            'charter': charter,
            'metadata': {
                'generatedAt': datetime.now().isoformat(),
                'estimatedCost': '0.025'  # Adjusted for longer output
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
