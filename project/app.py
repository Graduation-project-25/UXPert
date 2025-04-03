import json
import os
import textwrap
import traceback
import pandas as pd
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import app
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository

from dotenv import load_dotenv
import base64, json, traceback
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import openai
from openai import OpenAI 
import requests
# from flask_limiter import Limiter
import json 

# limiter = Limiter(app1, key_func=lambda: 'global')

load_dotenv()  
# openai.api_key = os.getenv("OPENAI_API_KEY")
# print(f"OpenAI Key: {openai.api_key}")
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Add this to your Flask app startup
try:
    models = openai.models.list()
    print("Available models:", [m.id for m in models.data])
except Exception as e:
    print("OpenAI connection failed:", str(e))

figma_repository = FigmaFeaturesRepository()       
feedback_repository = FeedbackRepository()       
# suggestion_repository = SuggestionsRepository() 
# recognition_suggestion = RecognitionSuggestions()

# Initialize Flask
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    #Extract Design Information
    user_name = data.get("user_name", "Unknown User")
    design_name = data.get("design_name", "Untitled Design")
    page_name = data.get("page_name", "DefaultPage")
    frame_info = data.get("frame", {})
    frame_name = frame_info.get("frameName", "")
    elements = data.get('elements', [])
    
    if not elements:
        return jsonify({"error": "No elements found"}), 400
    print(f"Received design from {user_name}: {design_name} on frame {frame_name}")

    #Convert Elements to DataFrame
    elements_df = pd.DataFrame(elements)
    print(elements_df)

    try:
        # Prepare feature data
        feature_data = {
            "user_name": user_name,
            "design_name": design_name,
            "page_name": page_name,
            "frame_name": frame_name,
            "screen_size": frame_info,
            "elements": elements
        }
        recognition_feedback_list = []  # Store feedback for all elements


        #Insert data into MongoDB
        print("Attempting to insert data into MongoDB...")
        insert_result = figma_repository.update_or_insert_frame(feature_data)
        # insert_result = suggestion_repository.save_suggested_features(feature_data)
        print("Data inserted successfully.")
        if insert_result.matched_count > 0:
            print(f"Frame added to existing design: {design_name}")
        else:
            print(f"New design document created: {design_name}")


        #Retrieve Saved Design
        latest_saved_data = figma_repository.get_saved_design(design_name, frame_name)

        if not latest_saved_data:
            print("Failed to retrieve saved design data from MongoDB")
            return jsonify({"error": "Failed to retrieve saved design data"}), 500


        # Extract elements from the retrieved design data
        frames = latest_saved_data.get("frames", [])
        if not frames:
            return jsonify({"error": "No frames found in the retrieved design"}), 500

        elements_list = [elem for frame in frames for elem in frame.get("elements", [])]

        if not elements_list:
            return jsonify({"error": "No elements found in the retrieved frames"}), 500

        elements_db = pd.DataFrame(elements_list)

        # Run heuristic evaluations
        # Get screen width and height
        screen_width = frame_info["screen_width"]  
        screen_height = frame_info["screen_height"]  

        # Call Rules
        consistency_evaluator = HeuristicFactory.check_rule("consistency")
        minimalist_evaluator = HeuristicFactory.check_rule("minimalist")
        recognition_evaluator = HeuristicFactory.check_rule("recognition")
        error_handling_evaluator = HeuristicFactory.check_rule("errorHandling")
        error_prevention_evaluator = HeuristicFactory.check_rule("errorPrevention")

        # Evaluate Rules
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)
        minimalist_results, minimalist_score = minimalist_evaluator.evaluate_rule({"elements": elements}, screen_width, screen_height)
        error_handling_results = error_handling_evaluator.evaluate_rule(elements_df)
        error_prevention_results = error_prevention_evaluator.evaluate_rule(elements_db)
        for element in elements:
            recognition_results = recognition_evaluator.evaluate_rule(element, element["type"], screen_width, screen_height, element["isIconLabeled"], element["width"], element["height"])
            if recognition_results:  
                recognition_feedback = {
                    "element_id": element["id"],
                    "element_name": element["name"],
                    "element_type": element["type"],
                    "Feedback": recognition_results,  
                }
                recognition_feedback_list.append(recognition_feedback)  # Store feedback for each element
                print("************************************************************************")
                print(element["name"])
                print(element["width"])
                print(element["height"])
                print(recognition_feedback)
                print("************************************************************************")


        # Prepare human-readable feedback
        consistency_feedback = {
            "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
            "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
            "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
            # "TotalConsistency": f"Total consistency score is {consistency_results.get('TotalConsistency', 0)}%.",
            "Feedback": consistency_results.get('Feedback', {})
        }

        error_feedback = {
            "ErrorPreventionScore": f"Error Prevention Score: {error_prevention_results.get('ErrorPreventionScore', 0)}%.",
            "ValidationIssues": error_prevention_results.get("ValidationIssues", []),
            "ConfirmationIssues": error_prevention_results.get("ConfirmationIssues", []),
            "Feedback": error_prevention_results.get("Feedback", {})
        }
        
        error_handling_feedback = {
            "ErrorHandlingScore": f"Error Handling Score: {error_handling_results.get('ErrorHandlingScore', 0)}%.",
            "ErrorIssues": error_handling_results.get("ErrorIssues", []),
            "RecoveryIssues": error_handling_results.get("RecoveryIssues", []),
            "Feedback": error_handling_results
        }
        minimalist_feedback = {
            "Feedback": minimalist_results,  # List of feedback messages from Minimalist
            # "Score": f"Final Score: {minimalist_score:.2f}%"  # Score from Minimalist
        }

        feedback_data = {
            "error_prevention_results": error_prevention_results,
            "consistency_results": consistency_results,
            "error_handling_results": error_handling_results,
            "minimalist_results": minimalist_feedback,  
        }
        if recognition_feedback_list:  # Add only if there are results
            feedback_data["recognition_results"] = recognition_feedback_list

        # Update feedback in database
        update_result = feedback_repository.update_feedback(design_name, frame_name, feedback_data)

        if update_result.matched_count == 0:
            print("Error updating feedback in MongoDB.")
            return jsonify({"error": "Failed to update feedback in database"}), 500
        print("Feedback saved successfully.")


        # Prepare final response
        response_data = {
            "message": "Design processed successfully!",
            "status": 200,
            "error_prevention_results": error_feedback,
            "consistency_results": consistency_feedback,
            "error_handling_results": error_handling_feedback,
            "minimalist_results": minimalist_feedback,
        }
        if recognition_feedback_list:  # Add only if there are results
            response_data["recognition_results"] = recognition_feedback_list


        
        print("Sending to Figma:", response_data) 
        # recognition_suggestion.save_updated_elements(design_name, frame_name)
        return jsonify(response_data), 200
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# @app.route('/modify-design', methods=['POST'])
# def modify_design():
#     try:
#         print("Received modify-design request")  # Debug log
#         data = request.get_json()
#         if not data or 'screenshot' not in data or 'elements' not in data:
#             print("Missing required data")  # Debug log
#             return jsonify({"error": "Missing required data"}), 400

#         screenshot_b64 = data['screenshot'].split(',')[1]
#         figma_json = data['elements']
#         print(f"Elements received: {json.dumps(figma_json, indent=2)[:500]}...")  # Debug log

#         NIELSEN_PROMPT = """Analyze this UI design against the 10 UI/UX Nielsen's heuristics
#         Return JSON with:
#         - "issues": [{"heuristic": 1, "element": "button1", "problem": "No loading indicator"}]
#         - "changes": [{"element": "button1", "property": "color", "new_value": "#3366FF"}]
#         - "dalle_prompt": "Redesign description for DALL-E"
#         """

#         print("Calling GPT-4o...")  # Debug log
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {
#                     "role": "user", 
#                     "content": [
#                         {"type": "text", "text": f"{NIELSEN_PROMPT}\n\nCurrent Design:\n{json.dumps(figma_json)}"},
#                         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}}
#                     ]
#                 }
#             ],
#             response_format={"type": "json_object"},
#             max_tokens=2000
#         )
        
#         ai_response = json.loads(response.choices[0].message.content)
#         print(f"AI Response: {json.dumps(ai_response, indent=2)}")  # Debug log

#         print("Generating DALL-E image...")  # Debug log
#         img_response = client.images.generate(
#             model="dall-e-3",
#             prompt = f"""
# Create an improved version of THIS EXACT UI DESIGN that fixes the identified heuristic violations.
# MAINTAIN ALL OF THESE ORIGINAL ELEMENTS:
# - Color scheme
# - Layout structure
# - Typography
# - Core visual identity

# ONLY MAKE THESE SPECIFIC CHANGES TO IMPROVE USABILITY:
# {ai_response.get('dalle_prompt')}

# Important constraints:
# 1. Keep 90% of the original design unchanged
# 2. Only modify elements that violate heuristics
# 3. Preserve all branding elements
# 4. Maintain identical dimensions and proportions
# """,         
#             size="1024x1024",
#             quality="hd"
#         )
#         print(f"DALL-E Response: {img_response}")  # Debug log
#         dalle_url = img_response.data[0].url
#         image_response = requests.get(dalle_url)
#         image_bytes = image_response.content
#         modified_image_b64 = base64.b64encode(image_bytes).decode('utf-8')

       
#         # Build instructions array
#         instructions = []
#         if 'issues' in ai_response:
#             instructions.extend([f"Heuristic {issue.get('heuristic', '?')}: {issue.get('problem', 'No problem description')}" 
#                                for issue in ai_response['issues']])
#         if 'dalle_prompt' in ai_response:
#             instructions.append(ai_response['dalle_prompt'])
#         if not instructions:
#             instructions.append("No specific instructions provided")

#         return jsonify({
#             "status": "success",
#             "modified_image": f"data:image/png;base64,{modified_image_b64}",  # Now sending as base64
#             "modified_json": ai_response.get('changes', []),
#             "analysis": ai_response.get('issues', []),
#             "instructions": instructions
#         })

        
#     except Exception as e:
#         print(f"Error: {str(e)}\n{traceback.format_exc()}")  # Debug log
#         return jsonify({
#             "error": str(e),
#             "traceback": traceback.format_exc()
#         }), 500

# second way 
# try:
#     font = ImageFont.load_default()
# except:
#     font = None

# def apply_text_modification(draw, x, y, text, font_path="arial.ttf", font_size=12):
#     """Apply text modification to image"""
#     try:
#         font = ImageFont.truetype(font_path, font_size)
#     except:
#         font = ImageFont.load_default()
    
#     draw.text((x, y), text, fill="#000000", font=font)

# def apply_color_modification(draw, x, y, width, height, color):
#     """Apply color modification to image"""
#     try:
#         if color.startswith("#"):
#             draw.rectangle([x, y, x+width, y+height], fill=color)
#         elif color.lower() in ["red", "green", "blue", "yellow"]:
#             colors = {
#                 "red": "#FF0000",
#                 "green": "#00FF00",
#                 "blue": "#0000FF",
#                 "yellow": "#FFFF00"
#             }
#             draw.rectangle([x, y, x+width, y+height], fill=colors[color.lower()])
#     except:
#         print(f"Couldn't apply color: {color}")

# def apply_border_modification(draw, x, y, width, height, border_spec):
#     """Apply border modification to image"""
#     try:
#         if "solid" in border_spec.lower():
#             color = border_spec.split("solid")[-1].strip()
#             draw.rectangle([x, y, x+width, y+height], outline=color, width=2)
#     except:
#         print(f"Couldn't apply border: {border_spec}")

# @app.route('/modify-design', methods=['POST', 'OPTIONS'])
# def modify_design():
#     if request.method == 'OPTIONS':
#         return Response(status=200)
    
#     try:
#         data = request.get_json()
#         if not data or 'screenshot' not in data:
#             return jsonify({"error": "Missing screenshot data"}), 400

#         screenshot_b64 = data['screenshot'].split(',')[-1]
        
#         # Step 1: Get precise modification instructions
#         PROMPT = """Analyze this UI design against Nielsen's 10 heuristics and provide EXACT pixel-level modifications. Return JSON with:
#         {
#             "analysis": [{
#                 "heuristic": "Heuristic name",
#                 "element": "UI element",
#                 "problem": "Specific issue",
#                 "solution": "Precise change needed"
#             }],
#             "modifications": [{
#                 "type": "text/color/border",
#                 "x": int, "y": int,
#                 "width": int, "height": int,
#                 "value": "For text: new text, color: hex code, border: '2px solid #color'",
#                 "element_id": "optional element identifier"
#             }]
#         }"""

#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": PROMPT},
#                     {"type": "image_url", "image_url": {
#                         "url": f"data:image/png;base64,{screenshot_b64}"
#                     }}
#                 ]
#             }],
#             response_format={"type": "json_object"},
#             max_tokens=2000
#         )
        
#         # Parse and validate response
#         ai_response = json.loads(response.choices[0].message.content)
#         print("AI Response:", json.dumps(ai_response, indent=2))
        
#         if not ai_response.get("modifications"):
#             raise ValueError("No valid modifications received")

#         # Step 2: Apply modifications precisely
#         original_img = Image.open(BytesIO(base64.b64decode(screenshot_b64)))
#         modified_img = original_img.copy()
#         draw = ImageDraw.Draw(modified_img)
        
#         for mod in ai_response["modifications"]:
#             try:
#                 if mod["type"] == "text":
#                     apply_text_modification(
#                         draw, mod["x"], mod["y"], 
#                         mod["value"]
#                     )
#                 elif mod["type"] == "color":
#                     apply_color_modification(
#                         draw, mod["x"], mod["y"],
#                         mod["width"], mod["height"],
#                         mod["value"]
#                     )
#                 elif mod["type"] == "border":
#                     apply_border_modification(
#                         draw, mod["x"], mod["y"],
#                         mod["width"], mod["height"],
#                         mod["value"]
#                     )
#             except Exception as e:
#                 print(f"Modification failed: {str(e)}")
#                 continue

#         # Convert to base64
#         buffered = BytesIO()
#         modified_img.save(buffered, format="PNG")
#         modified_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

#         return jsonify({
#             "status": "success",
#             "modified_image": f"data:image/png;base64,{modified_b64}",
#             "analysis": ai_response.get("analysis", []),
#             "modifications": ai_response.get("modifications", [])
#         })

#     except Exception as e:
#         print(f"Error: {str(e)}\n{traceback.format_exc()}")
#         return jsonify({
#             "error": str(e),
#             "traceback": traceback.format_exc()
#         }), 500




#  the direct gpt-4o image modificaions trial 

# def extract_image_url(text):
#     """Extract image URL from GPT-4o response"""
#     # Try to find URL in various formats
#     url_patterns = [
#         r'Modified Image:\s*(https?://\S+)',
#         r'Image URL:\s*(https?://\S+)',
#         r'(https?://\S+\.(?:png|jpg|jpeg))'
#     ]
    
#     for pattern in url_patterns:
#         match = re.search(pattern, text)
#         if match:
#             return match.group(1)
#     return None

# @app.route('/modify-design', methods=['POST', 'OPTIONS'])
# def modify_design():
#     if request.method == 'OPTIONS':
#         return Response(status=200)
    
#     try:
#         data = request.get_json()
#         if not data or 'screenshot' not in data:
#             return jsonify({"error": "Missing screenshot data"}), 400

#         screenshot_b64 = data['screenshot'].split(',')[-1]
        
#         # Enhanced prompt with clear instructions
#         PROMPT = """Analyze this UI design against Nielsen's 10 usability heuristics and:
#         1. Generate a modified version with improvements
#         2. List the specific changes made
#         3. Provide the modified image URL
        
#         Format your response EXACTLY like this:
        
#         ### Modified Image ###
#         [INSERT IMAGE URL HERE]
        
#         ### Changes Made ###
#         - Change 1: [description]
#         - Change 2: [description]
#         - etc.
        
#         Focus on these heuristics:
#         1. Visibility of system status
#         2. Match with real world
#         3. User control
#         4. Consistency
#         5. Error prevention
#         6. Recognition
#         7. Flexibility
#         8. Minimalist design
#         9. Error recovery
#         10. Help documentation"""

#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": PROMPT},
#                     {"type": "image_url", "image_url": {
#                         "url": f"data:image/png;base64,{screenshot_b64}"
#                     }}
#                 ]
#             }],
#             max_tokens=2000
#         )
        
#         response_text = response.choices[0].message.content
#         print("AI Response:", response_text)  # Debug output
        
#         # Extract image URL
#         image_url = extract_image_url(response_text)
#         if not image_url:
#             raise ValueError("Could not find image URL in AI response")
        
#         # Download the image
#         image_response = requests.get(image_url)
#         if image_response.status_code != 200:
#             raise ValueError(f"Failed to download image from {image_url}")
        
#         modified_b64 = base64.b64encode(image_response.content).decode('utf-8')
        
#         # Extract changes
#         changes = []
#         if "### Changes Made ###" in response_text:
#             changes_section = response_text.split("### Changes Made ###")[1]
#             changes = [
#                 line.strip() for line in changes_section.split("\n") 
#                 if line.startswith("-")
#             ]
        
#         return jsonify({
#             "status": "success",
#             "modified_image": f"data:image/png;base64,{modified_b64}",
#             "changes": changes,
#             "analysis": response_text
#         })

#     except Exception as e:
#         print(f"Error: {str(e)}\n{traceback.format_exc()}")
#         return jsonify({
#             "error": str(e),
#             "traceback": traceback.format_exc(),
#             "ai_response": response_text if 'response_text' in locals() else None
#         }), 500


@app.route('/modify-design', methods=['POST', 'OPTIONS'])
def modify_design():
    if request.method == 'OPTIONS':
        return Response(status=200)
    
    try:
        data = request.get_json()
        if not data or 'design_json' not in data:
            return jsonify({"error": "Missing design data"}), 400

        design_json = data['design_json']
        screenshot_b64 = data.get('screenshot', '')

        # Enhanced prompt with specific instructions
        PROMPT = """You are a UI/UX expert analyzing a design against Nielsen's 10 usability heuristics. 
        Carefully examine the provided design JSON and identify specific improvements needed.

        For each issue you find:
        1. Specify the exact node_id from the design JSON
        2. Name the specific property to modify (color, text, size, etc.)
        3. Provide the exact new value
        4. Explain which heuristic this addresses
        5. Give a clear reason for the change

        Return a JSON response with this structure:
        {
            "modifications": [
                {
                    "node_id": "I123:45",
                    "property": "color",
                    "value": "#4285F4",
                    "heuristic": "Consistency",
                    "reason": "Primary buttons should use the brand's primary color consistently"
                },
                {
                    "node_id": "I456:78",
                    "property": "text",
                    "value": "Submit Order",
                    "heuristic": "Match with real world",
                    "reason": "The label should use familiar terms that match user mental models"
                }
            ]
        }

        Design JSON:
        {design_json}""".format(design_json=json.dumps(design_json, indent=2))

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a UI/UX expert specializing in applying Nielsen's heuristics to improve designs."
            }, {
                "role": "user",
                "content": PROMPT
            }],
            response_format={ "type": "json_object" },
            temperature=0.7,  # Slightly more creative
            max_tokens=2000
        )
        
        # Parse and validate response
        result = json.loads(response.choices[0].message.content)
        modifications = result.get("modifications", [])
        
        if not modifications:
            # If no modifications found, provide a default response that makes sense
            modifications = [{
                "node_id": "N/A",
                "property": "N/A",
                "value": "N/A",
                "heuristic": "N/A",
                "reason": "The design already follows Nielsen's heuristics well. No modifications needed."
            }]

        return jsonify({
            "status": "success",
            "modifications": modifications,
            "original_image": screenshot_b64
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/proxy-image')
def proxy_image():
    try:
        image_url = request.args.get('url')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(image_url, headers=headers, stream=True)
        return Response(response.iter_content(chunk_size=1024), 
                      content_type=response.headers['Content-Type'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)


