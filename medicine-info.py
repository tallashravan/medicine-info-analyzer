import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from dotenv import load_dotenv
from phi.tools.tavily import TavilyTools
from prompts import INSTRUCTIONS, SYSTEM_PROMPT
import os
from PIL import Image
import io
import csv

# Load Environment Variables
load_dotenv()

# Set API Keys
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize Tavily Agent
tavily_agent = Agent(
    name="tavily",
    instructions=INSTRUCTIONS,
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[TavilyTools()],
    markdown=True,
    system_prompt=SYSTEM_PROMPT
)

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Medicine Analyzer",
    page_icon="💊",
    layout="wide",
)

# App Title and Description
st.title("💊 AI Medicine Analyzer")
st.write(
    "Upload an image of the medicine label to get started. 📸  "
    "Want to see it in action? Explore **Example Images** for a quick demo! 🖼️  "
    "Curious to know more? Check out the **About** tab for details. ℹ️"
)

# Tabs for Main Upload, Example Images, and About
tab1, tab2, tab3, tab4 = st.tabs(["Upload Image", "Example Images", "About", "Feedback"])

### --- TAB 1: UPLOAD IMAGE ---
with tab1:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Upload a Medicine Label Image", type=["png", "jpg", "jpeg"])

    # Function to analyze the image
    def analyze_medicine(image_bytes):
        temp_image_path = "temp_image.jpg"
        try:
            # Save Image Temporarily
            with open(temp_image_path, "wb") as f:
                f.write(image_bytes)

            # Analyze Image with Tavily Agent
            response = tavily_agent.run(
                "Analyze the medicine composition image",
                images=[temp_image_path]
            )
            return response.content

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return "An error occurred while analyzing the image. Please try again later."
        finally:
            os.remove(temp_image_path)

    # Handle Image Upload
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        image = Image.open(uploaded_file)
        image_bytes = io.BytesIO()
        image = image.convert('RGB')
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()

        if st.button("Analyze Uploaded Image"):
            with st.spinner("Analyzing... Please wait."):
                result = analyze_medicine(image_bytes)
                if result.startswith("Error"):
                    st.error(result)
                else:
                    with st.expander("Analysis Results", expanded=True):
                        st.success("Analysis Complete! Here are the details:")
                        st.markdown(result)
    else:
        st.info(
            """
            **Upload an image of the medicine label to get started. 📸**  
            - Want to see it in action? Explore **Example Images** for a quick demo! 🖼️  
            - Curious to know more? Check out the **About** tab for details. ℹ️  
            """
        )
    # Disclaimer
    st.warning("💡 **Disclaimer:** This information is for educational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional.")

### --- TAB 2: EXAMPLE IMAGES ---
with tab2:
    st.header("Example Images")
    example_images = {
        "Example 1": "images/benadryl.jpeg",
        "Example 2": "images/dolo.jpeg",
    }

    cols = st.columns(2)
    for idx, (label, image_path) in enumerate(example_images.items()):
        with cols[idx % 2]:
            st.image(image_path, caption=label, width=300)
            if st.button(f"Analyze {label}"):
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                with st.spinner("Analyzing... Please wait."):
                    result = analyze_medicine(image_bytes)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        with st.expander(f"Analysis Results for {label}", expanded=True):
                            st.success("Analysis Complete! Here are the details:")
                            st.markdown(result)
    
    # Disclaimer
    st.warning("💡 **Disclaimer:** This information is for educational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional.")




### --- TAB 3: ABOUT ---
with tab3:
    st.header("About the AI Medicine Analyzer")
    st.write(
        """
        **AI Medicine Analyzer** is a tool designed to help you quickly understand medicines by analyzing their labels.  
        - Get details about **uses**, **benefits**, **side effects**, and **safety tips**.  
        - Simplified explanations make it accessible to everyone, even kids! 👶  
        - Upload a medicine label to get started.  
        """
    )
    
### --- TAB 3: ABOUT ---
with tab4:
    st.header("💬 Share Your Feedback")
    st.write("We'd love to hear your thoughts about the app! 😊")

    # Create a feedback form
    with st.form(key="feedback_form"):
        name = st.text_input("Name (Optional):")
        feedback = st.text_area("Your Feedback:")
        rating = st.slider("Rate your experience (1 - Poor, 5 - Excellent):", 1, 5, 3)
        submit_button = st.form_submit_button(label="Submit Feedback")

    # Save feedback to CSV
    feedback_file = "local_feedback/feedback.csv"

    # Ensure the directory exists
    if not os.path.exists("local_feedback"):
        os.makedirs("local_feedback")

    if submit_button:
        if feedback:  # Only save if feedback is provided
            # Check if file exists
            file_exists = os.path.exists(feedback_file)
            
            # Write feedback data
            with open(feedback_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:  # Write header if file is new
                    writer.writerow(["Name", "Feedback", "Rating"])
                writer.writerow([name, feedback, rating])
            
            st.success("🎉 Thank you for your feedback! 🙌")
        else:
            st.warning("⚠️ Feedback cannot be empty. Please share your thoughts!")

### --- SUPPORT SECTION ---
st.markdown("---")
st.markdown(
                """
                ### 🌟 Liked the app?  
                Support this project by **giving it a star⭐ on GitHub**!  👉 https://github.com/tallashravan/medicine-info-analyzer  
                """
            )
st.markdown("---")
st.markdown(
                """
                ### 🚀 Want to see more projects like this?  
                **Follow me on GitHub** to stay updated on my latest projects on GitHub**!  👉 https://github.com/tallashravan/""")
st.markdown("---")
st.write("Made with ❤️ by [Shravan](https://github.com/tallashravan/)")