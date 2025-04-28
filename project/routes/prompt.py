class Prompt:
    def get_gpt_image_1_prompt(self, design_image):
        return f"""
            You are an expert UI/UX designer tasked with analyzing a design screenshot of any interface, provided as a base64-encoded image: `{design_image}`. Decode and analyze the screenshot to identify its layout (e.g., header, navigation, main content area, sidebar if present, footer), color scheme, typography, and interactive elements (e.g., buttons, links, forms, search bars). The design could belong to any type of interface (e.g., website, app, dashboard) with any purpose.

            Your goal is to evaluate the design against Nielsen's 10 Usability Heuristics and apply a mask or annotation directly on the original design screenshot to highlight areas that violate these heuristics. Do NOT modify, redesign, or generate a new version of the design—only overlay visual indicators on the provided screenshot to mark the problematic areas.

            **Steps**:
            1. **Analyze the Design**:
               - Identify the layout structure (e.g., header, main content, sidebar, footer).
               - Note the color scheme, typography, and interactive elements (e.g., buttons, links, forms, search bars).
               - Understand the design’s purpose based on its content and structure.

            2. **Apply Nielsen's 10 Usability Heuristics**:
               - Evaluate:
               1. Visibility of system status: Check for feedback on actions (e.g., loading indicators).
               2. Match between system and real world: Ensure language/icons are intuitive.
               3. User control and freedom: Look for undo/clear options (e.g., in forms or search bars).
               4. Consistency and standards: Verify consistent styles for navigation, buttons, or links.
               5. Error prevention: Check for input validation (e.g., in forms).
               6. Recognition rather than recall: Ensure active states are highlighted (e.g., current menu item).
               7. Flexibility and efficiency of use: Look for features like shortcuts or filters.
               8. Aesthetic and minimalist design: Identify clutter if present.
               9. Help users recognize, diagnose, and recover from errors: Ensure error messages are clear.
               10. Help and documentation: Check for accessible help options.
               - Identify all violations of the heuristics (up to 5 for clarity) based on the design’s context (e.g., missing clear button in a search bar, lack of active state highlight, no help link).

            3. **Apply Masks or Annotations on the Original Design**:
               - Overlay a visual mask or annotation directly on the provided design screenshot to highlight each identified violation:
               - Use a semi-transparent colored overlay (e.g., red with 30% opacity) to mask the area, ensuring the original design remains fully visible underneath.
               - Alternatively, use a dashed outline (e.g., red dashed border, 2px thickness) or a label (e.g., text box with the heuristic number and brief description like "Heuristic #3: Missing Clear Button").
               - Ensure the mask or annotation does not obscure the original design elements (e.g., text, buttons, images should remain legible).
               - Do NOT modify the design itself—no elements should be changed, added, removed, or redesigned. Only overlay the masks or annotations on the original screenshot.

            **Constraints**:
            - Do NOT change the overall layout, screen size, or resolution of the original screenshot.
            - Do NOT alter the color scheme, typography, imagery, or content of the original design.
            - Only overlay masks or annotations to highlight violations—do not edit or redesign any part of the design.
            - Limit the number of highlighted violations to 5 to avoid overcrowding the output.

            **Output**:
            - The original design screenshot with masks or annotations overlaid on the areas that violate Nielsen’s heuristics.
            - A brief summary (100-150 words) listing:
            - Heuristics violated in the design.
            - The specific areas highlighted (e.g., search bar, navigation menu) and the type of mask/annotation used.
            - A brief explanation of each violation (e.g., why it violates the heuristic)."""
    
    def get_gpt_4o_messages(self,base64_image):
        return [
                    {
                        "role": "system",
                        "content": "You are an expert UX/UI designer. Apply Nielsen's 10 Usability Heuristics."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze the uploaded design image. Identify up to 5 heuristic violations and suggest clear improvements for each."
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
        