class Prompt:
    def __init__(self, design_image):
        self.design_image = design_image
    
    NIELSEN_HEURISTICS = {
        "Visibility of system status": "The system should always keep users informed about what is going on",
        "Match between system and real world": "The system should speak the users' language",
        "User control and freedom": "Users need clearly marked 'emergency exits'",
        "Consistency and standards": "Users should not have to wonder if different words mean the same thing",
        "Error prevention": "Prevent problems from occurring in the first place",
        "Recognition rather than recall": "Minimize the user's memory load",
        "Flexibility and efficiency": "Allow users to tailor frequent actions",
        "Aesthetic and minimalist design": "Dialogues should not contain irrelevant information",
        "Help users recognize errors": "Error messages should be expressed in plain language",
        "Help and documentation": "Even though it's better if the system can be used without documentation"
    }


    def get_gpt_image_1_prompt(self, generated_text_suggestions,screen_width, screen_height):
        return f"""
        Using the uploaded UI design, make the following minimal improvements:
        {generated_text_suggestions} with image size of {screen_width}x{screen_height}

        - Keep the layout, style, theme, and visuals the same.
        - Only apply small UX changes according to the suggestions.
        - Ensure all text remains in English, as in the original design. Do not translate or change the language of any text.
               
        **Constraints**:
        - Do NOT change the overall layout, screen size, or resolution of the original screenshot.
        - Do NOT change the colors, only make it brighter or darker
        - Do NOT alter the color scheme, typography, imagery, or content of the original design.
        - Only overlay masks or annotations to highlight violations—do not edit or redesign any part of the design.
        - Limit the number of highlighted violations to 5 to avoid overcrowding the output."""
    
    def get_gpt_4o_messages(self,base64_image):
        return [
                    {
                        "role": "system",
                        "content": "You are an expert UX/UI designer. Apply Nielsen's 10 Usability Heuristics {NIELSEN_HEURISTICS}."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.get_gpt_4o_analyze_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]

    def get_gpt_4o_analyze_prompt(self):
        return f"""
            You are a usability expert.
            Analyze this uploaded UI design {self.design_image} based on Nielsen's 10 Usability Heuristics.
            Give me:
            1. List of detected heuristic violations (short bullet points)
            2. Small specific suggestions to fix them
            Keep suggestions minimal — don't redesign the whole page.
            """      