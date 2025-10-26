"""
Praxis Advisor - Project Charter Generator API
A Flask API that uses Claude AI to generate professional project charters
"""

from flask import Flask, request, jsonify
from anthropic import Anthropic
import os
from datetime import datetime

app = Flask(__name__)
rom flask_cors import CORS
CORS(app)
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

**Project Details:**
- Project Name: {project_name}
- Project Goal: {project_goal}
- Timeline: {timeline}
- Budget: {budget}
- Key Stakeholders: {stakeholders}
- Known Constraints: {constraints}
- Industry: {industry}
- Team Size: {team_size}

**Requirements:**
Create a professional project charter that includes:

1. **Executive Summary** (2-3 paragraphs)
   - Project purpose and business case
   - High-level scope
   - Expected benefits

2. **Project Objectives** (3-5 SMART objectives)
   - Specific, Measurable, Achievable, Relevant, Time-bound

3. **Scope Statement**
   - In-scope items (what will be delivered)
   - Out-of-scope items (what won't be included)
   - Key deliverables

4. **Stakeholder Analysis**
   - Primary stakeholders and their roles
   - Influence levels
   - Communication requirements

5. **High-Level Timeline**
   - Major phases
   - Key milestones with estimated dates

6. **Resource Requirements**
   - Team roles needed
   - Key competencies required

7. **Budget Overview**
   - High-level cost categories
   - Budget allocation recommendations

8. **Top 5 Risks**
   - Risk description
   - Impact level (High/Medium/Low)
   - Mitigation strategy

9. **Success Criteria**
   - Key performance indicators
   - Acceptance criteria

10. **Next Steps**
    - Immediate actions needed
    - Timeline for charter approval

Format the output in clean markdown with clear headers and bullet points. Make it ready to present to executive stakeholders."""
    
    try:
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        
        # Extract charter text
        charter_text = message.content[0].text
        
        # Calculate cost (approximate)
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        
        # Claude Sonnet 4.5 pricing: $3 per million input tokens, $15 per million output tokens
        estimated_cost = (input_tokens / 1_000_000 * 3) + (output_tokens / 1_000_000 * 15)
        
        # Build response
        response = {
            "success": True,
            "projectName": project_name,
            "charter": charter_text,
            "metadata": {
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "inputTokens": input_tokens,
                "outputTokens": output_tokens,
                "estimatedCost": f"{estimated_cost:.4f}",
                "model": "claude-sonnet-4-5-20250929"
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error generating charter: {str(e)}",
            "statusCode": 500
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": True,
        "message": "Endpoint not found. Use POST /webhook/praxis-charter",
        "statusCode": 404
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": True,
        "message": "Method not allowed. Use POST request.",
        "statusCode": 405
    }), 405

if __name__ == '__main__':
    # Check if API key is set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
    
    # Run the app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
